from fastapi import FastAPI
from database import criar_base_dados, guardar_ciclo, ver_historico, registar_utilizacao, registar_recolha
import sqlite3

app = FastAPI(title="CME - Sistema de Rastreabilidade")

criar_base_dados()

# ─── ROTA 1: Ver todo o histórico ───────────────────────────
@app.get("/historico")
def historico():
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ciclos")
    registos = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "lote_id": r[1],
            "timestamp": r[2],
            "temperatura": round(r[3], 2),
            "pressao": round(r[4], 2),
            "resultado": r[5]
        }
        for r in registos
    ]

# ─── ROTA 2: Ver só os BLOQUEADOS ───────────────────────────
@app.get("/bloqueados")
def bloqueados():
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ciclos WHERE resultado = 'BLOQUEADO'")
    registos = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "lote_id": r[1], "timestamp": r[2], "resultado": r[5]} for r in registos]

# ─── ROTA 3: Pesquisar por lote (Rastreabilidade Inversa) ───
@app.get("/ciclo/{lote_id}")
def ciclo_por_lote(lote_id: str):
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ciclos WHERE lote_id = ?", (lote_id,))
    registos = cursor.fetchall()
    conn.close()
    if not registos:
        return {"erro": f"Lote {lote_id} não encontrado"}
    return [{"id": r[0], "lote_id": r[1], "timestamp": r[2], "temperatura": r[3], "resultado": r[5]} for r in registos]

# ─── ROTA 4: Registar uso de dispositivo num utente ─────────
@app.post("/utilizar")
def utilizar_dispositivo(
    gsrn_utente: str,
    gsrn_profissional: str,
    gtin: str,
    lote_id: str,
    gln_origem: str
):
    resultado = registar_utilizacao(
        gsrn_utente, gsrn_profissional, gtin, lote_id, gln_origem
    )
    return resultado

# ─── ROTA 5: Recall — quem recebeu dispositivos de um lote ──
@app.get("/recall/{lote_id}")
def recall(lote_id: str):
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gsrn_utente, gsrn_profissional, gtin, timestamp, gln_origem
        FROM utilizacoes
        WHERE lote_id = ?
    """, (lote_id,))
    registos = cursor.fetchall()
    conn.close()

    if not registos:
        return {"mensagem": f"Nenhuma utilização registada para o lote {lote_id}"}

    return {
        "lote_id": lote_id,
        "total_utentes_afetados": len(registos),
        "utilizacoes": [
            {
                "gsrn_utente": r[0],
                "gsrn_profissional": r[1],
                "gtin": r[2],
                "timestamp": r[3],
                "gln_origem": r[4]
            }
            for r in registos
        ]
    }

# ─── ROTA 6: Registar recolha e transporte ──────────────────
@app.post("/recolha")
def recolha_material(
    id_contentor: str,
    ponto_origem: str,
    id_profissional: str
):
    resultado = registar_recolha(id_contentor, ponto_origem, id_profissional)
    return resultado
