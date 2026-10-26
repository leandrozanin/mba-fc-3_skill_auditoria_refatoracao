import re

from flask import jsonify, request

from models import user_repository

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def list_users():
    return jsonify({"dados": user_repository.list_users(), "sucesso": True})


def get_user(user_id):
    user = user_repository.get_user(user_id)
    if not user:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify({"dados": user, "sucesso": True})


def create_user():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"erro": "Dados inválidos"}), 400
    name = data.get("nome")
    email = data.get("email")
    password = data.get("senha")
    if not all(isinstance(value, str) and value.strip() for value in (name, email, password)):
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400
    email = email.strip().lower()
    if not EMAIL_PATTERN.fullmatch(email):
        return jsonify({"erro": "Email inválido"}), 400
    if user_repository.email_exists(email):
        return jsonify({"erro": "Email já cadastrado"}), 409
    user_id = user_repository.create_user(name.strip(), email, password)
    return jsonify({"dados": {"id": user_id}, "sucesso": True}), 201


def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"erro": "Dados inválidos"}), 400
    email = data.get("email")
    password = data.get("senha")
    if not isinstance(email, str) or not isinstance(password, str) or not email or not password:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400
    user = user_repository.authenticate(email.strip().lower(), password)
    if not user:
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
    return jsonify({"dados": user, "sucesso": True, "mensagem": "Login OK"})
