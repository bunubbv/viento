from sanic_ipware import get_client_ip
import aiosqlite
import datetime
import hashlib
import json
import re

async def date_time():
    return str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))

async def user_name():
    return str(get_client_ip(request, request_header_order=['Forwarded-For', 'X-Forwarded-For']))

async def user_link(name):
    if re.sub('\.([^.]*)\.([^.]*)$', '.*.*', name):
        return '<a href="/contribution/' + name + '/changes">' + name + '</a>'
    elif (':([^:]*):([^:]*)$', ':*:*', name):
        return '<a href="/contribution/' + name + '/changes">' + name + '</a>'
    else:
        return '<a href="/w/사용자:' + name + '">' + name + '</a>' 

async def namespace_check(data):
    return 0

async def wiki_setting():
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

async def user_check():
    return 0

async def admin_check(data):
    return 0

async def acl_check(data):
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

async def password_encode(data):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    encode_type = await db.execute('select data from wiki_set where name = "encode"')
    encode_type = await encode_type.fetchall()

    if encode_type[0][0] == 'sha256':
        return hashlib.sha256(bytes(data, 'utf-8')).hexdigest()
    elif encode_type[0][0] == 'sha3':
        return hashlib.sha3_256(bytes(data, 'utf-8')).hexdigest()

async def password_check(data):
    return 0