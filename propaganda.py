import time
import requests

print("""CRIADO POR: WILLIAN DE OLIVEIRA""")

# Configuração do Telegram
TELEGRAM_BOT_TOKEN = "7526642542:AAEu_z0DMl1k0YvtlA_GvLTRu81KEbNxp7I"
TELEGRAM_GROUP_ID = "-4659620768"

# Mensagem a ser enviada
mensagem_vip = (
    "🚀 Transforme seus Resultados no Mercado Financeiro! 🚀\n\n"
    "Amigos, quero compartilhar uma oportunidade incrível para quem está no grupo gratuito "
    "e deseja dar o próximo passo em sua jornada financeira. No nosso Grupo VIP, você não estará apenas "
    "investindo, mas aprendendo a operar de forma independente, com estratégias sólidas e ferramentas que realmente funcionam!\n\n"
    "✅ *Benefícios Exclusivos do Grupo VIP:*\n"
    "- Aprenda a operar por conta própria, com confiança e consistência.\n"
    "- Tenha acesso ao indicador exclusivo que programei especialmente para maximizar seus ganhos no mercado financeiro.\n"
    "- Receba suporte contínuo e personalizado para melhorar suas habilidades e resultados.\n"
    "- Acesso a previsões de preços para negociações em **Binárias** e **Criptomoedas**.\n"
    "- Ensino sobre como operar no mercado financeiro, como funcionam os mercados e as melhores estratégias para ter sucesso.\n"
    "- Aulas diárias com conteúdo exclusivo para aprimorar seu conhecimento e habilidades de negociação.\n\n"
    "💵 *Mensalidade do Grupo VIP:* R$60/mês\n\n"
    "👉 *Entre agora no VIP e comece a transformar sua vida financeira!*\n\n"
    "[**Acesse aqui o Grupo VIP**](https://t.me/+bXOL6kFrfMRmMDgx)\n\n"
    "Espero por você. Vamos juntos!"
)

# Função para enviar a mensagem
def enviar_mensagem_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_GROUP_ID,
        "text": mensagem,
        "parse_mode": "Markdown"  # Formatação para o Telegram
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Erro ao enviar mensagem: {response.text}")

# Envio periódico a cada 1 hora
while True:
    enviar_mensagem_telegram(mensagem_vip)
    print("Mensagem enviada. Aguardando 1 hora para o próximo envio...")
    time.sleep(60 * 60)  # 1 hora em segundos