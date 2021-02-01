import datetime
import hashlib
import json
import re
import secrets
import binascii

import aiosqlite
from sanic_session import Session

async def date_time():
    return str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))

async def user_name(request):
    if not request.ctx.session.get('id') or request.ctx.session.get('id') == 0:
        if request.ip == '127.0.0.1' or request.ip == '::1':
            ip = request.remote_addr
            return ip
        else:
            ip = request.ip
            return ip
    else:
        return request.ctx.session['id']

async def user_link(name):
    if re.sub('\.([^.]*)\.([^.]*)$', '.*.*', name):
        return '<a href="/contribution/' + name + '/changes">' + name + '</a>'
    elif (':([^:]*):([^:]*)$', ':*:*', name):
        return '<a href="/contribution/' + name + '/changes">' + name + '</a>'
    else:
        return '<a href="/w/사용자:' + name + '">' + name + '</a>' 

async def namespace_check(data):
    return 0

async def wiki_set(request, data):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data_footer = await db.execute("select data from wiki_set where name = 'license'")
    data_footer = await data_footer.fetchall()

    data_wiki = await db.execute("select data from wiki_set where name = 'name'")
    data_wiki = await data_wiki.fetchall()

    data_date = ''

    if data != 0:
        data_edit = await db.execute("select date from doc_his where title = ? order by date desc", [data])
        data_date = await data_edit.fetchall()

    if request.ctx.session.get("id") and request.ctx.session.get("id") != 0:
        data_login = 1
    else:
        data_login = 0

    data_footer = data_footer[0][0] if data_footer else 'ARR'
    data_wiki = data_wiki[0][0] if data_wiki else 'Wiki'
    data_date = data_date[0][0] if data_date else 0

    return data_footer, data_wiki, data_date, data_login

async def check_user():
    return 0

async def check_admin(data):
    return 0

async def check_acl(data):
    return 0

async def history_add(title, data, date, ip, send, leng):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    history_id = await db.execute("select id from doc_his where title = ? order by id + 0 desc limit 1", [title])
    history_id = await history_id.fetchall()

    send = re.sub('\(|\)|<|>', '', send)

    if len(send) > 128:
        send = send[:128]

    if history_id:
        id = str(int(history_id[0][0]) + 1) 
    else:
        id = '1'

    await db.execute("insert into doc_his (id, title, data, date, ip, send, leng) values (?, ?, ?, ?, ?, ?, ?)", [id, title, data, date, ip, send, leng])
    await db.commit()

async def password_encode(data, name):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    encode_type = await db.execute('select data from wiki_set where name = "encode"')
    encode_type = await encode_type.fetchall()

    if encode_type[0][0] == 'sha256':
        return hashlib.sha256(bytes(data, 'utf-8')).hexdigest()

    elif encode_type[0][0] == 'sha3':
        return hashlib.sha3_256(bytes(data, 'utf-8')).hexdigest()

    elif encode_type[0][0] == 'pbkdf2-sha512':
        #TODO : Need slow password hash algorithm
        return CreateAuth(name, data)

async def _hashpass(username: str, password: str, salt: str):
    hashsalt = (salt + username).encode('utf-8')
    password = password.encode('utf-8')
    curhash = hashlib.pbkdf2_hmac('sha512',password,hashsalt,100000,dklen=256)
    curhash = binascii.hexlify(curhash)
    curhash = str(curhash)
    #print(curhash)
    return curhash[2:-1]

async def CreateAuth(username: str, password: str):
    #min: 16+
    SALT_LEN=16
    salt = secrets.token_hex(SALT_LEN)
    curhash = await _hashpass(username,password,salt)
    return str(salt+'$'+curhash)

async def VerifyAuth(username:str,password:str,authstr:str):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    encode_type = await db.execute('select data from wiki_set where name = "encode"')
    encode_type = await encode_type.fetchall()

    if encode_type[0][0] == 'sha256':
        check_password = await db.execute('select pw from mbr where id = ?', [username])
        check_password = await check_password.fetchall()

        if hashlib.sha256(bytes(password, 'utf-8')).hexdigest() == check_password[0][0]:
            return 1
        else:
            return 0

    elif encode_type[0][0] == 'sha3':
        check_password = await db.execute('select pw from mbr where id = ?', [username])
        check_password = await check_password.fetchall()

        if hashlib.sha3_256(bytes(password, 'utf-8')).hexdigest() == check_password[0][0]:
            return 1
        else:
            return 0

    elif encode_type[0][0] == 'pbkdf2-sha512':
        salt = authstr.split('$')[0]
        hashdata = authstr.split('$')[1]
        if await _hashpass(username,password,salt) == hashdata:
            return 1
        else:
            return 0