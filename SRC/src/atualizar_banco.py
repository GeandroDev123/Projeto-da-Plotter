# ACRESCENTAR A COLUNA CLIENTE NA TABELA DE PRODUÇÃO

import sqlite3

def atualizar_tabela_banco():
    conn = sqlite3.connect('sistema_plotter.db')
    cursor = conn.cursor()

    try:
        cursor.execute('ALTER TABLE producao ADD COLUMN cliente TEXT')
        conn.commit()
        print("Coluna 'cliente' adicionada à tabela 'producao' com sucesso.")
    except sqlite3.OperationalError as e:
        if "duplicate column name: cliente" in str(e):
            print("A coluna 'cliente' já existe na tabela 'producao'.")
        else:
            print(f"Erro ao adicionar coluna 'cliente': {e}")

    conn.close()
    if __name__ == "__main__":
        atualizar_tabela_banco()
        print("Banco de dados atualizado com sucesso.")