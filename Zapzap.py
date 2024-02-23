import socket, threading, os, pickle, time, sys
from Config import *
from Classes import Mensagem, Membro, LamportClock, Contatos
from Criptography import encrypt, decrypt

print(whatsApp2)

# Dados
membros = []
conversa = set()
no_confirmed = set()
no_confirmed_lock = threading.Lock()

pkgCache = [] # Cache temporário de pacotes
waiting = [] # Cache de pacotes que precisam de confirmação
confirms = [] # Cache de confirmações (logicstamps de pacotes)

clock = LamportClock()
Contatos().initialize()

# Informações do usuário
nome_usuario = input("Digite o seu usuário: ")
usuario_obj: Membro = Contatos().get_contato(nome_usuario)
while usuario_obj == None:
    nome_usuario = input("Usuário inválido! Digite o seu usuário: ")
    usuario_obj = Contatos().get_contato(nome_usuario)
usuario_obj.status = ON
membros.append(usuario_obj)

HOST = usuario_obj.address[0]
PORT = usuario_obj.address[1]

# Informações do grupo
nomes_membros = input("Insira os membros: ")
for nome_membro in nomes_membros.split():
    membro_obj: Membro = Contatos().get_contato(nome_membro)
    membros.append(membro_obj)

password = input("Insira a senha de criptografia do grupo: ")

# Socket e relógio Lógico
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

# Envia pacotes
def send(sock, clock, message, membros, type, target_address= None):
    try:
        logicstamp = 0
        
        if type == SYN:
            logicstamp = clock.increment()

        data = pickle.dumps((message, logicstamp, type))

        if target_address == None: # Manda para todos se não for especificado o alvo
            for membro in membros:
                if membro.address != (HOST, PORT):
                    sock.sendto(data, membro.address)
        else:
            sock.sendto(data, target_address)

    except socket.error as e:
        print(f"Erro de conexão! {e.strerror}\nTente novamente mais tarde...")
        time.sleep(5)
        sys.exit()

# Envia os pacotes que necessitam de confirmação
def assure_send(message, membros, type, target_address= None, is_resend= False):
    try:
        logicstamp = 0
        timestamp = time.time()
        
        if type == MSG:
            if not is_resend: # Verifica se é a primeira vez que manda a mensagem ou se é um reenvio de pacote
                logicstamp = clock.increment()
                mensage_obj = Mensagem(usuario_obj, message, logicstamp, membros)
                mensage_obj.confirmations[usuario_obj.address] = True

                no_confirmed.update([mensage_obj])
                message_dumped = pickle.dumps(mensage_obj)
            else:
                logicstamp = message.logicstamp
                message_dumped = pickle.dumps(message)

        elif type == CSP: 
            if not is_resend: # Verifica se é a primeira vez que manda a mensagem ou se é um reenvio de pacote
                logicstamp = clock.increment()
                message_dumped = pickle.dumps(message)
            else:
                logicstamp = message.logicstamp
                message_dumped = pickle.dumps(message)

        else:
            message_dumped = message

        data = pickle.dumps((message_dumped, logicstamp, type)) # Carrega o data

        if target_address == None: # Manda para todos se não for especificado o alvo
            for membro in membros:
                if membro.address != (HOST, PORT):
                    sock.sendto(data, membro.address)
                    waiting.append((logicstamp, timestamp, message_dumped, type, membro.address)) # Adiciona a referencia ao pacote para cada um que enviou

        else: # Manda apenas pro alvo especificado
            sock.sendto(data, target_address)
            waiting.append((logicstamp, timestamp, message_dumped, type, target_address))

    except socket.error as e:
        print(f"Erro de conexão! {e.strerror}\nTente novamente mais tarde...")
        time.sleep(5)
        sys.exit()

# Envia a sua conversa
def sendChat(adress):
    try:
        for mensagemOBJ in conversa:
            assure_send(message= mensagemOBJ, membros= membros, type= CSP, target_address= adress)
            
    except socket.error as e:
        print(f"Erro de conexão! {e.strerror}\nTente novamente mais tarde...")
        time.sleep(5)
        sys.exit()

