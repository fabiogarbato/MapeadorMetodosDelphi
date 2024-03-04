import os, re, csv

def listar_arquivos_sem_mpssombraconex_e_padrao(diretorio, diretorio_saida):
    extensao_pas = ".pas"
    arquivos_sem_mpssombraconex_e_padrao = []

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_pas) and arquivo.startswith("C"):
                if not (arquivo.endswith("Tests.pas") or arquivo.endswith("Testes.pas") or arquivo.startswith("ConvMed") or arquivo.startswith("Coparticipacao")):
                    caminho_completo = os.path.join(raiz, arquivo)
                    with open(caminho_completo, 'r', encoding='iso-8859-1') as f:
                        conteudo = f.read()
                        if "MPSSombraConex" not in conteudo:
                            arquivos_sem_mpssombraconex_e_padrao.append(arquivo)

    nome_arquivo_saida = os.path.join(diretorio_saida, "arquivos_sem_mpssombraconex_e_padrao.txt")
    try:
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
            f.write("\n".join(sorted(arquivos_sem_mpssombraconex_e_padrao)))
        print(f"Lista de arquivos DataModule {nome_arquivo_saida}")
    except Exception as e:
        print(f"Erro ao escrever no arquivo: {e}")

def relacionar_classes_formularios(diretorio, arquivo_classes, diretorio_saida):
    extensao_pas = ".pas"
    relacionamentos = []
    classes_sem_formulario = []

    with open(arquivo_classes, 'r', encoding='utf-8') as f:
        classes = [linha.strip() for linha in f.readlines()]

    for classe in classes:
        nome_formulario = "F" + classe[1:]
        formulario_encontrado = False
        for raiz, diretorios, arquivos in os.walk(diretorio):
            for arquivo in arquivos:
                if arquivo.startswith(nome_formulario) and arquivo.endswith(extensao_pas):
                    caminho_completo = os.path.join(raiz, arquivo)
                    relacionamentos.append(f"{classe} -> {arquivo}")
                    formulario_encontrado = True
                    break
            if formulario_encontrado:
                break

        if not formulario_encontrado:
            classes_sem_formulario.append(classe)

    nome_arquivo_saida = os.path.join(diretorio_saida, "relacionamentos_classes_formularios.txt")
    try:
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
            f.write("\n".join(sorted(relacionamentos)))
        print(f"Relacionamentos gravados em {nome_arquivo_saida}")
    except Exception as e:
        print(f"Erro ao escrever no arquivo: {e}")

    nome_arquivo_sem_formulario = os.path.join(diretorio_saida, "classes_sem_formulario.txt")
    try:
        with open(nome_arquivo_sem_formulario, 'w', encoding='utf-8') as f:
            f.write("\n".join(sorted(classes_sem_formulario)))
        print(f"Classes sem formulário gravadas em {nome_arquivo_sem_formulario}")
    except Exception as e:
        print(f"Erro ao escrever no arquivo: {e}")

def extrair_banco_DataModules(diretorio, arquivo_classes, diretorio_saida):
    extensao_dfm = ".dfm"
    informacoes_totais = []

    with open(arquivo_classes, 'r', encoding='utf-8') as f:
        classes = [linha.strip() for linha in f.readlines()]

    for classe in classes:
        nome_dfm = os.path.splitext(classe)[0] + extensao_dfm
        caminho_dfm = None
        for raiz, diretorios, arquivos in os.walk(diretorio):
            for arquivo in arquivos:
                if arquivo == nome_dfm:
                    caminho_dfm = os.path.join(raiz, arquivo)
                    break
            if caminho_dfm:
                break

        if caminho_dfm:
            with open(caminho_dfm, 'r', encoding='iso-8859-1') as f:
                conteudo_dfm = f.read()
                stored_proc_matches = re.findall(r'StoredProcName\s*=\s*\'(.*?)\'', conteudo_dfm)
                for match in stored_proc_matches:
                    informacoes_totais.append(f"{os.path.splitext(classe)[0]}: StoredProcName: {match}")

                inicio_sql = 0
                while True:
                    inicio_sql = conteudo_dfm.find('SQL.Strings = (', inicio_sql)
                    if inicio_sql == -1:
                        break
                    parenteses_count = 1
                    i = inicio_sql + 15
                    sql_query_lines = []
                    while i < len(conteudo_dfm) and parenteses_count > 0:
                        if conteudo_dfm[i] == '(':
                            parenteses_count += 1
                        elif conteudo_dfm[i] == ')':
                            parenteses_count -= 1
                        if parenteses_count > 0:
                            sql_query_lines.append(conteudo_dfm[i])
                        i += 1
                    sql_query = ''.join(sql_query_lines)
                    sql_query = sql_query.replace("#9", " ").replace("'", "").strip()
                    sql_query = re.sub(r'\s*\+\s*\'', '', sql_query, flags=re.MULTILINE)
                    sql_query = re.sub(r'\s*\+\s*', '', sql_query)
                    sql_query = ' '.join(sql_query.split())
                    informacoes_totais.append(f"{os.path.splitext(classe)[0]}: SQL.Query:\n{sql_query}\n")
                    inicio_sql = i
        else:
            print(f"Arquivo DFM não encontrado para a classe: {classe}")

    nome_arquivo_saida = os.path.join(diretorio_saida, "informacoes_dfm.txt")
    with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("\n".join(informacoes_totais))