import sqlite3
from datetime import datetime

def criar_base_dados():
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()

# 1 Tabela de recolha e transporte (A origem)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recolhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_recolha TEXT,
            id_contentor TEXT,
            ponto_origem TEXT,
            id_profissional TEXT
        )
    """)
# 2 Tabela de descontaminação 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS descontaminacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id TEXT,
            timestamp TEXT, 
            temp_descontaminacao REAL,
            pressao_descontaminacao REAL
        )
    """)
# 3 Tabela inspeção e embalagem
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embalagem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gtin TEXT,
            numero_serie TEXT,
            lote_id TEXT,
            data_validade TEXT,
            tipo_involucro TEXT,
            timestamp TEXT
        )
    """)
# 4 Tabela principal do ciclo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ciclos_esterilizacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id TEXT,
            autoclave_id TEXT,
            timestamp TEXT,
            temp_esterilizacao REAL,
            pressao_esterilizacao REAL,
            indicador_quimico TEXT,
            indicador_biologico TEXT,
            resultado TEXT
        )
    """)
    # 5 Tabela de associação (Um lote contém vários dispositivos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_ciclo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id TEXT,
            gtin TEXT,
            numero_serie TEXT
        )
    """)
#  Tabela original dos ciclos
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
            id_utente TEXT,
            id_profissional TEXT,
            gtin TEXT,
            lote_id TEXT,
            timestamp TEXT,
            ponto_origem TEXT
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
#base de dados para recolha e transporte
def registar_recolha_log(id_contentor, ponto_origem, id_profissional):
    """
    Regista o evento de recolha na tabela de recolhas.
    Esta função aceita exclusivamente strings, ao contrário da guardar_ciclo.
    """
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    
    # A hora é gerada automaticamente
    timestamp = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO recolhas (timestamp_recolha, id_contentor, ponto_origem, id_profissional)
        VALUES (?, ?, ?, ?)
    """, (timestamp, id_contentor, ponto_origem, id_profissional))
    
    conn.commit()
    conn.close()
    print(f"Log de recolha guardado: Contentor {id_contentor} vindo de {ponto_origem}.")
#base de dados esterilização
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

def registar_utilizacao(id_utente, id_profissional, gtin, lote_id, ponto_origem):
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
        (id_utente, id_profissional, gtin, lote_id, timestamp, ponto_origem)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id_utente, id_profissional, gtin, lote_id, datetime.now().isoformat(), ponto_origem))
    conn.commit()
    conn.close()
    return {"permitido": True, "motivo": "Ciclo conforme — uso autorizado"}

def ver_historico_recolhas():
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recolhas")
    registos = cursor.fetchall()
    conn.close()
    print("\n--- Histórico de Recolhas ---")
    for r in registos:
        print(f"ID:{r[0]} | Data/Hora:{r[1]} | Contentor:{r[2]} | Origem:{r[3]} | Profissional:{r[4]}")

def guardar_descontaminacao(lote_id, temperatura, pressao):
    """Regista os parâmetros finais do ciclo de descontaminação na base de dados."""
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    from datetime import datetime
    cursor.execute("""
        INSERT INTO descontaminacao (lote_id, timestamp, temp_descontaminacao, pressao_descontaminacao)
        VALUES (?, ?, ?, ?)
    """, (lote_id, datetime.now().isoformat(), temperatura, pressao))
    conn.commit()
    conn.close()
    print(f"Registo de descontaminação do lote {lote_id} efetuado.")

def ver_historico_descontaminacao():
    """Consulta e imprime o histórico de lavagem/descontaminação."""
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM descontaminacao")
    registos = cursor.fetchall()
    conn.close()
    print("\n--- Histórico de Descontaminação ---")
    for r in registos:
        print(f"ID:{r[0]} | Lote:{r[1]} | {r[2]} | {r[3]:.1f}°C | {r[4]:.2f} bar")

def registar_inspecao_embalagem(gtin, serial, lote, validade, involucro):
    """Regista a prontidão do dispositivo para esterilização."""
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    from datetime import datetime
    cursor.execute("""
        INSERT INTO embalagem (gtin, numero_serie, lote_id, data_validade, tipo_involucro, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (gtin, serial, lote, validade, involucro, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print(f"Dispositivo {serial} inspecionado e embalado em {involucro}. Lote: {lote}")

def ver_historico_embalagem():
    """Exibe o histórico da Zona Limpa."""
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM embalagem")
    registos = cursor.fetchall()
    conn.close()
    print("\n--- Histórico de Inspeção e Embalagem ---")
    for r in registos:
        print(f"ID:{r[0]} | SN:{r[2]} | Lote:{r[3]} | Validade:{r[4]} | Tipo:{r[5]}")
def guardar_ciclo_esterilizacao(lote_id, autoclave_id, temp, pressao, ind_quimico, ind_biologico, resultado, dispositivos):
    """Guarda os dados do ciclo e associa os dispositivos contidos na carga."""
    from datetime import datetime
    import sqlite3
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    
    # Registo da transação na autoclave
    cursor.execute("""
        INSERT INTO ciclos_esterilizacao (lote_id, autoclave_id, timestamp, temp_esterilizacao, pressao_esterilizacao, indicador_quimico, indicador_biologico, resultado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (lote_id, autoclave_id, datetime.now().isoformat(), temp, pressao, ind_quimico, ind_biologico, resultado))

    # Registo dos itens (IA 10 liga GTINs ao Lote)
    for d in dispositivos:
        cursor.execute("""
            INSERT INTO itens_ciclo (lote_id, gtin, numero_serie)
            VALUES (?, ?, ?)
        """, (lote_id, d['gtin'], d['serial']))

    conn.commit()
    conn.close()

def ver_historico_esterilizacao():
    import sqlite3
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ciclos_esterilizacao")
    ciclos = cursor.fetchall()
    
    print("\n--- Histórico de Esterilização (Validação) ---")
    for c in ciclos:
        print(f"Lote: {c[1]} | Autoclave: {c[2]} | Ind. Químico: {c[6]} | Ind. Biológico: {c[7]} | Resultado Final: {c[8]}")
        
        # Obter os itens pertencentes a este lote
        cursor.execute("SELECT gtin, numero_serie FROM itens_ciclo WHERE lote_id = ?", (c[1],))
        itens = cursor.fetchall()
        print(f"   ↳ Carga ({len(itens)} itens): {itens}")
        
    conn.close()