# Recebe pacotes
def listner(sock, clock):
    while True:
        try:
            pacote = sock.recvfrom(1024)
            pkgCache.append(pacote)
        except:
            pass

# Trata os pacotes recebidos
def pkgSort(sock, clock):
    while True:
        if len(pkgCache) > 0:
            data, address = pkgCache.pop() # Tupla contendo Data e ClientAddress (nessa ordem)
            message, logicstamp, type = pickle.loads(data) # Interpreta o Data

            if type == MSG or type == SYN or type == CSP:
                clock.update(logicstamp)

            if type == MSG:
                mensagem_obj = pickle.loads(message)
                no_confirmed.update([mensagem_obj])

                send(sock, clock, logicstamp, membros, ACK, target_address= address) # ACK da mensagem

                printSort()

            elif type == SYN and message == 'first':
                send(sock, clock, None, membros, SYN, target_address= address) # Mensagem para sincronizar o relógio
                sendChat(address)

            elif type == ACK:
                confirms.append(logicstamp)

                with no_confirmed_lock:
                    for msg in no_confirmed.copy(): 
                        if msg.logicstamp == message:
                            msg.confirmations[address] = True # Adiciono um confirm a mensagem
            
            elif type == SHOW:
                send(sock, clock, logicstamp, membros, ACK, target_address= address) # ACK da mensagem

                for msg in no_confirmed.copy():
                    if msg.logicstamp == message:
                        conversa.update([msg])
                        no_confirmed.remove(msg)
                        printSort()

            elif type == CSP:
                messageOBJ = pickle.loads(message)
                conversa.update([messageOBJ])

                send(sock, clock, logicstamp, membros, ACK, target_address= address) # ACK da mensagem

                printSort()
            
            elif type == PING:
                send(sock, clock, None, membros, PONG) # Pong reverberado para todos

            elif type == PONG:
                for membro in membros:
                    if membro.address == address:
                        membro.status = ON

        with no_confirmed_lock:
            for msg in no_confirmed.copy(): # Verifica se a mensagem já possui todos os confirms
                if all(msg.confirmations[membro.address] for membro in membros if membro.status != OFF): 
                    conversa.update([msg])
                    no_confirmed.discard(msg)
                    assure_send(message= msg.logicstamp, membros= membros, type= SHOW) # Envia o show para todos
                    printSort()
        
# Trata as confirmações         0         1        2      3        4
def confirm_handler(): # (logicstamp, timestamp, type, message, address)
    while True:
        try:
            tempo_atual = time.time() # Timestamp do momento atual

            pacote = waiting.pop()
            if pacote[0] not in confirms:
                # Se precisa de reenvio e se passou 1 segundo desde que foi enviado
                if tempo_atual >= pacote[1] + RESEND_TIME and any(filter(lambda membro: membro.address == pacote[4] and membro.status != OFF, membros)):
                    assure_send(message= pacote[3], membros= membros, type= pacote[2], target_address= pacote[4], is_resend= True)
                    pacote[1] = time.time()
                    waiting.append(pacote) 
            else:
                confirms.remove(pacote[0])

        except IndexError as e:
            continue

# Envia pings
def online_requester(sock, clock):
    while True:
        try:
            data = pickle.dumps(('', 0, PING))
            for membro in membros:
                if membro.address != (HOST, PORT):
                    if membro.status == ON:
                        membro.status = UKN
                    elif membro.status == UKN:
                        membro.status = OFF

                    sock.sendto(data, membro.address)

        except socket.error as e:
            print(f"Erro de conexão! {e.strerror}\nTente novamente mais tarde...")
            time.sleep(5)
            sys.exit()

        finally:
            time.sleep(ONLINE_SYNC_TIME)

# Ordena as mensagens
def consensusSort(sortableChat):
    if bool(sortableChat):
        sortableChat.sort(key=lambda x: (x.logicstamp, x.user.address))

