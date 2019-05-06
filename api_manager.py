import vdsina_api as api
import time
import db_helpers as db
from exceptions import *

class User:
    def __init__(self):
        self.balanse_data = {}
        self.last_update = 0
        self.cookie = {}
        
class ApiManager:
    def __init__(self):
        # кеш данных пользователей
        self.users = {}
    
    async def _update_profile(self, user_id): # отдельная функция, т.к. предусмотрено сохранение кеша
        # достаем куки
        cookie = self._get_user_cookie(user_id)
        # достаем обновления
        data = await api.get_user_info(cookie)
        # обновляем кеш
        user = self._get_user(user_id)
        user.balanse_data = data
        user.last_update = time.time() # для ограничения rps пользователя
        return data

    def _get_user(self, user_id):
        if user_id in self.users:
            return self.users[user_id]
        else:
            # если менеджер видит пользователя впервые
            self.users[user_id] = user = User()
            user.user_id = user_id
            return user
    
    def _get_user_cookie(self, user_id):
        user = self._get_user(user_id)
        if user.cookie:
            # возвращаем куки из кеша
            return user.cookie
        else:
            # достаем из базы куки
            cookie = db.get_user_cookie(user_id)
            # и кладем их в кеш пользователя
            user.cookie = cookie
            # возвращаем куки
            return cookie
    
    async def get_user_info(self, user_id):
        user = self._get_user(user_id)
        if user.balanse_data:
            if time.time() - user.last_update > 5:
                # если обновление было более 5 секунд назад
                return await self._update_profile(user_id)
            else:
                # если обновление было недавно
                return user.balanse_data
        else:
            # если информации о пользователе нет в кеше
            return await self._update_profile(user_id)
    
    async def get_user_servers(self, user_id):
        cookie = self._get_user_cookie(user_id)
        return await api.get_servers_info(cookie)
    
    async def get_server_info(self, user_id, server_id):
        cookie = self._get_user_cookie(user_id)
        return await api.get_server_info(cookie, server_id)
    
    async def auth_user(self, user_id, login, password):
        cookie = await api.get_auth_cookies(login, password)
        if user_id not in self.users:
            self.users[user_id] = user = User()
        else:
            user = self.users[user_id]
        db.set_user_cookie(user_id, str(cookie))
        user.cookie = cookie
    
    