from Server.Database.User import *

# Database config
db_host = '127.0.0.1'
db_port = 3306
db_user = 'mysql'
db_password = 'mysql'
db_charset = 'utf8mb4'
db_user_database = 'userdatabase'
elements = User()
db_table_elements = {
    'user': [el for el in elements.__dict__.keys()]
}
# end

if __name__ == '__main__':
    print(*db_table_elements.items(), sep='\n')
