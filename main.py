#import logging
from aiogram import Bot, types
from aiogram.utils.helper import Helper
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from os import mkdir, getcwd, system
import urllib
from loguru import logger
import sqlite3 as sq
from time import time


from config import TOKEN
PATH = getcwd()
#logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logger.add("debug.json", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

def db_checker(id):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        select = f"SELECT id FROM users WHERE id == {id}"
        cur.execute(select)
        res = cur.fetchall()
        if res != []:
            return True
        else:
            return False


def add_user(id):
    with sq.connect("db.db") as con:
        cur = con.cursor()
        insert = f"INSERT INTO users VALUES({id},datetime('now','localtime'))"
        cur.execute(insert)


def make_dir(dirname):
    try:
        mkdir(dirname)
    except OSError as e:
        return False
    else:
        return True


class Form(StatesGroup):
    name = State()
    SAM = State()
    SYSTEM = State()
    HASH = State()


class Users(StatesGroup):
    user_id = State()


class Hash(StatesGroup):
    HASH = State()


class John(StatesGroup):
    name_dir = State()
    hash = State()


@dp.message_handler(commands=['start','help'])
async def start_procces(msg:types.Message):
    await bot.send_message(msg.chat.id, "Hello, this bot was created for automatic brutforce Windows hashes")

@dp.message_handler(commands=['add_user'])
async def process_add(message: types.Message):
    if message.chat.id == 450047498:
        await Users.user_id.set()
        await bot.send_message(message.chat.id, "Кого будем добавлять? (Только ID)")
    else:
        await bot.send_message(message.chat.id, "Ты не админ, кыш")


