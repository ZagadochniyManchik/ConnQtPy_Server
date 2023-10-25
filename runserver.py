import socket
# import os
import threading
import decoder
from server_config import *
from request_handler import *
from dataparser import *
from PyQt5 import QtCore, QtGui, QtWidgets


# func to run main code
def run_server():

    server = Server()
    server.bind()

    while True:
        try:
            server.run()
        except Exception as error_arg:
            print(f'\n{time_now()}\n!!!WARNING\n{error_arg}\nWARNING!!!\n')


class Server:

    def __init__(self):
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.__host = host
        self.__port = port

        self.__addr = None
        self.__conn = None

        self._connections = {}
        self._threads = {}

    # bind server to host and port
    def bind(self) -> None:

        print(f"Server bind to ({(self.__host, self.__port)})")
        self.__server.bind((self.__host, self.__port))

        print(f'\n{"-"*80}\nServer listen for connection\n{"-"*80}\n')

    # server start to listen and accept connections
    def run(self) -> None:

        self.__server.listen()

        self.__conn, self.__addr = self.__server.accept()
        thr = Connection(self.__conn, self.__addr)
        self._threads[self.__addr] = thr
        thr.start()


class Connection(threading.Thread):

    def __init__(self, conn, addr):
        threading.Thread.__init__(self, name=addr[0])

        self.__conn = conn
        self.__addr = addr

        print(f'\nConnection with {self.__addr} open\n')
        self.handler = Handler()

    # Running function after creating object of self class
    def run(self):

        status = 'None'

        try:
            try:
                while True:
                    data = self.__conn.recv(1024)
                    try:
                        data = parser(data)
                    except IndexError:
                        continue
                    print(f'{time_now()}: {self.__addr} -> {data[0]}')
                    status = self.handler.call_method(data, addr=self.__addr)
                    if status == '<CLOSE-CONNECTION>':
                        break
                    print(f'{data[0]} for addr[{self.__addr}]:\n{status}')
                    self.send(status)
            except ConnectionResetError:
                print(f'Connection with {self.__addr} closed with ConnectionResetError')
        except ValueError as error_arg:
            print(f'Connection with {self.__addr} closed with Error:\n{error_arg}')
        finally:
            print(f'{status}\nConnection with {self.__addr} closed')

    def send(self, data):
        self.__conn.send(pencode(data))


if __name__ == '__main__':
    run_server()
