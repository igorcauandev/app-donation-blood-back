from flask import Flask, request, jsonify
import json
import os

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ARQUIVO = 'data.json'
TIPOS_SANGUINEOS  = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
STATUS_BOLSA      = ['ativo', 'inativo']
STATUS_CAMPANHA   = ['ativa', 'inativa', 'expirada']


def carregar_dados():
    with open(ARQUIVO, 'r') as f:
        return json.load(f)


def salvar_dados(dados):
    with open(ARQUIVO, 'w') as f:
        json.dump(dados, f, indent=2)


def proximo_id(lista):
    maior = 0
    for item in lista:
        n = int(item.get("id"))
        if n > maior:
            maior = n
    return maior + 1


@app.get('/bolsas/<int:id>')
def get_bolsa(id):
    dados = carregar_dados()
    for bolsa in dados['bolsas']:
        if bolsa.get('id') == id:
            return jsonify(bolsa), 200
    return jsonify({"mensagem": f"Bolsa com id {id} não encontrada"}), 404


@app.get('/bolsas')
def get_bolsas():
    dados = carregar_dados()
    tipo   = request.args.get('tipoSanguineo')
    status = request.args.get('status')
    centro = request.args.get('idCentro')

    resultado = []
    for bolsa in dados['bolsas']:
        if tipo   and bolsa.get('tipoSanguineo') != tipo:
            continue
        if status and bolsa.get('status') != status:
            continue
        if centro and str(bolsa.get('idCentro')) != str(centro):
            continue
        resultado.append(bolsa)

    return jsonify(resultado), 200


@app.put('/bolsas/<int:id>')
def atualizar_bolsa(id):
    dados_req = request.json
    dados_req.pop('id', None)

    campos = [
        ('tipoSanguineo', str,   False),
        ('idPaciente',    int,   False),
        ('idDoacao',      int,   False),
        ('idCentro',      int,   False),
        ('volume',        float, False),
        ('status',        str,   False),
        ('dataValidade',  str,   False),
    ]
    for campo, tipo, obrigatorio in campos:
        valor = dados_req.get(campo)
        if obrigatorio and not valor:
            return jsonify({"mensagem": f"Campo {campo} é obrigatório"}), 400
        if valor and type(valor) is not tipo:
            return jsonify({"mensagem": f"Campo {campo} deve ser do tipo {tipo.__name__}"}), 422

    if dados_req.get('tipoSanguineo') and dados_req['tipoSanguineo'] not in TIPOS_SANGUINEOS:
        return jsonify({"mensagem": f"tipoSanguineo inválido. Aceitos: {TIPOS_SANGUINEOS}"}), 422

    if dados_req.get('status') and dados_req['status'] not in STATUS_BOLSA:
        return jsonify({"mensagem": f"status inválido. Aceitos: {STATUS_BOLSA}"}), 422

    dados = carregar_dados()

    for bolsa in dados['bolsas']:
        if bolsa.get('id') == id:
            bolsa.update(dados_req)
            salvar_dados(dados)
            return jsonify({"mensagem": "Bolsa atualizada com sucesso!"}), 200

    return jsonify({"mensagem": f"Bolsa com id {id} não encontrada"}), 404


@app.delete('/bolsas/<int:id>')
def deletar_bolsa(id):
    dados = carregar_dados()

    for bolsa in dados['bolsas']:
        if bolsa.get('id') == id:
            dados['bolsas'].remove(bolsa)
            salvar_dados(dados)
            return jsonify({"mensagem": "Bolsa removida com sucesso!"}), 200

    return jsonify({"mensagem": f"Bolsa com id {id} não encontrada"}), 404


@app.get('/pacientes/<int:id>')
def get_paciente(id):
    dados = carregar_dados()
    for paciente in dados['pacientes']:
        if paciente.get('id') == id:
            return jsonify(paciente), 200
    return jsonify({"mensagem": f"Paciente com id {id} não encontrado"}), 404


@app.get('/pacientes')
def get_pacientes():
    dados = carregar_dados()
    tipo     = request.args.get('tipoSanguineo')
    genero   = request.args.get('genero')
    elegivel = request.args.get('elegivelParaDoar')

    resultado = []
    for paciente in dados['pacientes']:
        if tipo     and paciente.get('tipoSanguineo') != tipo:
            continue
        if genero   and paciente.get('genero') != genero:
            continue
        if elegivel and str(paciente.get('elegivelParaDoar')) != str(elegivel):
            continue
        resultado.append(paciente)

    return jsonify(resultado), 200


