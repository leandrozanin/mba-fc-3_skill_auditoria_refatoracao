from flask import Blueprint, jsonify

from controllers import health_controller, order_controller, product_controller, user_controller

api = Blueprint("api", __name__)


@api.get("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@api.get("/produtos")
def list_products():
    return product_controller.list_products()


@api.get("/produtos/busca")
def search_products():
    return product_controller.search_products()


@api.get("/produtos/<int:product_id>")
def get_product(product_id):
    return product_controller.get_product(product_id)


@api.post("/produtos")
def create_product():
    return product_controller.create_product()


@api.put("/produtos/<int:product_id>")
def update_product(product_id):
    return product_controller.update_product(product_id)


@api.delete("/produtos/<int:product_id>")
def delete_product(product_id):
    return product_controller.delete_product(product_id)


@api.get("/usuarios")
def list_users():
    return user_controller.list_users()


@api.get("/usuarios/<int:user_id>")
def get_user(user_id):
    return user_controller.get_user(user_id)


@api.post("/usuarios")
def create_user():
    return user_controller.create_user()


@api.post("/login")
def login():
    return user_controller.login()


@api.post("/pedidos")
def create_order():
    return order_controller.create_order()


@api.get("/pedidos")
def list_orders():
    return order_controller.list_orders()


@api.get("/pedidos/usuario/<int:user_id>")
def list_user_orders(user_id):
    return order_controller.list_user_orders(user_id)


@api.put("/pedidos/<int:order_id>/status")
def update_order_status(order_id):
    return order_controller.update_order_status(order_id)


@api.get("/relatorios/vendas")
def sales_report():
    return order_controller.sales_report()


@api.get("/health")
def health():
    return health_controller.health()


@api.post("/admin/reset-db")
def reset_database():
    return jsonify({"erro": "Endpoint desativado"}), 403


@api.post("/admin/query")
def execute_query():
    return jsonify({"erro": "Endpoint removido por segurança"}), 410


@api.get("/admin/query")
def removed_query_endpoint():
    return jsonify({"erro": "Endpoint removido por segurança"}), 410
