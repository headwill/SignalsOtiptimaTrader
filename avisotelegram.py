import time
import requests

# Configuração do Telegram
TELEGRAM_BOT_TOKEN = "7526642542:AAEu_z0DMl1k0YvtlA_GvLTRu81KEbNxp7I"
TELEGRAM_GROUP_ID = "-4659620768"

# Mensagem de boas-vindas e explicação do propósito do grupo
message = """

Investidotes;

É um prazer estar com vocês novamente para mais uma negociação. Neste momento, estamos analisando o mercado de criptomoedas. 

Especialistas afirmam que esta volatilidade é característica do mercado cripto, muitas vezes impulsionada por fatores como adoção institucional, decisões regulatórias e oscilações no sentimento do investidor. O Bitcoin continua sendo considerado um ativo de reserva de valor por muitos, especialmente em meio a incertezas econômicas globais.

Desejo que essa jornada seja repleta de ótimos lucros e aprendizado constante. Conte comigo para alcançar seus objetivos no mercado.


🌟 *OPTIMA TRADE* 🔍
"""

# Função para enviar mensagem via Telegram
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

# Enviar a mensagem de boas-vindas
enviar_mensagem_telegram(message)

