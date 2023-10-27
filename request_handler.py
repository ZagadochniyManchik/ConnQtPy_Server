from Database.database import *
from Database.database_config import *
from Database.User import *
from decoder import *
from CFIE import *
import pickle
import hashlib

garbage = []


# Handler for clients connections
class Handler:

    # connecting to database to work with data
    def __init__(self):
        self.garbage = None
        self.__request = None
        self.database = Database()
        if self.database.is_alive:
            self.database.connect()
        self.allowed_methods = {
            '<CLOSE-CONNECTION>': 'close_connection',
            '<REGISTRATION>': 'registration',
            '<LOGIN>': 'login',
            '<SEND-MESSAGE>': 'send_message'
                                }

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
        return getattr(self, self.allowed_methods.get(method))(data, addr)

    # method that close connection with client
    def close_connection(self) -> str:
        self.garbage += '\npython_is_trash\n'
        return '<CLOSE-CONNECTION>'

    # method registration that adds new checked user data into database
    def registration(self, data: dict, addr: tuple) -> str:
        user_account = User()
        items = user_account.__dict__
        for key, value in data.items():
            items[key] = value
        items['ip'] = addr[0]
        del items['id']
        password = hashlib.sha512(items.get('password').encode('utf-8'))
        static_status = check_all_for_reg(login=items.get('login'), password=items.get('password'),
                                          email=items.get('email'), db=self.database)
        if static_status != '<SUCCESS>':
            return static_status
        items['password'] = password.hexdigest()
        print(f"({addr[0]}:{addr[1]}): {self.database.insert(name='user', subject_values=items)}")
        print(f'<SUCCESS> New user added to database')
        return '<SUCCESS>'

    # method calling with entry to account from client
    def login(self, data: dict, addr: tuple) -> str:
        user_data = find_login(data.get('login'), self.database)
        if user_data == '<DENIED>' or user_data == ():
            return 'Такого логина не существует'
        if data.get('password') != user_data.get('password'):
            return 'Неправильный пароль'
        print(f'<SUCCESS> User enter into account with: \nlogin[{data.get("login")}] - id[{data.get("id")}]')
        return '<SUCCESS>'

    def send_message(self, data, addr):
        self.garbage = True
        return [f'{addr}: {data}', '<SEND-MESSAGE>']

