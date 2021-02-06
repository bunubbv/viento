from sanic import Sanic, response, Blueprint
from sanic.request import RequestParameters
from sanic_jinja2 import SanicJinja2
from sanic_session import Session, AIORedisSessionInterface
import aiosqlite
import aiofiles
import aioredis
import asyncio
import json
import html
import os
import re

from route.tool.tool import *
from route.mark.py.namumark import *

setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
version_load = json.loads(open('data/version.json', encoding='utf-8').read())

engine_version = version_load["main"]["engine_version"]
markup_version = version_load["main"]["markup_version"]
build_count = version_load["main"]["build_count"]
renew_count = version_load["main"]["renew_count"]

print('')
print('VientoEngine')
print('engine_version : ' + engine_version)
print('markup_version : ' + markup_version)
print('build_count : ' + build_count)
print('renew_count : ' + renew_count)
print('')

for route_file in os.listdir("route"):
    py_file = re.search(r"(.+)\.py$", route_file)
    if py_file:
        py_file = py_file.groups()[0]

        exec("from route." + py_file + " import *")

## 위키 설정

async def run():
    server_setting = { 
        "host" : {
            "setting": "host",
            "default": "0.0.0.0"
        },
        "port" : {
            "setting": "port",
            "default": "3000"
        },
        "lang" : {
            "setting": "lang",
            "default": "ko-KR",
            "list" : ["ko-KR", "en-US"]
        },
        "encode" : {
            "setting": "encode",
            "default": "pbkdf2-sha512",
            "list" : ["sha3", "sha256", "pbkdf2-sha512"]
        }
    }

    try:
        async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
            setting_data = json.loads(await f.read())

        if not 'db_type' and 'db_name' and 'host' and 'port' in setting_data:
            try:
                os.remove('data/setting.json')
            except:
                print('Error : Please delete data/setting.json')
                raise
        else:
            print('db_type : ' + setting_data['db_type'])
            print('db_name : ' + setting_data['db_name'])
            print('\n', end='')
            print('host : ' + setting_data['host'])
            print('port : ' + setting_data['port'])
    except:
        setting_json = ['sqlite', '', '', '']
        db_type = ['sqlite']

        print('db_type : sqlite')        
        print('db_name : ', end = '')

        setting_json[1] = str(input())
        if setting_json[1] == '':
            setting_json[1] = 'data'

        print('\n', end='')

        print('host (' + server_setting['host']['default'] + ') : ', end = '')
        setting_json[2] = str(input())
        if setting_json[2] == '':
            setting_json[2] = server_setting['host']['default']
        
        print('port (' + server_setting['port']['default'] + ') : ', end = '')
        setting_json[3] = str(input())
        if setting_json[3] == '':
            setting_json[3] = server_setting['port']['default']

        async with aiofiles.open('data/setting.json', 'w', encoding = 'utf8') as f:
            await f.write('{ "db_name" : "' + setting_json[1] + '", "db_type" : "' + setting_json[0] + '", "host" : "' + setting_json[2] + '", "port" : "' + setting_json[3] + '" }')

    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    db_create = {}
    db_create['table'] = ['doc', 'doc_cac', 'doc_his', 'rec_dis', 'rec_ban', 'rec_log', 'mbr', 'mbr_set', 'mbr_log', 'ban', 'dis', 'dis_log', 'acl', 'backlink', 'wiki_set', 'list_per', 'list_fil', 'html_fil', 'list_alarm', 'list_watch', 'list_inter']
    
    for i in db_create['table']:
        try:
            await db.execute('select test from ' + i + ' limit 1')
        except:
            try:
                await db.execute('create table ' + i + '(test longtext)')
            except:
                await db.execute("alter table " + i + " add test longtext default ''")

    db_setup = 0
    try:
        db_ver = await db.execute('select data from wiki_set where name = "db_ver"')
        db_ver = await db_ver.fetchall()
        if not db_ver:
            db_setup = 1
        else:
            if int(version_load['main']['renew_count']) > int(db_ver[0][0]):
                db_setup = 1
    except:
        db_setup = 1

    if db_setup != 0:
        db_create['doc'] = ['title', 'data']
        db_create['doc_cac'] = ['title', 'data']
        db_create['doc_his'] = ['id', 'title', 'data', 'date', 'ip', 'send', 'leng', 'hide', 'type']
        db_create['rec_dis'] = ['title', 'sub', 'date', 'band', 'stop', 'agree']
        db_create['rec_ban'] = ['block', 'end', 'today', 'blocker', 'why', 'band']
        db_create['rec_log'] = ['who', 'what', 'time']
        db_create['mbr'] = ['id', 'pw', 'acl', 'date', 'email']
        db_create['mbr_set'] = ['name', 'id', 'data']
        db_create['mbr_log'] = ['name', 'ip', 'ua', 'today', 'sub']
        db_create['ban'] = ['block', 'end', 'why', 'band', 'login']
        db_create['dis'] = ['doc', 'title', 'id', 'state', 'date', 'agree']
        db_create['dis_log'] = ['id', 'data', 'date', 'ip', 'block', 'top', 'code', 'doc']
        db_create['acl'] = ['title', 'decu', 'dis', 'view', 'why']
        db_create['backlink'] = ['title', 'link', 'type']
        db_create['wiki_set'] = ['name', 'data', 'coverage']
        db_create['list_per'] = ['name', 'acl']
        db_create['list_fil'] = ['name', 'regex', 'sub']
        db_create['html_fil'] = ['html', 'kind', 'plus']
        db_create['list_alarm'] = ['name', 'data', 'date']
        db_create['list_watch'] = ['user', 'title']
        db_create['list_inter'] = ['title', 'link', 'icon']

        for create_table in db_create['table']:
            for create in db_create[create_table]:
                try:
                    await db.execute('select ' + create + ' from ' + create_table + ' limit 1')
                except:
                    await db.execute("alter table " + create_table + " add " + create + " longtext default ''")

                try:
                    await db.execute('create index index_' + create_table + '_' + create + ' on ' + create_table + '(' + create + ')')
                except:
                    pass

    await db.execute('delete from wiki_set where name = "db_ver"')
    await db.execute('insert into wiki_set (name, data) values (?, ?)', ["db_ver", version_load['main']['renew_count']])
    await db.commit()

    first_setup = await db.execute('select data from wiki_set where name = "lang"')
    first_setup = await first_setup.fetchall()

    if not first_setup:
        lang = server_setting['lang']['list'][0] + ', ' + server_setting['lang']['list'][1]
        print('lang [' + lang + '] (' + server_setting['lang']['default'] + ') : ', end = '')
        setting_lang = str(input())
        if setting_lang == '':
            setting_lang = server_setting['lang']['default']
        await db.execute('insert into wiki_set (name, data) values (?, ?)', ['lang', setting_lang])

        encode = server_setting['encode']['list'][0] + ', ' + server_setting['encode']['list'][1] + ', ' + server_setting['encode']['list'][2]
        print('encode [' + encode + '] (' + server_setting['encode']['default'] + ') : ', end = '')
        setting_encode = str(input())
        if setting_encode == '':
            setting_encode = server_setting['encode']['default']
        await db.execute('insert into wiki_set (name, data) values (?, ?)', ['encode', setting_encode])
        await db.commit()
    else:
        encode_check = await db.execute('select data from wiki_set where name = "encode"')
        encode_check = await encode_check.fetchall()
        
        print('lang : ' + first_setup[0][0])
        print('encode : ' + encode_check[0][0])

    print("\n", end='')
    
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
    
