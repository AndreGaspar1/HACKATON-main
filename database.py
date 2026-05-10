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
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS descontaminacao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lote_id TEXT,
        timestamp TEXT, 
        temp_descontaminacao REAL,
        pressao_descontaminacao REAL,
        detergente_diluicao_ok INTEGER, -- 1 para Sim, 0 para Não
        tempo_imersao_minutos INTEGER,
        valor_atp REAL,
        resultado_whiteley TEXT
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
# 6 Tabela de armazenamento e distribuição
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS armazenamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gtin TEXT,
        numero_serie TEXT,
        lote_id TEXT,
        data_validade TEXT,
        gln_localizacao TEXT,
        estado TEXT DEFAULT 'Em Armazém',
        timestamp TEXT
    )
""")
# 7 Tabela de Utilização Clínica (Ligação Utente - Dispositivo)
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
# Atualizar a função de gravação:
def guardar_descontaminacao(lote_id, temperatura, pressao, diluicao_ok, tempo_imersao, valor_atp, resultado_whiteley):
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO descontaminacao (
            lote_id, timestamp, temp_descontaminacao, pressao_descontaminacao, 
            detergente_diluicao_ok, tempo_imersao_minutos, valor_atp, resultado_whiteley
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (lote_id, datetime.now().isoformat(), temperatura, pressao, diluicao_ok, tempo_imersao, valor_atp, resultado_whiteley))
    conn.commit()
    conn.close()


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

def registar_armazenamento(gtin, serial, lote, validade, gln):
    """Regista a entrada de material no armazém com localização específica."""
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO armazenamento (gtin, numero_serie, lote_id, data_validade, gln_localizacao, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (gtin, serial, lote, validade, gln, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def obter_proximo_fefo():
    """Identifica o item com validade mais curta disponível em armazém."""
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, gtin, numero_serie, lote_id, data_validade, gln_localizacao 
        FROM armazenamento 
        WHERE estado = 'Em Armazém'
        ORDER BY data_validade ASC LIMIT 1
    """)
    registo = cursor.fetchone()
    conn.close()
    return registo

def registar_expedicao(id_armazenamento):
    """Atualiza o estado do material para expedido."""
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE armazenamento SET estado = 'Expedido' WHERE id = ?", (id_armazenamento,))
    conn.commit()
    conn.close()
def ver_historico_armazenamento():
    """Consulta e imprime o histórico de entrada e saída do armazém."""
    import sqlite3
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, numero_serie, lote_id, data_validade, gln_localizacao, estado, timestamp FROM armazenamento")
    registos = cursor.fetchall()
    conn.close()
    
    print("\n--- Histórico de Armazenamento e Distribuição ---")
    if not registos:
        print("Nenhum registo encontrado.")
        return
        
    for r in registos:
        print(f"ID:{r[0]} | SN:{r[1]} | Lote:{r[2]} | Validade:{r[3]} | GLN:{r[4]} | Estado:{r[5]} | Data:{r[6]}")

def baixar_inventario_esteril(gtin, serial):
    """
    Remove o dispositivo do inventário ativo alterando o seu estado.
    Retorna o lote associado para efeitos de validação de segurança (Hard Stop).
    """
    import sqlite3
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT lote_id FROM armazenamento 
        WHERE gtin = ? AND numero_serie = ? AND estado = 'Expedido'
    """, (gtin, serial))
    registo = cursor.fetchone()
    
    if registo:
        lote_id = registo[0]
        cursor.execute("""
            UPDATE armazenamento 
            SET estado = 'Utilizado Clinicamente' 
            WHERE gtin = ? AND numero_serie = ?
        """, (gtin, serial))
        conn.commit()
        conn.close()
        return lote_id
        
    conn.close()
    return None

def ver_historico_utilizacao():
    """Consulta e expõe os registos de ligação entre utente e dispositivo."""
    import sqlite3
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, id_utente, id_profissional, gtin, lote_id, timestamp, ponto_origem FROM utilizacoes")
    registos = cursor.fetchall()
    conn.close()
    
    print("\n--- Histórico de Utilização Clínica (Registo de Saúde) ---")
    if not registos:
        print("Sem registos de utilização.")
        return
        
    for r in registos:
        print(f"ID:{r[0]} | GSRN(Utente):{r[1]} | GSRN(Profissional):{r[2]} | GTIN:{r[3]} | Lote:{r[4]} | Local:{r[6]} | Data:{r[5]}")