# Mostra as mensagens em ordem
def printSort(optmize= OPTIMIZE_PRINT, optmize_size= OPTIMIZE_SIZE):
    sortableChat = list(conversa)
    consensusSort(sortableChat)

    # Otimiza a lista para mostrar apenas as 20 últimas mensagens
    if optmize and len(sortableChat) > optmize_size:
        sortableChat = sortableChat[-optmize_size:]
    
    # Exibe na tela
    os.system(LIMPAR)
    for msg in sortableChat:
        msg: Mensagem
        colorIndex = f"\033[38;5;{(sum(int(digito) for digito in msg.user.address[0] if digito.isdigit()) + msg.user.address[1] ) % (255 + 1)}m"

        if (msg.user.address[0] == HOST and msg.user.address[1] == PORT):
            print(f'{colorIndex}Você\033[0m: {decrypt(msg.texto, password)}')
        else:
            print(f'{colorIndex}{msg.user.name} - ({msg.user.status}) \033[0m: {decrypt(msg.texto, password)}')

    del sortableChat

# Lida com os comandos de chat
def comands_handler(message, sock):
    if message.split()[0] == "/help":
        help_str = '''
Lista de comandos:
/membros -> Vê os membros do grupo e seu status online ou offline
/chave -> Vê a chave de criptografia do grupo
/ver (todas ou quantidade) -> exibe a quantidade de mensagens indicada ou todas
/input -> Envia todas as mensagens presentes no arquivo de input, uma por linha
/output -> Gera um arquivo com todas as mensagens da conversa'''
        os.system(LIMPAR)
        print(help_str)

    # Mostra os membros do grupo e o status deles
    elif message.split()[0] == "/membros":
        for membro in membros:
            print(f"{membro.name} - {membro.address[0]} ({membro.status}) ")

    # Mostra a chave de encriptação
    elif message.split()[0] == "/chave":
        print(f"Chave de criptografia: {password}")
    
    # Mostra uma quantidade diferente de mensagens na tela
    elif message.split()[0] == "/ver":
        if message.split()[1] == "todas":
            printSort(optmize= False)

        elif message.split()[1].isdigit():
            printSort(optmize= True, optmize_size= int(message.split()[1]))

    # Gera o arquivo de output
    elif message.split()[0] == "/output":
        if not os.path.exists("Data/"):
            os.makedirs("Data/")
            
        with open("Data/output_file.txt", 'w', encoding='utf-8') as arquivo:
            sortableChat = list(conversa)
            consensusSort(sortableChat)

            for msg in sortableChat:
                arquivo.write(f'{msg.user.name} - {msg.user.address}: {decrypt(msg.texto, password)}' + "\n")
        
        print("Arquivo da conversa gerado.")
    
    # Gera o arquivo de input
    elif message.split()[0] == "/input":
        if not os.path.exists("Data/"):
            os.makedirs("Data/")
            
        with open("Data/input_file.txt", 'a+', encoding='utf-8') as arquivo:
            arquivo.seek(0) # Mover o cursos para o inicio
            for linha in arquivo:
                assure_send(encrypt(linha.rstrip('\n'), password), membros, MSG)
                printSort()
                time.sleep(INPUT_SEND_TIME)
            
            print("Mensagens do arquivo enviadas.")
        
    else:
        print(f"Comando desconhecido! tente /help")

def main():
    # Threads secundárias
    package_listner_thread = threading.Thread(target=listner, args=(sock, clock), daemon=True)
    package_listner_thread.start()

    package_sort_thread = threading.Thread(target=pkgSort, args=(sock, clock), daemon=True)
    package_sort_thread.start()

    online_requester_thread = threading.Thread(target= online_requester, args=(sock, clock), daemon=True)
    online_requester_thread.start()

    confirm_handler_thread = threading.Thread(target= confirm_handler, args=(), daemon=True)
    confirm_handler_thread.start()

    # Mensagem de sincronização de relógio inicial
    send(sock, clock, 'first', membros, SYN)
    while True:
        message = input(">:")
        while message == '':
            message = input(">:")

        # Se for uma mensagem comum
        if message[0] != "/":
            assure_send(encrypt(message, password), membros, MSG)
        
        # Se for um comando
        else:
            comands_handler(message, sock)

if __name__ == "__main__":
    main()