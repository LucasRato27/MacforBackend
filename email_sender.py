import yagmail

def enviar_email(destinatario, assunto, mensagem):
    remetente_email = "lucas.alencar.sampaio@gmail.com"
    remetente_senha = "Kjvw1761**"

    # Configurar o yagmail
    yag = yagmail.SMTP(remetente_email, remetente_senha)
    yag.send(to=destinatario, subject=assunto, contents=mensagem)
    print("E-mail enviado com sucesso!")

# Exemplo de uso
destinatario = "beatriz.guimaraes@macfor.com.br"
assunto = "Lembrete do Preenchimento Runrunnit"
mensagem = ("Boa tarde, Beatriz!\n Não esqueça de preencher o formulário sobre os ocorridos com os clientes: https://runrun.it/share/form/_IcBdNN_Xfc5D9Fi\n Agradecemos desde já, ITA Júnior.")
enviar_email(destinatario, assunto, mensagem)
