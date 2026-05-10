import sqlite3
import random
from database import criar_base_dados, registar_armazenamento, obter_proximo_fefo, registar_expedicao

def executar_simulacao():
    print("Simulador de Armazenamento e Distribuição Iniciado")
    print("--" * 40)
    
    criar_base_dados()

    # Definição de localizações físicas
    prateleiras = ["GLN-PRAT-01-A", "GLN-PRAT-01-B", "GLN-PRAT-02-A", "GLN-PRAT-03-C"]

    # Recuperar itens recém-embalados para colocar em armazém
    conn = sqlite3.connect("cme.db")
    cursor = conn.cursor()
    cursor.execute("SELECT gtin, numero_serie, lote_id, data_validade FROM embalagem")
    itens_para_armazenar = cursor.fetchall()
    conn.close()

    if not itens_para_armazenar:
        print("[AVISO] Sem itens processados na tabela 'embalagem' para armazenar.")
        return

    print(">> Fase: Armazenamento")
    for item in itens_para_armazenar:
        gtin, serial, lote, validade = item
        localizacao = random.choice(prateleiras)
        
        registar_armazenamento(gtin, serial, lote, validade, localizacao)
        print(f"   [CHECK-IN] SN: {serial} | Local: {localizacao}")

    print("\n" + "=" * 40)
    print(">> Fase: Distribuição (Lógica FEFO)")
    
    # Aplicação da regra First Expired, First Out
    proximo = obter_proximo_fefo()
    
    if proximo:
        id_reg, gtin, serial, lote, validade, gln = proximo
        print(f"ALERTA FEFO: Expedir material com validade mais próxima.")
        print(f"   GTIN: {gtin}")
        print(f"   SN: {serial}")
        print(f"   Lote: {lote}")
        print(f"   Validade (IA 17): {validade}")
        print(f"   Localização (GLN): {gln}")
        
        registar_expedicao(id_reg)
        print("\n[INFO] Saída registada. Material removido do inventário ativo.")
    else:
        print("[ERRO] Falha ao identificar item para expedição.")

if __name__ == "__main__":
    executar_simulacao()