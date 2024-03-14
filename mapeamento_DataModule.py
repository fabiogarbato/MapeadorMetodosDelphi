import os, re, csv, psycopg2

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

                    def replace_hash_codes(s):
                        return re.sub(r'#(\d+)', lambda m: chr(int(m.group(1))), s)

                    sql_query = replace_hash_codes(sql_query.replace("#9", " ").replace("'", "").replace("#39", "'").strip())
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


def adicionar_objetos_banco_a_relacao_DataModule(diretorio_saida_FormDFM_DataModule):
    classes_por_form = {}
    with open(os.path.join(diretorio_saida_FormDFM_DataModule, "relacionamentos_classes_formularios.txt"), 'r', encoding='utf-8') as f:
        for linha in f:
            partes = linha.strip().split(" -> ")
            if len(partes) == 2:
                classe, form = partes
                classe = classe[:-4]  
                form = form[:-4]      
                classes_por_form[classe] = form

    informacoes_banco_por_classe = {}
    with open(os.path.join(diretorio_saida_FormDFM_DataModule, "informacoes_dfm.txt"), 'r', encoding='utf-8') as f:
        classe_atual = None
        consulta_sql = ""
        acumulando_sql = False
        for linha in f:
            partes = linha.strip().split(": ")
            if len(partes) >= 2:
                classe = partes[0]
                if classe in classes_por_form:
                    if "SQL.Query" in partes[1]:
                        if consulta_sql:  
                            informacoes_banco_por_classe.setdefault(classe_atual, []).append(f"SQL.Query: {consulta_sql.strip()}")
                        classe_atual = classe
                        consulta_sql = ": ".join(partes[2:]).strip() if len(partes) > 2 else ""
                        acumulando_sql = True
                    else:
                        if acumulando_sql:  
                            informacoes_banco_por_classe.setdefault(classe_atual, []).append(f"SQL.Query: {consulta_sql.strip()}")
                            acumulando_sql = False
                        consulta_sql = ""
                        informacoes_banco_por_classe.setdefault(classe, []).append(": ".join(partes[1:]).strip())
            elif classe_atual and acumulando_sql:
                consulta_sql += " " + linha.strip()

        if classe_atual and acumulando_sql: 
            informacoes_banco_por_classe.setdefault(classe_atual, []).append(f"SQL.Query: {consulta_sql.strip()}")

    relacao_atualizada = []
    for classe, form in classes_por_form.items():
        informacoes_banco = informacoes_banco_por_classe.get(classe, [])
        relacao_atualizada.append(f"{classe} -> {form} | {' | '.join(informacoes_banco)}")

    nome_arquivo_relacao_atualizada = os.path.join(diretorio_saida_FormDFM_DataModule, "relacao_forms_classes_objetos.txt")
    with open(nome_arquivo_relacao_atualizada, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(relacao_atualizada)))

    print(f"Relação atualizada entre forms, classes e objetos de banco (com tipos) salva em {nome_arquivo_relacao_atualizada}")

def exportar_para_csv_DataModule(diretorio_saida, nome_arquivo_entrada, nome_arquivo_saida):
    caminho_arquivo_entrada = os.path.join(diretorio_saida, nome_arquivo_entrada)
    caminho_arquivo_saida = os.path.join(diretorio_saida, nome_arquivo_saida)

    dados = []
    with open(caminho_arquivo_entrada, 'r', encoding='utf-8') as f:
        for linha in f:
            partes = linha.strip().split(" -> ")
            if len(partes) == 2:
                classe_form, objetos_banco = partes
                dados.append([classe_form] + objetos_banco.split(" | "))

    with open(caminho_arquivo_saida, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f)
        escritor.writerow(['Classe/Form', 'Objetos de Banco'])
        for linha in dados:
            escritor.writerow(linha)

    print(f"Dados exportados para {caminho_arquivo_saida}")

def inserir_no_banco_mapa(diretorio_saida, nome_arquivo_entrada):
    caminho_arquivo_entrada = os.path.join(diretorio_saida, nome_arquivo_entrada)

    conn = psycopg2.connect(host='cerato.mps.interno', dbname='migracaoSql', user='FabioGarbato', password='BPt3bpMRzivTo3tamwC9')
    cursor = conn.cursor()

    with open(caminho_arquivo_entrada, 'r', encoding='utf-8') as f:
        for linha in f:
            partes = linha.strip().split(" -> ")
            if len(partes) == 2:
                classe, resto = partes
                if ' | ' in resto:
                    form, objetos_banco = resto.split(' | ', 1)
                else:
                    form = resto
                    objetos_banco = None 

                cursor.execute(
                    "INSERT INTO Mapa (Form, Classe, Sombra, Relatorio, ObjetoBanco) VALUES (%s, %s, %s, %s, %s)",
                    (form.strip(), classe.strip(), None, None, objetos_banco.strip() if objetos_banco else None)
                )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Dados inseridos no banco a partir de {caminho_arquivo_entrada}")

