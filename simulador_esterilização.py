from database import criar_tabelas_esterilizacao, guardar_ciclo_esterilizacao, ver_historico_esterilizacao
import random
import time

print("Simulador de Esterilização e Validação Iniciado")
print("--" * 40)

criar_tabelas_esterilizacao()

# Identificação do equipamento (GIAI ou GLN)
autoclave_gln = "GLN-AUTOCLAVE-01"

# Identificador de Aplicação 10 (Lote)
lote_id = f"LOTE-EST-{random.randint(1000, 9999)}"

# Array de dispositivos provenientes da Zona Limpa (GTIN + Serial)
dispositivos_carga = [
    {"gtin": "05601234567890", "serial": "SN-A100"},
    {"gtin": "05601234567890", "serial": "SN-B250"},
    {"gtin": "05609876543210", "serial": "SN-Z999"}
]

fases = [
    {"nome": "Pré-vácuo", "temp_alvo": 60, "pressao_alvo": 0.2, "duracao": 2},
    {"nome": "Esterilização", "temp_alvo": 134, "pressao_alvo": 3.0, "duracao": 5},
    {"nome": "Secagem", "temp_alvo": 60, "pressao_alvo": 0.2, "duracao": 2}
]

ciclo_ok = True
temp_esterilizacao = 0.0
pressao_esterilizacao = 0.0

for fase in fases:
    print(f">> Fase: {fase['nome']}")
    temp_real = fase["temp_alvo"] + random.uniform(-0.5, 0.5)
    pressao_real = fase["pressao_alvo"] + random.uniform(-0.05, 0.05)

    if fase["nome"] == "Esterilização":
        temp_esterilizacao = temp_real
        pressao_esterilizacao = pressao_real
        if temp_real < 133.9 or pressao_real < 3.0:
            ciclo_ok = False

    time.sleep(fase["duracao"])

# Anexo de Dados de Validação (Indicadores)
indicador_quimico = "Aprovado (Mudança de Cor)" if ciclo_ok else "Reprovado (Falha na Cor)"
indicador_biologico = "Negativo (Crescimento Zero)" if ciclo_ok else "Positivo (Crescimento Ativo)"
resultado_final = "APROVADO" if ciclo_ok else "BLOQUEADO"

print("\n" + "=" * 40)
print(f"Decisão Técnica - Lote {lote_id} | {autoclave_gln}: {resultado_final}")
print("=" * 40)

# Inserção transacional com dados de validação e carga associada
guardar_ciclo_esterilizacao(
    lote_id,
    autoclave_gln,
    temp_esterilizacao,
    pressao_esterilizacao,
    indicador_quimico,
    indicador_biologico,
    resultado_final,
    dispositivos_carga
)

ver_historico_esterilizacao()