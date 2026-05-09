from database import criar_base_dados, registar_recolha, registar_recolha_log, ver_historico_recolhas
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
    id_contentor = f"CONT-{random.randint(1000, 9999)}"
    ponto_origem = random.choice(pontos_origem)
    id_profissional = random.choice(profissionais)
    
    print(f"\n>> Simulação {i}/{num_contentores}: Recolha de material")
    print(f"   GRAI(Contentor)    : {id_contentor}")
    print(f"   GLN(Origem)     : {ponto_origem}")
    print(f"   GSRN(Profissional) : {id_profissional}")
    
    # Simula o tempo de transporte até à zona suja da CME
    tempo_transporte = random.uniform(1.0, 3.0)
    time.sleep(tempo_transporte)
    
    # Registo na base de dados
    resultado = registar_recolha(id_contentor, ponto_origem, id_profissional)
    
    if resultado.get("sucesso"):
        print(f"   [REGISTO OK] Contentor {id_contentor} entregue na zona suja.")
    else:
        print(f"   [ERRO] Falha no registo do contentor {id_contentor}.")

print("\n" + "=" * 40)
print("Fase de recolha concluída. Material pronto para lavagem/esterilização.")
print("=" * 40)

registar_recolha_log(id_contentor, ponto_origem, id_profissional)  # Guardar um ciclo de recolha para rastreabilidade

ver_historico_recolhas()