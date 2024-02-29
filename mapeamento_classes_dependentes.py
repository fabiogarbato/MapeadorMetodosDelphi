import os
import re

def mapeamento_classes_dependentes(diretorio, diretorio_saida):
    extensao_dpr = ".dpr"
    extensao_pas = ".pas"

    def extrair_units(caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
            conteudo = f.read()
        units = re.findall(r'\buses\b(.*?);', conteudo, re.DOTALL)
        if units:
            return [unit.strip().split(' ')[0] for unit in units[0].split(',')]
        return []

    def contar_metodos(caminho_arquivo, metodo):
        with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
            conteudo = f.read()
        return conteudo.count(metodo)

    def procurar_lookup_classe(caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
            conteudo = f.read()
        return 'LookupClasse' in conteudo in conteudo

    def procurar_validar_em_classe(caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
            conteudo = f.read()
        return 'ValidarEmClasse' in conteudo

    def extrair_classes_lookup(caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
            conteudo = f.read()
        padrao = r"LookupClasse\(\s*'([^']*)'"
        classes = re.findall(padrao, conteudo, re.DOTALL)
        return classes

    def extrair_classes_ValidarEmClasse(caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
            conteudo = f.read()
        padrao = r"ValidarEmClasse\([^,]*,\s*'([^']*)'"
        classes = re.findall(padrao, conteudo)
        return classes

    def imprimir_detalhes_unit(unit_nome):
        if unit_nome in classes_com_lookup_total:
            modulo, qtd, classes = classes_com_lookup_total[unit_nome]
            print("")
            print(f"LookupClasse em {unit_nome} - Modulo {modulo} - Ocorrências: {qtd}")
            for classe in classes:
                print(f"    {classe}")
        else:
            print("")
            print(f"Nenhum LookupClasse encontrado em {unit_nome}")

        if unit_nome in classes_com_validar_total:
            modulo, qtd, classes = classes_com_validar_total[unit_nome]
            print("")
            print(f"ValidarEmClasse em {unit_nome} - Modulo {modulo} - Ocorrências: {qtd}")
            for classe in classes:
                print(f"    {classe}")
        else:
            print("")
            print(f"Nenhum ValidarEmClasse encontrado em {unit_nome}")


    arquivos_encontrados = []
    classes_com_lookup_total = {}
    classes_com_validar_total = {}

    for raiz, diretorios, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(extensao_dpr):
                caminho_completo = os.path.join(raiz, arquivo)
                units = extrair_units(caminho_completo)
                qtd_units = len(units)
                arquivos_encontrados.append((caminho_completo, qtd_units))

                nome_pasta = os.path.splitext(arquivo)[0]
                pasta_saida = os.path.join(diretorio_saida, nome_pasta)
                os.makedirs(pasta_saida, exist_ok=True)

                nome_arquivo_saida = os.path.join(pasta_saida, f"{nome_pasta}_units.txt")
                with open(nome_arquivo_saida, 'w', encoding='iso-8859-1') as f:
                    f.write("\n".join(units))

                for unit in units:
                    caminho_unit = os.path.join(raiz, unit + extensao_pas)
                    if os.path.exists(caminho_unit):
                        qtd_lookup = contar_metodos(caminho_unit, 'LookupClasse')
                        qtd_validar = contar_metodos(caminho_unit, 'ValidarEmClasse')
                        classes_lookup = extrair_classes_lookup(caminho_unit)
                        classes_validar = extrair_classes_ValidarEmClasse(caminho_unit)

                        if qtd_lookup > 0:
                            classes_com_lookup_total[unit] = (nome_pasta, qtd_lookup, classes_lookup)
                        if qtd_validar > 0:
                            classes_com_validar_total[unit] = (nome_pasta, qtd_validar, classes_validar)

    #Descomentar esse metodo para DEBUG das dpr
    # with open(os.path.join(diretorio_saida, "resumo_dpr.txt"), 'w', encoding='iso-8859-1') as f:
    #     f.write("Arquivos .dpr e quantidade de units:\n")
    #     for arquivo, qtd_units in arquivos_encontrados:
    #         f.write(f"{arquivo}: {qtd_units} units\n")

    soma_ocorrencias_lookup = 0

    if classes_com_lookup_total:
        with open(os.path.join(diretorio_saida, "LookupClasse.txt"), 'w', encoding='iso-8859-1') as f:
            f.write("Units em todo o Delphi que contém o método 'LookupClasse'\n")
            f.write("-----------------------------------------\n")
            f.write(f"Total de units: {len(classes_com_lookup_total)}\n\n")
            for unit, (modulo, qtd, classes) in sorted(classes_com_lookup_total.items()):
                f.write(f"{unit} - Modulo {modulo} - Ocorrências: {qtd}\n")
                soma_ocorrencias_lookup += qtd
                for classe in classes:
                    f.write(f"    {classe}\n")
            f.write(f"Total de Ocorrências: {soma_ocorrencias_lookup}\n")


    soma_ocorrencias_validar = 0

    if classes_com_validar_total:
        with open(os.path.join(diretorio_saida, "ValidarEmClasse.txt"), 'w', encoding='iso-8859-1') as f:
            f.write("Units em todo o Delphi que contém o método 'ValidarEmClasse'\n")
            f.write("-----------------------------------------\n")
            f.write(f"Total de units: {len(classes_com_validar_total)}\n\n")
            for unit, (modulo, qtd, classes) in sorted(classes_com_validar_total.items()):
                f.write(f"{unit} - Modulo {modulo} - Ocorrências: {qtd}\n")
                soma_ocorrencias_validar += qtd
                for classe in classes:
                    f.write(f"    {classe}\n")
            f.write(f"Total de Ocorrências: {soma_ocorrencias_validar}\n")


    # print(f"Lista de arquivos .dpr e quantidade de units salva em {os.path.join(diretorio_saida, 'resumo_dpr.txt')}")
    print(f"Lista de todas as classes com LookupClasse salva em {os.path.join(diretorio_saida, 'LookupClasse.txt')}")
    print(f"Lista de todas as classes com ValidarEmClasse salva em {os.path.join(diretorio_saida, 'ValidarEmClasse.txt')}")

    nome_unit = input("Digite o nome da unit para exibir os detalhes de LookupClasse e ValidarEmClasse: ")
    imprimir_detalhes_unit(nome_unit)