app = Sanic(__name__)
jinja = SanicJinja2(app, pkg_path='skins')
session = Session(app)
app.static('/skins', './skins')
    
## 주소 설정

'''@app.listener('before_server_start')
async def server_init(app, loop):
    app.redis = await aioredis.create_pool(
        ('localhost', 6379),
        minsize=5,
        maxsize=10,
        loop=loop
    )
    session.init_app(app, interface=AIORedisSessionInterface(app.redis))'''

@app.route('/')
async def wiki_frontpage(request):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data_get = await db.execute("select data from wiki_set where name = ?", ['frontpage'])
    data_get = await data_get.fetchall()

    if data_get:
        return response.redirect('/w/' + data_get[0][0])
    else:
        return response.redirect('/w/FrontPage')

@app.route("/w/<name:string>")
async def wiki_read(request, name):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data = await db.execute("select data from doc where title = ?", [name])
    data = await data.fetchall()

    if data:    
        return jinja.render("index.html", request, wiki_set = await wiki_set(request, name),
            data = await namumark(data[0][0]),
            title = name,
            sub = 0,
            menu = [['edit/' + name, '편집'], ['discuss/' + name, '토론'], ['backlink/' + name, '역링크'], ['history/' + name, '역사'], ['acl/' + name, 'ACL']]
        )
    else:
        return jinja.render("index.html", request, wiki_set = await wiki_set(request, name),
            data = "해당 문서를 찾을 수 없습니다.", 
            title = name,
            sub = 0,
            menu = [['edit/' + name, '편집'], ['discuss/' + name, '토론'], ['backlink/' + name, '역링크'], ['history/' + name, '역사'], ['acl/' + name, 'ACL']]
        )
        
