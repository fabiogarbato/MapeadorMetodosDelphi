import os, re, csv
import pandas as pd
import psycopg2
import fnmatch

conn = psycopg2.connect(host='cerato.mps.interno', dbname='migracaoSql', user='FabioGarbato', password='BPt3bpMRzivTo3tamwC9')
cursor = conn.cursor()

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
                    classe_atual = None
                    for linha in f:
                        if 'TMClienteClasse' in linha:
                            partes = linha.split(':')
                            if len(partes) >= 2:
                                classe_atual = partes[1].strip()
                        elif 'NomeServidor' in linha and classe_atual:
                            partes = linha.split('=')
                            if len(partes) >= 2:
                                nome_servidor = partes[1].strip().strip("'")
                                informacoes_dfm.append(f"{nome_dfm} - {classe_atual} - {nome_servidor}")
                                classe_atual = None

    nome_arquivo_saida = os.path.join(diretorio_saida, "forms_dfms.txt")
    with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(forms_dfms)))

    nome_arquivo_informacoes = os.path.join(diretorio_saida, "informacoes_dfm.txt")
    with open(nome_arquivo_informacoes, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(informacoes_dfm)))

    print(f"Lista de arquivos DFM que começam com 'F' salva em {nome_arquivo_saida}")
    print(f"Informações extraídas dos arquivos DFM salvas em {nome_arquivo_informacoes}")

def extrair_classes_registrar(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
        conteudo = f.read()
    padrao = r"Registrar\('([^']*)'"
    classes = re.findall(padrao, conteudo)
    return classes

def listar_e_extrair_classes(diretorio, diretorio_saida):
    extensao_pas = ".pas"
    classes_registradas = []

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_pas) and arquivo.startswith("S"):
                caminho_completo = os.path.join(raiz, arquivo)
                classes = extrair_classes_registrar(caminho_completo)
                if classes:
                    nome_sombra = os.path.basename(arquivo)
                    for classe in classes:
                        classes_registradas.append(f"{nome_sombra} - {classe}")

    nome_arquivo_saida = os.path.join(diretorio_saida, "sombras.txt")
    try:
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
            f.write("\n".join(sorted(classes_registradas)))
    except Exception as e:
        print(f"Erro ao escrever no arquivo: {e}")

def relacionar_sombras_com_forms(diretorio_saida):
    informacoes_dfm = {}
    with open(os.path.join(diretorio_saida, "informacoes_dfm.txt"), 'r', encoding='utf-8') as f:
        for linha in f:
            partes = linha.strip().split(" - ")
            if len(partes) >= 3:
                form, _, classe = partes
                informacoes_dfm[classe] = form.replace('.dfm', '')

    sombras = []
    with open(os.path.join(diretorio_saida, "sombras.txt"), 'r', encoding='utf-8') as f:
        sombras = [linha.strip() for linha in f]

    relacao_forms_sombras = []
    for sombra in sombras:
        partes = sombra.split(" - ")
        if len(partes) >= 2:
            nome_sombra, classe_sombra = partes
            form_correspondente = informacoes_dfm.get(classe_sombra, "Form não encontrado")
            if form_correspondente != "Form não encontrado":
                relacao_forms_sombras.append(f"{form_correspondente} - {nome_sombra.replace('.pas', '')}")

    nome_arquivo_relacao = os.path.join(diretorio_saida, "relacao_forms_sombras.txt")
    with open(nome_arquivo_relacao, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(relacao_forms_sombras)))

    print(f"Relação entre forms e sombras salva em {nome_arquivo_relacao}")


