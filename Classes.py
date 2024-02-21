import threading, os
from Config import *

# OBJ membro
class Membro:
    def __init__(self, host, port, name):
        self.address = (host, int(port))
        self.name = name
        self.status = OFF

# OBJ mensagem
class Mensagem:
    def __init__(self, user: Membro, texto, logicstamp, membros):
        self.user = user
        self.texto = texto
        self.logicstamp = logicstamp
        self.confirmations = {membro.address: False for membro in membros}

    # Dois objetos Mensagem são considerados iguais se tiverem o mesmo logicstamp e user.address
    def __eq__(self, other):
        if isinstance(other, Mensagem):
            return self.logicstamp == other.logicstamp and self.user.address == other.user.address
        return False
    
    # Hash baseado no logicstamp e User.address para garantir unicidade no conjunto
    def __hash__(self):
        return hash((self.logicstamp, self.user.address))
    
# OBJ Relógio de Lamport
class LamportClock:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.value += 1
            return self.value

    def update(self, received_time):
        with self.lock:
            self.value = max(self.value, received_time) + 1
            return self.value

# OBJ contatos (classe Singleton)
class Contatos:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def initialize(self):
        if not self._initialized:
            self._initialized = True
            self.contatos = {}

            self.set_contatos()

    # Seta os contatos
    def set_contatos(self):
        if not os.path.exists("Data/"):
            os.makedirs("Data/")

        with open("Data/Contatos.txt", 'r+') as arquivo:
            # Se o arquivo não existia, cria ele vazio
            if not arquivo.read(1):
                arquivo.write('')
            
            # Recupera os contatos
            for linha in arquivo:
                nome = linha.strip().split(', ')[0]
                ip = linha.strip().split(', ')[1]
                porta = linha.strip().split(', ')[2]

                membro = Membro(host= ip, port= porta, name= nome)
                self.contatos[nome] = membro
                self.contatos[f"{ip}:{porta}"] = membro

    # Retorna um contato especificado pelo nome
    def get_contato(self, name):
        try:
            return self.contatos[name]
        except:
            return None
    
    # Retorna um contato especificado pelo endereço
    def get_contato_by_address(self, address):
        try:
            host_str = f"{address[0]}:{address[1]}"
            return self.contatos[host_str]
        except:
            return None
