import os
import re
import psycopg2

def mapear_Classes_Pas(diretorio):
    extensao_pas = ".pas"
    classes_pas = []
    informacoes_pas = []

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_pas) and arquivo.startswith("C"):
                nome_classe = os.path.basename(arquivo)[:-len(extensao_pas)]
                classes_pas.append(nome_classe)

                caminho_completo = os.path.join(raiz, arquivo)
                with open(caminho_completo, 'r', encoding='iso-8859-1') as f:
                    for linha in f:
                        if 'alguma_informacao_especifica' in linha:
                            pass

    conn = psycopg2.connect(host='cerato.mps.interno', dbname='migracaoSql', user='FabioGarbato', password='BPt3bpMRzivTo3tamwC9')
    cursor = conn.cursor()

    for nome_classe in classes_pas:
        cursor.execute("INSERT INTO Classes (NomeClasse) VALUES (%s)", (nome_classe,))
        conn.commit()

    cursor.close()
    conn.close()

    print(f"Nomes das classes inseridos na tabela Classes: {', '.join(classes_pas)}")

diretorio = r"C:\Projetos\HomePar\Fontes"
mapear_Classes_Pas(diretorio)
