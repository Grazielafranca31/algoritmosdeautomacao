import gspread
import json
import os
import pandas as pd
import sendgrid

from datetime import date, datetime
import requests
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
from sendgrid.helpers.mail import Mail, Email, To, Content

TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]
GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
with open("credenciais.json", mode="w") as arquivo:
  arquivo.write(GOOGLE_SHEETS_CREDENTIALS)
  print("pegou credenciais sheets")
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")
api = gspread.authorize(conta)
planilha_google = api.open_by_key("1CfUaR0wUAYZogt0KFXp3Sh4K0Tm71p4Z7zUMgnJqdbo")
aba_resultado_consulta = planilha_google.worksheet("Página1")
    
app = Flask(__name__)


@app.route("/")
def index():
    return "olá" #print(resultado_scraper)

def coleta_dados_view():
  urls = ['https://agenciatatu.com.br/wp-json/wp/v2/posts',
        'https://marcozero.org/wp-json/wp/v2/posts',
        'https://agenciaeconordeste.com.br/wp-json/wp/v2/posts']

  lista_materias = []

  for url in urls:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
      requisicao = requests.get(url, headers=headers).json()
    except requests.exceptions.RequestException as e:
      print(f"Erro na requisição: {e}")
      
    for materia in requisicao:
      titulo_materia = materia.get('title', {}).get('rendered', '')
      link_materia = materia.get('link', '')

      infos_materia = {'titulo_materia': titulo_materia,
                'link_materia': link_materia,            }
      lista_materias.append(infos_materia)

    df_total = pd.DataFrame(lista_materias)

    df_ultimas_materias = df_total

    exibe = df_ultimas_materias.to_html()

    return exibe

# #RASPA SITES E MOSTRA INFORMAÇÕES COMO DATAFRAME  
# @app.route("/raspagem")
# def coleta_dados_view():
#     # Criar uma lista de URLs dos sites a serem coletados
#     urls = [
#         'https://agenciatatu.com.br/wp-json/wp/v2/posts',
#         'https://marcozero.org/wp-json/wp/v2/posts',
#         'https://agenciaeconordeste.com.br/wp-json/wp/v2/posts'
#     ]

#     lista_materias = []

#     # Loop através das URLs e coletar dados de cada site
#     print("INICIA COLETA DAS URLS")
#     for url in urls:
#         print("Coleta URL")
#         print(url)
#         # Adicionar um header para evitar bloqueio por parte do servidor
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
#         }

#         # Coletar os dados do site
#         requisicao = requests.get(url, headers=headers).json()
#         try:
#             requisicao = requests.get(url, headers=headers).json()
#         except requests.exceptions.RequestException as e:
#             print(f"Erro na requisição: {e}")
          
  
                       
        # Iterar sobre as matérias coletadas
        for materia in requisicao:
            # Extrair o título e link da matéria
            titulo_materia = materia.get('title', {}).get('rendered', '')
            link_materia = materia.get('link', '')

            # Adicionar os dados da matéria à lista de matérias
            infos_materia = {
                'titulo_materia': titulo_materia,
                'link_materia': link_materia,
            }
            lista_materias.append(infos_materia)

    # Transformar a lista de matérias em um DataFrame
    df_total = pd.DataFrame(lista_materias)

    # Selecionar apenas as três últimas matérias
    df_ultimas_materias = df_total

    #enviar_dados(df_ultimas_materias)
    print(df_ultimas_materias)
    print("PEGOU DATAFRAME COM MATERIAS")
    return(df_ultimas_materias)
  
coleta_dados_view()
print("rodou coleta de dados")

#APAGA GOOGLE SHEETS E ATUALIZA COM NOVO DATAFRAME
@app.route("/planilha")
def enviar_dados_view():
    aba_resultado_consulta.batch_clear(['A:Z'])
    aba_resultado_consulta.append_rows(coleta_dados_view().values.tolist(), value_input_option="USER_ENTERED")
    print("Enviado para planilha!")

enviar_dados_view()
  
