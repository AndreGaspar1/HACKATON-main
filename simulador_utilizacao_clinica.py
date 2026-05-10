import sqlite3
import random
from database import criar_base_dados, registar_utilizacao, baixar_inventario_esteril, ver_historico_utilizacao

def executar_simulacao_clinica():
    print("Simulador de Utilização Clínica")
    print("--" * 40)
    
    criar_base_dados()

    # Identificadores de teste (GSRN)
    base_dados_utentes = ["GSRN-UTENTE-100456", "GSRN-UTENTE-200789"]
    base_dados_profissionais = ["GSRN-CIRURGIAO-991", "GSRN-ENFERMEIRO-882"]
    
    utente_alvo = random.choice(base_dados_utentes)
    profissional_alvo = random.choice(base_dados_profissionais)
    ponto_cuidado = "Bloco Operatório - Sala 3"

    print(">> Fase 1: Identificação de Atores")
    print(f"   Leitura Pulseira Doente      : {utente_alvo}")
    print(f"   Leitura Cartão Profissional  : {profissional_alvo}")

    # Extração de um dispositivo expedido para simular a leitura do invólucro
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT gtin, numero_serie FROM armazenamento WHERE estado = 'Expedido' LIMIT 1")
        dispositivo_alvo = cursor.fetchone()
    except sqlite3.OperationalError:
        dispositivo_alvo = None
    conn.close()

    if not dispositivo_alvo:
        print("\n[FALHA] Não existem dispositivos expedidos no sistema para consumo clínico.")
        return

    gtin_lido, serial_lido = dispositivo_alvo

    print("\n>> Fase 2: Identificação do Material Estéril")
    print(f"   Leitura Ótica (GTIN)         : {gtin_lido}")
    print(f"   Leitura Ótica (Nº Série)     : {serial_lido}")

    print("\n>> Fase 3: Processamento e Ligação Eletrónica")
    
    # Executa a baixa de inventário e recupera o lote para verificação de segurança
    lote_id = baixar_inventario_esteril(gtin_lido, serial_lido)

    if lote_id:
        # Tenta registar o uso. A função registar_utilizacao internamente bloqueia se o lote não estiver APROVADO.
        resultado_seguranca = registar_utilizacao(utente_alvo, profissional_alvo, gtin_lido, lote_id, ponto_cuidado)
        
        if resultado_seguranca.get("permitido"):
            print(f"   [ESTADO] {resultado_seguranca.get('motivo')}")
            print(f"   [SISTEMA] Dispositivo baixado do inventário estéril.")
            print(f"   [SISTEMA] Rastreabilidade unificada ao Registo de Saúde Eletrónico do Utente {utente_alvo}.")
        else:
            print(f"   [HARD STOP] INTERVENÇÃO BLOQUEADA.")
            print(f"   [MOTIVO] {resultado_seguranca.get('motivo')}.")
            print("   Instrução: Reter o material e notificar a Central de Esterilização.")
    else:
        print("   [ERRO] Dispositivo não localizado no inventário de expedição.")

    ver_historico_utilizacao()

if __name__ == "__main__":
    executar_simulacao_clinica()