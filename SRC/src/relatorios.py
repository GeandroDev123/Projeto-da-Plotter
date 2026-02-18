# Geração do relatório de produção da maquina de corte 
from datetime import datetime
import os
import sqlite3
import pandas as pd
import numpy as np

# Função para validar formato de data
"""
    Valida se uma string está no formato de data DD/MM/YY.

    Args:
        data_string (str): A string a ser validada como data.

    Returns:
        str: A string de data original se estiver no formato correto.
        None: Se a string não estiver no formato DD/MM/YY.
    """

def validar_data(data_str):
    try:
        datetime.strptime(data_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False
    
# Função para gerar o relatório de produção mensal
"""
    Executa uma consulta SQL para obter um resumo da produção mensal,
    agrupando os dados por mês e calculando o total da quantidade produzida,
    o total de placas utilizadas, a média da eficiência da produção e
    a média de pares por placa.

    Args:
        cursor (sqlite3.Cursor): O cursor do banco de dados SQLite.

    Returns:
        list: Uma lista de tuplas, onde cada tupla representa um mês e contém:
              - O número do mês (str).
              - O total da quantidade produzida (int).
              - O total de placas utilizadas (float).
              - A média da eficiência da produção (float).
              - A média de pares por placa (float).
              Retorna uma lista vazia em caso de erro ou ausência de dados.
    """
def gerar_relatorio_producao_mensal(cursor):
    try:
        cursor.execute('''SELECT strftime('%m', data) AS mes,
                            SUM(quantidade) AS total_quantidade_produzida,
                            SUM(placas_utilizadas) AS total_placas_utilizadas,
                            AVG(eficiencia_producao) AS media_eficiencia_producao,
                            AVG(pares_por_placa) AS media_pares_por_placa
                       FROM procucao
                       GROUP BY mes
                        ORDER BY mes''')
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao gerar relatório de produção mensal: {e}")
        return []
    
# Função para gerar um relatório de produção mensal e exportar para Excel
"""
    Gera um relatório de produção mensal a partir dos dados do banco SQLite,
    organiza os dados em um DataFrame do pandas e exporta o relatório para um
    arquivo Excel chamado 'relatorio_mensal.xlsx'.

    Args:
        cursor (sqlite3.Cursor): O cursor do banco de dados SQLite.
        output_path (str): O caminho onde o arquivo Excel será salvo.

    Returns:
        bool: True se o relatório foi gerado e exportado com sucesso, False caso contrário.
    """
def gerar_relatorio_mensal_excel(cursor, output_path):
    try:
        # Gerar o relatório de produção mensal
        gerar_relatorio_producao_mensal = gerar_relatorio_producao_mensal(cursor)

        # Criar um Dataframe a partir dos dados do relatório:
        df_relatorio = pd.DataFrame(gerar_relatorio_producao_mensal,
                                    columns=['Mes', 'Total Quantidade Produzida',
                                             'Total Placas Utilizadas',
                                             'Media Eficiencia Producao',
                                             'Media Pares por Placa'])
        meses_dicitionary = {
            '01': 'Janeiro',
            '02': 'Fevereiro',
            '03': 'Março',
            '04': 'Abril',
            '05': 'Maio',
            '06': 'Junho',
            '07': 'Julho',
            '08': 'Agosto',
            '09': 'Setembro',
            '10': 'Outubro',   
            '11': 'Novembro',
            '12': 'Dezembro'
        }