@app.route("/telegram", methods=["POST"])
def telegram_bot():
    update = request.json
    chat_id = update['message']['chat']['id']
    message = update["message"]["text"]
    first_name = update['message']['from']['first_name']
    last_name = update['message']['from']['last_name']
    user_name = update['message']['from'].get('username', None) # Adicionado o .get() para retornar None caso 'username' não exista
    sender_id = update['message']['from']['id']
    chat_id = update['message']['chat']['id']
    
    if "text" not in update["message"]:
        message = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        if "username" in update["message"]["from"]:
           username = f' @{update["message"]["from"]["username"]}'
        else:
           username = ""
        print(f"Nova mensagem de {first_name}{username} ({chat_id}): {message}")
    
    #planilha2 = []
    
    if "@" in message:
        palavras = message.split(" ")
        for palavra in palavras:
            if "@" in palavra:
                email = palavra
                texto_resposta = f"Obrigada por informar o e-mail {email}. Você começará a receber as notícias de veículos independentes do Nordeste!"
                break
        # Selecionando a primeira planilha
        gc = gspread.service_account(filename='credenciais.json')
        planilha = gc.open('1CfUaR0wUAYZogt0KFXp3Sh4K0Tm71p4Z7zUMgnJqdbo')
        
# @app.route('/telegram', methods=["POST"])
# def telegram_bot():
#     update = request.json
#     chat_id = update['message']['chat']['id']
#     message = update["message"]["text"]
#     first_name = update['message']['from']['first_name']
#     last_name = update['message']['from']['last_name']
#     user_name = update['message']['from']['username']
#     sender_id = update['message']['from']['id']
#     chat_id = update['message']['chat']['id']
#     #planilha2 = []
#     if "@" in message:
#         palavras = message.split(" ")
#         for palavra in palavras:
#             if "@" in palavra:
#                 email = palavra
#                 texto_resposta = f"Obrigada por informar o e-mail {email}. Você começará a receber as notícias de veículos independentes do Nordeste!"
#                 break
#         # Selecionando a primeira planilha
#         gc = gspread.service_account(filename='credenciais.json')
#         planilha = gc.open('nome_da_planilha').sheet1
        planilha.append_row([user_name, chat_id, email])
        nova_mensagem = {"chat_id": chat_id, "text": texto_resposta}
        resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
        print(resposta.text)
        return "Mensagens enviadas no Telegram!"
    else:
        texto_resposta = "Desculpe, este não é um e-mail válido. Pode enviar novamente, por favor?"
        nova_mensagem = {"chat_id": chat_id, "text": texto_resposta}
        resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_API_KEY}/sendMessage", data=nova_mensagem)
        print(resposta.text)
        return "Mensagens enviadas no Telegram!"
          
@app.route("/coletaplanilha")
def coletar_dados_planilha():

    emails = planilha_google.worksheet("emails")
    lista_emails = emails.get_all_records()
    return lista_emails
print(coletar_dados_planilha())

#DISPARA EMAILS COM AS MATÉRIAS QUE ESTÃO NO GOOGLE SHEETS
@app.route('/enviando')
def enviandoemail():
    ultimas_materias = coleta_dados_view()
    lista_emails = coletar_dados_planilha()
    resultado_scraper = []

    news = "\n".join(resultado_scraper)
    linhas = []
    texto = f"Nesta semana os veículos independentes do Nordeste publicaram as seguintes matérias:\n{news}"
    print(texto)
        
    sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)

    for email_dict in lista_emails:
        email = email_dict.get('Email', 'email não encontrado')
        mail = Mail(
            from_email=Email("ola@agenciatatu.com.br"),
            to_emails=email,
            subject="Matérias de veículos independentes do Nordeste desta semana",
            html_content=ultimas_noticias.to_html()
        )

        mail_json = mail.get()
        response = sg.client.mail.send.post(request_body=mail_json)
        print(f"Status do envio para {email}: {response.status_code}")
        print(response.headers)

    return 'E-mails enviados com sucesso!'

# if _name_ == '_main_':
#     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 

# @app.route('/enviando')
# def enviandoemail(lista_emails, resultado_scraper):
#     news = resultado_scraper
#     linhas = []
#     texto = f"Nesta semana os veículos independentes do Nordeste publicaram as seguintes matérias:\n{news}"
#     print(texto)
        
#     sg = sendgrid.SendGridAPIClient("SENDGRID")

#     for email_dict in lista_emails:
#         email = email_dict.get('Email', 'email não encontrado')
#         mail = Mail(
#             from_email=Email("ola@agenciatatu.com.br"),
#             to_emails=To(Email),
#             subject="Matérias de veículos independentes do Nordeste desta semana",
#             plain_text_content=texto
#         )

#         mail_json = mail.get()
#         response = sg.client.mail.send.post(request_body=mail_json)
#         print(f"Status do envio para {Email}: {response.status_code}")
#         print(response.headers)
  
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
