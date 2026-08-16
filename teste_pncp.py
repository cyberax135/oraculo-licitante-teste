import requests
import time
import datetime
import json
import os

LOG_FILE = "pncp_smoke_test.log"

def teste_pncp():
    url = "https://pncp.gov.br/api/pncp/v1/orgaos/26989715000185"
    
    agora_br = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
    timestamp = agora_br.strftime("%Y-%m-%d %H:%M:%S")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    start_time = time.time()
    try:
        response = requests.get(url, headers=headers, timeout=15)
        elapsed = time.time() - start_time
        status_code = response.status_code
        
        valido_json = False
        if status_code == 200:
            try:
                dados = response.json()
                # Verifica se retornou dados estruturados (ex: cnpj)
                if "cnpj" in dados or "razaoSocial" in dados:
                    valido_json = True
            except json.JSONDecodeError:
                valido_json = False

        msg = f"[{timestamp}] Status: {status_code} | JSON Valido: {valido_json} | Tempo: {elapsed:.2f}s | Erro: Nenhum\n"

    except Exception as e:
        elapsed = time.time() - start_time
        msg = f"[{timestamp}] Status: N/A | JSON Valido: False | Tempo: {elapsed:.2f}s | Erro: {str(e)}\n"

    print(msg.strip())
    
    # Faz o append no log local
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg)

if __name__ == "__main__":
    teste_pncp()
