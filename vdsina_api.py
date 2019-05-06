import requests
import time
from const import *
import aiohttp
import asyncio
import json
from exceptions import *
import time


async def get_auth_cookies(login, password):
    async with aiohttp.ClientSession() as sess:
        # достаем csrf-токен
        print(login, password)
        async with sess.get(api + 'login') as resp:
            json = await resp.json()
            csrf = json['_csrf']
        # формируем тело запроса
        data = auth_form.format(login, password, csrf)
        
        # отправляем пакет
        async with sess.post(api + 'login', data=data, headers=multipart_head) as resp:
            auth_json = await resp.json()
        
        if auth_json['status'] == 'ok':
            # возвращаем куки из сессии
            return cookies_to_dict(sess.cookie_jar)
        else:
            raise InvalidAuthData()


async def get_user_info(cookie):
    async with aiohttp.ClientSession(cookies=cookie) as sess:
        json = await get_json(sess, api)
        print(json)
        if json['status'] == 'ok':
            
            # информация о балансах
            json_balance = json['balance']
            
            data = {key: json_balance[key]['value'] for key in keys_USER}
            
            # прогноз срока отключения
            data['forecast'] = json['forecast']['value']
            return data
        else:
            raise InvalidCookie()

def _prepare_server(vps):
    # основная информация о сервере
    
    vps_info = {k:vps[k]['value'] for k in keys_VPS}
    vps_info['can_reboot'] = vps['can_reboot']
    
    traff_current = vps['service_traff']['current']['value'] + ' ' + vps['service_traff']['current']['text']
    traff_last = vps['service_traff']['last']['value'] + ' ' + vps['service_traff']['last']['text']
    
    vps_info['traf_curr'] = traff_current
    vps_info['traf_last'] = traff_last
    # информация о тарифе
    json_plan = vps['service_data']['value']['plan']['data']
    vps_info['cpu'] = json_plan['vCPU']
    vps_info['ram'] = json_plan['RAM']
    vps_info['ram'] = json_plan['SSD']
    vps_info['traffic_limit'] = json_plan['Трафик']
    
    # =========
    server_data = vps['service_data']['value']
    
    # информация об IP
    vps_info['ip'] = server_data['ip']['ip']

    # информация о датацентре
    vps_info['dc'] = server_data['datacenter']['name']

    # информация об ОС
    vps_info['oc'] = server_data['template']['name']
    

    return vps_info

async def get_server_info(cookie, server_id):
    async with aiohttp.ClientSession(cookies=cookie) as sess:
        json = await get_json(sess, info_VPS + str(server_id))
        
        if json['status'] == 'ok':
            return _prepare_server(json['service'])
        else:
            raise InvalidCookie()


async def get_servers_info(cookie):
    async with aiohttp.ClientSession(cookies=cookie) as sess:
        json = await get_json(sess, list_VPS)

        if json['status'] == 'ok':
            data = []
            for server in json['rows']:
                data.append({'service_name': server['service_name'],
                               'service_id': server['service_id']})
            return data
        else:
            raise InvalidCookie()

def cookies_to_dict(cookie):
    return {c.key: c.value for c in cookie}


def save_cookie_dict(cookie):
    with open('c.json', 'w') as file:
        file.write(json.dumps(cookie))


def get_cookie_from_file(filename):
    with open(filename, 'r') as file:
        return json.loads(file.read())


async def get_json(sess, url):
    async with sess.get(url) as resp:
        return await resp.json()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    cookie = get_cookie_from_file('c.json')
    cookies = loop.run_until_complete(get_server_info(cookie, 123754))
    print(cookies)
