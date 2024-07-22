from flask import Flask, request, jsonify
from google.cloud import datastore

app = Flask(__name__)

# Inicializar o cliente Datastore
datastore_client = datastore.Client.from_service_account_json('firebase.json')

def obter_historico_usuario(id_usuario):
    # Consulta ao Datastore para obter o histórico de alimentos do usuário
    historico_ref = datastore_client.query(kind='Historico', ancestor=datastore_client.key('Alimentos', id_usuario)).order('-ID')
    historico_docs = list(historico_ref.fetch())

    alimentos_info = []

    for doc in historico_docs:
        historico_data = dict(doc)
        alimento_id = historico_data['ID_ALIMENTO']
        risco_float = historico_data['RISCO_FLOAT']
        risco_str = historico_data['RISCO_STR']

        # Obter informações adicionais do alimento
        alimento_ref = datastore_client.get(datastore_client.key('ALIMENTO', alimento_id))
        alimento_info = dict(alimento_ref)
        
        # Obter link da imagem do alimento
        imagem_ref = datastore_client.query(kind='IMAGEM').add_filter('ALIMENTO_ID', '=', alimento_id)
        imagem_docs = list(imagem_ref.fetch())
        imagem_url = imagem_docs[0]['IMAGEM'] if imagem_docs else None

        alimentos_info.append({
            'nome': alimento_info['NOME'],
            'risco_float': risco_float,
            'risco_str': risco_str,
            'texto_ajuda': alimento_info['TEXTO_AJUDA'],
            'imageUrl': imagem_url
        })

    return alimentos_info

@app.route('/historico_alimentos', methods=['POST'])
def historico_alimentos():
    # Receber dados JSON da solicitação
    data = request.get_json()
    if not data or 'id_usuario' not in data:
        return jsonify({'error': 'ID do usuário não fornecido'}), 400

    id_usuario = data['id_usuario']

    # Obter o histórico do usuário
    historico = obter_historico_usuario(id_usuario)

    # Retornar o histórico de alimentos
    return jsonify({'historico_alimentos': historico})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
