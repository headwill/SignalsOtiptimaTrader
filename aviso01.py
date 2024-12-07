import requests
import schedule
import time
import os

# Configuração do Telegram
TELEGRAM_BOT_TOKEN = "7526642542:AAEu_z0DMl1k0YvtlA_GvLTRu81KEbNxp7I"
TELEGRAM_GROUP_ID = "-4659620768"
CAMINHO_IMAGEM = "/storage/emulated/0/sinopse/W.jpg"  # Corrigido para o caminho absoluto correto

# Verificando se o arquivo existe
if os.path.exists(CAMINHO_IMAGEM):  # Corrigido para a variável com o nome correto
    print("Arquivo encontrado!")

    # Envia a imagem
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(CAMINHO_IMAGEM, "rb") as imagem:  # Corrigido para usar CAMINHO_IMAGEM
        payload = {
            "chat_id": TELEGRAM_GROUP_ID,
            "caption": "Junte-se ao time vencedor com o *Optima Trade*!Investir em renda variável é a escolha dos visionários que buscam aproveitar as melhores oportunidades do mercado financeiro. No entanto, sabemos que o caminho para o sucesso é árduo. Com grandes riscos vêm grandes recompensas, mas a chave para prosperar está em uma gestão de risco sólida e estratégias bem definidas. Nosso compromisso é guiá-lo nessa jornada, fornecendo as melhores recomendações para que você maximize seus lucros com segurança",  # Adicionando uma legenda para a imagem
            "parse_mode": "Markdown"  # Formatação para a legenda
        }
        files = {"photo": imagem}
        response = requests.post(url, data=payload, files=files)
        if response.status_code == 200:
            print("Imagem enviada com sucesso!")
        else:
            print(f"Erro ao enviar imagem: {response.text}")
else:
    print("Arquivo não encontrado. Verifique o caminho.")


def enviar_mensagem_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_GROUP_ID,
        "text": message,
        "parse_mode": "Markdown"  # Formatação para o Telegram
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Mensagem com link enviada com sucesso!")
    else:
        print(f"Erro ao enviar mensagem com link: {response.text}")

# Função para enviar a imagem e depois a mensagem com o link
def enviar_conteudo():
    # Primeiro envia a imagem
    if os.path.exists(CAMINHO_IMAGEM):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open(CAMINHO_IMAGEM, "rb") as imagem:
            payload = {
                "chat_id": TELEGRAM_GROUP_ID,
                "caption": "Junte-se ao time vencedor com o *Optima Trade*!",
                "parse_mode": "Markdown"
            }
            files = {"photo": imagem}
            response = requests.post(url, data=payload, files=files)
            if response.status_code == 200:
                print("Imagem enviada com sucesso!")
            else:
                print(f"Erro ao enviar imagem: {response.text}")
    
    # Mensagem com link (exemplo)
    message = "Confira nossas dicas e estratégias no Optima Trade!"
    # Depois envia a mensagem com o link
    enviar_mensagem_telegram(message)

# Agendar as mensagens para as 8h e 17h
schedule.every().day.at("08:00").do(enviar_conteudo)
schedule.every().day.at("17:00").do(enviar_conteudo)

# Loop para agendar as mensagens
while True:
    schedule.run_pending()
    time.sleep(1)