@app.post('/pacientes')
def criar_paciente():
    dados_req = request.json

    campos = [
        ('nome',             str,   True),
        ('endereco',         dict,  True),
        ('email',            str,   False),
        ('telefone',         str,   False),
        ('tipoSanguineo',    str,   False),
        ('idade',            int,   False),
        ('genero',           str,   False),
        ('peso',             float, False),
        ('altura',           float, False),
        ('dataNascimento',   str,   False),
        ('elegivelParaDoar', bool,  False),
    ]
    for campo, tipo, obrigatorio in campos:
        valor = dados_req.get(campo)
        if obrigatorio and not valor:
            return jsonify({"mensagem": f"Campo {campo} é obrigatório"}), 400
        if valor and type(valor) is not tipo:
            return jsonify({"mensagem": f"Campo {campo} deve ser do tipo {tipo.__name__}"}), 422

    if dados_req.get('tipoSanguineo') and dados_req['tipoSanguineo'] not in TIPOS_SANGUINEOS:
        return jsonify({"mensagem": f"tipoSanguineo inválido. Aceitos: {TIPOS_SANGUINEOS}"}), 422

    dados = carregar_dados()
    dados_req['id'] = proximo_id(dados['pacientes'])
    dados['pacientes'].append(dados_req)
    salvar_dados(dados)
    return jsonify({"mensagem": "Paciente cadastrado com sucesso!"}), 201


@app.put('/pacientes/<int:id>')
def atualizar_paciente(id):
    dados_req = request.json
    dados_req.pop('id', None)

    campos = [
        ('nome',             str,   True),
        ('endereco',         dict,  True),
        ('email',            str,   False),
        ('telefone',         str,   False),
        ('tipoSanguineo',    str,   False),
        ('idade',            int,   False),
        ('genero',           str,   False),
        ('peso',             float, False),
        ('altura',           float, False),
        ('dataNascimento',   str,   False),
        ('elegivelParaDoar', bool,  False),
    ]
    for campo, tipo, obrigatorio in campos:
        valor = dados_req.get(campo)
        if obrigatorio and not valor:
            return jsonify({"mensagem": f"Campo {campo} é obrigatório"}), 400
        if valor and type(valor) is not tipo:
            return jsonify({"mensagem": f"Campo {campo} deve ser do tipo {tipo.__name__}"}), 422

    if dados_req.get('tipoSanguineo') and dados_req['tipoSanguineo'] not in TIPOS_SANGUINEOS:
        return jsonify({"mensagem": f"tipoSanguineo inválido. Aceitos: {TIPOS_SANGUINEOS}"}), 422

    dados = carregar_dados()

    for paciente in dados['pacientes']:
        if paciente.get('id') == id:
            paciente.update(dados_req)
            salvar_dados(dados)
            return jsonify({"mensagem": "Paciente atualizado com sucesso!"}), 200

    return jsonify({"mensagem": f"Paciente com id {id} não encontrado"}), 404


@app.delete('/pacientes/<int:id>')
def deletar_paciente(id):
    dados = carregar_dados()

    for paciente in dados['pacientes']:
        if paciente.get('id') == id:
            dados['pacientes'].remove(paciente)
            salvar_dados(dados)
            return jsonify({"mensagem": "Paciente removido com sucesso!"}), 200

    return jsonify({"mensagem": f"Paciente com id {id} não encontrado"}), 404


@app.get('/doacoes/<int:id>')
def get_doacao(id):
    dados = carregar_dados()
    for doacao in dados['doacoes']:
        if doacao.get('id') == id:
            return jsonify(doacao), 200
    return jsonify({"mensagem": f"Doação com id {id} não encontrada"}), 404


@app.get('/doacoes')
def get_doacoes():
    dados = carregar_dados()
    return jsonify(dados['doacoes']), 200