def adicionar_objetos_banco_a_relacao(diretorio_saida_sombra, diretorio_saida_FormDFM):
    sombras_por_form = {}
    with open(os.path.join(diretorio_saida_FormDFM, "relacao_forms_sombras.txt"), 'r', encoding='utf-8') as f:
        for linha in f:
            partes = linha.strip().split(" - ")
            if len(partes) >= 2:
                form, sombra = partes
                sombras_por_form.setdefault(form, []).append(sombra)

    classes_por_form = {}
    with open(os.path.join(diretorio_saida_FormDFM, "informacoes_dfm.txt"), 'r', encoding='utf-8') as f:
        for linha in f:
            partes = linha.strip().split(" - ")
            if len(partes) >= 3:
                form, _, classe = partes
                classe = 'C' + classe[6:]
                form = form.replace('.dfm', '')
                classes_por_form.setdefault(form, []).append(classe)

    objetos_banco_por_sombra = {}
    with open(os.path.join(diretorio_saida_sombra, "relatorio.txt"), 'r', encoding='utf-8') as f:
        for linha in f:
            partes = linha.strip().split(" - ")
            if len(partes) >= 4:
                sombra, _, objeto, tipo = partes
                tipo = tipo.split(":")[-1].strip()
                tipo = tipo.replace("objeto", "")
                objetos_banco_por_sombra.setdefault(sombra, []).append(f"{objeto} - Tipo: {tipo}")

    relacao_atualizada = []
    for form, sombras in sombras_por_form.items():
        classes = classes_por_form.get(form, ["C não encontrada"] * len(sombras))
        for classe, sombra in zip(classes, sombras):
            objetos_banco = objetos_banco_por_sombra.get(sombra, [])
            relacao_atualizada.append(f"{form} - {classe} - {sombra} - {' | '.join(objetos_banco)}")

    nome_arquivo_relacao_atualizada = os.path.join(diretorio_saida_FormDFM, "relacao_forms_sombras_objetos.txt")
    with open(nome_arquivo_relacao_atualizada, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted(relacao_atualizada)))

    print(f"Relação atualizada entre forms, classes, sombras e objetos de banco (com tipos) salva em {nome_arquivo_relacao_atualizada}")


def exportar_para_csv(diretorio_saida, nome_arquivo_entrada, nome_arquivo_saida):
    caminho_arquivo_entrada = os.path.join(diretorio_saida, nome_arquivo_entrada)

    caminho_arquivo_saida = os.path.join(diretorio_saida, nome_arquivo_saida)

    dados = []
    with open(caminho_arquivo_entrada, 'r', encoding='utf-8') as f:
        for linha in f:
            partes = linha.strip().split(" - ")
            dados.append(partes)

    with open(caminho_arquivo_saida, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f)
        escritor.writerow(['Form', 'Sombra', 'Objetos de Banco'])  
        for linha in dados:
            escritor.writerow(linha)

    print(f"Dados exportados para {caminho_arquivo_saida}")

def inserir_no_banco(diretorio_saida, nome_arquivo_entrada):
    caminho_arquivo_entrada = os.path.join(diretorio_saida, nome_arquivo_entrada)

    conn = psycopg2.connect(host='cerato.mps.interno', dbname='migracaoSql', user='FabioGarbato', password='BPt3bpMRzivTo3tamwC9')
    cursor = conn.cursor()

    with open(caminho_arquivo_entrada, 'r', encoding='utf-8') as f:
        for linha in f:
            partes = linha.strip().split(" - ")
            if len(partes) > 4:
                partes[3] = " - ".join(partes[3:])  
                partes = partes[:4]
            partes += [None] * (4 - len(partes))  
            form, classe, sombra, objeto_banco = partes
            relatorio = None  
            cursor.execute(
                "INSERT INTO Mapa (Form, Classe, Sombra, Relatorio, ObjetoBanco) VALUES (%s, %s, %s, %s, %s)",
                (form, classe, sombra, relatorio, objeto_banco)
            )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Dados inseridos no banco a partir de {caminho_arquivo_entrada}")
    