@app.route("/edit/<name:string>", methods=['POST', 'GET'])
async def wiki_edit(request, name):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data_get = await db.execute("select data from doc where title = ? ", [name])
    data_get = await data_get.fetchall()
    
    data = ""
    olddata = ''

    if data_get:
        data = data_get[0][0]
        olddata = data

    if request.method == 'POST':
        data = request.form.get('wiki_edit_textarea_1', '')
        send = request.form.get('wiki_edit_textbox_1', '')
        
        if data_get:
            if data_get[0][0] == data:
                return response.redirect("/w/" + name)
            
            else:
                data = re.sub('\n', '<br>', data)
                await db.execute("update doc set data = ? where title = ?", [data, name])
                await db.commit()
                await history_add(name, data, await date_time(), await user_name(request), send, str(len(data) - len(olddata)))
                return response.redirect("/w/" + name)
                
        else:
            data = re.sub('\n', '<br>', data)
            await db.execute("insert into doc (title, data) values (?, ?)", [name, data])
            await db.commit()
            await history_add(name, data, await date_time(), await user_name(request), send, str(len(data)))
            return response.redirect("/w/" + name)
            
    return jinja.render("index.html", request, wiki_set = await wiki_set(request, name),
            data = '''
                <form method="post">
                    <textarea rows="25" class="wiki_textarea" name="wiki_edit_textarea_1">''' + html.escape(re.sub('<br>', '\n', data)) + '''</textarea>
                    <hr class="wiki_hr">
                    <input type="text" placeholder="요약" class="wiki_textbox" name="wiki_edit_textbox_1">
                    <hr class="wiki_hr">
                    <button type="submit" class="wiki_button" name="wiki_edit_button_1">저장</button>
                </form>
            ''',
            title = name,
            sub = '편집',
            menu = [['delete/' + name, '삭제'], ['move/' + name, '이동'], ['w/' + name, '문서']]
        )
        
@app.route("/history/<name:string>")
async def wiki_history(request, name):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')
    
    data = ''
    data_get = await db.execute("select id, title, date, ip, send, leng from doc_his where title = ? order by id + 0 desc limit 30", [name])
    data_get = await data_get.fetchall()

    # if request.method == 'POST': 비교 기능 등
        
    for history_data in data_get:
        if data_get:
            data += '<li class="wiki_li">' + history_data[2] + ' | <a href="/raw/' + history_data[1] + '?num=' + history_data[0] + '">[원본]</a> <a href="/revert/' + history_data[1] + '?num=' + history_data[0] + '">[복구]</a> <a href="/raw/' + history_data[1] + '?num=' + history_data[0] + '">[비교]</a> | ' + await user_link(history_data[3]) + ' | r' + history_data[0] + ' |  <a href="/w/' + history_data[1] + '">' + history_data[1] + '</a> | (' + history_data[5] + ') (' + history_data[4] + ')' '</li>'

    return jinja.render("index.html", request, wiki_set = await wiki_set(request, name),
            data = data,
            title = name,
            sub = '역사',
            menu = [['w/' + name, '문서']]
    )

@app.route("/delete/<name:string>", methods=['POST', 'GET'])
async def wiki_delete(request, name):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data_get = await db.execute("select data from doc where title = ? ", [name])
    data_get = await data_get.fetchall()

    if request.method == 'POST':
            send = request.form.get('wiki_delete_textbox_1', '')
            await db.execute("delete from doc where title = ?", [name])
            await db.commit()
            await history_add(name, '', await date_time(), await user_name(request), send, '0')
            return response.redirect("/w/" + name)
            
    if data_get:
        return jinja.render("index.html", request, wiki_set = await wiki_set(request, name),
            data = '''
                <form method="post">
                    <input type="text" placeholder="요약" class="wiki_textbox" name="wiki_delete_textbox_1">
                    <hr class="wiki_hr">
                    <button type="submit" class="wiki_button" name="wiki_delete_button_1">확인</button>
                </form>
            ''',
            title = name,
            sub = '삭제',
            menu = [['w/' + name, '문서']]
        )
    else:
        return response.redirect("/error/") # 오류 페이지 구현 필요

