import google.generativeai as genai
import PIL.Image
from flask import Flask, request
import json
from google.cloud import datastore
import uuid
import os

app = Flask(__name__)

# Ler a chave da API do arquivo
apikey = os.getenv('API_KEY')

genai.configure(api_key=apikey)
model = genai.GenerativeModel('gemini-1.5-flash')

# Acessar a variável de ambiente
datastore_credentials_str = os.getenv('DATASTORE_CREDENTIALS')

# Verificar se as credenciais foram lidas corretamente
if datastore_credentials_str:
    # Carregar as credenciais diretamente
    datastore_credentials = json.loads(datastore_credentials_str)

    # Inicializar o cliente Datastore diretamente com as credenciais
    datastore_client = datastore.Client.from_service_account_info(datastore_credentials)
else:
    raise Exception("Não foi possível ler as credenciais do Datastore")

@app.route("/reconhecer-imagem", methods = ['POST'])
def recImage():
    img = request.files['image']
    user_id = request.form['user_id']
    imagem = PIL.Image.open(img)
    
    response = model.generate_content([imagem,'Eu quero a resposta exatamente nesse formato e você só preence os valores sem mudar nada na estrutura, não coloque a palavra json na resposta, apenas preence os valores, obs se a imagem não for de alimento apenas preencha a primeira variavel chamada e_alimento como False: {"e_alimento": "True/False" , "alimento_nome": "Valor", "ingredientes_com_lactose": "["ingrediente1","ingrediente2"...]", "quantidade_proteina": "Valor", "quantidade_gordura": "Valor", "quantidade_carboidrato": "Valor", "receitasemlactose_link": "link", "quantidade_calorias": "Valor". Obs: O valor de proteina, carboidrato, gordura e caloria é em 100g do alimento.)'], stream=True)
    response.resolve()
    resposta_alimento = json.loads(response.text)

    if resposta_alimento['e_alimento'] == "True":
        response_risco = model.generate_content('O alimento é: ' + resposta_alimento['alimento_nome'] + ', eu quero o risco de um alimento ter lactose e eu quero que você se baseie nos seguintes critérios: Inexistente (0): Definição: Alimentos que não contêm lactose sob nenhuma circunstância; Baixo (1-20): Definição: Alimentos que podem conter lactose em quantidades muito pequenas, geralmente devido a contaminação cruzada ou adição mínima; Médio (21-50): Definição: Alimentos que frequentemente contêm lactose em quantidades moderadas, seja como ingrediente primário ou secundário; Alto (51-80): Definição: Alimentos que geralmente contêm uma quantidade significativa de lactose e são comuns em dietas que incluem produtos lácteos; Muito Alto (81-100): Definição: Alimentos que contêm uma quantidade substancial de lactose e são essencialmente produtos lácteos. Retorne a resposta nesse seguinte formato, apenas preencha sem alterar nada: {"risco_int": "número inteiro do risco", "risco_str": "classificação do risco"}',stream=True)
        response_risco.resolve()
        resposta_risco = json.loads(response_risco.text)
        respostaFinal = {**resposta_alimento, **resposta_risco}
    
    else:
        respostaFinal = resposta_alimento
        
    # Gerar um ID único para o alimento
    alimento_id = str(uuid.uuid4())

    # Salvar as informações no Datastore agrupadas pelo ID do usuário
    key = datastore_client.key('Alimentos', user_id, 'Historico', alimento_id)
    entity = datastore.Entity(key=key)
    entity.update(respostaFinal)
    datastore_client.put(entity)

    return respostaFinal

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)