def listar_arquivos_com_inicio_d_r(diretorio, diretorio_saida):
    extensao_pas = ".pas"
    arquivos_agrupados = {}

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_pas) and (arquivo.startswith("D") or arquivo.startswith("R")):
                nome_correspondente_f = "F" + arquivo[1:]
                if nome_correspondente_f in arquivos:
                    nome_base = arquivo[1:-4]  
                    if nome_base not in arquivos_agrupados:
                        arquivos_agrupados[nome_base] = {"F": "", "D": "", "R": ""}
                    arquivos_agrupados[nome_base][arquivo[0]] = arquivo
                    arquivos_agrupados[nome_base]["F"] = nome_correspondente_f

    for nome_base in arquivos_agrupados:
        arquivo_d = arquivos_agrupados[nome_base]["D"]
        if arquivo_d:
            nome_inicio_r = "R" + arquivo_d[1:]
            for arquivo in os.listdir(diretorio):
                if arquivo.startswith(nome_inicio_r):
                    arquivos_agrupados[nome_base]["R"] = arquivo
                    break

    nome_arquivo_saida = os.path.join(diretorio_saida, "arquivos_com_inicio_f_d_r.csv")
    try:
        with open(nome_arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Arquivo F', 'Arquivo D', 'Arquivo R'])
            for nome_base in sorted(arquivos_agrupados.keys()):
                csvwriter.writerow([arquivos_agrupados[nome_base]["F"], arquivos_agrupados[nome_base]["D"], arquivos_agrupados[nome_base]["R"]])
        print(f"Lista de arquivos .pas agrupados por F, D e R: {nome_arquivo_saida}")
    except Exception as e:
        print(f"Erro ao escrever no arquivo CSV: {e}")

def extrair_banco_DataModules_D(diretorio, diretorio_saida):
    extensao_dfm = ".dfm"
    informacoes_totais = []

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_dfm) and arquivo.startswith("D"):
                caminho_dfm = os.path.join(raiz, arquivo)
                with open(caminho_dfm, 'r', encoding='iso-8859-1') as f:
                    conteudo_dfm = f.read()
                    stored_proc_matches = re.findall(r'StoredProcName\s*=\s*\'(.*?)\'', conteudo_dfm)
                    for match in stored_proc_matches:
                        informacoes_totais.append([os.path.splitext(arquivo)[0], "StoredProcName", match])

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

                        def replace_hash_codes(s):
                            return re.sub(r'#(\d+)', lambda m: chr(int(m.group(1))), s)

                        sql_query = replace_hash_codes(sql_query.replace("#9", " ").replace("'", "").replace("#39", "'").strip())
                        sql_query = re.sub(r'\s*\+\s*\'', '', sql_query, flags=re.MULTILINE)
                        sql_query = re.sub(r'\s*\+\s*', '', sql_query)
                        sql_query = ' '.join(sql_query.split())
                        informacoes_totais.append([os.path.splitext(arquivo)[0], "SQL.Query", sql_query])
                        inicio_sql = i

    nome_arquivo_saida = os.path.join(diretorio_saida, "informacoes_dfm_D.csv")
    with open(nome_arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Arquivo', 'Tipo', 'Conteudo'])
        csvwriter.writerows(informacoes_totais)

def combinar_arquivos_e_objetos(diretorio_arquivos, diretorio_objetos, diretorio_saida):
    arquivos_agrupados = {}
    with open(diretorio_arquivos, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  
        for row in csvreader:
            nome_arquivo_d = row[1].replace('.pas', '')
            arquivos_agrupados[nome_arquivo_d] = row  

    informacoes_objetos = {}
    with open(diretorio_objetos, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader) 
        for row in csvreader:
            nome_arquivo_d = row[0]
            tipo = row[1]
            conteudo = row[2]
            if nome_arquivo_d in informacoes_objetos:
                informacoes_objetos[nome_arquivo_d].append(f"{tipo}: {conteudo}")
            else:
                informacoes_objetos[nome_arquivo_d] = [f"{tipo}: {conteudo}"]

    nome_arquivo_saida = os.path.join(diretorio_saida, "arquivos_e_objetos_combinados.csv")
    with open(nome_arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Arquivo F', 'Arquivo D', 'Arquivo R', 'Objetos'])
        for nome_arquivo_d, arquivos in arquivos_agrupados.items():
            objetos = " | ".join(informacoes_objetos.get(nome_arquivo_d, []))
            csvwriter.writerow(arquivos + [objetos])

    print(f"Arquivo combinado criado: {nome_arquivo_saida}")

def inserir_dados_combinados_no_banco(diretorio_saida, nome_arquivo_entrada):
    caminho_arquivo_entrada = os.path.join(diretorio_saida, nome_arquivo_entrada)

    conn = psycopg2.connect(host='cerato.mps.interno', dbname='migracaoSql', user='FabioGarbato', password='BPt3bpMRzivTo3tamwC9')
    cursor = conn.cursor()

    with open(caminho_arquivo_entrada, 'r', encoding='utf-8') as f:
        csvreader = csv.reader(f)
        next(csvreader) 
        for linha in csvreader:
            arquivo_f, arquivo_d, arquivo_r, objetos = linha
            
            relatorio = None if not arquivo_r.strip() else arquivo_r.strip()
            objeto_banco = None if not objetos.strip() else objetos.strip()

            arquivo_f_sem_extensao = arquivo_f.strip().split('.')[0]
            arquivo_d_sem_extensao = arquivo_d.strip().split('.')[0]

            cursor.execute(
                "INSERT INTO Mapa (Form, Classe, Sombra, Relatorio, ObjetoBanco) VALUES (%s, %s, %s, %s, %s)",
                (arquivo_f_sem_extensao, arquivo_d_sem_extensao, None, relatorio, objeto_banco)
            )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Dados inseridos no banco a partir de {caminho_arquivo_entrada}")





