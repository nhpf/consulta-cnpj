import os
import json
import subprocess

import pandas as pd
import sqlite3
import networkx as nx

import config
from rede_cnpj import RedeCNPJ
import interface
import postprocessing


def consulta(tipo_consulta, objeto_consulta, qualificacoes, path_BD, nivel_max, path_output,
             csv=False, colunas_csv=None, csv_sep=',', graphml=False, gexf=False, viz=False,
             path_conexoes=None):
    try:
        conBD = sqlite3.connect(path_BD)

        try:
            rede = RedeCNPJ(conBD, nivel_max=nivel_max, qualificacoes=qualificacoes)

            if tipo_consulta == 'file':
                df_file = pd.read_csv(objeto_consulta, sep=csv_sep, header=None, dtype=str)

                qtd_colunas = len(df_file.columns)

                for _, linha in df_file.iterrows():
                    if qtd_colunas >= 2:
                        try:
                            consulta_item(rede, linha[0].strip(), linha[1].strip())
                        except KeyError as e:
                            print('Item nao encontrado ({}): {}'.format(linha[0].strip(),
                                                                        linha[1].strip()))
                    else:
                        try:
                            consulta_item(rede, 'cnpj', linha[0].strip())
                        except KeyError as e:
                            print('CNPJ nao encontrado: {}'.format(linha[0].strip()))
            else:
                consulta_item(rede, tipo_consulta, objeto_consulta)

            if not os.path.exists(path_output):
                os.mkdir(path_output)

            if csv:
                df_nodes = pd.DataFrame(columns=colunas_csv).append(rede.dataframe_pessoas(), sort=False)

                # Verifica se teve ao menos um registro encontrado
                if len(df_nodes) > 0:
                    df_nodes[colunas_csv].to_csv(os.path.join(path_output, 'pf-pj.csv'), index_label='id', sep=csv_sep, encoding='utf-8-sig')

                    df_edges = rede.dataframe_vinculos()
                    if len(df_edges) > 0:
                        df_edges.to_csv(os.path.join(path_output, 'vinculos.csv'), sep=csv_sep, encoding='utf-8-sig')
                else:
                    print('Nenhum registro foi localizado. Arquivos de output nao foram gerados.')

            if graphml:
                rede.gera_graphml(os.path.join(path_output, 'rede.graphml'))

            if gexf:
                rede.gera_gexf(os.path.join(path_output, 'rede.gexf'))

            if viz:
                try:
                    with open('viz/template.html', 'r', encoding='utf-8') as template:
                        str_html = template.read().replace('<!--GRAFO-->', json.dumps(rede.json()))

                    path_html = os.path.join(path_output, 'grafo.html')
                    with open(path_html, 'w', encoding='utf-8') as html:
                        html.write(str_html)

                    if config.PATH_NAVEGADOR:
                        subprocess.Popen([config.PATH_NAVEGADOR, os.path.abspath(path_html)])

                except Exception as e:
                    print('Não foi possível gerar a visualização. [{}]'.format(e))

            if path_conexoes:
                df_conexoes = pd.read_csv(path_conexoes, sep=csv_sep, header=None, dtype=str)

                qtd_colunas = len(df_conexoes.columns)

                if qtd_colunas >= 2:
                    G_undirected = rede.G.to_undirected()
                    lista_conexoes = []

                    for _, linha in df_conexoes.iterrows():
                        pessoa_A = linha[0].strip()
                        pessoa_B = linha[1].strip()

                        conexao = ''
                        try:
                            lst_pessoas_conexao = nx.shortest_path(G_undirected, pessoa_A, pessoa_B)
                            conexao = ' | '.join(lst_pessoas_conexao)
                        except:
                            conexao = 'SEM CONEXAO'

                        lista_conexoes.append((pessoa_A, pessoa_B, conexao))

                    pd.DataFrame(lista_conexoes).to_csv(os.path.join(path_output, 'conexoes.csv'),
                                                        sep=csv_sep,
                                                        header=None,
                                                        index=None, encoding='utf-8-sig')

                else:
                    print('''
Arquivo de vinculos precisa ter pelo menos duas colunas, contendo a identificacao das pessoas (CNPJ ou cpf+nome).
No caso de pessoa fisica, informar cpf seguido imediatamente do nome (ex: "***123456**NOME COMPLETO DA PESSOA").
                    ''')

            print('Consulta finalizada. Verifique o(s) arquivo(s) de saida na pasta "{}".'.format(path_output))

        except Exception as e:
            print('Um erro ocorreu:\n{}'.format(e))
        finally:
            conBD.close()

    except:
        print('Nao foi possivel encontrar ou conectar ao BD {}'.format(path_BD))


def consulta_item(rede, tipo_item, item):
    if tipo_item == 'cnpj':
        # print('Consultando CNPJ: {}'.format(item))
        rede.insere_pessoa(1, item.replace('.', '').replace('/', '').replace('-', '').zfill(14))

    elif tipo_item == 'nome_socio':
        # print('Consultando socios com nome: {}'.format(item))
        rede.insere_com_cpf_ou_nome(nome=item.upper())

    elif tipo_item == 'cpf':
        cpf = mascara_cpf(item.replace('.', '').replace('-', ''))
        # print('Consultando socios com cpf (mascarado): {}.'.format(cpf))
        rede.insere_com_cpf_ou_nome(cpf=cpf)

    elif tipo_item == 'cpf_nome':
        cpf = mascara_cpf(item[:11])
        nome = item[11:]

        # print('Consultando socio com cpf (mascarado) {} e nome {}'.format(cpf,nome))
        rede.insere_pessoa(2, (cpf, nome))

        # Se nao tem vinculo, nao existe socio com esse par cpf e nome
        if len(rede.dataframe_vinculos()) == 0:
            print('Nenhum socio encontrado com cpf "{}" e nome "{}"'.format(cpf, nome))
            rede.G.remove_node(cpf + nome)
    else:
        print('Tipo de consulta invalido: {}.\nTipos possiveis: cnpj, nome_socio, cpf, cpf_nome'.format(tipo_item))


def mascara_cpf(cpf_original):
    cpf = cpf_original.zfill(11)
    if cpf[0:3] != '***':
        cpf = '***' + cpf[3:9] + '**'
    return cpf


def main():
    graphml = False
    gexf = False
    viz = False
    nivel = config.NIVEL_MAX_DEFAULT
    path_conexoes = None

    resultados_interface = interface.get_consulta_paths()

    consulta("file", resultados_interface[1],
             config.QUALIFICACOES,
             resultados_interface[0],
             nivel,
             resultados_interface[2],
             csv=True, colunas_csv=config.COLUNAS_CSV, csv_sep=config.SEP_CSV,
             graphml=graphml,
             gexf=gexf,
             viz=viz,
             path_conexoes=path_conexoes)

    postprocessing.adapt_to_excel(os.path.join(resultados_interface[2], 'pf-pj.csv'))
    postprocessing.adapt_to_excel(os.path.join(resultados_interface[2], 'vinculos.csv'))

    interface.final_confirmation_window(resultados_interface[2])


if __name__ == '__main__':
    main()
