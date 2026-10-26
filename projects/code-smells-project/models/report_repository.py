from database import get_db


def sales_report():
    db = get_db()
    counts = db.execute("SELECT status, COUNT(*) AS total FROM pedidos GROUP BY status").fetchall()
    order_count = sum(row["total"] for row in counts)
    gross = db.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos").fetchone()[0]
    by_status = {row["status"]: row["total"] for row in counts}
    rate = 0.1 if gross > 10000 else 0.05 if gross > 5000 else 0.02 if gross > 1000 else 0
    discount = round(gross * rate, 2)
    return {
        "total_pedidos": order_count,
        "faturamento_bruto": round(gross, 2),
        "desconto_aplicavel": discount,
        "faturamento_liquido": round(gross - discount, 2),
        "pedidos_pendentes": by_status.get("pendente", 0),
        "pedidos_aprovados": by_status.get("aprovado", 0),
        "pedidos_cancelados": by_status.get("cancelado", 0),
        "ticket_medio": round(gross / order_count, 2) if order_count else 0,
    }
