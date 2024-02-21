import platform

# Tipos de mensagens
MSG = "mensage"
SYN = "sync"
CSP = "chatSyncPart"
MSG_ACK = "mensage ack"
SHOW = "mensage show"

# Constantes de sincronização
PING = "online ping"
PING_ACK = "online ack"

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
                                                                #        #
                                                                #        #
'''