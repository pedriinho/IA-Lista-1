import math
from dados import dados as base
import pandas as pd
import json

def montar_arvore(root, valor_caracteristica_anterior, data_treino, label, lista_classe):
    if data_treino.shape[0] != 0:
        info = buscar_maior_ganho(calcular_entropia(data_treino, entropia_total(data_treino, label, lista_classe), lista_classe))
        contagem_valor_caracteristica_dict = data_treino[info].value_counts(sort=False)  

        tree_cp = {}
        for valor_caracteristica, contagem in contagem_valor_caracteristica_dict.items():
            dados_valor_caracteristica = data_treino[data_treino[info] == valor_caracteristica] 

            atribuido_ao_no = False  
            for c in lista_classe:
                contagem_classe = dados_valor_caracteristica[dados_valor_caracteristica[label] == c].shape[0] 

                if contagem_classe == contagem: 
                    tree_cp[valor_caracteristica] = c 
                    data_treino = data_treino[data_treino[info] != valor_caracteristica] 
                    atribuido_ao_no = True
            if not atribuido_ao_no: 
                tree_cp[valor_caracteristica] = "?" 
        
        proximo_no = None

        if valor_caracteristica_anterior != None:
            root[valor_caracteristica_anterior] = dict()
            root[valor_caracteristica_anterior][info] = tree_cp
            proximo_no = root[valor_caracteristica_anterior][info]
        else:
            root[info] = tree_cp
            proximo_no = root[info]
        
        for no, ramo in list(proximo_no.items()):
            if ramo == '?':
                dados_valor_caracteristica = data_treino[data_treino[info] == no]
                montar_arvore(proximo_no, no, dados_valor_caracteristica, label, lista_classe)

def buscar_maior_ganho(caminhos_entropia):
    maior_ganho = 0
    maior_ganho_caminho = ''
    for i in caminhos_entropia:
        if caminhos_entropia[i]['razao_ganho'] > maior_ganho:
            maior_ganho = caminhos_entropia[i]['razao_ganho']
            maior_ganho_caminho = i

    return maior_ganho_caminho

def calcular_entropia(filtro, entropia, lista_classe):
    separar_dados = {}
    caminhos_entropia = {}

    for i in filtro:
        if i == 'risco':
            continue
        separar_dados[i] = {}
        caminhos_entropia[i] = {}
        for j in filtro[i]:
            entropia_cp = 0
            separar_dados[i][j] = {
                'Alto': len(filtro[(filtro[i] == j) & (filtro['risco'] == 'Alto')]),
                'Moderado': len(filtro[(filtro[i] == j) & (filtro['risco'] == 'Moderado')]),
                'Baixo': len(filtro[(filtro[i] == j) & (filtro['risco'] == 'Baixo')]),
            }
            for k in separar_dados[i][j]:
                if separar_dados[i][j][k] == 0:
                    continue
                entropia_cp -= (separar_dados[i][j][k] / len(filtro[filtro[i] == j])) * math.log2(separar_dados[i][j][k] / len(filtro[filtro[i] == j]))
            caminhos_entropia[i][j] = entropia_cp
        ganho_cp = entropia
        split = 0
        for j in set(filtro[i]):
            for classe in lista_classe:
                ganho_cp -= (len(filtro[(filtro["risco"] == classe) & (filtro[i] == j)]) / len(filtro)) * caminhos_entropia[i][j]
            caminhos_entropia[i]['ganho'] = ganho_cp
            split -= (len(filtro[filtro[i] == j]) / len(filtro)) * math.log2(len(filtro[filtro[i] == j]) / len(filtro))
        caminhos_entropia[i]['split'] = split
        
        if split != 0:
            caminhos_entropia[i]['razao_ganho'] = caminhos_entropia[i]['ganho'] / caminhos_entropia[i]['split']
        else:
            caminhos_entropia[i]['razao_ganho'] = 0
    
    return caminhos_entropia

def entropia_total(data, atributo_saida, lista_classe):
    value = 0

    for classe in lista_classe:
        if len(data[data[atributo_saida] == classe]) != 0:
            value -= (len(data[data[atributo_saida] == classe]) / len(data)) * math.log2(len(data[data[atributo_saida] == classe]) / len(data))
    return value

def c4_5(df):
    df_cp = df.copy()
    tree = {}
    montar_arvore(tree, None, df_cp, 'risco', ['Alto', 'Moderado', 'Baixo'])
    return tree

df = pd.DataFrame(base)

with open('saida_c4_5.json', 'w') as json_file:
    json.dump(c4_5(df), json_file, indent=4)