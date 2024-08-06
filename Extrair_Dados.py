import os
import re
import PyPDF2
import tabula
from datetime import datetime

def extrair_data(texto):
    padrao = re.compile(r'\b\w+,\s+\d{2}\s+de\s+\w+\s+de\s+\d{4}\b')
    correspondencias = padrao.findall(texto)
    return correspondencias

def converter_data(data_texto):
    meses = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }
    partes = data_texto.split()
    dia = partes[1]
    mes = meses[partes[3].lower()]
    ano = partes[5]
    return f"{dia}/{mes}/{ano}"

def extrair_edicao(texto):
    padrao_edicao = re.compile(r'Edição N°:\s*(\d+)')
    correspondencia_edicao = padrao_edicao.search(texto)
    return correspondencia_edicao.group(1) if correspondencia_edicao else None

def verificar_tabelas(caminho_pdf, pagina):
    try:
        tabelas = tabula.read_pdf(caminho_pdf, pages=pagina + 1, multiple_tables=True)
        return len(tabelas) > 0
    except Exception as e:
        print(f"Erro ao verificar tabelas: {e}")
        return False

def ler_pagina_pdf(caminho_pdf, pagina_num):
    with open(caminho_pdf, 'rb') as file:
        leitor_pdf = PyPDF2.PdfReader(file)
        if len(leitor_pdf.pages) <= pagina_num:
            return ""
        pagina = leitor_pdf.pages[pagina_num]
        texto = pagina.extract_text()
        return texto

def ler_todas_paginas_pdf(caminho_pdf):
    with open(caminho_pdf, 'rb') as file:
        leitor_pdf = PyPDF2.PdfReader(file)
        textos = []
        for pagina in leitor_pdf.pages:
            textos.append(pagina.extract_text())
        return textos

portaria_regex = re.compile(r'PORTARIA\s*Nº\s*[\d\w\-/.]*', re.IGNORECASE)
cpf_regex = re.compile(r'\d{3}\.\d{3}\.\d{3}-\d{2}')

def extrair_portarias(texto):
    return portaria_regex.findall(texto)

def encontrar_texto_portaria(texto, portaria):
    start_idx = texto.find(portaria)
    if start_idx == -1:
        return ""

    end_idx = start_idx + len(portaria)
    fragmento = texto[start_idx:end_idx]
    fragmento += texto[end_idx:end_idx + 800]  # Ajuste conforme necessário
    return fragmento.strip()

def extrair_cpfs(texto):
    return cpf_regex.findall(texto)

def processar_arquivo(caminho_pdf):
    with open("resultado.txt", "w", encoding="utf-8") as resultado:
        texto_segunda_pagina = ler_pagina_pdf(caminho_pdf, 1)
        datas = extrair_data(texto_segunda_pagina)
        edicao = extrair_edicao(texto_segunda_pagina)
        
        if datas:
            data_formatada = converter_data(datas[0]) if datas else "Data não encontrada"
            resultado.write(f"Arquivo: {os.path.basename(caminho_pdf)}\n")
            resultado.write(f"Edição do Documento: {edicao}\n")
            resultado.write(f"Data: {data_formatada}\n")
        
        textos_paginas = ler_todas_paginas_pdf(caminho_pdf)
        for page_num, texto in enumerate(textos_paginas):
            if texto:
                portarias = extrair_portarias(texto)
                for portaria in portarias:
                    texto_portaria = encontrar_texto_portaria(texto, portaria)
                    cpfs = extrair_cpfs(texto_portaria)
                    if cpfs:  # Filtra apenas as portarias que contêm CPFs
                        cpfs_texto = ", ".join(cpfs)
                        resultado.write(f"Página: {page_num + 1}\n")
                        resultado.write(f"Número da Portaria: {portaria}\n")
                        resultado.write(f"CPFs: {cpfs_texto}\n")
                        resultado.write(f"Texto da Portaria: {texto_portaria}\n\n")

if __name__ == "__main__":
    caminho_pdf = "C:/Users/bnascimento/Documents/Code/Projeto-Diario/TalvezFinal/scrapydoe/scrapydoe/spiders/pdfs/2024/doe-20230103.pdf"
    processar_arquivo(caminho_pdf)
