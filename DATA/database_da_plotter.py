# PROJECT MANAGEMENT
# Sistema para gestão da plotter máquina de corte industrial de palmilhas onde faremos monitoramento e controle de produção"
# Importando bibliotecas necessárias para o sistema se conectar ao banco de dados relacionais e manipular"
# os dados utilizando o pandas.E datetime"
# Essas bibliotecas são essenciais para a construção do sistema, pois permitem a interação com o banco de dados e a
# manipulação eficiente dos dados.

import sqlite3
import os
from datetime import datetime
import numpy as np
import pandas as pd

# Função para conectar ao banco de dados
def conectar_banco(db_name: str = 'sistema_plotter.db'):
    # Procura o arquivo do banco em locais comuns do projeto
    possible_paths = [db_name, os.path.join('DATA', db_name), os.path.join('..', db_name)]
    db_path = None
    for p in possible_paths:
        if os.path.exists(p):
            db_path = p
            break
    # Se não existir, usa o caminho padrão (será criado ao conectar)
    if db_path is None:
        db_path = db_name

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor

# Função para criar a tabela
def criar_tabelas():
    conn, cursor = conectar_banco()

    # Tabela produtos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        codigo INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        cliente TEXT NOT NULL,
        unidade TEXT NOT NULL,
        navalha TEXT NOT NULL,
        modelo TEXT NOT NULL,
        consumo REAL NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('ativo', 'inativo'))
    )
    ''')

    # Tabela pedidos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_pedido DATE NOT NULL,
        numero_pedido TEXT NOT NULL,
        cliente TEXT NOT NULL,
        codigo INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        quantidade_esperada INTEGER NOT NULL,
        data_entrega DATE NOT NULL,
        projecao_placas INTEGER NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('ABERTO', 'FINALIZADO', 'ANDAMENTO', 'CANCELADO', 'PENDENTE')),
        FOREIGN KEY (codigo) REFERENCES produtos(codigo)
    )
    ''')

    # Tabela producao
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS producao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_inicial DATE NOT NULL,
        numero_pedido TEXT NOT NULL,
        codigo INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        hora_inicio TIME,
        hora_termino TIME,
        data_finalizacao DATE,
        quantidade_produzida INTEGER NOT NULL,
        quantidade_esperada INTEGER NOT NULL,
        eficiencia REAL,
        status TEXT NOT NULL CHECK(status IN ('PENDENTE', 'ANDAMENTO', 'FINALIZADO')),
        placas_utilizadas REAL,
        sobras_placas REAL,
        media_pares_por_placa REAL,
        FOREIGN KEY (codigo) REFERENCES produtos(codigo),
        FOREIGN KEY (numero_pedido) REFERENCES pedidos(numero_pedido)
    )
    ''')

    conn.commit()
    conn.close()
    print("Tabelas criadas/validadas com sucesso!")
    return True


def corrigir_tabela_pedidos():
    """Se existir uma versão antiga da tabela 'pedidos' com status 'FECHADO',
    recria a tabela com os valores de status atualizados para 'FINALIZADO'."""
    conn, cursor = conectar_banco()
    try:
        # Verifica se a tabela pedidos existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pedidos'")
        if cursor.fetchone() is None:
            return False

        # Renomeia a tabela existente e cria a nova estrutura atual
        cursor.execute("ALTER TABLE pedidos RENAME TO pedidos_old")

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_pedido DATE NOT NULL,
            numero_pedido TEXT NOT NULL,
            cliente TEXT NOT NULL,
            codigo INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            quantidade_esperada INTEGER NOT NULL,
            data_entrega DATE NOT NULL,
            projecao_placas INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('ABERTO', 'FINALIZADO', 'ANDAMENTO', 'CANCELADO', 'PENDENTE')),
            FOREIGN KEY (codigo) REFERENCES produtos(codigo)
        )
        ''')

        cursor.execute('''
            INSERT INTO pedidos (id, data_pedido, numero_pedido, cliente, codigo, descricao, quantidade_esperada, data_entrega, projecao_placas, status)
            SELECT id, data_pedido, numero_pedido, cliente, codigo, descricao, quantidade_esperada, data_entrega, projecao_placas,
                   CASE WHEN status = 'FECHADO' THEN 'FINALIZADO' ELSE status END
            FROM pedidos_old
        ''')

        cursor.execute("DROP TABLE IF EXISTS pedidos_old")
        conn.commit()
        print("Migração da tabela 'pedidos' concluída (se aplicável).")
        return True
    except Exception as e:
        print(f"Erro na migração da tabela 'pedidos': {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    criar_tabelas()
    correg = corrigir_tabela_pedidos()
    if correg:
        print('Migração executada.')
