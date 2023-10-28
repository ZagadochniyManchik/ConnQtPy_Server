
class User:

    def __init__(self):
        self.id = None
        self.ip = None
        self.login = None
        self.password = None
        self.email = None
        self.gender = None
        self.online = 'False'

    def set_items(self, items):
        if len(self.__dict__.items()) != len(items.items()):
            raise ValueError('Items length doesnt match to self.__dict__')
        self.__dict__ = items


if __name__ == '__main__':
    ...
    # user = User()
    # print(user.__dict__)
    # user.set_items({'login': 'Ivankov', 'password': 'iva123456', 'gender': 'Male', 'email': 'ivachan@gmail.com'})
    # print(user.__dict__)
