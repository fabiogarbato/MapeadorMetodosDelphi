import os
import re
import json

def mapear_Formsdfms(diretorio, diretorio_saida):
    extensao_dfm = ".dfm"
    forms_dfms = []
    informacoes_dfm = []

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_dfm) and arquivo.startswith("F"):
                nome_dfm = os.path.basename(arquivo)
                forms_dfms.append(nome_dfm)

                caminho_completo = os.path.join(raiz, arquivo)
                with open(caminho_completo, 'r', encoding='iso-8859-1') as f:
                    for linha in f:
                        if 'inherited' in linha and ':' in linha:
                            classe = linha.split(':')[1].strip()
                        elif 'NomeServidor' in linha:
                            partes = linha.split('=')
                            if len(partes) >= 2:
                                nome_servidor = partes[1].strip().strip("'")
                                informacoes_dfm.append(f"{nome_dfm} - {nome_servidor}")
                                break  

    nome_arquivo_saida = os.path.join(diretorio_saida, "forms_dfms.txt")
    with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(forms_dfms)))

    nome_arquivo_informacoes = os.path.join(diretorio_saida, "informacoes_dfm.txt")
    with open(nome_arquivo_informacoes, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(informacoes_dfm)))

    print(f"Lista de arquivos DFM que começam com 'F' salva em {nome_arquivo_saida}")
    print(f"Informações extraídas dos arquivos DFM salvas em {nome_arquivo_informacoes}")
