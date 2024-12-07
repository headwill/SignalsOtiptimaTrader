import time
import requests

# Configuração do Telegram
TELEGRAM_BOT_TOKEN = "7526642542:AAEu_z0DMl1k0YvtlA_GvLTRu81KEbNxp7I"
TELEGRAM_GROUP_ID = "-4659620768"

message = """

Investidores,

Investir em renda variável é a escolha dos visionários que buscam aproveitar as melhores oportunidades do mercado financeiro. No entanto, sabemos que o caminho para o sucesso é cheio de desafios e incertezas. Mas, com a estratégia certa e o parceiro certo, você pode alcançar seus objetivos.

Com grandes riscos vêm grandes recompensas, mas a chave para prosperar está em uma gestão de risco sólida e estratégias bem definidas. Até mesmo os investidores mais experientes enfrentam desafios, mas com a ajuda certa, esses desafios se transformam em oportunidades.

No Optima Trade, nosso compromisso é guiá-lo nessa jornada, fornecendo as melhores recomendações para que você maximize seus lucros com segurança. Lembre-se, investir é sobre visão e estratégia.

Caso ainda não tenha conta em uma corretora, aproveite a oportunidade para se juntar aos melhores no mercado de criptomoedas.

🌟 Abra já sua conta na Binance 🌟
https://www.binance.info/activity/referral-entry/CPA/together-v4?hl=en&ref=CPA_0010YMQBYS

Estamos prontos para transformar desafios em conquistas. Invista com confiança e conte conosco para alcançar seus objetivos financeiros!

🌟 OPTIMA TRADE – Seu parceiro em negociações de sucesso! 🔍
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
