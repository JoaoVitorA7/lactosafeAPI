import google.generativeai as genai
import PIL.Image
from flask import Flask, request
import json
from google.cloud import datastore
import uuid

app = Flask(__name__)

# Ler a chave da API do arquivo
with open('apikey.txt', 'r') as file:
    apikey = file.read().strip()

genai.configure(api_key=apikey)
model = genai.GenerativeModel('gemini-1.5-flash')

# Inicializar o cliente Datastore
datastore_client = datastore.Client.from_service_account_json('firebase.json')

@app.route("/reconhecer-imagem", methods = ['POST'])
def recImage():
    img = request.files['image']
    user_id = request.form['user_id']
    imagem = PIL.Image.open(img)
    response = model.generate_content([imagem,'Eu quero a resposta nesse formato: {"Variavel1": "Valor1", "Variavel2": "Valor2"}, vou deixar os nomes para as variáveis em parenteses para você saber qual nome colocar, se a imagem não for de um alimento preencha a variável "Check" como "False" e retorne apenas ela, em caso dela ser "True" continue para as outras variáveis: É alimento? (Check); Qual alimento é esse? (alimento); Todos os ingredientes na receita que podem conter lactose (ingredientes); Quantidade de proteina gordura e carboidrato em 100g(Proteina) (Gordura) (Carboidrato); Link dessa receita sem lactose (Link); Quantidade de calorias em 100g (Calorias)'], stream=True)
    response.resolve()
    print(response.text)
    respostaFinal = json.loads(response.text)
    
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