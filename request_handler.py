from Database.database import *
from Database.User import User
from decoder import *
from CFIE import *
from runserver import threads
import pickle
import hashlib

garbage = []


# Handler for clients connections
class Handler:

    # connecting to database to work with data
    def __init__(self, conn, addr):
        self.garbage = None
        self.__request = None
        self.database = Database()
        if self.database.is_alive:
            self.database.connect()
        self.allowed_methods = {
            '<CLOSE-CONNECTION>': 'close_connection',
            '<REGISTRATION>': 'registration',
            '<LOGIN>': 'login',
            '<SEND-MESSAGE>': 'send_message',
            '<ONLINE>': 'online',
            '<OFFLINE>': 'offline',
            '<SEND-USER-DATA>': 'send_user_data',
            '<SEND-USER-SOCIAL>': 'send_user_social',
            '<SEND-FRIEND-DATA>': 'send_friend_data',
            '<SEND-IMAGE>': 'send_image',
            '<SAVE-USER-DATA>': 'save_user_data',
            '<SET-IMAGE>': 'set_image',
            '<CHANGE-LOGIN>': 'change_login',
            '<CHANGE-PASSWORD>': 'change_password',
            '<ADD-FRIEND>': 'add_friend',
            '<CALL-CLIENT-METHOD>': 'call_client_method'
            }

        self.connections = {}

        self.addr = addr
        self.conn = conn

        self.reserve_conn = self.conn

    # function for tests
    def set_request(self, request: str) -> None:
        self.__request = request

    # function for tests
    def get_request(self) -> str:
        return self.__request

    # calling method to run it
    def call_method(self, data: list, addr: tuple) -> str:
        method = data[0]
        data = data[-1]
        print(f'Starting method: [{method}]')
        if method not in self.allowed_methods.keys():
            raise ValueError(f"Request denied: Method[{method}] doesn't exist")
        return getattr(self, self.allowed_methods.get(method))(data)

    # method that close connection with client
    def close_connection(self, data) -> str:
        self.garbage = f'\n{data}\n'
        self.conn.close()
        return '<CLOSE-CONNECTION>'

    # method registration that adds new checked user data into database
    def registration(self, data: dict) -> str:
        user_account = User()
        items = user_account.__dict__
        for key, value in data.items():
            items[key] = value
        items['ip'] = f'{self.addr[0]}'
        del items['id']
        password = hashlib.sha512(items.get('password').encode('utf-8'))
        static_status = check_all_for_reg(login=items.get('login'), password=items.get('password'),
                                          email=items.get('email'), db=self.database)
        if static_status != '<SUCCESS>':
            return static_status
        items['password'] = password.hexdigest()
        print(f"({self.addr[0]}:{self.addr[1]}): {self.database.insert(name='user', subject_values=items)}")
        user_data = items
        user_social = Social()
        items = user_social.__dict__
        id = self.database.select(table_name='user', criterion='login',
                                  id=user_data.get('login'), subject='id')[0].get('id')
        items['id'] = id
        print(f"({self.addr[0]}:{self.addr[1]}): {self.database.insert(name='social', subject_values=items)}")
        with open('static/pfp_image_standard.png', 'rb') as image:
            image_bytes = image.read()
        self.database.insert(name='images', subject_values={'id': id, 'pfp': 'None'})
        self.database.update(table_name='images', id=id, subject='pfp', subject_value=image_bytes)
        print(f'<SUCCESS> New user added to database')
        return '<SUCCESS>'

    # method calling with entry to account from client
    def login(self, data: dict) -> str:
        user_data = find_login(data.get('login'), self.database)
        if user_data == '<DENIED>' or user_data == ():
            return 'Такого логина не существует'
        if data.get('password') != user_data.get('password'):
            return 'Неправильный пароль'
        if user_data.get('online') == 'True':
            return 'В этот аккаунт уже вошли с другого устройства'
        print(f'<SUCCESS> User enter into account with: \nlogin[{data.get("login")}] - id[{data.get("id")}]')
        return '<SUCCESS>'

    def online(self, data):
        self.connections[self.addr] = {'conn': self.conn, 'login': data.get('login')}
        print(self.connections)
        print(self.database.update(
            table_name='user', id=data.get('login'), subject='online',
            subject_value='True', criterion='login'
        ))
        return '<COMPLETE>'

    def offline(self, data):
        self.garbage = data
        login = self.connections.get(self.addr).get('login')
        del self.connections[self.addr]
        print(self.database.update(
            table_name='user', id=login, subject='online',
            subject_value='False', criterion='login'
        ))
        return '<COMPLETE>'

    def send_data(self, data, status, NF=True) -> None:
        if NF:
            self.connections.get(self.addr).get('conn').send(b'<NOTIFICATION-MESSAGE>')
        if status == 'None':
            self.connections.get(self.addr).get('conn').send(pencode(data))
        else:
            self.connections.get(self.addr).get('conn').send(pencode(data) + b'<END>' + pencode(status) + b'<END>')

    def send_user_data(self, data):
        user_data = self.database.select(table_name='user', criterion='login', id=data.get('login'))[0]
        self.send_data(user_data, '<SET-USER-DATA>')
        return '<COMPLETE>'

    def send_user_social(self, data):
        user_social = self.database.select(table_name='social', id=data.get('id'))[0]
        self.send_data(user_social, '<SET-USER-SOCIAL>')
        return '<COMPLETE>'

    def save_user_data(self, data) -> str:
        for key, value in data.items():
            self.database.update(
                table_name='user', id=data.get('id'),
                subject=key, subject_value=value
            )
        return '<COMPLETE>'

    def save_user_social(self, data) -> str:
        for key, value in data.items():
            self.database.update(
                table_name='social', id=data.get('id'),
                subject=key, subject_value=value
            )
        return '<COMPLETE>'

    def change_login(self, data):
        login = data.get('login')
        static_status = check_login(login, self.database)
        if static_status != '<SUCCESS>':
            self.send_data(static_status, '<SET-REQUEST-STATUS>')
            return '<DENIED>'
        self.connections.get(self.addr)['login'] = login
        time.sleep(0.1)
        self.send_data(self.save_user_data(data), '<SET-REQUEST-STATUS>')
        return '<SUCCESS>'

    def change_password(self, data):
        password = data.get('password')
        static_status = check_password(password)
        if static_status != '<SUCCESS>':
            self.send_data(static_status, '<SET-REQUEST-STATUS>')
            return '<DENIED>'
        password = hashlib.sha512(password.encode())
        data['password'] = password.hexdigest()
        time.sleep(0.1)
        self.send_data(self.save_user_data(data), '<SET-REQUEST-STATUS>')
        return '<SUCCESS>'

    def send_friend_data(self, data):
        friend_login = data.get('login')
        needed_data = ['login', 'id', 'online', 'status', 'name', 'gender']
        friend_data = {}
        for nd in needed_data:
            friend_data[nd] = self.database.select(
                table_name='user', criterion='login',
                id=friend_login, subject=nd)[0].get(nd)
        self.send_data(friend_data, status='None', NF=False)
        return '<COMPLETE>'

    def call_client_method(self, data):
        self.send_data(data=data.get('data'), status=data.get('method'))
        return '<COMPLETE>'

    def send_image(self, data):
        image_name = data.get('image_name')
        if 'friend' in image_name:
            image_name = 'pfp'
        image_bytes = self.database.select(
            table_name='images', id=data.get('id'), subject=image_name)[0].get(image_name)
        self.send_data({'image_name': data.get("image_name")}, '<GET-IMAGE>')

        self.connections.get(self.addr).get('conn').sendall(image_bytes)
        time.sleep(0.1)
        self.connections.get(self.addr).get('conn').send(b"<IMAGE-END>")
        self.connections.get(self.addr).get('conn').send(b"<SUCCESS>")

        return '<SUCCESS>'

    def set_image(self, data):
        image_name = data.get('image_name')
        image_bytes = b""

        done = False
        while not done:
            image = self.connections.get(self.addr).get('conn').recv(1024)
            if image[-11:] == b"<IMAGE-END>":
                image_bytes += image.split(b"<IMAGE-END>")[0]
                done = True
            else:
                image_bytes += image

        print(self.database.update(
            table_name='images', id=data.get('id'), subject=image_name, subject_value=image_bytes))
        return '<SUCCESS>'

    def add_friend(self, data):
        friend_login = data.get('friend_login')
        static = find_login(friend_login, self.database)
        if static == '<DENIED>' or static == ():
            return 'Такого логина не существует'
        user_login = data.get('user_login')
        user_id = data.get('id')
        friend_id = self.database.select(
            table_name='user', criterion='login', id=friend_login, subject='id')[0].get('id')
        for id, login in [[user_id, friend_login], [friend_id, user_login]]:
            data = self.database.select(table_name='social', id=id)[0].get('friends').decode('utf-8')
            if data == 'None':
                data = ''
            new_data = data + login + '<NEXT>'
            print(self.database.update(table_name='social', id=id, subject='friends', subject_value=new_data))
        return '<SUCCESS>'
