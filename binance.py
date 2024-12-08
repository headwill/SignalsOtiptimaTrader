import torch
import torch.nn as nn
import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import finta as ft
import time
import hmac
import hashlib

# Definições de parâmetros
symbol = 'BTCUSDT'
interval = '5m'
limit = 5000  # Pega mais dados históricos
lookback = 60  # Lookback maior para capturar melhor a tendência
stop_loss_percentage = 0.02
take_profit_percentage = 0.03
api_key = 'iRvIBeyT0fXUmw23NM49sdPzZJCbgqS2h2u7JqByZPfFsWTPUAZdeq7LWXTVaLYq'
api_secret = 'o4k8vMZLERNvSyYqFesxHFdRASFa5gXgfMUIeQ7Ldv0kTtbNR0jkxWXWaSl5WyM6'

# Função para obter dados da Binance
def obter_dados_binance():
    url = f"https://api.binance.com/api/v3/klines"
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    response = requests.get(url, params=params)
    data = response.json()

    # Organizando os dados no DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                     'close_time', 'quote_asset_volume', 'number_of_trades',
                                     'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['close'] = df['close'].astype(float)
    return df

# Função para normalizar os dados
def normalizar_dados(df):
    scaler = MinMaxScaler(feature_range=(0, 1))
    df_scaled = scaler.fit_transform(df['close'].values.reshape(-1, 1))
    return df_scaled, scaler

# Função para preparar os dados para LSTM
def preparar_dados_lstm(df_scaled, lookback=60):
    X, y = [], []
    for i in range(lookback, len(df_scaled)):
        X.append(df_scaled[i-lookback:i, 0])  # Dados de entrada
        y.append(df_scaled[i, 0])  # Preço alvo (próximo valor)
    return np.array(X), np.array(y)

# Modelo LSTM
class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=50, output_size=1, num_layers=2):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_layer_size, batch_first=True, num_layers=num_layers)
        self.fc = nn.Linear(hidden_layer_size, output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        predictions = self.fc(lstm_out[:, -1])
        return predictions

# Função para calcular RSI e outras métricas
def indicadores_tecnicos(df):
    df['RSI'] = ft.RSI(df, period=14)
    df['EMA_50'] = ft.EMA(df, period=50)
    df['EMA_200'] = ft.EMA(df, period=200)
    df['Jaw'] = ft.EMA(df, period=13)  # Alligator
    df['Teeth'] = ft.EMA(df, period=8)
    df['Lips'] = ft.EMA(df, period=5)
    return df

# Função para calcular saldo disponível
def obter_saldo():
    url = 'https://api.binance.com/api/v3/account'
    params = {
        'timestamp': int(time.time() * 1000),
        'recvWindow': 5000
    }
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': api_key}
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    balance = next(item for item in data['balances'] if item['asset'] == 'USDT')
    return float(balance['free'])

# Função para enviar uma ordem de mercado
def enviar_ordem(tipo_ordem, quantidade):
    url = 'https://api.binance.com/api/v3/order'
    params = {
        'symbol': symbol,
        'side': tipo_ordem,
        'type': 'MARKET',
        'quantity': quantidade,
        'timestamp': int(time.time() * 1000),
        'recvWindow': 5000
    }
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': api_key}
    response = requests.post(url, params=params, headers=headers)
    return response.json()

# Função para calcular sinal de venda
def calcular_sinal_venda(df, model, scaler):
    df_scaled, _ = normalizar_dados(df)
    X, y = preparar_dados_lstm(df_scaled)
    X = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(y, dtype=torch.float32)

    # Realizando a previsão usando o modelo LSTM
    with torch.no_grad():
        model.eval()
        predicted = model(X)
        predicted_price = scaler.inverse_transform(predicted.numpy().reshape(-1, 1))

    last_close = df['close'].iloc[-1]
    predicted_price = predicted_price[-1][0]

    # Cálculo de variação percentual
    variacao_percentual = ((predicted_price - last_close) / last_close) * 100

    # Analisando indicadores técnicos
    rsi = df['RSI'].iloc[-1]
    ema_50 = df['EMA_50'].iloc[-1]
    ema_200 = df['EMA_200'].iloc[-1]
    jaw = df['Jaw'].iloc[-1]
    teeth = df['Teeth'].iloc[-1]
    lips = df['Lips'].iloc[-1]

    # Gerando sinal de venda
    if rsi > 70 and ema_50 < ema_200 and jaw < teeth < lips:
        action = "💥 Vender agora!"
        trend_message = f"Previsão de queda para {symbol}: RSI alto ({rsi:.2f}), indicando sobrecompra. "
    elif variacao_percentual < -20:
        action = "💥 Vender agora!"
        trend_message = f"Previsão de queda acentuada para {symbol}: -{variacao_percentual:.2f}%. "
    else:
        action = "✅ Nenhuma ação recomendada."
        trend_message = f"Tendência estável para {symbol}: {variacao_percentual:.2f}%. "

    # Montando mensagem final
    message = (
        f"{action}\n"
        f"{trend_message}\n"
        f"Preço atual: ${last_close:.2f}.\n\n"
        f"*Recomendação de proteção de capital: Meta 15% a 20%*\n\n"
    )
    print(message)

    # Ações de compra e venda
    saldo_disponivel = obter_saldo()
    quantidade_para_comprar = saldo_disponivel * 0.06 / last_close  # 6% do capital disponível

    if action == "💥 Vender agora!":
        print(f"Vendendo {quantidade_para_comprar} {symbol}")
        resultado = enviar_ordem('SELL', quantidade_para_comprar)
        print(f"Resultado da venda: {resultado}")
    elif action == "✅ Nenhuma ação recomendada.":
        print("Nenhuma operação realizada.")

# Execução do código
if __name__ == "__main__":
    model, scaler = treinar_modelo()
    df = obter_dados_binance()
    df = indicadores_tecnicos(df)
    calcular_sinal_venda(df, model, scaler)