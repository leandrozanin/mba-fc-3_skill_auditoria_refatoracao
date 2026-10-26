from database import get_db

ORDER_STATUSES = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}


def _serialize_orders(rows):
    orders = {}
    for row in rows:
        order = orders.setdefault(row["id"], {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": [],
        })
        if row["produto_id"] is not None:
            order["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(orders.values())


def create_order(user_id, items):
    db = get_db()
    quantities = {}
    for item in items:
        product_id = item["produto_id"]
        quantities[product_id] = quantities.get(product_id, 0) + item["quantidade"]
    with db:
        products = {}
        for product_id, quantity in quantities.items():
            product = db.execute("SELECT id, preco, estoque FROM produtos WHERE id = ?", (product_id,)).fetchone()
            if not product:
                raise ValueError("Produto não encontrado")
            if product["estoque"] < quantity:
                raise ValueError(f"Estoque insuficiente para o produto {product_id}")
            products[product_id] = product
        total = sum(products[product_id]["preco"] * quantity for product_id, quantity in quantities.items())
        cursor = db.execute("INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)", (user_id, total))
        order_id = cursor.lastrowid
        for product_id, quantity in quantities.items():
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (order_id, product_id, quantity, products[product_id]["preco"]),
            )
            updated = db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (quantity, product_id, quantity),
            )
            if updated.rowcount != 1:
                raise ValueError(f"Estoque insuficiente para o produto {product_id}")
    return {"pedido_id": order_id, "total": total}


def list_orders(user_id=None):
    query = """
        SELECT o.*, i.produto_id, i.quantidade, i.preco_unitario, p.nome AS produto_nome
        FROM pedidos o
        LEFT JOIN itens_pedido i ON i.pedido_id = o.id
        LEFT JOIN produtos p ON p.id = i.produto_id
    """
    parameters = ()
    if user_id is not None:
        query += " WHERE o.usuario_id = ?"
        parameters = (user_id,)
    rows = get_db().execute(query + " ORDER BY o.id, i.id", parameters).fetchall()
    return _serialize_orders(rows)


def update_order_status(order_id, new_status):
    if new_status not in ORDER_STATUSES:
        raise ValueError("Status inválido")
    db = get_db()
    with db:
        order = db.execute("SELECT status FROM pedidos WHERE id = ?", (order_id,)).fetchone()
        if not order:
            return False
        if new_status == "cancelado" and order["status"] != "cancelado":
            items = db.execute("SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = ?", (order_id,)).fetchall()
            for item in items:
                db.execute("UPDATE produtos SET estoque = estoque + ? WHERE id = ?", (item["quantidade"], item["produto_id"]))
        db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (new_status, order_id))
    return True
