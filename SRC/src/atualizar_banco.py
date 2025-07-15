# # #ACRESCENTAR A COLUNA STATUS NA TABELA DE PRODUÇÃO

# import sqlite3

# def atualizar_tabela_producao():
#     conn = sqlite3.connect('sistema_plotter.db')
#     cursor = conn.cursor()

#     try:
#         cursor.execute('ALTER TABLE producao ADD COLUMN status TEXT')
#         conn.commit()
#         print("Coluna 'status' adicionada com sucesso à tabela 'producao'.")
#     except sqlite3.OperationalError as e:
#         if "duplicate column name" in str(e):
#             print("A coluna 'status' já existe.")
#         else:
#             print(f"Erro ao adicionar coluna: {e}")

#     conn.close()

# if __name__ == "__main__":
#     atualizar_tabela_producao()

# import sqlite3
# print(sqlite3.sqlite_version)

    

   