@app.route("/move/<name:string>", methods=['POST', 'GET'])
async def wiki_move(request, name):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data_get = await db.execute("select data from doc where title = ? ", [name])
    data_get = await data_get.fetchall()

    if request.method == 'POST':
            change_name = request.form.get('wiki_move_textbox_1', '')
            send = request.form.get('wiki_move_textbox_2', '')
            await db.execute("update doc set title = ? where title = ?", [change_name, name])
            await db.execute("update doc_his set title = ? where title = ?", [change_name, name])
            await db.commit()
            await history_add(change_name, '', await date_time(), await user_name(request), send, '0')
            return response.redirect("/w/" + change_name)
            
    if data_get:
        return jinja.render("index.html", request, wiki_set = await wiki_set(request, name),
            data = '''
                <form method="post">
                    <input type="text" value="''' + name + '''" class="wiki_textbox" name="wiki_move_textbox_1">
                    <hr class="wiki_hr">
                    <input type="text" placeholder="요약" class="wiki_textbox" name="wiki_move_textbox_2">
                    <hr class="wiki_hr">
                    <button type="submit" class="wiki_button" name="wiki_move_button_1">확인</button>
                </form>
            ''',
            title = name,
            sub = '이동',
            menu = [['w/' + name, '문서']]
        )
    else:
        return response.redirect("/error/") # 오류 페이지 구현 필요

@app.route("/revert/<name:string>", methods=['POST', 'GET'])
async def wiki_revert(request, name):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    args = RequestParameters()
    num = request.args.get('num', '1')
    
    dbdata = await db.execute("select data from doc_his order by cast(id as integer) desc limit 1")
    dbdata = await dbdata.fetchall()
    current = dbdata[0][0]

    data_get = await db.execute("select data from doc_his where id = ?", [num])
    data_get = await data_get.fetchall()
    data_get = data_get[0][0]

    if request.method == 'POST':
        send = request.form.get('wiki_revert_textbox_2', '')
        data_get = re.sub('\n', '<br>', data_get)
        await db.execute("update doc set data = ? where title = ?", [data_get, name])
        await db.commit()
        await history_add(name, data_get, await date_time(), await user_name(request), send, str(len(current) - len(data_get)))
        return response.redirect("/w/" + name)

    if data_get:
        return jinja.render("index.html", request, wiki_set = await wiki_set(request, name),
            data = '''
                <form method="post">
                    <textarea rows="25" class="wiki_textarea" name="wiki_revert_textarea_1" readonly>''' + data_get + '''</textarea>
                    <hr class="wiki_hr">
                    <input type="text" placeholder="요약" class="wiki_textbox" name="wiki_revert_textbox_2">
                    <hr class="wiki_hr">
                    <button type="submit" class="wiki_button" name="wiki_revert_button_1">확인</button>
                </form>
            ''',
            title = name,
            sub = 'r' + num + ' 복구',
            menu = [['w/' + name, '문서']]
        )
    else:
        return response.redirect("/error/") # 오류 페이지 구현 필요

