import sys
import os

# Adiciona o diretório pai ao caminho do sistema para importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from SRC.produtos import menu_produtos
from SRC.pedidos import menu_pedidos
from SRC.producao import menu_producao
from DATA.database_da_plotter import conectar_banco


def main():
    """Função principal do sistema de gerenciamento de produção."""
    conn = None
    cursor = None
    
    try:
        # Conectar ao banco de dados
        print("Conectando ao banco de dados...")
        conn, cursor = conectar_banco()
        
        if conn is None or cursor is None:
            print("Erro: Não foi possível conectar ao banco de dados.")
            return
        
        print("Conexão estabelecida com sucesso!\n")
        
        # Menu principal
        while True:
            try:
                print("\n" + "="*40)
                print("         MENU PRINCIPAL")
                print("="*40)
                print("1. Gerenciar Produtos")
                print("2. Gerenciar Pedidos")
                print("3. Gerenciar Produção")
                print("4. Sair do Sistema")
                print("="*40)
                
                opcao = input("\nEscolha uma opção: ").strip()

                if opcao == '1':
                    menu_produtos(cursor, conn)
                elif opcao == '2':
                    menu_pedidos(cursor, conn)
                elif opcao == '3':
                    menu_producao(cursor, conn)
                elif opcao == '4':
                    print("\nEncerrando o sistema...")
                    break
                else:
                    print("Opção inválida! Escolha entre 1 e 4.")
                    
            except KeyboardInterrupt:
                print("\n\nSistema interrompido pelo usuário.")
                break
            except Exception as e:
                print(f"Erro ao processar opção: {e}")
                print("Por favor, tente novamente.")
    
    except Exception as e:
        print(f"Erro crítico ao inicializar o sistema: {e}")
    
    finally:
        # Garantir fechamento da conexão
        if conn is not None:
            try:
                conn.close()
                print("Conexão encerrada com sucesso.")
            except Exception as e:
                print(f"Erro ao fechar conexão: {e}")


if __name__ == "__main__":
    main()
    
    
