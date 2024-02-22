import platform

# Tipos de mensagens
ACK = "ack" # Send
SYN = "sync" # Send
MSG = "mensage" # Assure Send
CSP = "chatSyncPart" # Assure Send
SHOW = "mensage show" # Assure Send

# Constantes de sincronização
RESEND_TIME = 0.5

PING = "online ping" # Send
PONG = "online ack" # Send

ON = "online"
OFF = "offline"
UKN = "unknow"

# Portas
DEFAULT_PORT = 6000

DTGSIZE = 1024
ONLINE_SYNC_TIME = 1

LIMPAR_WIN = "cls"
LIMPAR_LINUX = "clear"
LIMPAR = LIMPAR_LINUX if platform.system() == "Linux" else LIMPAR_WIN

# Outros
OPTIMIZE_SIZE = 20
OPTIMIZE_PRINT = True

whatsApp2 = '''
          #                   #                                                             ####
 #     #  #                   #                           #                                #    #   TM
 #     #  #                   #                           #                                     #
 #     #  ######    ######  ######    #####              ###    ######   ######                #
 #  #  #  #     #  #     #    #      #                   # #    #     #  #     #              #
 # # # #  #     #  #     #    #       ####              #####   #     #  #     #             #
 ##   ##  #     #  #    ##    #           #             #   #   #     #  #     #            #
 #     #  #     #   #### #     ###   #####             ##   ##  ######   ######            ######
                      _                                         #        #
                     | |                                        #        #                    
   ___       _ __ ___| |_ ___  _ __ _ __   ___  
  / _ \     | '__/ _ \ __/ _ \| '__| '_ \ / _ \ 
 | (_) |    | | |  __/ || (_) | |  | | | | (_) |
  \___/     |_|  \___|\__\___/|_|  |_| |_|\___/ o o o
                                             
                                             
'''