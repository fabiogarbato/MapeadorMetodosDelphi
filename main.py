from mapeamento_classes_dependentes import mapeamento_classes_dependentes
from mapeamento_dfm import mapear_dfms
from mapear_objetos_banco import mapearSombra, extrair_e_salvar_informacoes_dfm
from mapeamento_Forms import mapear_Formsdfms, listar_e_extrair_classes, relacionar_sombras_com_forms, adicionar_objetos_banco_a_relacao, exportar_para_csv

def main():
    diretorio = r"C:\Projetos\HomePar\Fontes"
    diretorio_saida = r"C:\Projetos\MigracaoSQL\MigraçãoSQL\Log"
    diretorio_saida_dfm = r"C:\Projetos\MigracaoSQL\Log_DFM"
    diretorio_saida_FormDFM = r"C:\Projetos\MigracaoSQL\Log_Forms"
    diretorio_saida_csv = r"C:\Projetos\MigracaoSQL\MapeadorObjetosDelphiFront\src\text"
    diretorio_saida_sombra = r"C:\Projetos\MigracaoSQL\Log_ObjetosBanco\Sombras"

    mapeamento_classes_dependentes(diretorio, diretorio_saida)
    mapear_dfms(diretorio, diretorio_saida_dfm)
    mapearSombra(diretorio, diretorio_saida_sombra)
    extrair_e_salvar_informacoes_dfm(diretorio, diretorio_saida_sombra)
    mapear_Formsdfms(diretorio, diretorio_saida_FormDFM)
    listar_e_extrair_classes(diretorio, diretorio_saida_FormDFM)
    relacionar_sombras_com_forms(diretorio_saida_FormDFM)
    adicionar_objetos_banco_a_relacao(diretorio_saida_sombra, diretorio_saida_FormDFM)
    exportar_para_csv(diretorio_saida_csv, "relacao_forms_sombras_objetos.txt", "relacao_forms_sombras_objetos.csv")

if __name__ == "__main__":
    main()
