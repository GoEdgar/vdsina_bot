import sqlite3
from db_class import DB
from exceptions import *


id = 425439946

db = DB()

def is_new_user(user_id):
    try:
        db.fast_query('insert into users(user_id) values(?)', (user_id,))
    except sqlite3.IntegrityError:
        return False
    else:
        return True

def get_user_cookie(user_id):
    answer = db.select('select cookie from users where user_id=? and cookie not null ', (user_id,))
    if answer:
        # строку выгружаем в словарь
        return eval(answer[0][0])
    else:
        raise CookieNotFound()

def set_user_cookie(user_id, cookie):
    db.fast_query('update users set cookie=? where user_id=?', (cookie, user_id))

if __name__ == '__main__':
    db.fast_query('drop table users')
    db.fast_query('CREATE TABLE users (user_id integer unique, cookie text)')
    #db.fast_query('update users set cookie=?', ('''{"_user": "2bb1975c341efd8209a38d37f64fa7d53556f073654d965da5d62d19b9286ac83a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_user%22%3Bi%3A1%3Bs%3A50%3A%22%5B62935%2C%22ef9840cb989abefa405bbf9d8c9ae77c%22%2C2592000%5D%22%3B%7D"}''',))
    print(get_user_cookie(id))
    
