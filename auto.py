import requests
import pandas as pd
import numpy as np
import time
import hmac
import hashlib

# Configurações iniciais
symbol = 'BTCUSDT'
interval = '5m'
limit = 500  # Dados históricos
lookback = 60  # Período de análise
stop_loss_percentage = 0.10  # Stop Loss de 10%
take_profit_percentage = 0.50  # Take Profit de 50%
api_key = 'iRvIBeyT0fXUmw23NM49sdPzZJCbgqS2h2u7JqByZPfFsWTPUAZdeq7LWXTVaLYq'
api_secret = 'o4k8vMZLERNvSyYqFesxHFdRASFa5gXgfMUIeQ7Ldv0kTtbNR0jkxWXWaSl5WyM6'
alavancagem = 10
percentual_capital = 0.06  # 6% do capital disponível

# Função para obter saldo disponível
def obter_saldo():
    url = 'https://api.binance.com/sapi/v1/margin/account'
    params = {
        'timestamp': int(time.time() * 1000)
    }
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': api_key}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        for asset in data['userAssets']:
            if asset['asset'] == 'USDT':
                return float(asset['free'])
    print("Erro ao obter saldo.")
    return 0

# Função para obter dados de mercado
def obter_dados_binance():
    url = f"https://api.binance.com/api/v3/klines"
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Erro ao obter dados: {response.status_code}")
        return pd.DataFrame()
    data = response.json()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                     'close_time', 'quote_asset_volume', 'number_of_trades',
                                     'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = df['close'].astype(float)
    return df

# Função para calcular indicadores técnicos
def calcular_indicadores(df):
    # Média Móvel Simples (SMA)
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    df['SMA_200'] = df['close'].rolling(window=200).mean()

    # Índice de Força Relativa (RSI)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df

# Função para enviar ordens
def enviar_ordem(tipo, quantidade):
    url = 'https://api.binance.com/api/v3/order'
    params = {
        'symbol': symbol,
        'side': tipo,
        'type': 'MARKET',
        'quantity': quantidade,
        'timestamp': int(time.time() * 1000)
    }
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': api_key}
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        print(f"Ordem {tipo} enviada com sucesso.")
    else:
        print(f"Erro ao enviar ordem: {response.json()}")

# Função para analisar o momento e enviar ordens
def analisar_e_operar(df):
    atual = df['close'].iloc[-1]
    saldo_disponivel = obter_saldo()
    quantidade = (saldo_disponivel * percentual_capital * alavancagem) / atual

    print(f"Preço atual: {atual:.2f} USDT")
    
    # Análise Quantitativa: baseando-se em médias móveis e RSI
    sma_50 = df['SMA_50'].iloc[-1]
    sma_200 = df['SMA_200'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    
    print(f"SMA 50: {sma_50:.2f}")
    print(f"SMA 200: {sma_200:.2f}")
    print(f"RSI: {rsi:.2f}")

    if sma_50 > sma_200 and rsi < 30:  # Sinal de compra
        print("ALERTA: Alta significativa prevista. Enviando ordem de COMPRA.")
        enviar_ordem('BUY', round(quantidade, 6))
    elif sma_50 < sma_200 and rsi > 70:  # Sinal de venda
        print("ALERTA: Queda significativa prevista. Enviando ordem de VENDA.")
        enviar_ordem('SELL', round(quantidade, 6))
    else:
        print("Mercado estável. Nenhuma ação realizada.")

# Função principal para análise contínua
def monitorar_mercado():
    print("Iniciando monitoramento do mercado...")
    while True:
        df = obter_dados_binance()
        if df.empty:
            print("Erro ao obter dados, tentando novamente em 1 minuto.")
            time.sleep(60)
            continue
        df = calcular_indicadores(df)
        analisar_e_operar(df)
        print("Aguardando 10 minutos para próxima análise...\n")
        time.sleep(600)  # Espera de 10 minutos entre análises

# Executar o script
if __name__ == "__main__":
    monitorar_mercado()
