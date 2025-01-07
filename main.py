import MetaTrader5 as mt5
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import numpy as np
import time
from datetime import datetime
import requests  # Para comunicação com a API do Telegram

# Configurações do Telegram
TELEGRAM_TOKEN = "8093586455:AAHl5MqLBECNiTW2yZPOLj9djd4lz-1y6oM"
TELEGRAM_CHAT_ID = "6848292341"

# Configurações gerais
TakeProfit = 50
StopLoss = 50
Slippage = 3
DailyProfitTarget = 5.0
Volume = 0.1

# Configuração de pares de moedas
symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD"]

# Inicialização de variáveis
totalProfit = {symbol: 0.0 for symbol in symbols}
dailyTrades = {symbol: 0 for symbol in symbols}
maxDailyTrades = 10  # Limite de 10 entradas por dia

# Função para enviar mensagens no Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Mensagem enviada para o Telegram.")
        else:
            print("Erro ao enviar mensagem no Telegram:", response.text)
    except Exception as e:
        print("Erro ao conectar ao Telegram:", e)

# Inicializando MetaTrader 5
def initialize():
    print("Óptima Trade - Estratégia Scalping iniciada")
    send_telegram_message("Óptima Trade iniciada!")
    if not mt5.initialize():
        error_message = f"Erro ao inicializar MetaTrader5: {mt5.last_error()}"
        print(error_message)
        send_telegram_message(error_message)
        quit()

    # Solicitando credenciais ao usuário
    account_number = int(input("Digite o número da sua conta: "))
    account_password = input("Digite a senha da conta: ")
    server = input("Digite o servidor: ")

    # Conectando à conta
    if not mt5.login(account_number, password=account_password, server=server):
        error_message = f"Erro ao fazer login: {mt5.last_error()}"
        print(error_message)
        send_telegram_message(error_message)
        quit()
    success_message = f"Login realizado com sucesso na conta {account_number}"
    print(success_message)
    send_telegram_message(success_message)

# Finalizando MetaTrader 5
def deinitialize():
    close_all_positions()
    mt5.shutdown()
    send_telegram_message("Óptima Trade encerrada.")

# Função para abrir uma ordem
def open_order(symbol, action):
    # Obter saldo da conta
    account_info = mt5.account_info()
    balance = account_info.balance if account_info else 0.0

    # Calcular o volume com base no saldo da conta (exemplo: mínimo 1% do saldo)
    volume = max(0.01, balance * 0.01)  # Aqui você ajusta conforme o mínimo desejado

    action_type = mt5.ORDER_BUY if action == "buy" else mt5.ORDER_SELL
    price = mt5.symbol_info_tick(symbol).ask if action == "buy" else mt5.symbol_info_tick(symbol).bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": action_type,
        "price": price,
        "sl": price - StopLoss if action == "buy" else price + StopLoss,
        "tp": price + TakeProfit if action == "buy" else price - TakeProfit,
        "deviation": Slippage,
        "magic": 123456,
        "comment": "Óptima Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"Ordem {action} aberta com sucesso para {symbol} com volume {volume}.")
        send_telegram_message(f"Ordem {action} aberta com sucesso para {symbol} com volume {volume}.")
        return True
    else:
        print(f"Erro ao abrir ordem {action} para {symbol}: {result.comment}")
        send_telegram_message(f"Erro ao abrir ordem {action} para {symbol}: {result.comment}")
        return False

# Função para preparar dados para o modelo LSTM
def prepare_data(symbol, timeframe, lookback=50):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, lookback)
    if rates is None or len(rates) == 0:
        return None, None

    data = np.array([rate.close for rate in rates])
    X = np.array([data[i:i+lookback] for i in range(len(data)-lookback)])
    y = np.array([data[i+lookback] for i in range(len(data)-lookback)])

    return X, y

# Função para construir o modelo LSTM
def build_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Função para prever o sinal de compra ou venda
def predict_signal(model, symbol, timeframe, lookback=50):
    X, _ = prepare_data(symbol, timeframe, lookback)
    if X is None:
        return None
    X = np.expand_dims(X, axis=-1)
    prediction = model.predict(X[-1:])
    return prediction[0][0]

# Função para re-treinar o modelo periodicamente
def retrain_model(models, symbol, lookback=50):
    X_train, y_train = prepare_data(symbol, mt5.TIMEFRAME_M1, lookback)
    if X_train is None:
        return models
    X_train = np.expand_dims(X_train, axis=-1)
    models[symbol].fit(X_train, y_train, epochs=1, batch_size=32)  # Treinamento contínuo
    return models

# Função principal
def main():
    initialize()

    # Treinamento inicial do modelo para cada par de moedas
    models = {}
    for symbol in symbols:
        X_train, y_train = prepare_data(symbol, mt5.TIMEFRAME_M1, lookback=50)
        if X_train is None:
            continue
        X_train = np.expand_dims(X_train, axis=-1)
        model = build_lstm_model((X_train.shape[1], 1))
        model.fit(X_train, y_train, epochs=10, batch_size=32)
        models[symbol] = model
    send_telegram_message("Treinamento inicial do modelo concluído.")

    while True:
        try:
            for symbol in symbols:
                # Verificar se o limite diário foi atingido
                if dailyTrades[symbol] >= maxDailyTrades:
                    continue

                # Previsão de sinal
                prediction = predict_signal(models[symbol], symbol, mt5.TIMEFRAME_M1, lookback=50)
                if prediction is not None:
                    last_price = mt5.symbol_info_tick(symbol).last
                    if prediction > last_price:  # Previsão de alta
                        if open_order(symbol, "buy"):
                            dailyTrades[symbol] += 1
                    elif prediction < last_price:  # Previsão de baixa
                        if open_order(symbol, "sell"):
                            dailyTrades[symbol] += 1

                # Verificação de lucro diário para encerrar operações
                if totalProfit[symbol] >= DailyProfitTarget:
                    send_telegram_message(f"Meta de lucro atingida para {symbol}. Parando operações.")
                    continue

            # Re-treinamento do modelo a cada 10 minutos
            models = retrain_model(models, symbol)
            
            # Intervalo de 1 minuto entre execuções
            time.sleep(60)
        except KeyboardInterrupt:
            print("Execução interrompida pelo usuário.")
            send_telegram_message("Execução interrompida pelo usuário.")
            break

    deinitialize()

# Execução
if __name__ == "__main__":
    main()