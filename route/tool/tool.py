from sanic_ipware import get_client_ip
import aiosqlite
import datetime
import json
import re

async def date_time():
    return str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"))

async def get_ip(request):
    return str(get_client_ip(request, request_header_order=['Forwarded-For', 'X-Forwarded-For']))

async def user_link(name):
    if re.sub('\.([^.]*)\.([^.]*)$', '.*.*', name):
        return '<a href="/contribution/' + name + '/changes">' + name + '</a>'
    elif (':([^:]*):([^:]*)$', ':*:*', name):
        return '<a href="/contribution/' + name + '/changes">' + name + '</a>'
    else:
        return '<a href="/w/사용자:' + name + '">' + name + '</a>' 

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