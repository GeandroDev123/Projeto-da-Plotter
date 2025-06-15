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

def buscar_pedido(cursor, conn ):
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




# Função para inserir dados de produção
# Data Final, Hora final, Quantidade produzida,placass utilizadas,
# sobras de placas

def solicitar_data_final():
    data_final = input("Digite a data final da produção (dd/mm/yyyy): ").strip()
    try:
        # Verifica se a data está no formato correto
        datetime.strptime(data_final, "%d/%m/%Y")
        return data_final
    except ValueError:
        print("Data final inválida. Utilize o formato dd/mm/yyyy.")
        return None