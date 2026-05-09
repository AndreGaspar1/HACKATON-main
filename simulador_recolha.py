from database import criar_base_dados, registar_recolha, registar_recolha_log, ver_historico
import random
import time

print("Simulação de Recolha e Transporte Iniciada")
print("--" * 40)

# Garantir que a base de dados e a tabela existem
criar_base_dados()

# Dados de teste para simulação
pontos_origem = ["Bloco Operatório A", "Bloco Operatório B", "Urgência", "Ortopedia", "Pequena Cirurgia"]
profissionais = ["ENF-1001", "ENF-1002", "AUX-2001", "AUX-2002"]

num_contentores = 4

for i in range(1, num_contentores + 1):
    GRAI = f"CONT-{random.randint(1000, 9999)}"
    GLN = random.choice(pontos_origem)
    GSRN = random.choice(profissionais)
    
    print(f"\n>> Simulação {i}/{num_contentores}: Recolha de material")
    print(f"   GRAI(Contentor)    : {GRAI}")
    print(f"   GLN(Origem)     : {GLN}")
    print(f"   GSRN(Profissional) : {GSRN}")
    
    # Simula o tempo de transporte até à zona suja da CME
    tempo_transporte = random.uniform(1.0, 3.0)
    time.sleep(tempo_transporte)
    
    # Registo na base de dados
    resultado = registar_recolha(GRAI, GLN, GSRN)
    
    if resultado.get("sucesso"):
        print(f"   [REGISTO OK] Contentor {GRAI} entregue na zona suja.")
    else:
        print(f"   [ERRO] Falha no registo do contentor {GRAI}.")

print("\n" + "=" * 40)
print("Fase de recolha concluída. Material pronto para lavagem/esterilização.")
print("=" * 40)

registar_recolha_log(GRAI, GLN, GSRN)  # Guardar um ciclo de recolha para rastreabilidade
ver_historico()