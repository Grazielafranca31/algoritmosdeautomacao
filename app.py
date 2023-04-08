from flask import Flask, render_template
import requests
import pandas as pd
import json
import sendgrid
import os
from datetime import date, datetime
from oauth2client.service_account import ServiceAccountCredentials
from sendgrid.helpers.mail import Mail, Email, To, Content
import gspread
from scraper import coleta_dados
from planilha import enviar_dados

app = Flask(__name__)

@app.route("/")
def index():
    table_html = resultado_scraper.to_html()
    return render_template('index.html', table_html=table_html)

@app.route('/sobre')
def coleta_dados_view():
    # Criar uma lista de URLs dos sites a serem coletados
    urls = [
        'https://agenciatatu.com.br/wp-json/wp/v2/posts',
        'https://marcozero.org/wp-json/wp/v2/posts',
        'https://agenciaeconordeste.com.br/wp-json/wp/v2/posts'
    ]

    lista_materias = []

    # Loop através das URLs e coletar dados de cada site
    for url in urls:
        # Adicionar um header para evitar bloqueio por parte do servidor
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        # Coletar os dados do site
        requisicao = requests.get(url, headers=headers).json()

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
    df_ultimas_materias = df_total.tail(3)

    enviar_dados(df_ultimas_materias)
    return str(df_ultimas_materias)

@app.route('/planilha')
def enviar_dados_view():
    GOOGLE_SHEETS_CREDENTIALS = os.environ["GOOGLE_SHEETS_CREDENTIALS"]
    with open("credenciais.json", mode="w") as arquivo:
        arquivo.write(GOOGLE_SHEETS_CREDENTIALS)
    conta = ServiceAccountCredentials.from_service_account_file("credenciais.json")
    api = gspread.authorize(conta)
    planilha_google = api.open_by_key("1CfUaR0wUAYZogt0KFXp3Sh4K0Tm71p4Z7zUMgnJqdbo")
    aba_resultado_consulta = planilha_google.worksheet("Página2")
    aba_resultado_consulta.append_rows(resultado_scraper.values.tolist(), value_input_option="USER_ENTERED")
    print('deu certo!')

@app.route('/coletaplanilha')
def coletar_dados_planilha():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = Credentials.from_service_account_file('credenciais.json', scopes=scopes)
    gc = gspread.authorize(credentials)
    planilha = gc.open_by_key("1CfUaR0wUAYZogt0KFXp3Sh4K0Tm71p4Z7zUMgnJqdbo")
    emails = planilha.worksheet("emails")
    lista_emails = emails.get_all_records()
    return lista_emails
  
@app.route('/enviando')
def enviandoemail(lista_emails, resultado_scraper):
    table_html = resultado_scraper.to_html()
    linhas = []
    texto = f"Nesta semana os veículos independentes do Nordeste publicaram as seguintes matérias:\n{table_html}"
    print(texto)
        
    sg = sendgrid.SendGridAPIClient("SENDGRID")

    for email_dict in lista_emails:
        email = email_dict.get('Email', 'email não encontrado')
        mail = Mail(
            from_email=Email("ola@agenciatatu.com.br"),
            to_emails=To(email),
            subject="Matérias de veículos independentes do Nordeste desta semana",
            plain_text_content=texto
        )

        mail_json = mail.get()
        response = sg.client.mail.send.post(request_body=mail_json)
        print(f"Status do envio para {email}: {response.status_code}")
        print(response.headers)
  
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