@app.post('/doacoes')
def criar_doacao():
    dados_req = request.json

    campos = [
        ('idPaciente', int,   True),
        ('dataDoacao', str,   True),
        ('idCentro',   int,   False),
        ('quantidade', float, False),
    ]
    for campo, tipo, obrigatorio in campos:
        valor = dados_req.get(campo)
        if obrigatorio and not valor:
            return jsonify({"mensagem": f"Campo {campo} é obrigatório"}), 400
        if valor and type(valor) is not tipo:
            return jsonify({"mensagem": f"Campo {campo} deve ser do tipo {tipo.__name__}"}), 422

    dados = carregar_dados()

    paciente = None
    for p in dados['pacientes']:
        if p.get('id') == dados_req['idPaciente']:
            paciente = p
            break

    if not paciente:
        return jsonify({"mensagem": "Paciente não encontrado"}), 404

    doacao = {
        "id":         proximo_id(dados['doacoes']),
        "idPaciente": dados_req['idPaciente'],
        "idCentro":   dados_req.get('idCentro'),
        "dataDoacao": dados_req['dataDoacao'],
        "quantidade": dados_req.get('quantidade'),
    }
    dados['doacoes'].append(doacao)

    bolsa = {
        "id":           proximo_id(dados['bolsas']),
        "idDoacao":     doacao['id'],
        "idPaciente":   doacao['idPaciente'],
        "idCentro":     doacao.get('idCentro'),
        "tipoSanguineo": paciente.get('tipoSanguineo', ''),
        "volume":       doacao.get('quantidade'),
        "status":       "ativo",
    }
    dados['bolsas'].append(bolsa)

    salvar_dados(dados)
    return jsonify({"mensagem": "Doação registrada com sucesso!", "doacao": doacao, "bolsa": bolsa}), 201


@app.put('/doacoes/<int:id>')
def atualizar_doacao(id):
    dados_req = request.json
    dados_req.pop('id', None)

    campos = [
        ('idPaciente', int,   True),
        ('dataDoacao', str,   True),
        ('idCentro',   int,   False),
        ('quantidade', float, False),
    ]
    for campo, tipo, obrigatorio in campos:
        valor = dados_req.get(campo)
        if obrigatorio and not valor:
            return jsonify({"mensagem": f"Campo {campo} é obrigatório"}), 400
        if valor and type(valor) is not tipo:
            return jsonify({"mensagem": f"Campo {campo} deve ser do tipo {tipo.__name__}"}), 422

    dados = carregar_dados()

    for doacao in dados['doacoes']:
        if doacao.get('id') == id:
            doacao.update(dados_req)
            salvar_dados(dados)
            return jsonify({"mensagem": "Doação atualizada com sucesso!"}), 200

    return jsonify({"mensagem": f"Doação com id {id} não encontrada"}), 404


@app.delete('/doacoes/<int:id>')
def deletar_doacao(id):
    dados = carregar_dados()

    for doacao in dados['doacoes']:
        if doacao.get('id') == id:
            dados['doacoes'].remove(doacao)
            salvar_dados(dados)
            return jsonify({"mensagem": "Doação removida com sucesso!"}), 200

    return jsonify({"mensagem": f"Doação com id {id} não encontrada"}), 404


@app.get('/centros/<int:id>')
def get_centro(id):
    dados = carregar_dados()
    for centro in dados['centros']:
        if centro.get('id') == id:
            return jsonify(centro), 200
    return jsonify({"mensagem": f"Centro com id {id} não encontrado"}), 404


@app.get('/centros')
def get_centros():
    dados = carregar_dados()
    return jsonify(dados['centros']), 200


@app.post('/centros')
def criar_centro():
    dados_req = request.json

    campos = [
        ('nome',     str, True),
        ('endereco', str, False),
        ('cidade',   str, False),
        ('estado',   str, False),
        ('telefone', str, False),
        ('email',    str, False),
    ]
    for campo, tipo, obrigatorio in campos:
        valor = dados_req.get(campo)
        if obrigatorio and not valor:
            return jsonify({"mensagem": f"Campo {campo} é obrigatório"}), 400
        if valor and type(valor) is not tipo:
            return jsonify({"mensagem": f"Campo {campo} deve ser do tipo {tipo.__name__}"}), 422

    dados = carregar_dados()
    dados_req['id'] = proximo_id(dados['centros'])
    dados['centros'].append(dados_req)
    salvar_dados(dados)
    return jsonify({"mensagem": "Centro cadastrado com sucesso!"}), 201


