import os
import re
import json

def mapearSombra(diretorio, diretorio_saida):
    extensao_dfm = ".dfm"
    sombras = []

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_dfm) and arquivo.startswith("S"):
                nome_dfm = os.path.basename(arquivo)
                sombras.append(nome_dfm)

    nome_arquivo_saida = os.path.join(diretorio_saida, "sombras.txt")
    with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(sombras)))

    print(f"Lista de arquivos DFM que começam com 'S' salva em {nome_arquivo_saida}")

def extrair_e_salvar_informacoes_dfm(diretorio, diretorio_saida):
    extensao_dfm = ".dfm"
    relatorio = []

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_dfm) and arquivo.startswith("S"):
                caminho_arquivo = os.path.join(raiz, arquivo)
                informacoes_mapas = []
                dentro_de_objetos = False

                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    for linha in f:
                        if 'Objetos = ' in linha:
                            dentro_de_objetos = True
                        elif dentro_de_objetos and 'end>' in linha:
                            dentro_de_objetos = False
                        elif not dentro_de_objetos and 'Nome = ' in linha:
                            nome = linha.split('\'')[1]
                            informacoes_mapas.append({
                                'NomeArquivo': os.path.splitext(arquivo)[0],
                                'NomeMapa': nome,
                                'NomeObjeto': '',
                                'TipoObjeto': ''
                            })
                        elif 'Tipo = ' in linha and informacoes_mapas:
                            informacoes_mapas[-1]['TipoObjeto'] = linha.split('=')[1].strip()

                nome_arquivo_saida = os.path.join(diretorio_saida, f"{os.path.splitext(arquivo)[0]}.json")
                with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
                    json.dump(informacoes_mapas, f, indent=4)

                informacoes_temporarias = {}
                for informacoes in informacoes_mapas:
                    if informacoes['TipoObjeto'] == '':
                        informacoes_temporarias['NomeMapa'] = informacoes['NomeMapa']
                    elif informacoes['TipoObjeto'] not in ['', 'objetoConsulta']:
                        if 'NomeMapa' in informacoes_temporarias:
                            relatorio.append(f"{informacoes['NomeArquivo']} - Mapa: {informacoes_temporarias['NomeMapa']} - Objeto: {informacoes['NomeMapa']} - Tipo: {informacoes['TipoObjeto']}")
                            informacoes_temporarias = {}  # Resetar as informações temporárias após usá-las


    nome_arquivo_relatorio = os.path.join(diretorio_saida, "relatorio.txt")
    with open(nome_arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write("\n".join(relatorio))
        
    print(f"Informações extraídas e salvas em arquivos JSON no diretório {diretorio_saida}")
    print(f"Relatório salvo em {nome_arquivo_relatorio}")
