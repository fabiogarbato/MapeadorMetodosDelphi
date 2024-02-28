import os
import re

diretorio = r"C:\Projetos\HomePar\Fontes"
extensao_dpr = ".dpr"
extensao_pas = ".pas"
diretorio_saida = r"C:\Users\fabio.garbato\Desktop\HomePar\MigraçãoSQL\Log"

def extrair_units(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
        conteudo = f.read()
    units = re.findall(r'\buses\b(.*?);', conteudo, re.DOTALL)
    if units:
        return [unit.strip().split(' ')[0] for unit in units[0].split(',')]
    return []

def procurar_lookup_classe(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
        conteudo = f.read()
    return 'LookupClasse' in conteudo or 'ValidarEmClasse' in conteudo

def procurar_validar_em_classe(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
        conteudo = f.read()
    return 'ValidarEmClasse' in conteudo

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

            classes_com_lookup = []
            for unit in units:
                caminho_unit = os.path.join(raiz, unit + extensao_pas)
                if os.path.exists(caminho_unit):
                    if procurar_lookup_classe(caminho_unit):
                        classes_com_lookup.append(unit)
                        classes_com_lookup_total[unit] = nome_pasta
                    if procurar_validar_em_classe(caminho_unit):
                        classes_com_validar_total[unit] = nome_pasta

            if classes_com_lookup:
                nome_arquivo_lookup = os.path.join(pasta_saida, f"{nome_pasta}_lookup_classes.txt")
                with open(nome_arquivo_lookup, 'w', encoding='iso-8859-1') as f:
                    f.write("\n".join(classes_com_lookup))

with open(os.path.join(diretorio_saida, "resumo_dpr.txt"), 'w', encoding='iso-8859-1') as f:
    f.write("Arquivos .dpr e quantidade de units:\n")
    for arquivo, qtd_units in arquivos_encontrados:
        f.write(f"{arquivo}: {qtd_units} units\n")

if classes_com_lookup_total:
    with open(os.path.join(diretorio_saida, "LookupClasse.txt"), 'w', encoding='iso-8859-1') as f:
        f.write("Units que contém o método 'LookupClasse'\n")
        f.write("-----------------------------------------\n")
        f.write(f"Total de units: {len(classes_com_lookup_total)}\n\n")
        for classe, modulo in sorted(classes_com_lookup_total.items()):
            f.write(f"{classe} - Modulo {modulo}\n")

if classes_com_validar_total:
    with open(os.path.join(diretorio_saida, "ValidarEmClasse.txt"), 'w', encoding='iso-8859-1') as f:
        f.write("Units que contém o método 'ValidarEmClasse'\n")
        f.write("-----------------------------------------\n")
        f.write(f"Total de units: {len(classes_com_validar_total)}\n\n")
        for classe, modulo in sorted(classes_com_validar_total.items()):
            f.write(f"{classe} - Modulo {modulo}\n")

print(f"Lista de arquivos .dpr e quantidade de units salva em {os.path.join(diretorio_saida, 'resumo_dpr.txt')}")
print(f"Lista de todas as classes com LookupClasse salva em {os.path.join(diretorio_saida, 'LookupClasse.txt')}")
print(f"Lista de todas as classes com ValidarEmClasse salva em {os.path.join(diretorio_saida, 'ValidarEmClasse.txt')}")
