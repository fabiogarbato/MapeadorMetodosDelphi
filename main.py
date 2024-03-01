from mapeamento_classes_dependentes import mapeamento_classes_dependentes
from mapeamento_dfm import mapear_dfms
from mapear_objetos_banco import mapearSombra, extrair_e_salvar_informacoes_dfm
from mapeamento_Forms import mapear_Formsdfms

def main():
    diretorio = r"C:\Projetos\HomePar\Fontes"
    diretorio_saida = r"C:\Users\fabio.garbato\Desktop\HomePar\MigraçãoSQL\Log"
    diretorio_saida_dfm = r"C:\Users\fabio.garbato\Desktop\HomePar\MigraçãoSQL\Log_DFM"
    diretorio_saida_FormDFM = r"C:\Users\fabio.garbato\Desktop\HomePar\MigraçãoSQL\Log_Forms"
    diretorio_saida_sombra = r"C:\Users\fabio.garbato\Desktop\HomePar\MigraçãoSQL\Log_ObjetosBanco\Sombras"
    mapeamento_classes_dependentes(diretorio, diretorio_saida)
    mapear_dfms(diretorio, diretorio_saida_dfm)
    mapearSombra(diretorio, diretorio_saida_sombra)
    extrair_e_salvar_informacoes_dfm(diretorio, diretorio_saida_sombra)
    mapear_Formsdfms(diretorio, diretorio_saida_FormDFM)

if __name__ == "__main__":
    main()

