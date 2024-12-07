import time
import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

print("""CRIADO POR: WILLIAN DE OLIVEIRA""")

# Configuração do Telegram
TELEGRAM_BOT_TOKEN = "7526642542:AAEu_z0DMl1k0YvtlA_GvLTRu81KEbNxp7I"
TELEGRAM_GROUP_ID = "-4659620768"

# Definições de parâmetros
symbol = 'BTCUSDT'
interval = '5m'
limit = 100
lookback = 10
stop_loss_percentage = 0.02  # 2% de Stop Loss
take_profit_percentage = 0.03  # 3% de Take Profit
cotacao_usd_brl = 5.00  # Taxa de câmbio fictícia para conversão USD para BRL

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

# Função para calcular o sinal de compra ou venda
def calcular_sinal(df):
    # Calculando a média móvel
    df['moving_average'] = df['close'].rolling(window=lookback).mean()
    df = df.dropna(subset=['moving_average'])
    df['timestamp_ordinal'] = df['timestamp'].apply(lambda x: x.toordinal())

    # Prevendo o próximo preço usando regressão linear
    model = LinearRegression()
    X = df['timestamp_ordinal'].values.reshape(-1, 1)
    y = df['close'].values
    model.fit(X, y)

    next_time = datetime.now().toordinal() + 1
    next_price = model.predict([[next_time]])
    last_close = df['close'].iloc[-1]

    # Cálculo de variação percentual
    variacao_percentual = ((next_price - last_close) / last_close) * 100

    # Cálculo de Stop Loss e Take Profit com base no preço de fechamento
    stop_loss = last_close * (1 - stop_loss_percentage)
    take_profit = last_close * (1 + take_profit_percentage)

    # Determinar ação com base na variação
    if variacao_percentual > 20:
        action = "⚖️ Comprar agora!"
        trend_message = f"Previsão de alta acentuada para {symbol}: +{variacao_percentual[0]:.2f}%."
    elif variacao_percentual < -20:
        action = "⚖️ Vender agora!"
        trend_message = f"Previsão de baixa acentuada para {symbol}: {variacao_percentual[0]:.2f}%."
    else:
        action = "⚖️ Nenhuma ação recomendada."
        trend_message = f"Tendência estável para {symbol}: {variacao_percentual[0]:.2f}%."

    # Montando mensagem final
    message = (
        f"{action}\n"
        f"{trend_message}\n"
        f"Preço atual: ${last_close:.2f}.\n\n"
        f"*Recomendação de proteção de capital: Meta 15% a 20%*\n\n"
        f"🎯 Take Profit: ${take_profit:.2f}\n"
        f"🛑 Stop Loss: ${stop_loss:.2f}\n"
        f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Relatório de negociação
    lucro_brl = 0
    if action == "⚖️ Comprar agora!":
        lucro_brl = (take_profit - last_close) * cotacao_usd_brl
    elif action == "⚖️ Vender agora!":
        lucro_brl = (last_close - take_profit) * cotacao_usd_brl

    relatorio = {
        "data": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "acao": action,
        "preco_inicial_usd": last_close,
        "preco_final_usd": take_profit,
        "variacao_percentual": variacao_percentual[0],
        "lucro_brl": lucro_brl
    }

    # Salvar o relatório em um arquivo CSV
    relatorio_df = pd.DataFrame([relatorio])
    relatorio_df.to_csv("relatorio_negociacoes.csv", mode='a', header=False, index=False)

    return message

# Função para enviar mensagem para o Telegram
def enviar_mensagem_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_GROUP_ID,
        "text": message,
        "parse_mode": "Markdown"  # Formatação para o Telegram
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Erro ao enviar mensagem: {response.text}")

# Mensagem inicial
mensagem_inicial = (
    "Investidores, espero poder ajudar vocês como o meu criador me instruiu,\n"
    "mas lembrem-se, sou apenas um auxílio para as suas negociações. Sem mais delongas...\n\n"
    "Preparem suas contas, em 1 minuto iniciaremos a negociação."
)
enviar_mensagem_telegram(mensagem_inicial)

time.sleep(60)  # Esperar 1 minuto antes de iniciar

# Loop para envio a cada 10 minutos
while True:
    print("\nInvestidores, preparem suas contas, iniciaremos a análise.")
    
    # Obter dados e calcular sinal
    df = obter_dados_binance()
    mensagem = calcular_sinal(df)
    
    # Enviar sinal
    enviar_mensagem_telegram(mensagem)
    
    # Aguardar 10 minutos antes de repetir a análise
    print("Aguardando 10 minutos para a próxima análise...")
    time.sleep(600)  # 10 minutos em segundos