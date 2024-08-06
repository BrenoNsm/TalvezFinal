import os
import re
import PyPDF2
import tabula

def extrair_data(texto):
    padrao = re.compile(r'\b\w+,\s+\d{2}\s+de\s+\w+\s+de\s+\d{4}\b')
    correspondencias = padrao.findall(texto)
    return correspondencias

def extrair_edicao(texto):
    padrao_edicao = re.compile(r'Edição N°:\s*\d+')
    correspondencia_edicao = padrao_edicao.findall(texto)
    return correspondencia_edicao

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

def extrair_portarias(texto):
    return portaria_regex.findall(texto)

def encontrar_texto_portaria(texto, portaria):
    start_idx = texto.find(portaria)
    if start_idx == -1:
        return ""

    end_idx = start_idx + len(portaria)
    fragmento = texto[start_idx:end_idx]
    fragmento += texto[end_idx:end_idx + 800]  
    return fragmento.strip()

def processar_arquivo(caminho_pdf):
    with open("resultado.txt", "w", encoding="utf-8") as resultado:
        texto_segunda_pagina = ler_pagina_pdf(caminho_pdf, 1)
        if texto_segunda_pagina:
            datas = extrair_data(texto_segunda_pagina)
            edicoes = extrair_edicao(texto_segunda_pagina)
            if datas or edicoes:
                resultado.write(f"Arquivo: {os.path.basename(caminho_pdf)}\n")
                for data in datas:
                    resultado.write(f"Data: {data}\n")
                for edicao in edicoes:
                    resultado.write(f"{edicao}\n")
        
        textos_paginas = ler_todas_paginas_pdf(caminho_pdf)
        for page_num, texto in enumerate(textos_paginas):
            if texto:
                portarias = extrair_portarias(texto)
                resultado.write(f"Arquivo: {os.path.basename(caminho_pdf)}, Página: {page_num + 1} \nNúmero de portarias encontradas: {len(portarias)}\n")
                for portaria in portarias:
                    if verificar_tabelas(caminho_pdf, page_num):
                        resultado.write(f"Encontrada portaria no arquivo {os.path.basename(caminho_pdf)}, página {page_num + 1}: tabela\n")
                    else:
                        texto_portaria = encontrar_texto_portaria(texto, portaria)
                        resultado.write(f"Encontrada portaria no arquivo {os.path.basename(caminho_pdf)}, página {page_num + 1}: {texto_portaria}\n")

if __name__ == "__main__":
    caminho_pdf = "/home/breno/Documentos/Projetos/Codigos/Tribunal/TalvezFinal/PDFS/doe-20240223.pdf"
    processar_arquivo(caminho_pdf)
