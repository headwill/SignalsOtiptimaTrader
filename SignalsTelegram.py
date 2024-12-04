import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

print(""" CRIADO POR: WILLIAN DE OLIVEIRA""")

# Configuração do Telegram
TELEGRAM_BOT_TOKEN = "7526642542:AAEu_z0DMl1k0YvtlA_GvLTRu81KEbNxp7I"
TELEGRAM_GROUP_ID = "-4659620768"

# Definições de parâmetros
symbol = 'BTCUSDT'
interval = '15m'
limit = 100
lookback = 10
stop_loss_percentage = 0.02  # 2% de Stop Loss
take_profit_percentage = 0.03  # 3% de Take Profit

# Coleta de dados de preço da Binance
url = f"https://api.binance.com/api/v3/klines"
params = {
    'symbol': symbol,
    'interval': interval,
    'limit': limit
}
response = requests.get(url, params=params)
data = response.json()

# Organizando dados no DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                 'close_time', 'quote_asset_volume', 'number_of_trades', 
                                 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df['close'] = df['close'].astype(float)

# Calculando média móvel
df['moving_average'] = df['close'].rolling(window=lookback).mean()

# Calculando drawdown
df['peak'] = df['close'].cummax()
df['drawdown'] = (df['close'] - df['peak']) / df['peak']

# Prevendo próximo preço usando regressão linear
df = df.dropna(subset=['moving_average'])
df['timestamp_ordinal'] = df['timestamp'].apply(lambda x: x.toordinal())

model = LinearRegression()
X = df['timestamp_ordinal'].values.reshape(-1, 1)
y = df['close'].values
model.fit(X, y)

# Previsão do próximo preço de fechamento
next_time = datetime.now().toordinal() + 1
next_price = model.predict([[next_time]])

# Sinal de Compra ou Venda com base na previsão
last_close = df['close'].iloc[-1]

# Cálculo de Stop Loss e Take Profit com base no preço de fechamento
stop_loss = last_close * (1 - stop_loss_percentage)
take_profit = last_close * (1 + take_profit_percentage)

# Verificando se a tendência é de alta, baixa ou lateral
if next_price > last_close:
    trend_signal = "Alta"
    action = f"📈 Comprar agora! Previsão de alta para {symbol}. Preço atual: ${last_close:.2f}"
elif next_price < last_close:
    trend_signal = "Baixa"
    action = f"📉 Vender agora! Previsão de baixa para {symbol}. Preço atual: ${last_close:.2f}"
else:
    trend_signal = "Lateral"
    action = f"⚖️ Tendência lateral para {symbol}. Nenhuma ação recomendada."

# Mensagem com Stop Loss e Take Profit
message = (
    f"{action}\n"
    f"🎯 Take Profit: ${take_profit:.2f}\n"
    f"🛑 Stop Loss: ${stop_loss:.2f}\n"
    f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# Função para enviar mensagem ao Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_GROUP_ID, 
        "text": message,
        "disable_notification": False  # Garante que a notificação será enviada
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Erro ao enviar mensagem: {response.text}")

# Enviando sinal ao Telegram
send_telegram_message(message)

# Exibir no terminal
print("\nDados de Preço com Média Móvel e Drawdown:")
print(df[['timestamp', 'close', 'moving_average', 'drawdown']].tail(10))
print("\nPrevisão do próximo preço de fechamento:", next_price[0])
print("\nSinal de tendência:", trend_signal)