import os
import re
import json

def dfm_para_json(caminho_arquivo_dfm, caminho_arquivo_json):
    with open(caminho_arquivo_dfm, 'r', encoding='iso-8859-1') as f:
        conteudo = f.read()

    nome_classe = re.search(r'inherited\s+(\w+):', conteudo)
    nome_classe = nome_classe.group(1) if nome_classe else None

    padrao_atributos = re.compile(r'item\s*(.*?)\s*end', re.DOTALL)
    itens_atributos = padrao_atributos.findall(conteudo)
    atributos = []
    for item in itens_atributos:
        atributo = {}
        for linha in item.split('\n'):
            linha = linha.strip()
            if linha and ' = ' in linha:
                chave, valor = linha.split(' = ', maxsplit=1)
                atributo[chave] = valor.strip("'")
        atributos.append(atributo)

    nome_servidor = re.search(r'NomeServidor\s*=\s*\'(.*?)\'', conteudo)
    nome_servidor = nome_servidor.group(1) if nome_servidor else None

    sem_owner = 'SemOwner = True' in conteudo

    json_obj = {
        'NomeClasse': nome_classe,
        'atributos': atributos,
        'NomeServidor': nome_servidor,
        'SemOwner': sem_owner,
    }

    with open(caminho_arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(json_obj, f, indent=4)

def mapear_dfms(diretorio, diretorio_saida):
    extensao_dpr = ".dpr"
    extensao_dfm = ".dfm"

    dfms_por_modulo = {}
    classes_agregadas_por_dfm = {}
    diretorio_json = os.path.join(diretorio_saida, "JSON")
    os.makedirs(diretorio_json, exist_ok=True)

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_dpr):
                nome_modulo = os.path.splitext(arquivo)[0]
                dfms_por_modulo[nome_modulo] = []

            elif arquivo.endswith(extensao_dfm):
                caminho_completo = os.path.join(raiz, arquivo)
                nome_dfm = os.path.basename(caminho_completo)
                nome_modulo = os.path.basename(raiz)
                if nome_modulo in dfms_por_modulo:
                    dfms_por_modulo[nome_modulo].append(nome_dfm)
                else:
                    dfms_por_modulo[nome_modulo] = [nome_dfm]

                caminho_arquivo_json = os.path.join(diretorio_json, f"{nome_dfm}.json")
                dfm_para_json(caminho_completo, caminho_arquivo_json)
                with open(caminho_arquivo_json, 'r', encoding='utf-8') as f:
                    json_obj = json.load(f)
                    for atributo in json_obj.get('atributos', []):
                        if 'NomeClasse' in atributo:
                            classes_agregadas_por_dfm.setdefault(nome_dfm, set()).add(atributo['NomeClasse'])

    os.makedirs(diretorio_saida, exist_ok=True)

    for modulo, dfms in dfms_por_modulo.items():
        pasta_saida = os.path.join(diretorio_saida, modulo)
        os.makedirs(pasta_saida, exist_ok=True)

        nome_arquivo_saida = os.path.join(pasta_saida, f"{modulo}_dfms.txt")
        with open(nome_arquivo_saida, 'w', encoding='iso-8859-1') as f:
            f.write("\n".join(sorted(dfms)))

    todos_dfms = []
    for dfms in dfms_por_modulo.values():
        todos_dfms.extend(dfms)

    nome_arquivo_todos_dfms = os.path.join(diretorio_saida, "todos_dfms.txt")
    with open(nome_arquivo_todos_dfms, 'w', encoding='iso-8859-1') as f:
        f.write(f"Total de arquivos .dfm: {len(todos_dfms)}\n\n")
        f.write("\n".join(sorted(todos_dfms)))
    
    caminho_arquivo_dfms_nome_classe = os.path.join(diretorio_saida, "DFM_classesAgregadas.txt")
    with open(caminho_arquivo_dfms_nome_classe, 'w', encoding='iso-8859-1') as f:
        for dfm, classes_agregadas in classes_agregadas_por_dfm.items():
            f.write(f"{dfm}: {len(classes_agregadas)} classes agregadas diferentes\n")
            for classe_agregada in sorted(classes_agregadas):
                f.write(f"    - {classe_agregada}\n")
            f.write("\n")  

    print(f"Lista de todos os arquivos .dfm salva em {nome_arquivo_todos_dfms}")
    print(f"Lista de arquivos .dfm por módulo salva em {diretorio_saida}")
    print(f"Arquivos JSON gerados em {diretorio_json}")
    print(f"Lista de arquivos DFM com 'NomeClasse' salva em {caminho_arquivo_dfms_nome_classe}")
