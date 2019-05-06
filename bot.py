import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from db_helpers import *
from api_manager import ApiManager
from exceptions import *

InlineKeyboard = types.inline_keyboard.InlineKeyboardMarkup
InlineButton = types.inline_keyboard.InlineKeyboardButton
RemoveKeyboard = types.ReplyKeyboardRemove
ReplyKeyboard = types.ReplyKeyboardMarkup
ReplyButton = types.KeyboardButton

TOKEN = '699496323:AAHpHRNraSsW_DdZh4jNV518WDGglZKLaJY'

storage = MemoryStorage()
bot = Bot(TOKEN, parse_mode='Markdown', )
dp = Dispatcher(bot, storage=storage)

api = ApiManager()


class AuthForm(StatesGroup):
    login = State()
    password = State()


def start_filter(msg):
    return msg.chat.type == 'private' and msg.text == '/start'


def menu_btn():
    btn = ReplyKeyboard(resize_keyboard=True)
    btn.insert('👤 Профиль')
    return btn


def remove_btn():
    return RemoveKeyboard()


def auth_btn():
    btn = ReplyKeyboard(resize_keyboard=True)
    btn.insert('🔑 Авторизация')
    return btn


@dp.message_handler(start_filter)
async def main(msg: types.Message):
    if is_new_user(msg.chat.id):
        await bot.send_message(msg.chat.id, f'Привет, *{msg.chat.first_name}*!', reply_markup=menu_btn())
    else:
        await bot.send_message(msg.chat.id, f'Главное меню', reply_markup=menu_btn())


def msg_profile(data):
    text = f"Баланс: *{data['real']} р.*\n" \
           f"Бонусы: *{data['bonus']} р.*\n" \
           f"Прогноз отключения: *{data['forecast']}*"
    btn = InlineKeyboard()
    btn.add(InlineButton('🖥 Мои сервера', callback_data='servers'))
    return text, btn


@dp.message_handler(regexp='.*Профиль')
async def profile(msg: types.Message):
    try:
        data = await api.get_user_info(msg.chat.id)
    except InvalidCookie:
        await send_message_reauth(msg.chat.id)
    except CookieNotFound:
        await bot.send_message(msg.chat.id, 'ℹ️Для начала необходимо авторизоваться', reply_markup=auth_btn())
    else:
        text, btn = msg_profile(data)
        await bot.send_message(msg.chat.id, text, reply_markup=btn)

async def send_message_reauth(user_id, msg_id=None):
    text = '❗️*Ошибка авторизации.*\nПопробуйте авторизоваться заново'
    if msg_id:
        await bot.delete_message(user_id, msg_id)
    await bot.send_message(user_id, text, reply_markup=auth_btn())

@dp.message_handler(regexp='.*Авторизация')
async def profile(msg: types.Message):
    # указываем на сущность следующего сообщения - логин
    await AuthForm.login.set()
    await bot.send_message(msg.chat.id, '▪️ Введите логин', reply_markup=remove_btn())


@dp.message_handler(state=AuthForm.login)
async def profile(msg: types.Message, state):
    # добавляем в форму логин
    await state.update_data(login=msg.text)
    # указываем сущность следующего сообщения - пароль
    await AuthForm.next()
    await bot.send_message(msg.chat.id, '▪️ Введите пароль')


@dp.message_handler(state=AuthForm.password)
async def profile(msg: types.Message, state):
    # добавляем в форму пароль
    await state.update_data(password=msg.text)
    async with state.proxy() as data:
        # достаем из формы данные для авторизации
        login, password = data['login'], data['password']
        # очищаем форму
        data.state = None
        try:
            await api.auth_user(msg.chat.id, login, password)
        except InvalidAuthData:
            await bot.send_message(msg.chat.id, '⛔️ Неверный логин или пароль. Попробуйте снова', reply_markup=menu_btn())
        else:
            await bot.send_message(msg.chat.id, '✅ Вход выполнен', reply_markup=menu_btn())

async def msg_servers(user_id, *args):
    text = '🖥 Выберите сервер'
    servers = await api.get_user_servers(user_id)
    btn = InlineKeyboard(row_width=1)
    for server in servers:
        btn.insert(InlineButton(server['service_name'], callback_data=server['service_id']))
    btn.insert(InlineButton('Назад', callback_data='back_to_profile'))
    return text, btn

async def msg_server_info(user_id, _, calldata):
    # достаем информацию о сервере
    
    s = await api.get_server_info(user_id, calldata)   # в calldata лежит id сервера
    text =  f"*{s['service_name']}*\n" \
            f"{'〰️'* 10} \n"\
            f"ℹ️ IP-адрес: `{s['ip']}`\n"\
            f"🖥 Статус: *{s['service_status']}*\n"\
            f"🖲 Datacenter: *{s['dc']}*\n"\
            f"🌐 Трафик за месяц:\n"\
            f"    ▪️текущий: *{s['traf_curr']}*\n"\
            f"    ▪️прошлый: *{s['traf_last']}*\n"\
            f"💿 ОС: *{s['oc']}*\n"\
            f"📅 Дата создания: *{s['service_created']}*\n"\
            f"📅 Прогноз отключения: *{s['service_end']}*"
    btn = InlineKeyboard()
    btn.insert(InlineButton('Назад', callback_data='servers'))
    return text, btn

async def send_inline_with_auth(function, call):
    # обработчик ошибок для всех inline-сообщений
    user_id = call.message.chat.id
    msg_id = call.message.message_id
    try:
        text, btn = await function(user_id, msg_id, call.data)
    except InvalidCookie:
        # страховка - пользователь может сменить пароль в любой момент
        await send_message_reauth(user_id, msg_id)
    else:
        await bot.edit_message_text(text, user_id, msg_id, reply_markup=btn)


@dp.callback_query_handler() # общий inline-хандлер
async def callback(call: types.CallbackQuery):
    # на каждый callback.data регистрируем функцию
    inline_functions = {'servers': msg_servers}
    
    # отвечаем на колбек успехом
    await bot.answer_callback_query(call.id)
    if call.data in inline_functions:
        # вызываем обработчик, если у пришедшего callback.data есть функция
        await send_inline_with_auth(inline_functions[call.data], call)
        
    elif call.data.isdigit():
        # отдельное условие для динамического callback.data
        await send_inline_with_auth(msg_server_info, call)


        

executor.start_polling(dp, skip_updates=True)
