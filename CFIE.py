garbage = []


# check all data for registration
def check_all_for_reg(login, password, email, db) -> str:
    login_status = check_login(login, db)
    password_status = check_password(password)
    email_status = check_email(email)
    if login_status != '<SUCCESS>':
        return login_status
    if email_status != '<SUCCESS>':
        return email_status
    if password_status != '<SUCCESS>':
        return password_status
    return '<SUCCESS>'


# check for incorrect entry of login
def check_login(login: str, db) -> str:
    logins = []
    for el in db.select(table_name='user', subject='login'):
        logins.append(el.get('login'))
    if login in logins:
        return 'Такой логин уже существует!'
    if len(login) > 20:
        return 'Длина логина должна быть не более 20 символов'
    if len(login) < 5:
        return 'Длина логина должна быть не менее 5 символов'
    for el in login:
        if el.lower() in [i for i in 'qwertyuiopasdfghjklzxcvbnm01234567890']:
            continue
        else:
            return 'Логин должен состоять из символов A-Z и 0-9(опционально)'
    return '<SUCCESS>'


# check incorrect entry of password
def check_password(password: str) -> str:
    if len(password) > 60:
        return 'Длина пароля должна быть не более 60 символов'
    if len(password) < 6:
        return 'Длина пароля должна быть не менее 6 символов'
    for el in password:
        if el.lower() in [i for i in 'qwertyuiopasdfghjklzxcvbnm01234567890!@#$%&*()/']:
            continue
        else:
            return 'Логин должен состоять из символов A-Z и 0-9 и !@#$%&*()/'
    return '<SUCCESS>'


# and email ofc
def check_email(email: str) -> str:
    if len(email) > 319:
        return 'Длина эл.почты должна быть не более 319 символов'
    if len(email) < 12:
        return 'Длина эл.почты должна быть не менее 12 символов'
    cnt = email.count('@gmail.com') + email.count('@mail.ru') + email.count('@yandex.ru')
    if cnt == 0:
        return 'Допускаются только адреса с префиксами:\n "@gmail.com", "@mail.ru", "@yandex.ru"'
    if cnt > 1:
        return 'Некорректный ввод эл.почты!'
    return '<SUCCESS>'


# returns user data if exist
def find_login(login: str, db) -> str:
    try:
        return db.select(table_name='user', id=login, criterion='login')[0]
    except Exception as error:
        garbage.append(error)
        return '<DENIED>'