@dp.message_handler(state=Users.user_id)
async def process_test(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.text
        try:
            id = int(data['user_id'])
            add_user(id)
        except ValueError:
            await bot.send_message(message.chat.id, "Something wrong, try something else")
            await state.finish()
        else:
            await bot.send_message(message.chat.id, "User was added!")
            await state.finish()


@dp.message_handler(commands=["tg_loco"])
async def process_tg_loco(message: types.Message):
    if db_checker(message.chat.id) == True:
        await John.name_dir.set()
        await message.reply("Выберите название папки для проекта (без пробелов кавычек и прочего)")
    else:
        await bot.send_message(message.chat.id, "I didn`t know who are u...\n-_-")
        logger.error("ILLEGAL ACCES:"+str(message.chat.id)+'\n'+str(message.chat.username)+'\n')

@dp.message_handler(state=John.name_dir)
async def process_john(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name_dir'] = message.text
        if make_dir('files/tg_local/'+data['name_dir']):
            await bot.send_message(message.chat.id, "Папка была создана успешно!")
            await John.next()
            # BOLD
            await message.reply("Пришлите файл с хешем телеграма\nПример:\n$telegram$2*100000*a0ad816dfa35307efd3e3053a6077e9d2fa3e3ad9d703686750a998718c23b59*1127f695e267fd5e7a9b581995e7a6de5a5d1b3144e6572b780e8689b5e176b3e0c55f54edd41e2931d876af8c9585fb5757b9987323e8f7abcbc4f49ced2a0463f710292eaaddcf759c19f9c63f249a227fce492adc8509c5c66c8cb470965496863e17452ea46c759ba0524029f493cfa1e6878314db745b1bb9924e415e658a2d33a7cab2ba9ea1c0923bbf6e75666f245be4ac39780326d80a8e2bc479e043e7a530c56c73167eabb5858f011199c03c64124daff6016a0ce3cf280d9c195da7ef9ebf1ffad52e336d292c3e2174b8e00b5554caf853a32d6cc2bdb8fee18bd37358dcfd3565649d494a8b027f6083f8e4e42b3f438987321bbe0bcea13f0fb864c3a782431e132207f508e76b6a9768416ee015a2ad89c7cc620b2cb1fe")
        else:
            await bot.send_message(message.chat.id,"Название папки не подходит.\nHапишите /tg_loco и попробуйте ещё раз")
            await state.finish()


@dp.message_handler(content_types=['document'], state=John.hash)
async def process_John_hash(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['hash'] = True
        document_id = message.document.file_id
        file_info = await bot.get_file(document_id)
        fi = file_info.file_path
        name = message.document.file_name
        hash_path = 'files/tg_local/'+data['name_dir']
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',f"{hash_path}/{name}")
        await bot.send_message(message.from_user.id, f'Hash файл успешно сохранён {hash_path}/{name}.\nНачинаю брутфорс!')
        system(f"./cracken.sh john_tg {hash_path}/{name} {hash_path}/result.txt")
        with open(f"{hash_path}/result.txt","r",encoding="utf-8") as f:
            line = f.readline()
            await bot.send_message(message.chat.id, str(line.split(":")[1]))
            


@dp.message_handler(commands=['just_hash'])
async def process_try_hash(message: types.Message):
    if db_checker(message.chat.id) == False:
        await bot.send_message(message.chat.id, "I didn`t know who are u...\n-_-")
        logger.error("ILLEGAL ACCES:"+str(message.chat.id)+'\n'+str(message.chat.username)+'\n')
    else:
        await bot.send_message(message.chat.id, "Скиньте только хеш")
        await Hash.HASH.set()


@dp.message_handler(state=Hash.HASH)
async def process_hash(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['HASH'] = message.text
        await bot.send_message(message.chat.id, "Brute force started!")
        tmp_time = int(time())
        logger.info("WHOIS : "+str(data['HASH']+'\n'+str(tmp_time)))
        system(f"./cracken.sh cat_win {data['HASH']} /tmp/{tmp_time}.txt")

        await bot.send_message(message.chat.id, "Check result!")
        with open(f"/tmp/{tmp_time}.txt", "r") as r:
            try:
                text = r.readlines()
                await bot.send_message(message.chat.id, text[0])
            except Exception as e:
                await bot.send_message(message.chat.id, "Хеш не найден :(")
 
        await state.finish()


@dp.message_handler(commands=['brute'])
async def recv_message(message: types.Message):
    await Form.name.set()
    await message.reply("Выберите название папки для проекта (без пробелов кавычек и прочего)")

@dp.message_handler(state=Form.name)
async def process_test(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if db_checker(message.chat.id) == False:
            await bot.send_message(message.chat.id, "I didn`t know who are u...\n-_-")
            logger.error("ILLEGAL ACCES:"+str(message.chat.id)+'\n'+str(message.chat.username)+'\n')
            await state.finish()
        else:
            data['name'] = message.text
            if make_dir('files/'+data['name']):
                await bot.send_message(message.chat.id, "Папка была создана успешно!")
            else:
                await bot.send_message(message.chat.id, "Название папки не подходит.\nHапишите /brute и попробуйте ещё раз")

            global active_dir_path
            active_dir_path = PATH+'/'+'files/'+data['name']
            logger.info("WHOIS DIR : "+str(message.chat.id)+'\n'+str(message.chat.username)+'\n'+active_dir_path)

            await Form.next()
            await message.reply("Пришлите SAM файл :^)\n!!! Имена файлов должны быть в верхнем регистре !!!")

@dp.message_handler(lambda message: message.document.file_name == "SAM",content_types=['document'], state=Form.SAM)
async def process_SAM(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['SAM'] = True
        document_id = message.document.file_id
        file_info = await bot.get_file(document_id)
        fi = file_info.file_path
        name = message.document.file_name
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',f'{active_dir_path}/{name}')
        await bot.send_message(message.chat.id, f'DEBUG: Файл SAM успешно сохранён в {active_dir_path}/{name}')

    await Form.next()
    await message.reply("Хорошо, SAM загружен\nТеперь скиньте файл SYSTEM :^)")

@dp.message_handler(lambda message: message.document.file_name == "SYSTEM",content_types=['document'], state=Form.SYSTEM)
async def process_SYSTEM(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['SYSTEM'] = True
        document_id = message.document.file_id
        file_info = await bot.get_file(document_id)
        fi = file_info.file_path
        name = message.document.file_name
        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',f'{active_dir_path}/{name}')
        await bot.send_message(message.chat.id, f'Файл SYSTEM успешно сохранён {active_dir_path}/{name}')
        await bot.send_message(message.chat.id, "Вынятые хеши с файлов:")
        system(f'python3 secretsdump.py -sam {active_dir_path}/SAM -system {active_dir_path}/SYSTEM LOCAL >> {active_dir_path}/hashes_out.txt')
        with open(f"{active_dir_path}/hashes_out.txt", "r",encoding="utf-8") as f:
            for line in f:
                lines = line.split(":")
                name = lines[0]
                ha = lines[3]
                await bot.send_message(message.chat.id, name)
                await bot.send_message(message.chat.id, ha)
                #with open(f"{active_dir_path}/hashes_out.txt","rb") as f:
            #await bot.send_document(message.chat.id,f)
            await bot.send_message(message.chat.id,"Отправьте 1 хеш")

    await Form.next()

@dp.message_handler(state=Form.HASH)
async def process_test(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['HASH'] = message.text
        print(data['HASH'])
        await bot.send_message(message.chat.id, "Brute force started!")
        info = [data['name'], data['SAM'], data['SYSTEM'], data['HASH']]
        logger.info("WHOIS : "+str(info)+'\n'+active_dir_path)
        system(f"./cracken.sh cat_win {data['HASH']} {active_dir_path}/result.txt")

        await bot.send_message(message.chat.id, "Check result!")
        with open(f"{active_dir_path}/result.txt", "r") as r:
            try:
                text = r.readlines()
                await bot.send_message(message.chat.id, text[0])
            except Exception as e:
                await bot.send_message(message.chat.id, "Хеш не найден :(")
 
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp)