@app.put('/centros/<int:id>')
def atualizar_centro(id):
    dados_req = request.json
    dados_req.pop('id', None)

    campos = [
        ('nome',     str, True),
        ('endereco', str, False),
        ('cidade',   str, False),
        ('estado',   str, False),
        ('telefone', str, False),
        ('email',    str, False),
    ]
    for campo, tipo, obrigatorio in campos:
        valor = dados_req.get(campo)
        if obrigatorio and not valor:
            return jsonify({"mensagem": f"Campo {campo} é obrigatório"}), 400
        if valor and type(valor) is not tipo:
            return jsonify({"mensagem": f"Campo {campo} deve ser do tipo {tipo.__name__}"}), 422

    dados = carregar_dados()

    for centro in dados['centros']:
        if centro.get('id') == id:
            centro.update(dados_req)
            salvar_dados(dados)
            return jsonify({"mensagem": "Centro atualizado com sucesso!"}), 200

    return jsonify({"mensagem": f"Centro com id {id} não encontrado"}), 404


@app.delete('/centros/<int:id>')
def deletar_centro(id):
    dados = carregar_dados()

    for centro in dados['centros']:
        if centro.get('id') == id:
            dados['centros'].remove(centro)
            salvar_dados(dados)
            return jsonify({"mensagem": "Centro removido com sucesso!"}), 200

    return jsonify({"mensagem": f"Centro com id {id} não encontrado"}), 404


@app.get('/campanhas/<int:id>')
def get_campanha(id):
    dados = carregar_dados()
    for campanha in dados['campanhas']:
        if campanha.get('id') == id:
            return jsonify(campanha), 200
    return jsonify({"mensagem": f"Campanha com id {id} não encontrada"}), 404


@app.get('/campanhas')
def get_campanhas():
    dados = carregar_dados()
    return jsonify(dados['campanhas']), 200


@app.post('/campanhas')
def criar_campanha():
    dados_req = request.json

    campos = [
        ('titulo',     str, True),
        ('descricao',  str, False),
        ('dataInicio', str, False),
        ('dataFim',    str, False),
        ('status',     str, False),
        ('idCentro',   int, False),
    ]
    for campo, tipo, obrigatorio in campos:
        valor = dados_req.get(campo)
        if obrigatorio and not valor:
            return jsonify({"mensagem": f"Campo {campo} é obrigatório"}), 400
        if valor and type(valor) is not tipo:
            return jsonify({"mensagem": f"Campo {campo} deve ser do tipo {tipo.__name__}"}), 422

    if dados_req.get('status') and dados_req['status'] not in STATUS_CAMPANHA:
        return jsonify({"mensagem": f"status inválido. Aceitos: {STATUS_CAMPANHA}"}), 422

    dados = carregar_dados()
    dados_req['id'] = proximo_id(dados['campanhas'])
    dados['campanhas'].append(dados_req)
    salvar_dados(dados)
    return jsonify({"mensagem": "Campanha cadastrada com sucesso!"}), 201


@app.put('/campanhas/<int:id>')
def atualizar_campanha(id):
    dados_req = request.json
    dados_req.pop('id', None)

    campos = [
        ('titulo',     str, True),
        ('descricao',  str, False),
        ('dataInicio', str, False),
        ('dataFim',    str, False),
        ('status',     str, False),
        ('idCentro',   int, False),
    ]
    for campo, tipo, obrigatorio in campos:
        valor = dados_req.get(campo)
        if obrigatorio and not valor:
            return jsonify({"mensagem": f"Campo {campo} é obrigatório"}), 400
        if valor and type(valor) is not tipo:
            return jsonify({"mensagem": f"Campo {campo} deve ser do tipo {tipo.__name__}"}), 422

    if dados_req.get('status') and dados_req['status'] not in STATUS_CAMPANHA:
        return jsonify({"mensagem": f"status inválido. Aceitos: {STATUS_CAMPANHA}"}), 422

    dados = carregar_dados()

    for campanha in dados['campanhas']:
        if campanha.get('id') == id:
            campanha.update(dados_req)
            salvar_dados(dados)
            return jsonify({"mensagem": "Campanha atualizada com sucesso!"}), 200

    return jsonify({"mensagem": f"Campanha com id {id} não encontrada"}), 404


@app.delete('/campanhas/<int:id>')
def deletar_campanha(id):
    dados = carregar_dados()

    for campanha in dados['campanhas']:
        if campanha.get('id') == id:
            dados['campanhas'].remove(campanha)
            salvar_dados(dados)
            return jsonify({"mensagem": "Campanha removida com sucesso!"}), 200

    return jsonify({"mensagem": f"Campanha com id {id} não encontrada"}), 404


app.run(debug=True)