@app.route("/member/signup", methods=['POST', 'GET'])
async def wiki_signup(request):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    if request.ctx.session.get('id') == 1:
        return response.redirect('/')

    if request.method == 'POST':
        signup_id = request.form.get('wiki_signup_textbox_1', '')
        signup_password_1 = request.form.get('wiki_signup_textbox_2', '')
        signup_password_2 = request.form.get('wiki_signup_textbox_3', '')

        if not signup_password_1 and not signup_password_2:
            return response.redirect("/error/") # 오류 페이지 구현 필요

        if signup_password_1 != signup_password_2:
            return response.redirect("/error/") # 오류 페이지 구현 필요

        if re.search("(?:[^A-Za-z0-9가-힣])", signup_id):
            return response.redirect("/error/") # 오류 페이지 구현 필요

        if len(signup_id) > 24 or len(signup_id) < 3:
            return response.redirect("/error/") # 오류 페이지 구현 필요

        id_check = await db.execute("select id from mbr where id = ?", [signup_id])
        id_check = await id_check.fetchall()

        if id_check:
            return response.redirect("/error/")

        encode_password = await password_encode(signup_password_1, signup_id)
        
        first_check = await db.execute("select * from mbr limit 1")
        first_check = await first_check.fetchall()

        if not first_check:
            await db.execute("insert into mbr (id, pw, acl, date, email) values (?, ?, ?, ?, ?)", [signup_id, encode_password, 'owner', await date_time(), ''])
            await db.execute("insert into mbr_log (name, ip, ua, today) values (?, ?, ?, ?)", [signup_id, '0', '0', await date_time()])
            await db.commit()
            return response.redirect("/member/login")
        else:
            await db.execute("insert into mbr (id, pw, acl, date, email) values (?, ?, ?, ?, ?)", [signup_id, encode_password, 'member', await date_time(), '']) # 추후 권한 개편 시 member가 아닌 직접 선택하도록 변경.
            await db.execute("insert into mbr_log (name, ip, ua, today) values (?, ?, ?, ?)", [signup_id, '0', '0', await date_time()])
            await db.commit()
            return response.redirect("/member/login")

    return jinja.render("index.html", request, wiki_set = await wiki_set(request, 0),
        data = '''
            <form method="post">
                <input type="text" placeholder="아이디" class="wiki_textbox" name="wiki_signup_textbox_1">
                <hr class="wiki_hr">
                <input type="password" placeholder="비밀번호" class="wiki_textbox" name="wiki_signup_textbox_2">
                <hr class="wiki_hr">
                <input type="password" placeholder="비밀번호 확인" class="wiki_textbox" name="wiki_signup_textbox_3">
                <hr class="wiki_hr">
                <button type="submit" class="wiki_button" name="wiki_signup_button_1">확인</button>
            </form>
        ''',
        title = '계정 만들기',
        sub = 0,
        menu = 0
    )

@app.route("/member/login", methods=['POST', 'GET'])
async def wiki_login(request):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    if request.ctx.session.get('id') == 1:
        return response.redirect('/')

    if request.method == 'POST':
        wiki_id = request.form.get('wiki_login_textbox_1', '')
        wiki_password = request.form.get('wiki_login_textbox_2', '')

        wiki_pass_check = await VerifyAuth(wiki_id, wiki_password, 0)
        if wiki_pass_check == 1:
            request.ctx.session['id'] = wiki_id
            return response.redirect("/")
        else:
            return response.redirect('/error/') # 오류 페이지 구현 필요

    return jinja.render("index.html", request, wiki_set = await wiki_set(request, 0),
        data = '''
            <form method="post">
                <input type="text" placeholder="아이디" class="wiki_textbox" name="wiki_login_textbox_1">
                <hr class="wiki_hr">
                <input type="password" placeholder="비밀번호" class="wiki_textbox" name="wiki_login_textbox_2">
                <hr class="wiki_hr">
                <button type="submit" class="wiki_button" name="wiki_login_button_1">확인</button>
            </form>
        ''',
        title = '로그인',
        sub = 0,
        menu = 0
    )

@app.route("/member/logout", methods=['POST', 'GET'])
async def wiki_logout(request):
    if not request.ctx.session.get('id') or request.ctx.session.get('id') == 0:
            return response.redirect('/')

    request.ctx.session['id'] = 0
    return response.redirect("/")

@app.route("/discuss/<name:string>", methods=['POST', 'GET'])
async def wiki_discuss(request, name):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data = ''
    discuss_get = await db.execute("select title, id, state, date, agree from dis where doc = ?", [name])
    discuss_get = await discuss_get.fetchall()

    for discuss in discuss_get:
        discuss_preview = await db.execute("select")
        data += '<h2><a href="/discuss/' + name + '/' + discuss[1] + '">' + discuss[1] + '. ' + discuss[0] + '</a></h2><hr class="wiki_hr">'

    if request.method == "POST":
        discuss_title = request.form.get('wiki_discuss_textbox_1', '')
        discuss_data = request.form.get('wiki_discuss_textarea_1', '')

        if discuss_title == '' or discuss_data == '':
            return response.redirect("/error/") # 오류 구현 필요

        discuss_number = await db.execute("select id from dis where doc = ? order by id desc", [name])
        discuss_number = await discuss_number.fetchall()

        if not discuss_number:
            discuss_id = '1'
        else:
            discuss_id = str(int(discuss_number[0][0]) + 1)

        await db.execute("insert into dis (doc, title, id, state, date, agree) values (?, ?, ?, 'normal', ?, '0')", [name, discuss_title, discuss_id, await date_time()])
        await db.execute("insert into dis_log (id, data, date, ip, block, code, doc) values (?, ?, ?, ?, '0', ?, ?)", ['1', discuss_data, await date_time(), await user_name(request), discuss_id, name])
        await db.commit()

        return response.redirect("/discuss/" + name + '/' + discuss_id)

    return jinja.render("index.html", request, wiki_set = await wiki_set(request, name),
        data = data + '''
            <form method="post">
                <input type="text" placeholder="토론 제목" class="wiki_textbox" name="wiki_discuss_textbox_1">
                <hr class="wiki_hr">
                <textarea placeholder="토론 내용" class="wiki_textarea" name="wiki_discuss_textarea_1"></textarea>
                <hr class="wiki_hr">
                <button type="submit" class="wiki_button" name="wiki_discuss_button_1">확인</button>
            </form>
        ''',
        title = name,
        sub = '토론',
        menu = [['w/' + name, '문서']]
    )

