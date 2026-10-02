import os
import glob
import re
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from src.gerador_lista_va import processar_mes

def main():
    print("=" * 60)
    print(" AUTOMATIZADOR DE LISTA MENSAL - VALE ALIMENTAÇÃO ")
    print(" Prefeitura do Município de Piracicaba ")
    print("=" * 60)

    # 1. Localiza os PDFs disponíveis em data/
    todos_pdfs = glob.glob(os.path.join("data", "*.pdf"))
    if not todos_pdfs:
        print("❌ ERRO: Nenhum arquivo PDF encontrado na pasta 'data/'.")
        print("Por favor, coloque o relatório 'Funcionário por Cargo - MM-AAAA.pdf' na pasta 'data/'.")
        sys.exit(1)

    # Identifica PDF de transferências (se houver, ex: relatorio_tranferencia... ou relatorio_transferencia...)
    is_transf = lambda p: ("tranfer" in os.path.basename(p).lower() or "transfer" in os.path.basename(p).lower())
    pdfs_transferencias = [p for p in todos_pdfs if is_transf(p)]
    pdf_transferencias = sorted(pdfs_transferencias)[-1] if pdfs_transferencias else None

    # Identifica PDF oficial de admissões (Funcionário por Cargo)
    pdfs_admissoes = [p for p in todos_pdfs if not is_transf(p)]
    if not pdfs_admissoes:
        print("❌ ERRO: Nenhum relatório de admissões ('Funcionário por Cargo') encontrado na pasta 'data/'.")
        sys.exit(1)

    pdf_selecionado = sorted(pdfs_admissoes)[-1]
    nome_pdf = os.path.basename(pdf_selecionado)
    print(f"📄 Relatório de Admissões detectado: {nome_pdf}")
    if pdfs_transferencias:
        nomes_transf = ", ".join([os.path.basename(p) for p in pdfs_transferencias])
        print(f"📄 Relatório(s) de Transferências detectado(s): {nomes_transf}")

    # Tenta extrair mês e ano do nome do arquivo (ex: "09-2026")
    m = re.search(r'(\d{2})[-_](\d{4})', nome_pdf)
    if m:
        mes_num, ano_num = m.group(1), m.group(2)
        meses_extenso = {
            "01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril",
            "05": "Maio", "06": "Junho", "07": "Julho", "08": "Agosto",
            "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"
        }
        mes_nome = meses_extenso.get(mes_num, mes_num)
        mes_ref = f"{mes_nome}/{ano_num}"
    else:
        mes_ref = "Setembro/2026"

    print(f"📅 Mês de Referência: {mes_ref}")
    print("\nProcessando cruzamento e gerando folhas de entrega...")

    try:
        arquivo_gerado = processar_mes(
            pdf_selecionado,
            mes_ano_referencia=mes_ref,
            caminho_transferencias=pdfs_transferencias
        )
        print("\n" + "=" * 60)
        print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print(f"📁 Planilha salva em: {arquivo_gerado}")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ ERRO durante o processamento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
