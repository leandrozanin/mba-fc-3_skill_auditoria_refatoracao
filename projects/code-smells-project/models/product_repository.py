from database import get_db


def _serialize(row):
    return dict(row) if row else None


def list_products():
    rows = get_db().execute("SELECT * FROM produtos ORDER BY id").fetchall()
    return [_serialize(row) for row in rows]


def get_product(product_id):
    row = get_db().execute("SELECT * FROM produtos WHERE id = ?", (product_id,)).fetchone()
    return _serialize(row)


def create_product(name, description, price, stock, category):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (name, description, price, stock, category),
    )
    db.commit()
    return cursor.lastrowid


def update_product(product_id, name, description, price, stock, category):
    db = get_db()
    cursor = db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (name, description, price, stock, category, product_id),
    )
    db.commit()
    return cursor.rowcount > 0


def delete_product(product_id):
    db = get_db()
    cursor = db.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
    db.commit()
    return cursor.rowcount > 0


def search_products(term, category=None, price_min=None, price_max=None):
    clauses = []
    parameters = []
    if term:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        parameters.extend((f"%{term}%", f"%{term}%"))
    if category:
        clauses.append("categoria = ?")
        parameters.append(category)
    if price_min is not None:
        clauses.append("preco >= ?")
        parameters.append(price_min)
    if price_max is not None:
        clauses.append("preco <= ?")
        parameters.append(price_max)
    query = "SELECT * FROM produtos"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    rows = get_db().execute(query + " ORDER BY id", parameters).fetchall()
    return [_serialize(row) for row in rows]
