import math

from flask import jsonify, request

from models import product_repository

VALID_CATEGORIES = {"informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"}


def _payload():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def _valid_product(data):
    name = data.get("nome")
    price = data.get("preco")
    stock = data.get("estoque")
    category = data.get("categoria", "geral")
    if not isinstance(name, str) or not 2 <= len(name.strip()) <= 200:
        return "Nome deve ter entre 2 e 200 caracteres"
    if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price < 0:
        return "Preço inválido"
    if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
        return "Estoque inválido"
    if not isinstance(category, str) or category not in VALID_CATEGORIES:
        return "Categoria inválida"
    description = data.get("descricao", "")
    if not isinstance(description, str):
        return "Descrição inválida"
    return None


def list_products():
    return jsonify({"dados": product_repository.list_products(), "sucesso": True})


def get_product(product_id):
    product = product_repository.get_product(product_id)
    if not product:
        return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404
    return jsonify({"dados": product, "sucesso": True})


def search_products():
    term = request.args.get("q", "").strip()
    category = request.args.get("categoria")
    try:
        price_min = float(request.args["preco_min"]) if "preco_min" in request.args else None
        price_max = float(request.args["preco_max"]) if "preco_max" in request.args else None
    except ValueError:
        return jsonify({"erro": "Faixa de preço inválida"}), 400
    if any(value is not None and (not math.isfinite(value) or value < 0) for value in (price_min, price_max)):
        return jsonify({"erro": "Faixa de preço inválida"}), 400
    products = product_repository.search_products(term, category, price_min, price_max)
    return jsonify({"dados": products, "total": len(products), "sucesso": True})


def create_product():
    data = _payload()
    if data is None:
        return jsonify({"erro": "Dados inválidos"}), 400
    error = _valid_product(data)
    if error:
        return jsonify({"erro": error}), 400
    product_id = product_repository.create_product(
        data["nome"].strip(), data.get("descricao", ""), data["preco"], data["estoque"], data.get("categoria", "geral")
    )
    return jsonify({"dados": {"id": product_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def update_product(product_id):
    if not product_repository.get_product(product_id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    data = _payload()
    if data is None:
        return jsonify({"erro": "Dados inválidos"}), 400
    error = _valid_product(data)
    if error:
        return jsonify({"erro": error}), 400
    product_repository.update_product(
        product_id, data["nome"].strip(), data.get("descricao", ""), data["preco"], data["estoque"], data.get("categoria", "geral")
    )
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"})


def delete_product(product_id):
    if not product_repository.delete_product(product_id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"})
