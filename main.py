from mapeamento_classes_dependentes import mapeamento_classes_dependentes

def main():
    diretorio = r"C:\Projetos\HomePar\Fontes"
    diretorio_saida = r"C:\Users\fabio.garbato\Desktop\HomePar\MigraçãoSQL\Log"
    mapeamento_classes_dependentes(diretorio, diretorio_saida)

if __name__ == "__main__":
    main()
