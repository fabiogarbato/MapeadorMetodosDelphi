from mapeamento_classes_dependentes import mapeamento_classes_dependentes
from mapeamento_dfm import mapear_dfms
from mapear_objetos_banco import mapearSombra, extrair_e_salvar_informacoes_dfm
from mapeamento_Forms import mapear_Formsdfms, listar_e_extrair_classes, relacionar_sombras_com_forms, adicionar_objetos_banco_a_relacao, exportar_para_csv
from mapeamento_DataModule import listar_arquivos_sem_mpssombraconex_e_padrao, relacionar_classes_formularios, extrair_banco_DataModules, exportar_para_csv_DataModule, adicionar_objetos_banco_a_relacao_DataModule
from mapeamentoDcentro import listar_arquivos_dcentro, extrair_sql_dcentrosql

import os

def main():
    diretorio = r"C:\Projetos\HomePar\Fontes"
    diretorio_saida = r"C:\Projetos\MigraçãoSQL\Log"
    diretorio_saida_dfm = r"C:\Projetos\MigraçãoSQL\Log_DFM"
    diretorio_saida_FormDFM = r"C:\Projetos\MigraçãoSQL\Log_Forms"
    diretorio_saida_csv = r"C:\Projetos\MigraçãoSQL\MapeadorObjetosDelphiFront\src\text"
    diretorio_saida_sombra = r"C:\Projetos\MigraçãoSQL\Log_ObjetosBanco\Sombras"
    arquivo_classes = os.path.join(diretorio_saida_FormDFM, "arquivos_sem_mpssombraconex_e_padrao.txt")
    diretorio_saida_FormDFM_DataModule = r"C:\Projetos\MigraçãoSQL\Log_Forms\DataModule"
    diretorio_saida_DCentro = r"C:\Projetos\MigraçãoSQL\Log_DCentro"

    mapeamento_classes_dependentes(diretorio, diretorio_saida)
    # mapear_dfms(diretorio, diretorio_saida_dfm)
    # mapearSombra(diretorio, diretorio_saida_sombra)
    # extrair_e_salvar_informacoes_dfm(diretorio, diretorio_saida_sombra)
    # mapear_Formsdfms(diretorio, diretorio_saida_FormDFM)
    # listar_e_extrair_classes(diretorio, diretorio_saida_FormDFM)
    # relacionar_sombras_com_forms(diretorio_saida_FormDFM)
    # adicionar_objetos_banco_a_relacao(diretorio_saida_sombra, diretorio_saida_FormDFM)
    # exportar_para_csv(diretorio_saida_csv, "relacao_forms_sombras_objetos.txt", "relacao_forms_sombras_objetos.csv")
    # listar_arquivos_sem_mpssombraconex_e_padrao(diretorio, diretorio_saida_FormDFM)
    # relacionar_classes_formularios(diretorio, arquivo_classes, diretorio_saida_FormDFM_DataModule)
    # extrair_banco_DataModules(diretorio, arquivo_classes, diretorio_saida_FormDFM_DataModule)
    # adicionar_objetos_banco_a_relacao_DataModule(diretorio_saida_FormDFM_DataModule)
    # exportar_para_csv_DataModule(diretorio_saida_csv, "relacao_forms_classes_objetos.txt", "relacao_forms_classes_objetos.csv")
    # listar_arquivos_dcentro(diretorio, diretorio_saida_DCentro)
    # extrair_sql_dcentrosql(diretorio, diretorio_saida_DCentro)

if __name__ == "__main__":
    main()
