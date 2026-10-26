from flask import jsonify

from database import get_db


def health():
    db = get_db()
    counts = {
        "produtos": db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0],
        "usuarios": db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0],
        "pedidos": db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0],
    }
    return jsonify({"status": "ok", "database": "connected", "counts": counts, "versao": "1.0.0"})
