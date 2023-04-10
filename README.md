# Algoritmos de Automacao

## Trabalho final da disciplina de Algoritmos de Automação, do Master em Jornalismo de Dados do Insper.

O objetivo do trabalho é fazer a raspagem de matérias publicadas em veículos de jornalismo independente do Nordeste e enviar para os e-mails cadastrados 1x na semana. 
Para isso, fiz o scraping de três sites de notícias e salvei as matérias em uma planilha. Em uma segunda aba desta mesma planilha, inseri os e-mails que deveriam receber o scraping e integrei ao sedgrid. a automatização foi feita com o Pipedream.

## **O que encontro aqui?**


Esta documentação possui dois arquivos:


#### - app.py: Contém o códigos e a importação da biblioteca para executar as tarefas mencionadas anteriormente;
#### - requirements.txt: Contém as bibliotecas que devem ser instaladas.


## **Configurando o webhook do Telegram Execute o seguinte código:**
O webhook é uma função que é executada apenas uma vez em seu código e permite que receber atualizações do bot e enviar para uma determinada URL. Com o webhook ativo, não é possível utilizar o método getUpdates.

O código do webhook é o seguinte:
```
import getpass import requests

token = getpass.getpass() # token = "..." - não é boa prática! 
dados = {"url": "https://algoritmosautograzi.onrender.com/telegram"} # COLOQUE O SEU!! 
resposta = requests.post(f"https://api.telegram.org/bot{token}/setWebhook", data=dados) 
print(resposta.text)```
