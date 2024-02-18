import socket
import pickle
import time
from Config import *

# class OnlineTracker():
#     def __init__(self, my_adress,  membros: list, sock):
#         self.HOST = my_adress[0]
#         self.PORT = my_adress[1]
#         self.membros = membros
#         self.status = {(ip, porta): self.OFF for ip, porta in membros}
#         self.socket: socket = sock
#         self.cache = []

#     def request_status(self):
#         while True:
#             data = pickle.dumps(("", "", self.PING))
#             for pairAdress in self.membros:
#                 if pairAdress[0] != self.HOST:
#                     if self.status[pairAdress] == ON:
#                         self.status[pairAdress] = UKN

#                     elif self.status[pairAdress] == UKN:
#                         self.status[pairAdress] = OFF

#                     self.socket.sendto(data, pairAdress)

#             time.sleep(ONLINE_SYNC_TIME)

#     def send_status(self, adress):
#         print("ACK para", adress)
#         data = pickle.dumps(("", "", PING_ACK))
#         self.socket.sendto(data, adress)

#     def treat_package(self):
#             data, adress = self.cache.pop()
#             message, time, type = pickle.loads(data)

#             print("Tratei o pacote online do tipo ", type)

#             if type == PING:
#                 self.send_status(adress)

#             elif type == PING_ACK:
#                 self.status[adress] = ON