from mapeamento_classes_dependentes import mapeamento_classes_dependentes
from mapeamento_dfm import mapear_dfms

def main():
    diretorio = r"C:\Projetos\HomePar\Fontes"
    diretorio_saida = r"C:\Users\fabio.garbato\Desktop\HomePar\MigraçãoSQL\Log"
    diretorio_saida_dfm = r"C:\Users\fabio.garbato\Desktop\HomePar\MigraçãoSQL\Log_DFM"
    mapeamento_classes_dependentes(diretorio, diretorio_saida)
    mapear_dfms(diretorio, diretorio_saida_dfm)

if __name__ == "__main__":
    main()
