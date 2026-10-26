from flask import jsonify, request

from models import order_repository, report_repository, user_repository


def create_order():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"erro": "Dados inválidos"}), 400
    user_id = data.get("usuario_id")
    items = data.get("itens")
    if isinstance(user_id, bool) or not isinstance(user_id, int) or not user_repository.get_user(user_id):
        return jsonify({"erro": "Usuário não encontrado"}), 400
    if not isinstance(items, list) or not items:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400
    for item in items:
        if not isinstance(item, dict):
            return jsonify({"erro": "Item inválido"}), 400
        product_id = item.get("produto_id")
        quantity = item.get("quantidade")
        if isinstance(product_id, bool) or not isinstance(product_id, int) or product_id <= 0:
            return jsonify({"erro": "Produto inválido"}), 400
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"erro": "Quantidade inválida"}), 400
    try:
        result = order_repository.create_order(user_id, items)
    except ValueError as error:
        return jsonify({"erro": str(error), "sucesso": False}), 400
    return jsonify({"dados": result, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def list_orders():
    return jsonify({"dados": order_repository.list_orders(), "sucesso": True})


def list_user_orders(user_id):
    return jsonify({"dados": order_repository.list_orders(user_id), "sucesso": True})


def update_order_status(order_id):
    data = request.get_json(silent=True)
    status = data.get("status") if isinstance(data, dict) else None
    try:
        updated = order_repository.update_order_status(order_id, status)
    except ValueError as error:
        return jsonify({"erro": str(error)}), 400
    if not updated:
        return jsonify({"erro": "Pedido não encontrado"}), 404
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"})


def sales_report():
    return jsonify({"dados": report_repository.sales_report(), "sucesso": True})
