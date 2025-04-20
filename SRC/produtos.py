# Logica da tabela produtos: vamos armazenar os produtos que serão cortados pela plotter com os seguintes campos:
# codigo, descricao, cliente, unidade, navalha, modelo, consumo e status do produto.

# 1. Verifica se o produto já existe na tabela, caso exista, atualiza os dados do produto.
# 2. Caso não exista, insere o produto na tabela.
# 3. Retorna uma mensagem de sucesso ou erro.
# 4. Caso o produto esteja inativo, não será possível cadastrar pedidos para este produto.
# 5. Caso o produto esteja ativo, será possível cadastrar pedidos para este produto.

# Função para cadastrar produtos na tabela produtos:
def cadastrar_produto(cursor, conn):
    # Solicita os dados do produto ao usuário
    codigo = input("Digite o código do produto:").strip()
    descricao = input("Digite a descrição do produto: ").strip()
    cliente = input("Digite o nome do cliente:").strip()
    unidade = input("Digite a unidade de medida:").strip()
    navalha = input("Digite o tipo de navalha:").strip()
    modelo = input ("Digite o modelo do produto:").strip()
    consumo = int(float(input("Digite o consumo do produto:"))).strip()
    # O consumo deve ser um número inteiro ou um decimal, então usamos float() para converter a entrada do usuário.
    # Se o usuário não digitar nada, o valor padrão será 0.
    status = "ATIVO" # O status padrão do produto será ativo.

    # Verifica se o produto já existe na tabela
    cursor.execute("SELECT * FROM produtos WHERE codigo = ?", (codigo,))
    if cursor.fetchone():
        print(f"Produto com código {codigo} já existe na tabela.")
        return
    cadastrar_produto(cursor, conn)

    # Insere o produto na tabela
    cursor.execute('''
        INSERT INTO produtos (codigo, descricao, cliente, unidade, navalha, modelo, consumo, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (codigo, descricao, cliente, unidade, navalha, modelo, consumo, status))
    conn.commit() # Salva as alterações no banco de dados
    print(f"Produto cadastrado com sucesso!")

# Função para editar produtos na tabela produtos:
def editar_produto(cursor, conn):
    # Solicita o código do produto a ser editado ao usuário
    codigo = input("Digite o código do produto a ser editado: ")
    # Verifica se o produto existe na tabela
    cursor.execute("SELECT * FROM produtos WHERE codigo = ?", (codigo,))
    produto = cursor.fetchone()

    if produto:
        # Solicita os novos dados do produto ao usuário
        nova_descricao = input("Digite a nova descrição do produto:")
        novo_cliente = input("Digite o novo cliente: ")
        nova_unidade = input("Digite a nova unidade de medida: ")
        nova_navalha = input("Digite o novo tipo de navalha:")
        novo_modelo = input("Digite o novo modelo do produto: ")
        novo_consumo = float(input("Digite o novo consumo do produto:"))
        novo_status = input("Digite o novo status do produto (ATIVO/INATIVO):").upper()
        # Atualiza os dados do produto na tabela
        cursor.execute('''
            UPDATE produtos SET descricao = ?, cliente = ?, unidade = ?, navalha = ?, modelo = ?, consumo = ?, status = ?
            WHERE codigo = ?''', (nova_descricao, novo_cliente, nova_unidade, nova_navalha, novo_modelo, novo_consumo, 
                                  novo_status, codigo))
        conn.commit() # Salva as alterações no banco de dados

    





