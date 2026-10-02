import os
import re
import pdfplumber
from datetime import datetime

def extrair_transferencias_pdf(caminho_pdf):
    """
    Extrai as transferências de servidores a partir do PDF 'Relatório de Transferência'.
    Retorna uma lista de dicionários com:
    - nro_funcional_original (ex: '26.535-7')
    - funcional (inteiro, ex: 265357)
    - nome (str)
    - sec_fim_cod (int ou None, ex: 107)
    - local_fim (str)
    - dt_fim (str, ex: '31/08/2026')
    - dt_fim_dt (datetime.date ou None)
    - sec_ini_cod (int ou None, ex: 114)
    - local_ini (str)
    - dt_ini (str, ex: '01/09/2026')
    - dt_ini_dt (datetime.date ou None)
    """
    if not os.path.exists(caminho_pdf):
        raise FileNotFoundError(f"Arquivo PDF de transferência não encontrado: {caminho_pdf}")

    transferencias = []

    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 8:
                        continue
                    func_str = str(row[0]).strip() if row[0] else ''
                    if not re.search(r'\d{1,3}\.\d{3}-[\dwW]', func_str):
                        continue

                    nome = str(row[1]).replace('\n', ' ').strip() if row[1] else ''
                    col_fim = ' '.join([str(row[2] or ''), str(row[3] or '')]).replace('\n', ' ')
                    dt_fim_str = str(row[4]).strip() if row[4] else ''
                    col_ini = ' '.join([str(row[5] or ''), str(row[6] or '')]).replace('\n', ' ')
                    dt_ini_str = str(row[7]).strip() if row[7] else ''

                    # Extrai códigos de secretaria no formato Sec:XXX
                    m_sec_fim = re.search(r'Sec:(\d{3})', col_fim)
                    m_sec_ini = re.search(r'Sec:(\d{3})', col_ini)
                    sec_fim_cod = int(m_sec_fim.group(1)) if m_sec_fim else None
                    sec_ini_cod = int(m_sec_ini.group(1)) if m_sec_ini else None

                    # Extrai dígitos do funcional
                    func_digitos = re.sub(r'\D', '', func_str)
                    funcional_int = int(func_digitos) if func_digitos.isdigit() else func_str

                    # Converte datas
                    try:
                        dt_fim = datetime.strptime(dt_fim_str, "%d/%m/%Y").date() if dt_fim_str else None
                    except ValueError:
                        dt_fim = None

                    try:
                        dt_ini = datetime.strptime(dt_ini_str, "%d/%m/%Y").date() if dt_ini_str else None
                    except ValueError:
                        dt_ini = None

                    transferencias.append({
                        "nro_funcional_original": func_str,
                        "funcional": funcional_int,
                        "nome": nome,
                        "sec_fim_cod": sec_fim_cod,
                        "local_fim": col_fim,
                        "dt_fim": dt_fim_str,
                        "dt_fim_dt": dt_fim,
                        "sec_ini_cod": sec_ini_cod,
                        "local_ini": col_ini,
                        "dt_ini": dt_ini_str,
                        "dt_ini_dt": dt_ini
                    })

    return transferencias
