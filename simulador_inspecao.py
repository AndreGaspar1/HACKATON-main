from database import criar_base_dados, registar_inspecao_embalagem, ver_historico_embalagem
from datetime import datetime, timedelta
import random

print("Simulador de Inspeção e Embalagem (Zona Limpa)")
print("--" * 40)

criar_base_dados()

# Configuração de validade por tipo de invólucro (em dias)
protocolo_validade = {
    "Bolsa": 180,
    "Folha Polipropileno": 365,
    "Contentor Rígido": 1825
}

# Simulação de leitura ótica (GTIN + Serial)
dispositivos_para_embalar = [
    {"gtin": "05601234567890", "serial": "SN-A100"},
    {"gtin": "05601234567890", "serial": "SN-B250"},
    {"gtin": "05609876543210", "serial": "SN-Z999"}
]

# Geração do Lote de Esterilização (IA 10)
lote_esterilizacao = f"LOTE-EST-{random.randint(1000, 9999)}"

for item in dispositivos_para_embalar:
    print(f"\n>> Lendo DataMatrix: GTIN {item['gtin']} | Serial {item['serial']}")
    
    # Seleção do invólucro
    tipo_involucro = random.choice(list(protocolo_validade.keys()))
    dias_validade = protocolo_validade[tipo_involucro]
    
    # Cálculo da Data de Validade (IA 17)
    data_validade = (datetime.now() + timedelta(days=dias_validade)).strftime("%Y-%m-%d")
    
    # Registo
    registar_inspecao_embalagem(
        item['gtin'], 
        item['serial'], 
        lote_esterilizacao, 
        data_validade, 
        tipo_involucro
    )

print("\n" + "=" * 40)
ver_historico_embalagem()