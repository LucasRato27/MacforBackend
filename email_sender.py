import yagmail
import datetime
import os

def enviar_email(destinatario, assunto, mensagem):
    remetente_email = os.getenv("EMAIL_USER")
    remetente_senha = os.getenv("EMAIL_PASSWORD")

    # Configurar o yagmail
    yag = yagmail.SMTP(remetente_email, remetente_senha)
    yag.send(to=destinatario, subject=assunto, contents=mensagem)
    print("E-mail enviado com sucesso!")

# Verificar o dia da semana (0 = segunda-feira, 6 = domingo)
hoje = datetime.datetime.now().weekday()

# Executar o envio de e-mail apenas na segunda-feira
if hoje == 0:
    destinatario = "beatriz.guimaraes@macfor.com.br"
    assunto = "Lembrete do Preenchimento Runrunnit"
    mensagem = ("Boa tarde, Beatriz!\n"
                "Não esqueça de preencher o formulário sobre os ocorridos com os clientes: "
                "https://runrun.it/share/form/_IcBdNN_Xfc5D9Fi\n"
                "Agradecemos desde já, ITA Júnior.")
    enviar_email(destinatario, assunto, mensagem)
else:
    print("Hoje não é o dia de envio de e-mail.")
