# PRODUÇÃO NO SISTEMA
# Tabela de produção, aqui será controlado dados de produção da plotter:
# Data inicial de corte, numero do pedido, código do produto, descrição do produto,
# Hora de início, hora de término, data final, quantidade produzida, quantidade esperada,
# Eficiência, status da produção (PENDENTE, ANDAMENTO, FINALIZADO), placas utilizadas,
# sobras de placas, média de pares por placas

from datetime import datetime

# Função para buscar um pedido e inseri-lo na produção
# Os pedidos repetidos serão inseridos normalmente
# Depois do pedido Digitado ele deve trazer os seguintes dados cliente,codigo,descricao,quantidade:

def inserir_pedido_na_producao(cursor, conn):
    try:
        data_inicial = input("Digite a data inicial da produção (dd/mm/yyyy): ").strip()
        try:
            # Verifica se a data está no formato correto
            datetime.strptime(data_inicial, "%d/%m/%Y")
        except ValueError:
            print("Data inicial inválida. Por favor, utilize o formato dd/mm/yyyy.")
            return

        numero_pedido = input("Digite o número do pedido: ").strip()
        # cliente será inserido automaticamente
        # codigo será inserido automaticamente
        # descricao será inserida automaticamente
        hora_inicio = input("Digite a hora de inicio da produção (HH:MM): ").strip()
        # quantidade esperada será inserida automaticamente conforme o pedido cadastrado
        status_do_pedido = 'PENDENTE'  # Status inicial do pedido

        # buscar o pedido no banco de dados
        cursor.execute("SELECT cliente, codigo, descricao, quantidade_esperada FROM pedidos WHERE numero_pedido = ?", (numero_pedido,))
        pedido = cursor.fetchone()

        if pedido:
            cliente, codigo, descricao, quantidade_esperada = pedido

            # Inserir os dados na tabela de produção
            cursor.execute('''
                INSERT INTO producao (data_inicial, numero_pedido, cliente, codigo, descricao,hora_inicio, quantidade_esperada, status_do_pedido)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data_inicial, numero_pedido, cliente, codigo, descricao, hora_inicio, quantidade_esperada, status_do_pedido))
            conn.commit()
            print("Dados do pedido inseridos na produção com sucesso!")

        else:
            print("Pedido não encontrado. Verifique o número do pedido e tente novamente.")

    except Exception as e:
        print(f"Ocorreu um erro ao buscar o pedido: {e}")
        conn.rollback()


# Funções para inserir dados finais da produção
# Data Final, Hora final, Quantidade produzida,placass utilizadas,
# sobras de placas

# Função para solicitar e validar hora final
def hora_final():
    hora_final = input("Digite a hora final da produção (HH:MM): ").strip()
    try:
        datetime.strptime(hora_final, "%H:%M")
        return hora_final
    except ValueError:
        print("Hora inválida. Use o formato HH:MM.")
        return None

# Função para solicitar e validar data final
def data_final():
    data_final = input("Digite a data final da produção (dd/mm/yyyy): ").strip()
    try:
        datetime.strptime(data_final, "%d/%m/%Y")
        return data_final
    except ValueError:
        print("Data inválida. Use o formato dd/mm/yyyy.")
        return None

# Solicita os dados finais de produção
def dados_finais_da_producao():
    try:
        # Solicita dados finais da produção
        quantidade_produzida = int(input("Digite a quantidade produzida: ").strip())
        placas_utilizadas = float(input("Digite o número de placas utilizadas: ").strip().replace(',', '.'))
        sobras_placas = float(input("Digite o número de sobras de placas: ").strip().replace(',', '.'))
        return quantidade_produzida, placas_utilizadas, sobras_placas
    except ValueError:
        print("Todos os dados devem ser números.")
        return None, None, None

# Atualiza a linha da produção ainda pendente
def atualizar_producao(hora_final, data_final, quantidade_produzida, placas_utilizadas, sobras_placas, cursor, conn):
    try:
        # Buscar uma produção em aberto
        cursor.execute("SELECT id FROM producao WHERE data_final IS NULL AND hora_final IS NULL")
        producao = cursor.fetchone()

        if not producao:
            print("Nenhuma produção pendente encontrada.")
            return

        producao_id = producao[0]

        cursor.execute('''
            UPDATE producao
            SET hora_final = ?, data_final = ?, quantidade_produzida = ?,
                placas_utilizadas = ?, sobras_placas = ?
            WHERE id = ?
        ''', (hora_final, data_final, quantidade_produzida, placas_utilizadas, sobras_placas, producao_id))

        conn.commit()
        print("Produção finalizada com sucesso!")

    except Exception as e:
        print(f"Erro ao atualizar produção: {e}")
        conn.rollback()

# Função para calcular a eficiência da produção, após a inserção da quantidade produzida
# A eficiência é calculada e inserida na tabela de produção atutomaticamente
def calcular_eficiencia(cursor, conn):
    try:
        # Buscar uma produção finalizada
        cursor.execute("SELECT id, quantidade_esperada, quantidade_produzida FROM producao WHERE data_final IS NOT NULL ORDER BY id DESC LIMIT 1")
        producao = cursor.fetchone()

        if not producao:
            print("Nenhuma produção finalizada encontrada.")
            return
        
        producao_id, quantidade_esperada, quantidade_produzida = producao
        # Calcula a eficiência evitando divisão por zero 
        if quantidade_esperada == 0:
            eficiencia = 0
        else:
            eficiencia = round((quantidade_produzida / quantidade_esperada) * 100, 2)

        # Atualizar a eficiência na tabela de produção
        cursor.execute('''
            UPDATE producao
            SET eficiencia = ?
            WHERE id = ?
        ''', (eficiencia, producao_id))

        conn.commit()
        print(f"Eficiencia calculada e atualizada: {eficiencia:.2f}%")

    except Exception as e:
        print(f"Erro ao calcular eficiência: {e}")
        conn.rollback() 

# Função para atulizar o status da produção na tabela
# Status inicial será sempre PENDENTE
# Pedido com a quantidade produzida menor que 100% será atualizado para ANDAMENTO
# Pedido com a quantidade produzida igual ou superior a 100% será atualizado para FINALIZADO
# Quando o usuario inserir quantidade produzida
# O sistema deve atualizar o status dos pedidos na tabela de produção automaticamente

def atualizar_status_producao(quantidade_produzida,status_do_pedido, cursor, conn):
    try:
        # Buscar produção
        cursor.execute("SELECT numero_pedido, quantidade_produzida FROM producao WHERE data_final IS NOT NULL ORDER BY id DESC LIMIT 1")
        producao = cursor.fetchone()

        if not producao:
            print("Nenhuma produção finalizada encontrada.")
            return
        numero_pedido, quantidade_produzida = producao

        # Atualizar o status com base na quantidade produzida
        if quantidade_produzida < 100:
            status_do_pedido = 'ANDAMENTO'
        elif quantidade_produzida >= 100:
            status_do_pedido = 'FINALIZADO'
        else:
            status_do_pedido= 'PENDENTE'
        # Atualizar o status na tabela de produção
        cursor.execute('''
        UPDATE producao
        SET status_do_pedido = ?
        WHERE numero_pedido = ?
        ''', (status_do_pedido, numero_pedido))
        conn.commit()
        print(f"Status da produção atualizado para: {status_do_pedido}")
    except Exception as e:
        print(f"Erro ao atualizar status da produção: {e}")
        conn.rollback()

# Função para calcular a média de pares por placa
# Após o usuário inserir a quantidade produzida, placas utilizadas 
# Sistema deve calcular a média de pares por placa
# Quantidade produzida / placas utilizadas
# valor deve ser inserido na tabela de produção automaticamente

def calcular_media_pares_por_placa(quantidade_produzida:int, placas_utilizadas:float, cursor, conn)->None:
    try:
        # Verifica se as placas utilizadas são diferentes de zero,para evitar divisão por zero:
        if placas_utilizadas == 0:
            media_pares_por_placa = 0

        else:
            media_pares_por_placa = round(quantidade_produzida / placas_utilizadas, 2)

        # Buscar a última produção finalizada
        cursor.execute("SELECT id FROM producao WHERE data_final IS NOT NULL ORDER BY id DESC LIMIT 1")
        producao = cursor.fetchone()

        if not producao:
            print("Nenhuma produção finalizada encontrada.")
            return

        producao_id = producao[0]

        # Atualizar a média de pares por placa na tabela de produção
        cursor.execute('''
            UPDATE producao
            SET media_pares_por_placa = ?
            WHERE id = ?
        ''', (media_pares_por_placa, producao_id))

        conn.commit()
        print(f"Média de pares por placa calculada e atualizada: {media_pares_por_placa:.2f}")

    except Exception as e:
        print(f"Erro ao calcular média de pares por placa: {e}")
        conn.rollback()

# Função para exibir o menu de produção
def menu_producao(cursor, conn):
    while True:
        print("\nMenu da Produção:")
        print("1. Inserir pedido na produção")
        print("2. Dados finais da produção")
        print("3. Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            inserir_pedido_na_producao(cursor, conn)
        elif opcao == '2':
            dados_finais_da_producao(cursor, conn)
        elif opcao == '3':
            print("Saindo do menu de produção.")
            break
        else:
            print("Opção inválida. Tente novamente.")
