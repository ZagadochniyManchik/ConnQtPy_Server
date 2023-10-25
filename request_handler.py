from Database.database import *
from Database.database_config import *
from Database.User import *
from decoder import *
from CFIE import *
import pickle

garbage = []


class Handler:

    def __init__(self):
        self.garbage = None
        self.__request = None
        self.database = Database()
        if self.database.is_alive:
            self.database.connect()
        self.allowed_methods = {
            '<CLOSE-CONNECTION>': 'close_connection',
            '<REGISTRATION>': 'registration',
            '<LOGIN>': 'login'
                                }

    def set_request(self, request):
        self.__request = request

    def get_request(self):
        return self.__request

    def call_method(self, data, addr):
        method = data[0]
        data = data[-1]
        print(f'Starting method: [{method}]')
        if method not in self.allowed_methods.keys():
            raise ValueError(f"Request denied: Method[{method}] doesn't exist")
        return getattr(self, self.allowed_methods.get(method))(data, addr)

    def close_connection(self):
        self.garbage += '\npython_is_trash\n'
        return '<CLOSE-CONNECTION>'

    def registration(self, data, addr):
        user_account = User()
        items = user_account.__dict__
        for key, value in data.items():
            items[key] = value
        items['ip'] = addr[0]
        del items['id']
        static_status = check_all_for_reg(login=items.get('login'), password=items.get('password'),
                                          email=items.get('email'), db=self.database)
        if static_status != '<SUCCESS>':
            return static_status
        print(f"({addr[0]}:{addr[1]}): {self.database.insert(name='user', subject_values=items)}")
        print(f'<SUCCESS> New user added to database')
        return '<SUCCESS>'
