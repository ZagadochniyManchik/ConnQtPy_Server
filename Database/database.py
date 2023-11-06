import pymysql
from PIL import Image
import base64
import PIL.Image
import time
import logging
from Server.Database.User import *
from Server.Database.database_config import *


# Function for return time of this moment
def time_now() -> str:
    return f'Time[{time.strftime("%Y-%m-%d %H:%M:%S")}]'


# Function that display errors
def error(error_data: str):
    print(error_data)


# Class Database to connect and write/read data
class Database:

    # init block check connection with database
    def __init__(self):

        try:
            self._connection = pymysql.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database='userdatabase',
                charset=db_charset,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.is_alive = True
            self._connection.close()
            self._connection = None
        except Exception as error_data:
            self.is_alive = False
            raise ConnectionError(f"{str(error_data)}")

    # when use del self connection is close
    def __del__(self):
        try:
            self._connection.close()
        except Exception as error_data:
            self.error_report = error_data
            return

    # Connecting to any database
    def connect(self, db_name: str = 'userdatabase') -> str:
        try:
            self._connection = pymysql.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name,
                charset=db_charset,
                cursorclass=pymysql.cursors.DictCursor
            )

            return f'{time_now()} -> Connected to UserDatabase'

        except Exception as error_data:
            raise ConnectionError(f'{error_data}')

    # Executing MySQL code in DbServer
    def connection_proc(self, process) -> None:
        try:
            with self._connection.cursor() as self.cursor:
                conn_process = process
                self.cursor.execute(conn_process)
        except Exception as error_data:
            raise ValueError('(RequestError): ' + str(error_data))

    # reading data from table of current database
    def select(self, table_name: str = 'None', id: str = 'None', subject: str = '*', criterion: str = 'id') -> str:
        if table_name == 'None':
            raise ValueError(f'Table not specified in module "{self}.select"')

        if id == 'None':
            self.connection_proc(f"SELECT {subject} FROM `{table_name}`")
            return self.cursor.fetchall()

        self.connection_proc(f"SELECT {subject} FROM `{table_name}` WHERE {criterion} = '{id}'")
        return self.cursor.fetchall()

    # updating data from table of current database
    def update(self, table_name: str = 'user', id: str = 'None', subject: str = None, subject_value=None,
               criterion: str = 'id') -> str:
        if table_name == 'None':
            raise ValueError(f'Table not specified in module "{self}.update"')

        if subject_value is None or subject is None:
            raise ValueError(f'Update func doesnt get any type of data to update in module "{self}.update"')

        if table_name == 'images':
            if id == 'None':
                raise ValueError(f'ID is required to make UPDATE in images table')
            with self._connection.cursor() as self.cursor:
                conn_process = f"UPDATE `{table_name}` SET {subject} = %s WHERE `{criterion}` = '{id}'"
                arguments = (subject_value,)
                self.cursor.execute(conn_process, arguments)
            self._connection.commit()
            return f'{time_now()} -> Updated data in `{table_name}`["{subject}" = "image"] for {criterion}[{id}]'

        if id == 'None':
            self.connection_proc(f"UPDATE `{table_name}` SET {subject} = '{subject_value}'")
            self._connection.commit()
            return f'{time_now()} -> Updated data in `{table_name}`["{subject}" = "{subject_value}"] for all IDs'

        self.connection_proc(f"UPDATE `{table_name}` SET `{subject}` = '{subject_value}' WHERE `{criterion}` = '{id}'")
        self._connection.commit()
        return f'{time_now()} -> Updated data in `{table_name}`["{subject}" = "{subject_value}"] for {criterion}[{id}]'

    # create database or table
    def create(self, status: str = 'table', name: str = 'example', table_args: set[str] = None) -> str:
        if table_args is None:
            table_args = ('Row1 INT', 'Row2 VARCHAR(59)')  # standard values to create

        if status == 'database':
            self.connection_proc(f"CREATE {status.upper()} `{name}`")
            self._connection.commit()
            return f'{time_now()} -> Created {status.upper()} with name[{name}]'

        elif status == 'table':
            self.connection_proc(f"CREATE {status.upper()} `{name}` ({', '.join(table_args)})")
            self._connection.commit()
            return (f'{time_now()} -> Created {status.upper()} with name[{name}]\n'
                    f'Args: [{", ".join(table_args)}]')

        else:
            raise ValueError('Incorrect type of status, must be ("table", "database")')

    # insert a row in table
    def insert(self, name: str = 'user', subject_values=None) -> str:
        table_elements = db_table_elements.get(name)
        try:
            if name == 'user':
                table_elements.remove('id')
        except ValueError:
            pass

        if subject_values is None:
            raise ValueError("Subject values must be dict, not NoneType object")

        if len(subject_values) != len(table_elements):
            raise ValueError("Not enough values to make INSERT func")

        request = map(lambda x: "'"+str(x)+"'", subject_values.values())
        self.connection_proc(f"INSERT INTO `{name}` ({', '.join(table_elements)}) "
                             f"VALUES ({', '.join(list(request))});")
        self._connection.commit()
        return f"{time_now()} -> Inserted data in table {name}"

    # delete data from db
    def delete(self, table_name: str = None, id: str = None, criterion: str = 'id') -> str:
        if table_name is None or id is None:
            raise ValueError(f"Not enough data for module {self}.delete")

        self.connection_proc(f"DELETE FROM `{table_name}` WHERE id = '{id}'")
        self._connection.commit()
        return f"{time_now()} -> Deleted data from table:`{table_name}` where {criterion}:'{id}'"

    def get_connection(self):
        return self._connection


