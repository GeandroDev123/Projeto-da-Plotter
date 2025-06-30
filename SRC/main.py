import sys # Biblioteca para manipulação de sistema
# Adiciona o diretório pai ao caminho do sistema para importar módulos
import os # Biblioteca para manipulação de sistema
# Ele é usado para encontrar onde você está no computador (diretórios) de forma automática, 
# sem ter que escrever caminhos fixos.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from SRC.produtos import menu_produtos
from SRC.pedidos import menu_pedidos
from SRC.producao import menu_producao
from DATA.database_da_plotter import conectar_banco

def main():
    conn, cursor = conectar_banco()
    menu_produtos(cursor, conn)
    menu_pedidos(cursor, conn)
    menu_producao(cursor, conn)
    conn.close()

if __name__ == "__main__":
    main()
    # Executa a função principal do sistema
    # Se o arquivo for executado diretamente, a função main() será chamada.
    
    





