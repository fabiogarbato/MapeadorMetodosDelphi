import pandas as pd
import os, re

def combinar_sombra_e_datamodule(diretorio_saida_FormDFM, diretorio_saida_FormDFM_DataModule, diretorio_saida, arquivo_saida):
    caminho_sombra = os.path.join(diretorio_saida_FormDFM, "relacao_forms_sombras_objetos.txt")
    caminho_datamodule = os.path.join(diretorio_saida_FormDFM_DataModule, "relacao_forms_classes_objetos.txt")

    df_sombra = pd.read_csv(caminho_sombra, sep='\t')
    df_datamodule = pd.read_csv(caminho_datamodule, sep='\t')

    separador = pd.DataFrame([['' for _ in range(len(df_sombra.columns))]], columns=df_sombra.columns)
    cabeçalho_data_module = pd.DataFrame([['Data Module' for _ in range(len(df_sombra.columns))]], columns=df_sombra.columns)
    df_combinado = pd.concat([df_sombra, separador, cabeçalho_data_module, df_datamodule])

    caminho_saida = os.path.join(diretorio_saida, arquivo_saida)
    df_combinado.to_csv(caminho_saida, index=False)

    print(f"CSV com Sombras e DataModules salvos em: {caminho_saida}")

def filtrar_e_salvar_csv(caminho_csv_entrada, diretorio_saida, arquivo_saida):
    df = pd.read_csv(caminho_csv_entrada, dtype=str)
    palavras_filtradas = []

    for linha in df.values:
        encontrou_palavra_com_c = False
        for celula in linha:
            if isinstance(celula, str):
                partes = celula.split("SQL.Query:")
                linha_antes_sql_query = partes[0] if partes else celula

                linha_limpa = re.sub(r'(Objeto:|Table:).*', '', linha_antes_sql_query)
                
                palavras_comecam_com_c = re.findall(r'\bC\w+', linha_limpa)
                if palavras_comecam_com_c:
                    palavras_filtradas.append(palavras_comecam_com_c[0])
                    encontrou_palavra_com_c = True
                    break  
        if not encontrou_palavra_com_c:
            palavras_filtradas.append('')  

    df_filtrado = pd.DataFrame(palavras_filtradas, columns=['Palavras'])
    caminho_saida = os.path.join(diretorio_saida, arquivo_saida)
    df_filtrado.to_csv(caminho_saida, index=False)

    print(f"CSV filtrado salvo em: {caminho_saida}")

def remover_primeiro_c_e_salvar_csv(caminho_csv_entrada, diretorio_saida, arquivo_saida):
    df = pd.read_csv(caminho_csv_entrada, dtype=str)
    palavras_sem_primeiro_c = []

    for palavra in df['Palavras']:
        if isinstance(palavra, str) and palavra.startswith('C'):
            palavras_sem_primeiro_c.append(palavra[1:])  
        else:
            palavras_sem_primeiro_c.append(palavra) 

    df_modificado = pd.DataFrame(palavras_sem_primeiro_c, columns=['Palavras'])
    caminho_saida = os.path.join(diretorio_saida, arquivo_saida)
    df_modificado.to_csv(caminho_saida, index=False)

    print(f"CSV sem o primeiro 'C' salvo em: {caminho_saida}")







