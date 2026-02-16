# PRODUÇÃO NO SISTEMA
# Tabela de produção, aqui será controlado dados de produção da plotter:
# Data inicial de corte, numero do pedido, código do produto, descrição do produto,
# Hora de início, hora de término, data final, quantidade produzida, quantidade esperada,
# Eficiência, status da produção (PENDENTE, ANDAMENTO, FINALIZADO), placas utilizadas,
# sobras de placas, média de pares por placas

from datetime import datetime
from DATA.database_da_plotter import conectar_banco
from SRC.pedidos import atualizar_status_pedido
conn, cursor = conectar_banco()


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
        data_finalizacao = input("Digite a data final da produção (dd/mm/yyyy): ").strip()
        try:
            datetime.strptime(data_finalizacao, "%d/%m/%Y")
            return data_finalizacao
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
        cursor.execute("SELECT id, numero_pedido FROM producao WHERE data_finalizacao = '00/00/0000' AND hora_termino = '00:00'")
        producao = cursor.fetchone()

        if not producao:
            print("Nenhuma produção pendente encontrada.")
            return None

        producao_id = producao[0]
        numero_pedido = producao[1]

        cursor.execute('''
            UPDATE producao
            SET hora_termino = ?, data_finalizacao = ?, quantidade_produzida = ?,
                placas_utilizadas = ?, sobras_placas = ?
            WHERE id = ?
        ''', (hora_termino, data_finalizacao, quantidade_produzida, placas_utilizadas, sobras_placas, producao_id))

        conn.commit()
        print("Produção finalizada com sucesso!")
        return numero_pedido

    except Exception as e:
        print(f"Erro ao atualizar produção: {e}")
        conn.rollback()
        return None

# Função para calcular a eficiência da produção, após a inserção da quantidade produzida
# A eficiência é calculada e inserida na tabela de produção atutomaticamente
def calcular_eficiencia(cursor, conn):
    try:
        cursor.execute("""
            SELECT id, quantidade_esperada, quantidade_produzida
            FROM producao
            WHERE data_final IS NOT NULL
            ORDER BY id DESC
            LIMIT 1
        """)
        producao = cursor.fetchone()

        if not producao:
            print("Nenhuma produção finalizada encontrada.")
            return

        producao_id = producao["id"]
        quantidade_esperada = producao["quantidade_esperada"]
        quantidade_produzida = producao["quantidade_produzida"]

        if quantidade_esperada == 0:
            eficiencia = 0.0
        else:
            eficiencia = round(
                (quantidade_produzida / quantidade_esperada) * 100, 2
            )

        cursor.execute("""
            UPDATE producao
            SET eficiencia = ?
            WHERE id = ?
        """, (eficiencia, producao_id))

        conn.commit()
        print(f"Eficiência calculada corretamente: {eficiencia}%")

    except Exception as e:
        conn.rollback()
        print(f"Erro ao calcular eficiência: {e}")


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

# Função auxiliar para validar hora (HH:MM)
def validar_hora(hora: str) -> bool:
    """Valida formato de hora HH:MM"""
    try:
        datetime.strptime(hora, "%H:%M")
        return True
    except ValueError:
        return False

# Função auxiliar para validar data (DD/MM/YYYY)
def validar_data(data: str) -> bool:
    """Valida formato de data DD/MM/YYYY"""
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Função para editar o pedido na produção
# Essa função deve ser chamada quando o usuário quiser editar um pedido na produção
# ordem de exibição dos dados conforme a tabela de produção
from datetime import datetime