@app.route("/discuss/<name:string>/<num:int>", methods=['POST', 'GET'])
async def wiki_discuss_thread(request, name, num):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')
    
    data = ''
    thread_list = await db.execute("select id, data, date, ip, block, top from dis_log where code = ? and doc = ?", [num, name])
    thread_list = await thread_list.fetchall()

    if not thread_list:
        return response.redirect("/error/") # 오류 구현 필요

    for thread_data in thread_list:
        if thread_data[3] != '1':
            data += '''
                <div class="wiki_thread_table">
                    <div class="wiki_thread_table_top">
                        ''' + thread_data[0] + ''' ''' + thread_data[3] + ''' ''' + thread_data[4] + '''
                    </div>
                    <div class="wiki_thread_table_bottom">
                        ''' + thread_data[1] + '''
                    </div>
                </div>
            '''
        else:
            data += '''
                <div class="wiki_thread_table">
                    <div class="wiki_thread_table_top">
                        ''' + thread_data[0] + ''' ''' + thread_data[3] + ''' ''' + thread_data[2] + '''
                    </div>
                    <div class="wiki_thread_table_bottom">
                        블라인드된 스레드입니다.
                </div>
            '''

    if request.method == "POST":
        textarea_data = request.form.get('wiki_thread_textarea_1')
        if not textarea_data:
            return response.redirect("/error/")

        discuss_num = await db.execute("select id from dis_log where doc = ? order by id desc", [name])
        discuss_num = await discuss_num.fetchall()
        discuss_num = int(discuss_num[0][0]) + 1
 
        await db.execute("insert into dis_log (id, data, date, ip, block, top, code, doc) values (?, ?, ?, ?, '0', '0', ?, ?)", [discuss_num, textarea_data, await date_time(), await user_name(request), num, name])
        await db.commit()
        return response.redirect("/discuss/" + name + "/" + str(num))

    return jinja.render("index.html", request, wiki_set = await wiki_set(request, name),
        data = data + '''
            <form method="post">
                <textarea class="wiki_textarea" name="wiki_thread_textarea_1"></textarea>
                <hr class="wiki_hr">
                <button type="submit" class="wiki_button" name="wiki_thread_button_1">확인</button>
            </form>
        ''',
        title = name,
        sub = '토론',
        menu = [['w/' + name, '문서']]
    )

