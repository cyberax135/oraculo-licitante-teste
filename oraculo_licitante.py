import requests
import time
import datetime
import json
import os
import psycopg2

# --- CONFIGURACOES DE AMBIENTE ---
NEON_DB_URL = os.environ.get('NEON_DB_URL')
WAPPFLY_TOKEN = os.environ.get('WAPPFLY_TOKEN')

if not NEON_DB_URL or not WAPPFLY_TOKEN:
    print('Faltam credenciais de ambiente (NEON_DB_URL, WAPPFLY_TOKEN)')
    exit(1)

# Modalidades conforme Manual PNCP: 4(Conc Elet), 5(Conc Pres), 6(Pregao Elet), 7(Pregao Pres), 8(Dispensa)
MODALIDADES = [4, 5, 6, 7, 8]
SLEEP_TIME = 3.0

def obter_contratacoes_do_dia(hoje_str):
    resultados_brutos = []
    
    for modalidade in MODALIDADES:
        pagina = 1
        while True:
            url = f"https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial={hoje_str}&dataFinal={hoje_str}&codigoModalidadeContratacao={modalidade}&pagina={pagina}"
            headers = {"User-Agent": "Mozilla/5.0"}
            
            sucesso_pagina = False
            ultima_pagina = False
            
            for tentativa in range(1, 4):  # 1 tentativa original + 2 retries
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code == 200:
                        dados = response.json()
                        itens = dados.get('data', [])
                        resultados_brutos.extend(itens)
                        
                        if len(itens) == 0 or dados.get('totalPaginas', 1) <= pagina:
                            sucesso_pagina = True
                            ultima_pagina = True
                        else:
                            sucesso_pagina = True
                            ultima_pagina = False
                        break  # Sai do loop de tentativas
                        
                    elif response.status_code == 204:
                        sucesso_pagina = True
                        ultima_pagina = True
                        break  # Sai do loop de tentativas
                        
                    elif response.status_code == 429:
                        print(f'Rate Limit (429) na mod {modalidade}, pag {pagina}, tent {tentativa}')
                        time.sleep(15.0)
                        
                    else:
                        print(f'Erro PNCP (Status {response.status_code}) na mod {modalidade}, pag {pagina}, tent {tentativa}')
                        time.sleep(5.0)
                except Exception as e:
                    print(f'Falha na mod {modalidade}, pag {pagina}, tent {tentativa}: {e}')
                    time.sleep(5.0)
                    
            if not sucesso_pagina:
                print(f'Desistindo da modalidade {modalidade} apos 3 falhas na pagina {pagina}.')
                time.sleep(SLEEP_TIME)
                break  # Desiste desta modalidade e vai para a proxima
                
            if ultima_pagina:
                time.sleep(SLEEP_TIME)
                break  # Concluiu esta modalidade com sucesso
                
            pagina += 1
            time.sleep(SLEEP_TIME)
            
    # Deduplicacao em memoria baseada no ID ou numeroControlePNCP
    resultados_unicos = {}
    for item in resultados_brutos:
        item_id = item.get('id') or item.get('numeroControlePNCP')
        if item_id:
            resultados_unicos[item_id] = item
            
    return list(resultados_unicos.values())

def conectar_db():
    return psycopg2.connect(NEON_DB_URL)

def main():
    agora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
    hoje_str = agora.strftime("%Y%m%d")
    
    print('Iniciando captura PNCP (Bulk-fetch)...')
    editais = obter_contratacoes_do_dia(hoje_str)
    print(f'Total capturado hoje (cobrindo 5 modalidades): {len(editais)}')
    
    # Restante da logica de cruzamento/anti-spam a ser preenchida apos validacao
    print('Processamento concluido com sucesso.')

if __name__ == "__main__":
    main()
