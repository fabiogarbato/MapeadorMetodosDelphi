import os, re, csv, psycopg2

def listar_arquivos_dcentro(diretorio, diretorio_saida):
    extensao_dfm = ".dfm"
    arquivos_dcentro = []

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_dfm) and (arquivo.startswith("DCentro") or arquivo.startswith("DCentrosSql")):
                arquivos_dcentro.append(arquivo)

    nome_arquivo_saida = os.path.join(diretorio_saida, "arquivos_dcentro.txt")
    try:
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
            f.write("\n".join(sorted(arquivos_dcentro)))
        print(f"Lista de arquivos Dcentro {nome_arquivo_saida}")
    except Exception as e:
        print(f"Erro ao escrever no arquivo: {e}")

def extrair_sql_dcentrosql(diretorio, diretorio_saida):
    nome_arquivo = "DCentroSql"
    extensao_dfm = ".dfm"
    informacoes_sql = []

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo == nome_arquivo + extensao_dfm:
                caminho_dfm = os.path.join(raiz, arquivo)
                with open(caminho_dfm, 'r', encoding='iso-8859-1') as f:
                    conteudo_dfm = f.read()
                    sql_matches = re.findall(r'(Nome\s*=\s*\'(.*?)\'.*?SQL\.Strings\s*=\s*\((.*?)\)\n)', conteudo_dfm, re.DOTALL)
                    for match in sql_matches:
                        nome_objeto = match[1]
                        sql_query = match[2]
                        def replace_hash_codes(s):
                            return re.sub(r'#(\d+)', lambda m: chr(int(m.group(1))), s)
                        sql_query = replace_hash_codes(sql_query.replace("#9", " ").replace("'", "").replace("#39", "'").strip())
                        sql_query = sql_query.replace("'+", "\n").replace("+'", "\n").replace("+", "\n").strip()
                        sql_query = ' '.join(sql_query.split())
                        informacoes_sql.append(f"Nome: {nome_objeto}\nSQL.Query:\n{sql_query}\n------------------------------------------------")
                break

    nome_arquivo_saida = os.path.join(diretorio_saida, "sql_dcentrosql.txt")
    with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("\n".join(informacoes_sql))

def listar_arquivos_dcentro_sql(diretorio, diretorio_saida):
    extensao_pas = ".pas"
    termo_busca = "DCentroSql"
    arquivos_dcentro_sql = []

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_pas):
                caminho_completo = os.path.join(raiz, arquivo)
                with open(caminho_completo, 'r', encoding='iso-8859-1') as f:
                    conteudo = f.read()
                    if termo_busca in conteudo:
                        arquivos_dcentro_sql.append(caminho_completo)

    nome_arquivo_saida = os.path.join(diretorio_saida, "arquivos_dcentro_sql.csv")
    try:
        with open(nome_arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Caminho do Arquivo'])
            for arquivo in sorted(arquivos_dcentro_sql):
                csvwriter.writerow([arquivo])
        print(f"Lista de arquivos .pas que usam DCentroSql: {nome_arquivo_saida}")
    except Exception as e:
        print(f"Erro ao escrever no arquivo: {e}")

def ler_arquivos_csv(nome_arquivo):
    arquivos = []
    with open(nome_arquivo, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  
        for linha in csvreader:
            arquivos.append(linha[0])
    return arquivos

def listar_arquivos_com_e_sem_obter_sql(diretorio, arquivos, diretorio_saida):
    termo_busca = "DataCentroSQL.ObterSQL"
    arquivos_com_obter_sql = []
    arquivos_sem_obter_sql = []

    for arquivo in arquivos:
        caminho_completo = os.path.join(diretorio, arquivo)
        try:
            with open(caminho_completo, 'r', encoding='iso-8859-1') as f:
                conteudo = f.read()
                if termo_busca in conteudo:
                    arquivos_com_obter_sql.append(arquivo)
                else:
                    arquivos_sem_obter_sql.append(arquivo)
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {caminho_completo}")

    nome_arquivo_saida = os.path.join(diretorio_saida, "arquivos_com_e_sem_obter_sql.csv")
    try:
        with open(nome_arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Nome do Arquivo', 'Possui DataCentroSQL.ObterSQL'])
            for arquivo in sorted(arquivos_com_obter_sql):
                csvwriter.writerow([arquivo, 'Sim'])
            for arquivo in sorted(arquivos_sem_obter_sql):
                csvwriter.writerow([arquivo, 'Nao'])
        print(f"Lista de arquivos com e sem DataCentroSQL.ObterSQL: {nome_arquivo_saida}")
    except Exception as e:
        print(f"Erro ao escrever no arquivo: {e}")

def extrair_nomes_arquivos(caminho_csv):
    nomes_arquivos = []

    with open(caminho_csv, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  
        for linha in csvreader:
            caminho_completo = linha[0]
            nome_arquivo = os.path.basename(caminho_completo)
            possui_obter_sql = linha[1]
            nomes_arquivos.append([nome_arquivo, possui_obter_sql])

    diretorio_saida = os.path.dirname(caminho_csv)
    nome_arquivo_saida = os.path.join(diretorio_saida, "nomes_arquivos_com_e_sem_obter_sql.csv")

    with open(nome_arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Nome do Arquivo', 'Possui DataCentroSQL.ObterSQL'])
        for arquivo in nomes_arquivos:
            csvwriter.writerow(arquivo)

    print(f"Lista de nomes de arquivos com e sem DataCentroSQL.ObterSQL salva em: {nome_arquivo_saida}")

def verificar_classes_no_banco(caminho_csv, diretorio_saida):
    nomes_classes = []
    with open(caminho_csv, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  
        for linha in csvreader:
            caminho_completo = linha[0]
            nome_arquivo = os.path.basename(caminho_completo)
            classe = nome_arquivo.split('.')[0]  
            nomes_classes.append(classe)

    conn = psycopg2.connect(host='cerato.mps.interno', dbname='migracaoSql', user='FabioGarbato', password='BPt3bpMRzivTo3tamwC9')
    cursor = conn.cursor()

    classes_presentes = []
    classes_ausentes = []
    for classe in nomes_classes:
        cursor.execute("SELECT * FROM Mapa WHERE Classe = %s", (classe,))
        if cursor.fetchone():
            classes_presentes.append(classe)
        else:
            classes_ausentes.append(classe)

    cursor.close()
    conn.close()

    arquivo_saida = os.path.join(diretorio_saida, 'resultado_classes.csv')
    with open(arquivo_saida, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Classes presentes na tabela Mapa:'])
        csvwriter.writerows([[classe] for classe in classes_presentes])
        csvwriter.writerow([])
        csvwriter.writerow(['Classes ausentes na tabela Mapa:'])
        csvwriter.writerows([[classe] for classe in classes_ausentes])

    print(f'Resultados salvos em {arquivo_saida}')


