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
        data_finalizacao = "00/00/0000"  # Inicializa como "00/00/0000", será preenchido depois
        # Validar a data inicial
        
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
        hora_termino = "00:00"  # Inicializa como "00:00", será preenchido depois
        quantidade_produzida = "0" # Inicializa como 0, será preenchido depois
        eficiencia = "0.0"  # Inicializa como 0.0, será preenchido depois
        placas_utilizadas = "0.0"  # Inicializa como 0.0, será preenchido depois
        sobras_placas = "0.0"  # Inicializa como 0.0, será preenchido depois
        media_pares_por_placa = "0.0"  # Inicializa como 0.0, será preenchido depois
        # quantidade esperada será inserida automaticamente conforme o pedido cadastrado
        status = 'PENDENTE'  # Status inicial do pedido

        # buscar o pedido no banco de dados
        cursor.execute("SELECT cliente, codigo, descricao, quantidade_esperada FROM pedidos WHERE numero_pedido = ?", (numero_pedido,))
        pedido = cursor.fetchone()

        if pedido:
            cliente, codigo, descricao, quantidade_esperada = pedido

            # Inserir os dados na tabela de produção
            cursor.execute('''
                INSERT INTO producao (data_inicial,data_finalizacao, numero_pedido, cliente, codigo, descricao,hora_inicio,hora_termino, quantidade_esperada, quantidade_produzida, eficiencia, placas_utilizadas, sobras_placas, media_pares_por_placa, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data_inicial, data_finalizacao, numero_pedido, cliente, codigo, descricao, hora_inicio, hora_termino, quantidade_esperada, quantidade_produzida, eficiencia, placas_utilizadas, sobras_placas, media_pares_por_placa, status))
            conn.commit()
            print("Dados do pedido inseridos na produção com sucesso!")

        else:
            print("Pedido não encontrado. Verifique o número do pedido e tente novamente.")

    except Exception as e:
        print(f"Ocorreu um erro ao buscar o pedido: {e}")
        conn.rollback()


# Funções para inserir dados finais da produção
# Essa função só deverá ser chamada quando o pedido estiver finalizado
# Data Final, Hora termino, Quantidade produzida,placass utilizadas,
# sobras de placas

# Função para solicitar e validar hora de término
# Essa função deve ser chamada quando o pedido estiver finalizado
def hora_termino():
    hora_termino = input("Digite a hora de término da produção (HH:MM): ").strip()
    try:
        datetime.strptime(hora_termino, "%H:%M")
        return hora_termino
    except ValueError:
        print("Hora inválida. Use o formato HH:MM.")
        return None

# Função para solicitar e validar data final
def data_final():
    while True:
        data_final = input("Digite a data final da produção (dd/mm/yyyy): ").strip()
        try:
            datetime.strptime(data_final, "%d/%m/%Y")
            return data_final
        except ValueError:
            print("Data inválida. Use o formato dd/mm/yyyy.")

# Solicita os dados finais de produção
def dados_finais_da_producao():
    while True:
        try:
            quantidade_produzida = int(input("Digite a quantidade produzida: ").strip())
            placas_utilizadas = float(input("Digite o número de placas utilizadas: ").strip().replace(',', '.'))
            sobras_placas = float(input("Digite o número de sobras de placas: ").strip().replace(',', '.'))
            return quantidade_produzida, placas_utilizadas, sobras_placas
        except ValueError:
            print("Todos os dados devem ser números. Tente novamente.")

# Atualiza a linha da produção ainda pendente
def atualizar_producao(hora_termino, data_finalizacao, quantidade_produzida, placas_utilizadas, sobras_placas, cursor, conn):
    try:
        # Buscar uma produção em aberto
        cursor.execute("SELECT id FROM producao WHERE data_finalizacao = '00/00/0000' AND hora_termino = '00:00'")
        producao = cursor.fetchone()

        if not producao:
            print("Nenhuma produção pendente encontrada.")
            return False

        producao_id = producao[0]

        cursor.execute('''
            UPDATE producao
            SET hora_termino = ?, data_finalizacao = ?, quantidade_produzida = ?,
                placas_utilizadas = ?, sobras_placas = ?
            WHERE id = ?
        ''', (hora_termino, data_finalizacao, quantidade_produzida, placas_utilizadas, sobras_placas, producao_id))

        conn.commit()
        print("Produção finalizada com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao atualizar produção: {e}")
        conn.rollback()
        return False

# Função para calcular a eficiência da produção, após a inserção da quantidade produzida
# A eficiência é calculada e inserida na tabela de produção atutomaticamente
def calcular_eficiencia(cursor, conn):
    try:
        # Buscar uma produção finalizada
        cursor.execute("SELECT id, quantidade_esperada, quantidade_produzida FROM producao WHERE data_finalizacao != '00/00/0000' ORDER BY id DESC LIMIT 1")
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

def atualizar_status_producao(cursor, conn):
    try:
        # Buscar a última produção finalizada
        cursor.execute(
            "SELECT id, quantidade_esperada, quantidade_produzida FROM producao WHERE data_finalizacao != '00/00/0000' ORDER BY id DESC LIMIT 1"
        )
        producao = cursor.fetchone()

        if not producao:
            print("Nenhuma produção finalizada encontrada.")
            return

        producao_id, quantidade_esperada, quantidade_produzida = producao

        # Garante que os valores são numéricos
        try:
            quantidade_esperada = float(quantidade_esperada)
            quantidade_produzida = float(quantidade_produzida)
        except (TypeError, ValueError):
            print("Erro nos dados de quantidade. Não foi possível atualizar o status.")
            return

        # Atualizar o status com base na quantidade produzida
        if quantidade_produzida < quantidade_esperada:
            status = 'ANDAMENTO'
        else:
            status = 'FINALIZADO'

        # Atualizar o status na tabela de produção
        cursor.execute(
            '''
            UPDATE producao
            SET status = ?
            WHERE id = ?
            ''',
            (status, producao_id)
        )
        conn.commit()
        print(f"Status da produção atualizado para: {status}")
    except Exception as e:
        print(f"Erro ao atualizar status da produção: {e}")
        conn.rollback()

# Função para calcular a média de pares por placa
# Após o usuário inserir a quantidade produzida, placas utilizadas 
# Sistema deve calcular a média de pares por placa
# Quantidade produzida / placas utilizadas
# valor deve ser inserido na tabela de produção automaticamente

def calcular_media_pares_por_placa(quantidade_produzida: int, placas_utilizadas: float, cursor, conn) -> None:
    try:
        # Verifica se as placas utilizadas são diferentes de zero para evitar divisão por zero
        if placas_utilizadas == 0:
            media_pares_por_placa = 0
        else:
            media_pares_por_placa = round(quantidade_produzida / placas_utilizadas, 2)

        # Buscar a última produção finalizada
        cursor.execute("SELECT id FROM producao WHERE data_finalizacao != '00/00/0000' ORDER BY id DESC LIMIT 1")
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

# Função para editar o pedido na produção
# Essa função deve ser chamada quando o usuário quiser editar um pedido na produção
def editar_pedido_na_producao(cursor, conn):
    try:
        numero_pedido = input("Digite o número do pedido que deseja editar: ").strip()
        
        # Buscar o pedido na tabela de produção
        cursor.execute("SELECT * FROM producao WHERE numero_pedido = ?", (numero_pedido,))
        producao = cursor.fetchone()

        if not producao:
            print("Pedido não encontrado na produção.")
            return

        # Exibir os dados atuais do pedido conforme a ordem da tabela
        print("\nDados atuais do pedido:")
        print(f"ID: {producao[0]}")
        print(f"Data Inicial: {producao[1]}")
        print(f"Data Finalização: {producao[2]}")
        print(f"Número do Pedido: {producao[3]}")
        print(f"Cliente: {producao[4]}")
        print(f"Código: {producao[5]}")
        print(f"Descrição: {producao[6]}")
        print(f"Hora Início: {producao[7]}")
        print(f"Hora Término: {producao[8]}")
        print(f"Quantidade Esperada: {producao[9]}")
        print(f"Quantidade Produzida: {producao[10]}")
        print(f"Eficiencia: {producao[11]}%")
        print(f"Placas Utilizadas: {producao[12]}")
        print(f"Sobras de Placas: {producao[13]}")
        print(f"Média de Pares por Placa: {producao[14]}")
        print(f"Status: {producao[15]}")

        # Solicitar confirmação para editar o pedido
        confirmacao = input("Você deseja editar este pedido? (sim/não): ").strip().lower()
        if confirmacao != 'sim':
            print("Edição cancelada.")
            return
        
        # Editar os dados do pedido somente o que o usuário quiser
        print("\nDigite os novos dados para o pedido (deixe em branco para manter o valor atual):")
        nova_data_inicial = input(f"Nova data inicial (atual: {producao[1]}): ").strip() or producao[1]
        nova_hora_inicio = input(f"Nova hora de início (atual: {producao[7]}): ").strip() or producao[7]
        nova_hora_termino = input(f"Nova hora de término (atual: {producao[8]}): ").strip() or producao[8]
        nova_quantidade_produzida = input(f"Nova quantidade produzida (atual: {producao[10]}): ").strip() or producao[10]
        novas_placas_utilizadas = input(f"Novas placas utilizadas (atual: {producao[12]}): ").strip() or producao[12]
        novas_sobras_placas = input(f"Novas sobras de placas (atual: {producao[13]}): ").strip() or producao[13]

        # Conversão de tipos
        try:
            nova_quantidade_produzida = int(nova_quantidade_produzida)
            novas_placas_utilizadas = float(novas_placas_utilizadas)
            novas_sobras_placas = float(novas_sobras_placas)
        except ValueError:
            print("Erro: quantidade produzida, placas utilizadas e sobras devem ser numéricos.")
            return

        # Recalcular média de pares por placa
        if novas_placas_utilizadas == 0:
            nova_media_pares_por_placa = 0
        else:
            nova_media_pares_por_placa = round(nova_quantidade_produzida / novas_placas_utilizadas, 2)

        # Atualizar status
        quantidade_esperada = producao[9]
        status = 'FINALIZADO' if nova_quantidade_produzida >= quantidade_esperada else 'ANDAMENTO'

        # Validar a nova data inicial
        try:
            datetime.strptime(nova_data_inicial, "%d/%m/%Y")
        except ValueError:
            print("Data inicial inválida. Por favor, utilize o formato dd/mm/yyyy.")
            return

        # Atualizar os dados na tabela de produção
        cursor.execute('''
            UPDATE producao
            SET data_inicial = ?, hora_inicio = ?, hora_termino = ?, quantidade_produzida = ?, placas_utilizadas = ?, sobras_placas = ?, media_pares_por_placa = ?, status = ?
            WHERE id = ?
        ''', (nova_data_inicial, nova_hora_inicio, nova_hora_termino, nova_quantidade_produzida, novas_placas_utilizadas, novas_sobras_placas, nova_media_pares_por_placa, status, producao[0]))

        conn.commit()
        print("Pedido atualizado com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro ao editar o pedido: {e}")
        conn.rollback()

# Função para exibir o menu de produção
def menu_producao(cursor, conn):
    while True:
        print("\nMenu da Produção:")
        print("1. Inserir pedido na produção")
        print("2. Dados finais da produção")
        print("3. Editar pedido na produção")
        print("4. Sair")
        

        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            inserir_pedido_na_producao(cursor, conn)
        elif opcao == '2':
            hora_termino_value = hora_termino()
            if hora_termino_value:
                data_finalizacao_value = data_final()
                quantidade_produzida, placas_utilizadas, sobras_placas = dados_finais_da_producao()
                if atualizar_producao(hora_termino_value, data_finalizacao_value, quantidade_produzida, placas_utilizadas, sobras_placas, cursor, conn):
                    calcular_eficiencia(cursor, conn)
                    atualizar_status_producao(cursor, conn)
                    calcular_media_pares_por_placa(quantidade_produzida, placas_utilizadas, cursor, conn)
        elif opcao == '3':
            editar_pedido_na_producao(cursor, conn)
        elif opcao == '4':
            print("Saindo do menu de produção.")
            break
        else:
            print("Opção inválida. Tente novamente.")
