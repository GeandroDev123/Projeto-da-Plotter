# PEDIDOS NO SISTEMA
# A tabela pedidos será criada para armazenar os pedidos que serão
# cortados pela plotter com os seguintes campos:
# Data do pedido, número do pedido,
# cliente, código, descrição, quantidade esperada, data de entrega,
# projeção de placas e status do pedido.

from datetime import datetime

# Função para inserir data utal no formato correto:
def data_atual():
    return datetime.now().strftime("%d/%m/%Y")
# Função para inseir data de entrega no formato correto:
def data_entrega():
    return datetime.now().strftime("%d/%m/%Y")

# FUNÇÃO PARA CADASTRAR PEDIDOS NA TABELA:
# Os pedidos repetidos serão inseridos normalmente
# usuario deve digitar o código do produto e a descrição e o consumo devem ser inseridos automaticamente.

def cadastrar_pedido(cursor, conn):
    try:
        # Solicita os dados ao usuário
        data_do_pedido = data_atual()
        numero_do_pedido = input("Digite o número do pedido: ").strip()
        cliente = input("Digite o nome do cliente: ").strip()
        codigo = input("Digite o código do produto: ").strip()
        # A descrição do produto será inserida automaticamente
        quantidade_esperada = int(input("Digite a quantidade esperada: ").strip())
        data_entrega = input("Digite a data de entrega (dd/mm/aaaa): ").strip()
        # Projeção de placas será inserida automaticamente,
        # que será a divisão da quantidade esperada pelo consumo do produto.
        status_do_pedido = "ABERTO" # Status do pedido será inserido automaticamente como "ABERTO"

        # buscar a descrição do produto e consumo do produto
        cursor.execute("SELECT descricao, consumo FROM produtos WHERE codigo = ?", (codigo,))
        produto = cursor.fetchone()

        if produto:
            descricao = produto[0]
            consumo = produto[1]
            # Calcula a projeção de placas
            projecao_placas = quantidade_esperada / consumo if consumo != 0 else 0.0  # Tratamento de divisão por zero
            projecao_placas = round(projecao_placas, 2)

            # Insere o pedido na tabela pedidos
            cursor.execute('''
                INSERT INTO pedidos (data_pedido, numero_pedido, cliente, codigo, descricao,
                quantidade_esperada, data_entrega, projecao_placas, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data_do_pedido, numero_do_pedido, cliente, codigo, descricao,
                  quantidade_esperada, data_entrega, projecao_placas, status_do_pedido))
            conn.commit()  # Salva as alterações no banco de dados
            print(f"Pedido '{numero_do_pedido}' cadastrado com sucesso!")

        else:
            print(f"Produto com código {codigo} não encontrado na tabela produtos.")
        
    except ValueError:
            print("Erro: A quantidade esperada deve ser um número inteiro.")
    except Exception as e:
            print(f"Erro ao cadastrar pedido: {e}")

    
    # FUNÇÃO EDITAR PEDIDOS NA TABELA:
    # O usuário deve informar o número do pedido e o sistema irá buscar o pedido na tabela.
    # O usuário poderá editar os seguintes campos:
    # Data do pedido, número do pedido, cliente, código, descrição e 
    # quantidade esperada. A projeção de placas serão calculadas automaticamente.
    # Data de entrega podera ser editada.

def editar_pedido(cursor, conn):
    # Solicita o número do pedido a ser editado ao usuário
    try:
        numero_do_pedido = input("Digite o número do pedido a ser editado: ").strip()

        cursor.execute("""
            SELECT numero_pedido, data_pedido, cliente, codigo, quantidade_esperada, data_entrega
            FROM pedidos WHERE numero_pedido = ?
        """, (numero_do_pedido,))
        pedido = cursor.fetchone()

        if pedido:
            numero_pedido = pedido[0]
            data_pedido = pedido[1]
            cliente = pedido[2]
            codigo = pedido[3]
            quantidade_esperada = pedido[4]
            data_entrega = pedido[5]

            # Solicita novos dados ao usuário
            nova_data_pedido = input(f"Nova data do pedido (atual: {data_pedido}): ").strip() or data_pedido
            novo_cliente = input(f"Novo cliente (atual: {cliente}): ").strip() or cliente
            novo_codigo = input(f"Novo código do produto (atual: {codigo}): ").strip() or codigo
            nova_quantidade_esperada = input(f"Nova quantidade (atual: {quantidade_esperada}): ").strip() or str(quantidade_esperada)
            nova_data_entrega = input(f"Nova data de entrega (atual: {data_entrega}): ").strip() or data_entrega

            try:
                nova_quantidade_esperada = int(nova_quantidade_esperada.strip())
            except ValueError:
                print("Quantidade esperada inválida. Usando valor antigo.")
                nova_quantidade_esperada = quantidade_esperada

            # Busca descrição e consumo do novo produto
            cursor.execute("SELECT descricao, consumo FROM produtos WHERE codigo = ?", (novo_codigo,))
            produto = cursor.fetchone()

            if produto:
                descricao = produto[0]
                consumo = produto[1]
                projecao_placas = round(nova_quantidade_esperada / consumo, 2) if consumo else 0.0 # Tratamento de divisão por zero
            else:
                print("Produto não encontrado. Mantendo dados antigos.")
                cursor.execute("SELECT descricao, projecao_placas FROM pedidos WHERE numero_pedido = ?", (numero_do_pedido,))
                pedido_info = cursor.fetchone()
                descricao = pedido_info[0] if pedido_info else ""
                projecao_placas = pedido_info[1] if pedido_info else 0.0

            # Atualiza no banco
            cursor.execute("""
                UPDATE pedidos
                SET data_pedido = ?, cliente = ?, codigo = ?, descricao = ?,
                    quantidade_esperada = ?, data_entrega = ?, projecao_placas = ?
                WHERE numero_pedido = ?
            """, (
                nova_data_pedido, novo_cliente, novo_codigo, descricao,
                nova_quantidade_esperada, nova_data_entrega, projecao_placas,
                numero_do_pedido
            ))

            conn.commit()
            print(f"Pedido '{numero_do_pedido}' editado com sucesso!")

        else:
            print(f"Pedido com número {numero_do_pedido} não encontrado.")

    except Exception as e:
        print(f"Erro ao editar pedido: {e}")


# FUNÇÃO PARA EXCLUIR PEDIDOS NA TABELA:
# O usuário deve informar o número do pedido e o sistema irá buscar o pedido na tabela.
# O pedido será excluído da tabela.
# O usuário será avisado se o pedido não for encontrado.
# O usuário será avisado se o pedido for excluído com sucesso.
# A exclusão do pedido não será permitida se o status do pedido for igual "ANDAMENTO".
# O usuário será avisado se o pedido não puder ser excluído.
# O usuário será avisado se o pedido for excluído com sucesso.

def excluir_pedido(cursor, conn):
    try:
        # Solicita o número do pedido a ser excluido ao usuário
        numero_pedido = input("Digite o número do pedido a ser excluido: ").strip()

        # Buscar o pedido na tabela
        cursor.execute("SELECT numero_pedido, status FROM pedidos WHERE numero_pedido = ?", (numero_pedido,))
        pedido = cursor.fetchone()

        if pedido:
            numero_pedido, status_do_pedido = pedido

            # Verificar se o status do pedido é "ANDAMENTO ou "ABERTO"
            # Se o status for "ANDAMENTO" ou "ABERTO", o pedido pode ser excluído
            if status_do_pedido in ("ANDAMENTO", "ABERTO"):
                # Exclui o pedido da tabela:
                cursor.execute("DELETE FROM pedidos WHERE numero_pedido = ?", (numero_pedido,))
                conn.commit()
                print(f"Pedido '{numero_pedido}' excluído com sucesso!")
            else:
                print(f"Erro: O pedido '{numero_pedido}' não pode ser excluído porque o status é '{status_do_pedido}'.")
        else:
            print(f"Erro: Pedido com número '{numero_pedido}' não encontrado no sistema.")

    except Exception as e:
        print(f"Erro ao excluir pedido: {e}")

# FUNÇÃO PARA ALTERAR O STATUS DO PEDIDO NA TABELA:
# O usuário deve informar o número do pedido e o sistema irá buscar o pedido na tabela.
# O usuário poderá alterar o status do pedido para "ABERTO" ou "CANCELADO".
# O usuário será avisado se o pedido não for encontrado.
# O usuário será avisado se o status do pedido for alterado com sucesso.
# O usuário será avisado se o status do pedido não puder ser alterado.
# O status do pedido só poderá ser alterado se o status atual for "ABERTO".
# O usuário só poderá alterar o status se pedido se não tiver inciado o status de produção.

def alterar_status_pedido(cursor, conn):

    try:
        # Solicita o número do pedido a ser alterado ao usuário
        numero_pedido = input("Digite o número do pedido a ser alterado: ").strip()

        # Buscar o pedido na tabela
        cursor.execute("SELECT numero_pedido, status FROM pedidos WHERE numero_pedido = ?", (numero_pedido,))
        pedido = cursor.fetchone()

        if pedido:
            numero_encontrado, status_atual = pedido
    
            # Verifica se o status atual do pedido é "ABERTO" ou "CANCELADO"
            if status_atual == "ABERTO" or status_atual == "CANCELADO":
                # Solicita o novo status do pedido ao usuário
                novo_status = input("Digite o novo status do pedido('ABERTO' ou 'CANCELADO'): ").strip().upper()
                if novo_status in ["ABERTO", "CANCELADO"]:
                    # Atualiza o status do pedido na tabela
                    cursor.execute("UPDATE pedidos SET status = ? WHERE numero_pedido = ?", (novo_status, numero_pedido,))
                    conn.commit()
                    print(f"Status do pedido '{numero_pedido}' alterado para '{novo_status}' com sucesso!")
                else:
                    print("Erro: status inválido. O status deve ser  'ABERTO' ou 'CANCELADO'.")
            else:
                print(f"Erro: O status do pedido '{numero_pedido}' não pode ser alterado porque o status atual é '{status_atual}'.")
            
    except Exception as e:
        print(f"Erro ao alterar status do pedido: {e}")

# FUNÇÃO PARA ATUALIZAR O STATUS DO PEDIDO NA TABELA:
# O usuário não poderá atulizar o status do pedido 
# A atulização será feita automaticamente pelo sistema quando o pedido inciar a produção.
# O status inicial do pedido sempre será "ABERTO".
# Quando a quantidade produzida for 0 o status do pedido será "ABERTO".
# O status do pedido será atualizado para "ANDAMENTO" quando o usuário inserir a quantidade produzida.
# O status do pedido será atualizado para "FINALIZADO" quando o usuário inserir a quantidade produzida igual ou superior a 100%.

# CONSTANTES: STATUS DO PEDIDO
STATUS_ABERTO = "ABERTO"
STATUS_ANDAMENTO = "ANDAMENTO"
STATUS_FINALIZADO = "FINALIZADO"

# Função que atualiza o status do pedido com base na quantidade produzida
def atualizar_status_pedido(numero_pedido, quantidade_produzida, cursor, conn):
    try:
        # Verifica o status atual do pedido baseado no número do pedido
        cursor.execute("SELECT status_do_pedido FROM pedidos WHERE numero_pedido = ?", (numero_pedido,))
        resultado = cursor.fetchone()

        if resultado:
            status_do_pedido = resultado[0]  # status atual no banco

            # Lógica para determinar o novo status
            if quantidade_produzida == 0:
                novo_status = STATUS_ABERTO
            elif 0 < quantidade_produzida < 100:
                novo_status = STATUS_ANDAMENTO
            elif quantidade_produzida >= 100:
                novo_status = STATUS_FINALIZADO
            else:
                novo_status = status_do_pedido  # não muda se não atender os critérios

            # Atualiza o status do pedido no banco
            cursor.execute(
                "UPDATE pedidos SET status_do_pedido = ? WHERE numero_pedido = ?",
                (novo_status, numero_pedido)
            )
            conn.commit()

            # Mensagem de sucesso
            print(f"Status do pedido '{numero_pedido}' atualizado para '{novo_status}' com sucesso!")

        else:
            print(f"Erro: Pedido com número '{numero_pedido}' não encontrado.")

    except Exception as e:
        print(f"Erro ao atualizar status do pedido: {e}")


# FUNÇÃO PARA LISTAR PEDIDOS NA TABELA:
# O usuário poderá listar todos os pedidos cadastrados na tabela.
# O usuário poderá listar os pedidos cadastrados na tabela por cliente.
# O usuário poderá listar os pedidos "cadastrados na tabela por status.
# O usuário poderá listar os pedidos "ABERTO" na tabela.
# O usuário poderá listar os pedidos "ANDAMENTO" na tabela.
# O usuário poderá listar os pedidos "FECHADO" na tabela.
# O usuário poderá listar os pedidos "FINALIZADO" na tabela.
# O usuário poderá listar os pedidos "CANCELADO" na tabela.
# O usuário será avisado se não houver pedidos cadastrados na tabela.
# O usuário será avisado se não houver pedidos cadastrados na tabela com o cliente informado.
# O usuário será avisado se não houver pedidos cadastrados na tabela com o status informado.
# O usuário será avisado se não houver pedidos cadastrados na tabela com o status "ABERTO".
# O usuário será avisado se não houver pedidos cadastrados na tabela com o status "ANDAMENTO".
# O usuário será avisado se não houver pedidos cadastrados na tabela com o status "FECHADO".
# O usuário será avisado se não houver pedidos cadastrados na tabela com o status "CANCELADO".

def listar_pedidos(cursor, conn):
    try:
        # Solicita ao usuário o tipo de listagem desejada
        print("Escolha o tipo de listagem:")
        print("1.Listar todos os pedidos: ")
        print("2.Listar pedidos por cliente: ")
        print("3.Listar pedidos por status: ")

        opcao = input("Digite o número da opção desejada: ").strip()

        if opcao == "1":
            # Listar todos os pedidos
            cursor.execute("SELECT * FROM pedidos")
            pedidos = cursor.fetchall()
            if pedidos:
                print("Lista de todos os pedidos:")
                for pedido in pedidos:
                    print(pedido)
            else:
                print("Nenhum pedido cadastrado.")

        elif opcao == "2":
            # Listar pedidos por cliente
            cliente = input("Digite o nome do cliente: ").strip()
            cursor.execute("SELECT * FROM pedidos WHERE cliente = ?", (cliente,))
            pedidos = cursor.fetchall()
            if pedidos:
                print(f"Lista de pedidos do cliente '{cliente}':")
                for pedido in pedidos:
                    print(pedido)
            else:
                print(f"Nenhum pedido encontrado para o cliente '{cliente}'.")

        elif opcao == "3":
            # Listar pedidos por status
            status = input("Digite o status do pedido (ABERTO, ANDAMENTO, FECHADO, CANCELADO): ").strip().upper()
            cursor.execute("SELECT * FROM pedidos WHERE status = ?", (status,))
            pedidos = cursor.fetchall()
            if pedidos:
                print(f"Lista de pedidos com status '{status}':")
                for pedido in pedidos:
                    print(pedido)
            else:
                print(f"Nenhum pedido encontrado com o status '{status}'.")

        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

    except Exception as e:
        print(f"Erro ao listar pedidos: {e}")

# FUNÇÃO PARA MENU DE PEDIDOS:
def menu_pedidos(cursor, conn):
    while True:
        print("\nMenu dos Pedidos: ")
        print("1. Cadastrar Pedido: ")
        print("2. Editar Pedido: ")
        print("3. Excluir Pedido: ")
        print("4. Alterar Status do Pedido: ")
        print("5. Listar Pedidos: ")
        print("6. Sair: ")

        opcao = input("Escolha uma opção:").strip()

        if opcao == "1":
            cadastrar_pedido(cursor, conn)
        elif opcao == "2":
            editar_pedido(cursor, conn)
        elif opcao == "3":
            excluir_pedido(cursor, conn)
        elif opcao == "4":
            alterar_status_pedido(cursor, conn)
        elif opcao == "5":
            listar_pedidos(cursor, conn)
        elif opcao == "6":
            print("Saindo do menu dos pedidos...")
            break
        else:
            print("Opção inválida! Tente novamente.")

        
        




           






              



             

                    
                    

                    
                        
                  

                
                             


            

          