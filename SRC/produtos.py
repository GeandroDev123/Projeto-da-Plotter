# Logica da tabela produtos: vamos armazenar os produtos que serão cortados pela plotter com os seguintes campos:
# codigo, descricao, cliente, unidade, navalha, modelo, consumo e status do produto.

# 1. Verifica se o produto já existe na tabela, caso exista, atualiza os dados do produto.
# 2. Caso não exista, insere o produto na tabela.
# 3. Retorna uma mensagem de sucesso ou erro.
# 4. Caso o produto esteja inativo, não será possível cadastrar pedidos para este produto.
# 5. Caso o produto esteja ativo, será possível cadastrar pedidos para este produto.


# Função para cadastrar produtos na tabela produtos:
def cadastrar_produto(cursor, conn):
    try:
        # Solicita os dados do produto ao usuário
        codigo = input("Digite o código do produto: ").strip()
        descricao = input("Digite a descrição do produto: ").strip()
        cliente = input("Digite o cliente: ").strip()
        unidade = input("Digite a unidade de medida: ").strip()
        navalha = input("Digite o tipo de navalha: ").strip()
        modelo = input("Digite o modelo do produto: ").strip()
        consumo = float(input("Digite o consumo do produto: ").strip().replace(',', '.'))
        status = input("Digite o status do produto (ativo/inativo): ").strip().lower()

        # Verifica se o produto já existe na tabela
        cursor.execute("SELECT * FROM produtos WHERE codigo = ?", (codigo,))
        if cursor.fetchone():
            print(f"Produto com código {codigo} já existe na tabela.")
            return
        # Insere o novo produto na tabela
        cursor.execute('''
            INSERT INTO produtos (codigo, descricao, cliente, unidade, navalha, modelo, consumo, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (codigo, descricao, cliente, unidade, navalha, modelo, consumo, status))

        conn.commit()  # Salva as alterações no banco de dados
        print(f"Produto '{descricao}' cadastrado com sucesso!")
    except ValueError:
        print("Erro: O consumo deve ser um número.")
    except Exception as e:
        print(f"Erro ao cadastrar produto: {e}")



# Função para editar produtos na tabela produtos:
def editar_produto(cursor, conn):
    try:
        # Solicita o código do produto a ser editado
        codigo = input("Digite o código do produto a ser editado: ").strip()
        # Verifica se o produto existe na tabela
        cursor.execute("SELECT * FROM produtos WHERE codigo = ?", (codigo,))
        produto = cursor.fetchone()

        if produto:
            nova_descricao = input("Digite a nova descrição do produto: ").strip()
            novo_cliente = input("Digite o novo cliente: ").strip()
            nova_unidade = input("Digite a nova unidade de medida: ").strip()
            nova_navalha = input("Digite o novo tipo de navalha: ").strip()
            novo_modelo = input("Digite o novo modelo do produto: ").strip()
            novo_consumo = float(input("Digite o novo consumo do produto: ").strip().replace(',', '.'))
            

            # Atualiza os dados do produto na tabela
            cursor.execute('''
                UPDATE produtos
                SET descricao = ?, cliente = ?, unidade = ?, navalha = ?, modelo = ?, consumo = ?
                WHERE codigo = ?
            ''', (nova_descricao, novo_cliente, nova_unidade, nova_navalha, novo_modelo, novo_consumo, codigo))

            conn.commit()
            print(f"Produto '{produto[1]}' editado com sucesso!")

        else:
            print(f"Produto com código {codigo} não encontrado na tabela.")

    except ValueError:
        print("Erro: O consumo deve ser um número.")
    except Exception as e:
        print(f"Erro ao editar produto: {e}")

# Função para alterar o status do produto na tabela produtos:
def alterar_status_produto(cursor, conn):
    try:
        # Solicita o código do produto a ter status alterado
        codigo = input("Digite o código do produto a ter status alterado:").strip()

        # Verifica se o produto existe na tabela
        cursor.execute("SELECT * FROM produtos WHERE codigo = ?",(codigo,))
        produto = cursor.fetchone()

        if produto:
            novo_status = input("Digite o novo status do produto (ativo/inativo): ").strip().lower()
            if novo_status not in ['ativo', 'inativo']:
                print("Erro: O status deve ser ativo ou inativo.")
                return

            # Atualiza o status do produto na tabela
            cursor.execute('''
                UPDATE produtos
                SET status = ?
                WHERE codigo = ?
            ''', (novo_status, codigo))
            conn.commit()
            print(f"Status do produto {produto[1]} alterado para {novo_status} com sucesso!")

        else:
            print(f"Produto com código {codigo} não encontrado na tabela.")

    except Exception as e:
        print(f"Erro ao alterar status do produto: {e}")

# Função para excluir produtos na tabela produtos:
def excluir_produto(cursor, conn):
    try:
        # Solicita o código do produto a ser excluído ao usuário
        codigo = input("Digite o código do produto a ser excluído: ").strip()
        # Verificar se o produto existe na tabela
        cursor.execute("SELECT * FROM produtos WHERE codigo = ?", (codigo,))
        produto = cursor.fetchone()

        if produto:
            # Exclui o produto da tabela
            cursor.execute("DELETE FROM produtos WHERE codigo = ?", (codigo,))
            conn.commit()
            print(f"Produto '{produto[1]}' excluído com sucesso!")
        else:
            print(f"Produto com código {codigo} não encontrado na tabela.")
    except Exception as e:
        print(f"Erro ao excluir produto: {e}")

# Função para listar produtos na tabela produtos:
def listar_produtos(cursor, conn):
    try:
        # Solicita o status dos produtos a serem listados ao usuário
        status = input("Digite o status dos produtos a serem listados (ativo/inativo):").strip().lower()
        if status not in ['ativo','inativo']:
            # Verifica se o status é válido
            print("Erro: o status dever ser ativo ou inativo.")
            return
        # Consulta os produtos na tabela com o status especificado
        cursor.execute("SELECT * FROM produtos WHERE status = ?", (status,))
        produtos = cursor.fetchall()

        if produtos:
            print(f"\nProdutos com status {status}:")
            for produto in produtos:
                print("\nLista de produtos:")
                print(f"Código: {produto[0]}, Descrição: {produto[1]}, Cliente: {produto[2]}, Unidade: {produto[3]}, "
                      f"Navalha: {produto[4]}, Modelo: {produto[5]}, Consumo: {produto[6]}, Status: {produto[7]}")
                print("=".center(30, "="))
        else:
            print(f"Nenhum produto encontrado com status {status}.")
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")


# Função para Menu de Produtos:
def menu_produtos(cursor, conn):
    while True:
        print("\nMenu de Produtos:")
        print("1. Cadastrar Produto")
        print("2. Editar Produto")
        print("3. Alterar Status do Produto")
        print("4. Excluir Produto")
        print("5. Listar Produtos")
        print("6. Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            cadastrar_produto(cursor, conn)
        elif opcao == '2':
            editar_produto(cursor, conn)
        elif opcao == '3':
            alterar_status_produto(cursor, conn)
        elif opcao == '4':
            excluir_produto(cursor, conn)
        elif opcao == '5':
            listar_produtos(cursor, conn)
        elif opcao == '6':
            print("Saindo do menu de produtos...")
            break
        else:
            print("Opção inválida! Tente novamente.")

        