
from database import criar_base_dados, guardar_ciclo, ver_historico
import random
import time

print("Sistema CME iniciado")
criar_base_dados()

print("--" * 40)



# Definoção de 3 fases do ciclo de funcionamento

fases = [
    {"nome": "Pré-vácuo",       "temp_alvo": 60, "pressao_alvo": 0.2, "duracao": 5},
    {"nome": "Esterilização",   "temp_alvo": 134, "pressao_alvo": 3.0, "duracao": 8},
    {"nome": "Secagem",         "temp_alvo": 60, "pressao_alvo": 0.2, "duracao": 5},    
]

lote_id = "LOTE-001"
ciclo_ok = True
temp_esterilizacao = 0
pressao_esterilizacao = 0

for fase in fases:
    print(f"\n>> Fase: {fase['nome']}")
    
    # Simula leituras de sensor com pequeno ruído realista
    temp_real    = fase["temp_alvo"] + random.uniform(-0.5, 0.5)
    pressao_real = fase["pressao_alvo"] + random.uniform(-0.05, 0.05)
    
    print(f"   Temperatura : {temp_real:.1f} °C")
    print(f"   Pressão     : {pressao_real:.2f} bar")
    
    # Verifica se a esterilização atingiu os 134°C
    if fase["nome"] == "Esterilização":
        temp_esterilizacao = temp_real
        pressao_esterilizacao = pressao_real
        if temp_real < 133.9 or pressao_real < 3.0:
            print("   ALERTA: Parâmetros insuficientes!")
            ciclo_ok = False
    
    time.sleep(fase["duracao"])  # Simula a duração da fase

# Hard Stop — decisão final
print("\n" + "=" * 40)
if ciclo_ok:
    print(f"✅ Lote {lote_id} APROVADO — pode ser usado no utente.")
else:
    print(f"🚫 Lote {lote_id} BLOQUEADO — ciclo não conforme!")
print("=" * 40)

guardar_ciclo(lote_id, temp_esterilizacao, pressao_esterilizacao, "APROVADO" if ciclo_ok else "BLOQUEADO")
ver_historico()