@app.route("/discuss/<name:string>/<num:int>/setting", methods=['POST', 'GET'])
async def wiki_discuss_thread_setting(request, name, num):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    discuss_title = await db.execute("select title from dis where doc = ? and id = ?", [name, num])
    discuss_title = await discuss_title.fetchall()

    discuss_doc = await db.execute("select doc from dis where doc = ? and id = ?", [name, num])
    discuss_doc = await discuss_doc.fetchall()

    if request.method == 'POST':
        change_title = request.form.get('wiki_thread_textbox_setting_1', '')
        change_doc = request.form.get('wiki_thread_textbox_setting_2', '')

        if change_title == '' or change_doc == '':
            return response.redirect("/error/")

        if change_title == discuss_title[0][0] and change_doc == discuss_doc[0][0]:
            return response.redirect("setting")
        
        if change_title != discuss_title[0][0]:
            await db.execute("update dis set title = ? where doc = ? and id = ?", [change_title, discuss_doc[0][0], str(num)])
            await db.commit()
            return response.redirect("/discuss/" + discuss_doc[0][0] + "/" + str(num) + "/setting")
        
        if change_doc != discuss_doc[0][0]:
            number_check = await db.execute("select id from dis where doc = ? and id = ?", [change_doc, str(num)])
            number_check = await number_check.fetchall()

            if number_check:
                discuss_renew_num = await db.execute("select id from dis where doc = ? order by id desc", [change_doc])
                discuss_renew_num = await discuss_renew_num.fetchall()
                discuss_renew_num = str(int(discuss_renew_num[0][0]) + 1)

                await db.execute("update dis set doc = ?, id = ? where doc = ? and id = ?", [change_doc, discuss_renew_num, discuss_doc[0][0], str(num)])
                await db.execute("update dis_log set code = ?, doc = ? where code = ? and doc = ?", [discuss_renew_num, change_doc, str(num), discuss_doc[0][0]])
                await db.commit()
                return response.redirect("/discuss/" + change_doc + "/" + discuss_renew_num + "/setting")
            
            else:
                await db.execute("update dis set doc = ? where doc = ?", [change_doc, discuss_doc[0][0]])
                await db.execute("update dis_log set doc = ? where doc = ?", [change_doc, discuss_doc[0][0]])
                await db.commit()
                return response.redirect("/discuss/" + change_doc + "/" + str(num) + "/setting")

    return jinja.render("index.html", request, wiki_set = await wiki_set(request, name),
        data = '''
            <form method="post">
                <input class="wiki_textbox" name="wiki_thread_textbox_setting_1" value="''' + discuss_title[0][0] + '''">
                <hr class="wiki_hr">
                <input class="wiki_textbox" name="wiki_thread_textbox_setting_2" value="''' + discuss_doc[0][0] + '''">
                <hr class="wiki_hr">
                <button type="submit" class="wiki_button" name="wiki_thread_button_setting_1">확인</button>
            </form>
        ''',
        title = name,
        sub = '토론',
        menu = [['w/' + name, '문서']]
    )

@app.route("/recent/changes")
async def wiki_recent_changes(request):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data = ''
    data_get = await db.execute("select id, title, date, ip, send, leng from doc_his order by id + 0 desc limit 30")
    data_get = await data_get.fetchall()
        
    for history_data in data_get:
        if data_get:
            data += '<li>' + history_data[2] + ' ' + history_data[3] + '</li>'

    return jinja.render("index.html", request, wiki_set = await wiki_set(request, 0),
        data = data,
        title = '최근 변경',
        sub = 0,
        menu = 0
    )

@app.route("/recent/discuss")
async def wiki_recent_discuss(request):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data = ''
    data_get = await db.execute("select doc, title, id, date from dis where state = ? order by date desc limit 30", ['normal'])
    data_get = await data_get.fetchall()
        
    for discuss_data in data_get:
        if data_get:
            data += '<li>' + discuss_data[1] + ' ' + discuss_data[3] + '</li>'

    return jinja.render("index.html", request, wiki_set = await wiki_set(request, 0),
        data = data,
        title = '최근 토론',
        sub = 0,
        menu = 0
    )

@app.route("/raw/<name:string>")
async def wiki_raw(request, name):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    args = RequestParameters()
    num = request.args.get('num', '1')

    raw_data = await db.execute("select data from doc_his where id = ? and title = ?", [num, name])
    raw_data = await raw_data.fetchall()

    if raw_data:
        return jinja.render("index.html", request, wiki_set = await wiki_set(request, 0),
            data = '<textarea class="wiki_textarea" id="wiki_textarea_raw_1" readonly>' + raw_data[0][0] + '</textarea>',
            title = name,
            sub = 'r' + num + ' RAW',
            menu = [['w/' + name, '문서']]
        )
    else:
        return response.redirect("/error/")

@app.route("/diff/<name:string>")
async def wiki_diff(request, name):
    async with aiofiles.open('data/setting.json', encoding = 'utf8') as f:
        setting_data = json.loads(await f.read())
        db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    args = RequestParameters()
    num1 = request.args.get('first', '1')
    num2 = request.args.get('second', '2')

    data_get = await db.execute("")

## API
## 문서 내용, 문서 RAW, 토론 내용, 최근 변경, 최근 토론, 이미지

if __name__ == "__main__":
  app.run(debug=False, access_log=False, host=setting_data['host'], port=setting_data['port'])