# main
if __name__ == '__main__':
    from Server.decoder import *
    print(f"\nMain TestCase\n{'-'*60}")
    db = Database()
    print(f"Database live status is {db.is_alive}")
    print(db.connect())
    # print(*db.select(table_name='user'), sep='\n')
    # print(db.update(table_name='user', subject='login', subject_value="Profile9", id='83243'))
    profile_posts = str(pencode('Lorum ipsum'))
    test = {
        'ip': '127.0.0.1:25565',
        'login': 'TestFunction',
        'password': 'password123',
        'email': 'testemail@gmail.com',
        'gender': 'Не указано',
        'online': 'False',
        'profile_name': 'None',
        'profile_status': 'None',
        'profile_posts': 'Lorum ipsum'
    }
    print(db.select(table_name='user', id='17')[0])

    with open("D:\\PythonFiles\\Rannev_Python\\ConnQtPy\\ConnPyQtRU\\images\\pfp_image_standard.png", 'rb') as file:
        file_bytes = file.read()
    image = Image.open("D:\\PythonFiles\\Rannev_Python\\ConnQtPy\\ConnPyQtRU\\images\\pfp_image_standard.png")
    print(db.update(table_name='images', id='17', subject='pfp', subject_value=file_bytes))
    print(db.select(table_name='images', id='17')[0].get('pfp'))
    # request = "UPDATE images SET pfp = %s WHERE id = 16"
    # args = (file_bytes, )
    # cursor = db.get_connection().cursor()
    # cursor.execute(request, args)
    # db.get_connection().commit()
    # print(db.delete(table_name='user', criterion='login', id='TestFunction'))
    # print(db.insert('user', test))
    # print(db.update(table_name='user', id='TestFunction', criterion='login',
    #                 subject='profile_posts', subject_value=profile_posts
    #                 ))
    # print(db.create())
    # print(db.create(status='database', name='dbexample'))
    # print(db.insert(subject_values={
    #     'id': '516782',
    #     'ip': '192.168.0.32',
    #     'login': 'Profile99',
    #     'password': 'password123',
    #     'email': 'testemail2021@gmail.ru'
    # }))
    # print(db.delete(table_name='user', id='516782'))
    # print(db.update(table_name='user', id='15', subject='online', subject_value='False'))
    # print(db.update(table_name='user', id='16', subject='online', subject_value='False'))
    print(f"{'-'*60}")
    db_code_status = 'successful'
    print(db_code_status)
