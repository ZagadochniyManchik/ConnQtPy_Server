import pymysql
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

    # Executing MySQL code in Server PHPMyAdmin
    def connection_proc(self, process):
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
    def update(self, table_name: str = 'user', id: str = 'None', subject: str = None, subject_value: str = None,
               criterion: str = 'id') -> str:
        if table_name == 'None':
            raise ValueError(f'Table not specified in module "{self}.update"')

        if subject_value is None or subject is None:
            raise ValueError(f'Update func doesnt get any type of data to update in module "{self}.update"')

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
            table_elements.remove('id')
        except ValueError:
            pass

        if subject_values is None:
            subject_values = {
                'ip': '192.168.0.0',
                'login': 'Ivankov',
                'password': 'iva123',
                'email': 'testemail2023@gmail.com',
                'gender': 'Не указано'
            }

        if len(subject_values) != len(table_elements):
            raise ValueError("Not enough values to make INSERT func")

        request = map(lambda x: "'"+x+"'", subject_values.values())
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


# main
if __name__ == '__main__':
    print(f"\nMain TestCase\n{'-'*60}")
    db = Database()
    print(f"Database live status is {db.is_alive}")
    print(db.connect())
    # print(*db.select(table_name='user'), sep='\n')
    # print(db.update(table_name='user', subject='login', subject_value="Profile9", id='83243'))
    print(*db.select(table_name='user', subject='login'), sep='\n')
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
    print(db.update(table_name='user', id='15', subject='online', subject_value='False'))
    print(db.update(table_name='user', id='16', subject='online', subject_value='False'))
    print(f"{'-'*60}")
    db_code_status = 'successful'
    print(db_code_status)