def mapearSombraExecao(diretorio, diretorio_saida):

    nome_arquivo_saida = 'SombrasDiferentes.csv'
    nome_arquivo_encontrados = 'arquivosSombrasDiferentes.csv'
    nome_arquivo_queries = 'queries_extraidas.csv'

    conn = psycopg2.connect(
        host='cerato.mps.interno',
        dbname='migracaoSql',
        user='FabioGarbato',
        password='BPt3bpMRzivTo3tamwC9'
    )
    cursor = conn.cursor()

    consulta_sql = """
        SELECT Sombra FROM Mapa 
        WHERE ObjetoBanco IS NULL AND Sombra IS NOT NULL 
    """
    cursor.execute(consulta_sql)
    
    resultados = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    caminho_arquivo_saida = os.path.join(diretorio_saida, nome_arquivo_saida)
    
    with open(caminho_arquivo_saida, 'w', newline='', encoding='utf-8') as f:
        escritor = csv.writer(f)
        escritor.writerow(['Sombra'])  
        for linha in resultados:
            sombra = linha[0].rstrip('-')
            escritor.writerow([sombra])
    
    sombras_encontradas = []
    for sombra in resultados:
        sombra_arquivo = sombra[0].rstrip('-').strip() + '.pas'
        for diretorio_atual, _, arquivos in os.walk(diretorio):
            for nome_arquivo in fnmatch.filter(arquivos, sombra_arquivo):
                sombras_encontradas.append(os.path.join(diretorio_atual, nome_arquivo))
    
    caminho_arquivo_encontrados = os.path.join(diretorio_saida, nome_arquivo_encontrados)
    with open(caminho_arquivo_encontrados, 'w', newline='', encoding='iso-8859-1') as f:
        escritor = csv.writer(f)
        escritor.writerow(['Caminho Completo do Arquivo'])  
        for arquivo in sombras_encontradas:
            escritor.writerow([arquivo])
    
    def extrair_queries(arquivo):
        with open(arquivo, 'r', encoding='iso-8859-1') as f:
            conteudo = f.read()

        queries = []

        dentro_de_texto = False
        query_atual = ""
        ultimo_caractere = ""

        for caractere in conteudo:
            if caractere == "'" and ultimo_caractere in ['(', ',']:
                dentro_de_texto = True
                query_atual = ""
            elif caractere == "'" and dentro_de_texto:
                dentro_de_texto = False
                queries.append(query_atual)
                query_atual = ""
            elif dentro_de_texto:
                query_atual += caractere

            ultimo_caractere = caractere

        query_completa = ' '.join(queries)
        return query_completa

    caminho_arquivo_queries = os.path.join(diretorio_saida, nome_arquivo_queries)
    with open(caminho_arquivo_encontrados, 'r', newline='', encoding='iso-8859-1') as f_in, \
         open(caminho_arquivo_queries, 'w', newline='', encoding='iso-8859-1') as f_out:
        leitor = csv.reader(f_in)
        escritor = csv.writer(f_out)
        escritor.writerow(['Sombra', 'Query'])  
        next(leitor)  
        for linha in leitor:
            caminho_arquivo = linha[0]
            query = extrair_queries(caminho_arquivo)
            if query:  
                nome_arquivo = os.path.basename(caminho_arquivo)
                escritor.writerow([nome_arquivo, query])
                print(f"{nome_arquivo} - Query:\n{query}\n{'-' * 80}")
    
    conn = psycopg2.connect(
        host='cerato.mps.interno',
        dbname='migracaoSql',
        user='FabioGarbato',
        password='BPt3bpMRzivTo3tamwC9'
    )
    cursor = conn.cursor()

    with open(caminho_arquivo_queries, 'r', newline='', encoding='iso-8859-1') as f:
        leitor = csv.reader(f)
        next(leitor)  
        for linha in leitor:
            sombra, query = linha
            sombra_sem_extensao = sombra.rstrip('.pas')
            update_sql = f"""
                UPDATE Mapa
                SET ObjetoBanco = '{query}'
                WHERE Sombra = '{sombra_sem_extensao} -'
            """
            print(f"Query:\n{update_sql}\n{'-' * 80}")
            cursor.execute(update_sql)

    conn.commit()

    cursor.close()
    conn.close()












