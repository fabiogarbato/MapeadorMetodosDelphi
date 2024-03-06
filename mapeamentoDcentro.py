import os, re

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