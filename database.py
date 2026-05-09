import sqlite3
from datetime import datetime

def criar_base_dados():
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()

# Tabela de recolha e transporte (A origem)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recolhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_recolha TEXT,
            id_contentor TEXT,
            ponto_origem TEXT,
            id_profissional TEXT
        )
    """)

    # Tabela original dos ciclos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ciclos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id TEXT,
            timestamp TEXT,
            temp_esterilizacao REAL,
            pressao_esterilizacao REAL,
            resultado TEXT
        )
    """)

    # Tabela de dispositivos (O "Quê")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dispositivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gtin TEXT,
            numero_serie TEXT,
            descricao TEXT,
            lote_id TEXT
        )
    """)

    # Tabela de utentes (O "Quem")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilizacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gsrn_utente TEXT,
            gsrn_profissional TEXT,
            gtin TEXT,
            lote_id TEXT,
            timestamp TEXT,
            gln_origem TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Base de dados pronta.")

def registar_recolha(id_contentor, ponto_origem, id_profissional):
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    
    # A hora da recolha é gerada automaticamente no momento da inserção
    cursor.execute("""
        INSERT INTO recolhas (timestamp_recolha, id_contentor, ponto_origem, id_profissional)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().isoformat(), id_contentor, ponto_origem, id_profissional))
    
    conn.commit()
    conn.close()
    
    return {"sucesso": True, "motivo": f"Recolha do contentor {id_contentor} registada."}

def guardar_ciclo(lote_id, temperatura, pressao, resultado):
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ciclos (lote_id, timestamp, temp_esterilizacao, pressao_esterilizacao, resultado)
        VALUES (?, ?, ?, ?, ?)
    """, (lote_id, datetime.now().isoformat(), temperatura, pressao, resultado))
    conn.commit()
    conn.close()
    print(f"Ciclo {lote_id} guardado na base de dados.")

def ver_historico():
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ciclos")
    registos = cursor.fetchall()
    conn.close()
    print("\n--- Histórico de Ciclos ---")
    for r in registos:
        print(f"ID:{r[0]} | Lote:{r[1]} | {r[2]} | {r[3]}°C | {r[5]}")

def registar_utilizacao(gsrn_utente, gsrn_profissional, gtin, lote_id, gln_origem):
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()

    # Hard Stop — só deixa usar se o lote estiver APROVADO
    cursor.execute("""
        SELECT resultado FROM ciclos 
        WHERE lote_id = ? 
        ORDER BY timestamp DESC LIMIT 1
    """, (lote_id,))
    registo = cursor.fetchone()

    if not registo or registo[0] != "APROVADO":
        conn.close()
        return {"permitido": False, "motivo": f"Lote {lote_id} não tem ciclo aprovado"}

    from datetime import datetime
    cursor.execute("""
        INSERT INTO utilizacoes 
        (gsrn_utente, gsrn_profissional, gtin, lote_id, timestamp, gln_origem)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (gsrn_utente, gsrn_profissional, gtin, lote_id, datetime.now().isoformat(), gln_origem))
    conn.commit()
    conn.close()
    return {"permitido": True, "motivo": "Ciclo conforme — uso autorizado"}