def editar_pedido_na_producao(cursor, conn):
    try:
        numero_pedido = input("Digite o número do pedido que deseja editar: ").strip()
        if not numero_pedido:
            print("Número do pedido não pode estar vazio.")
            return

        cursor.execute("""
            SELECT
                id,
                data_inicial,
                numero_pedido,
                cliente,
                codigo,
                descricao,
                hora_inicio,
                hora_termino,
                data_finalizacao,
                quantidade_produzida,
                quantidade_esperada,
                eficiencia,
                status,
                placas_utilizadas,
                sobras_placas,
                media_pares_por_placa
            FROM producao
            WHERE numero_pedido = ?
        """, (numero_pedido,))

        producao = cursor.fetchone()
        if not producao:
            print("Pedido não encontrado.")
            return

        (
            producao_id,
            data_inicial,
            numero_pedido,
            cliente,
            codigo,
            descricao,
            hora_inicio,
            hora_termino,
            data_finalizacao,
            quantidade_produzida,
            quantidade_esperada,
            eficiencia,
            status_atual,
            placas_utilizadas,
            sobras_placas,
            media_pares_por_placa
        ) = producao

        quantidade_esperada = quantidade_esperada or 0
        quantidade_produzida = quantidade_produzida or 0
        placas_utilizadas = placas_utilizadas or 0
        sobras_placas = sobras_placas or 0

        print("\n" + "="*50)
        print("DADOS ATUAIS DO PEDIDO")
        print("="*50)
        print(f"Pedido: {numero_pedido}")
        print(f"Produzido: {quantidade_produzida}")
        print(f"Esperado: {quantidade_esperada}")
        print(f"Eficiência: {eficiencia}%")
        print(f"Status: {status_atual}")
        print("="*50)

        if input("\nDeseja editar? (sim/não): ").lower() != "sim":
            return

        nova_data_inicial = input(f"Data inicial [{data_inicial}]: ").strip() or data_inicial
        nova_hora_inicio = input(f"Hora início [{hora_inicio}]: ").strip() or hora_inicio
        nova_hora_termino = input(f"Hora término [{hora_termino}]: ").strip() or hora_termino
        nova_data_finalizacao = input(f"Data final [{data_finalizacao}]: ").strip() or data_finalizacao

        nova_quantidade_produzida = int(
            input(f"Quantidade produzida [{quantidade_produzida}]: ").strip() or quantidade_produzida
        )

        novas_placas_utilizadas = float(
            input(f"Placas utilizadas [{placas_utilizadas}]: ").strip().replace(',', '.') or placas_utilizadas
        )

        novas_sobras_placas = float(
            input(f"Sobras de placas [{sobras_placas}]: ").strip().replace(',', '.') or sobras_placas
        )

        # Média pares por placa
        nova_media_pares_por_placa = (
            round(nova_quantidade_produzida / novas_placas_utilizadas, 2)
            if novas_placas_utilizadas > 0 else 0
        )

        # Eficiência
        nova_eficiencia = (
            round((nova_quantidade_produzida / quantidade_esperada) * 100, 2)
            if quantidade_esperada > 0 else 0
        )

        # Status
        if nova_quantidade_produzida >= quantidade_esperada and quantidade_esperada > 0:
            novo_status = "FINALIZADO"
            if not nova_data_finalizacao or nova_data_finalizacao == "00/00/0000":
                nova_data_finalizacao = datetime.now().strftime("%d/%m/%Y")
        else:
            novo_status = "ANDAMENTO"

        cursor.execute("""
            UPDATE producao SET
                data_inicial = ?,
                hora_inicio = ?,
                hora_termino = ?,
                data_finalizacao = ?,
                quantidade_produzida = ?,
                placas_utilizadas = ?,
                sobras_placas = ?,
                media_pares_por_placa = ?,
                eficiencia = ?,
                status = ?
            WHERE id = ?
        """, (
            nova_data_inicial,
            nova_hora_inicio,
            nova_hora_termino,
            nova_data_finalizacao,
            nova_quantidade_produzida,
            novas_placas_utilizadas,
            novas_sobras_placas,
            nova_media_pares_por_placa,
            nova_eficiencia,
            novo_status,
            producao_id
        ))

        conn.commit()
        
        # Atualizar o status global do pedido na tabela de pedidos
        atualizar_status_pedido(cursor, conn, numero_pedido)
        print("\nPedido atualizado com sucesso!")

    except Exception as e:
        conn.rollback()
        print(f"\nErro ao editar pedido: {e}")

def menu_producao(cursor, conn):
    while True:
        print("\n" + "="*40)
        print("       MENU DE PRODUÇÃO")
        print("="*40)
        print("1. Inserir Pedido na Produção")
        print("2. Finalizar Produção")
        print("3. Editar Pedido na Produção")
        print("4. Voltar ao Menu Principal")
        print("="*40)

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == '1':
            inserir_pedido_na_producao(cursor, conn)
        elif opcao == '2':
            hora_fim = hora_termino()
            if not hora_fim:
                continue
            data_fim = data_final()
            quantidade_produzida, placas_utilizadas, sobras_placas = dados_finais_da_producao()
            
            numero_pedido_atualizado = atualizar_producao(hora_fim, data_fim, quantidade_produzida, placas_utilizadas, sobras_placas, cursor, conn)
            if numero_pedido_atualizado:
                calcular_eficiencia(cursor, conn)
                atualizar_status_producao(cursor, conn)
                calcular_media_pares_por_placa(quantidade_produzida, placas_utilizadas, cursor, conn)
                atualizar_status_pedido(cursor, conn, numero_pedido_atualizado)
        elif opcao == '3':
            editar_pedido_na_producao(cursor, conn)
        elif opcao == '4':
            break
        else:
            print("Opção inválida! Escolha entre 1 e 4.")
            continue
