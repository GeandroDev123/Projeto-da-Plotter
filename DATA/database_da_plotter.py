# PROJECT MANAGEMENT
# Sistema para gestão da plotter máquina de corte industrial de palmilhas onde faremos monitoramento e controle de produção"
# Importando bibliotecas necessárias para o sistema se conectar ao banco de dados relacionais e manipular"
# os dados utilizando o pandas.E datetime"
# Essas bibliotecas são essenciais para a construção do sistema, pois permitem a interação com o banco de dados e a
# manipulação eficiente dos dados.

import sqlite3
from datetime import datetime
import numpy as np
import pandas as pd

# Função para conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect('sistema_plotter.db')
    cursor = conn.cursor()
    return conn, cursor # conexão e cursor para executar comandos SQL no banco de dados

# Função para criar a tabela
def criar_tabelas():
    conn, cursor = conectar_banco() # Conecta ao banco de dados

    # CRIAÇÃO DA TABELA DE PRODUTOS
    # A tabela produtos será criada para armazenar os produtos que serão
    # cortados pela plotter com os seguintes campos:
    # codigo,descriçao,cliente,unidade de medida,navalha,modelo,
    # consumo e campo status para definir se o produto está ativo ou inativo.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        codigo INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        cliente TEXT NOT NULL,
        unidade TEXT NOT NULL,
        navalha TEXT NOT NULL,
        modelo TEXT NOT NULL,
        consumo FLOAT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('ativo', 'inativo'))
    )
    ''')
    # CRIAÇÃO DA TABELA DE PEDIDOS
    # A tabela pedidos será criada para armazenar os pedidos que serão
    # cortados pela plotter com os seguintes campos:Data do pedido, número do pedido,
    # cliente, código, descrição, quantidade esperada, data de entrega,projeção de placas
    # e status do pedido.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_pedido DATE NOT NULL,
        numero_pedido TEXT NOT NULL,
        cliente TEXT NOT NULL,
        codigo INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        quantidade_esperada INTEGER NOT NULL,
        data_entrega TEXT NOT NULL,
        projecao_placas INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('ABERTO', 'FINALIZADO', 'ANDAMENTO', 'CANCELADO','PENDENTE')),
        FOREIGN KEY (cliente) REFERENCES produtos(cliente),
        FOREIGN KEY (codigo) REFERENCES produtos(codigo)
    )
    ''')

    # CRIAÇÃO DA TABELA DE PRODUÇÃO
    # A tabela produção será criada para armazenar os dados de produção da plotter com os seguintes campos:
    # Data de inicial, número do pedido, código do produto, descrição do produto,hora de início,
    # hora de término,data finalização, quantidade produzida, quantidade esperada, eficiência,
    # status da produção(PENDENTE,ANDAMENTO,FINALIZADO),
    # placas utilizadas,sobras de placas,media de pares por placas

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS producao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_inicial DATE NOT NULL,
        numero_pedido TEXT NOT NULL,
        cliente TEXT NOT NULL,
        codigo INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        hora_inicio TIME,
        hora_termino TIME,
        data_final DATE,
        quantidade_produzida INTEGER NOT NULL,
        quantidade_esperada INTEGER NOT NULL,
        eficiencia FLOAT,
        status TEXT NOT NULL CHECK(status IN ('PENDENTE', 'ANDAMENTO', 'FINALIZADO')),
        placas_utilizadas FLOAT,
        sobras_placas FLOAT,
        media_pares_por_placa FLOAT,
        FOREIGN KEY (codigo) REFERENCES produtos(codigo),
        FOREIGN KEY (numero_pedido) REFERENCES pedidos(numero_pedido)
    )
    ''')
# Salva as alterações e fecha a conexão com o banco de dados
    conn.commit()
    conn.close()
    print("Tabelas criadas com sucesso!")
    return True
 # Executar a criação das tabelas

criar_tabelas()
