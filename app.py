from sanic import Sanic, response, Blueprint
from sanic.request import RequestParameters
from sanic_jinja2 import SanicJinja2
from sanic_session import Session, AIORedisSessionInterface
import aiosqlite
import aioredis
import asyncio
import json
import html
import os
import re

from route.tool.tool import *
from route.mark.namumark import *

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

## 카멜 표기법으로 변경 필요, 오픈나무는 별도의 툴을 통한 호환만 지원하며 구조를 완전히 다르게 변경. (alpha)

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
        setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
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

        with open('data/setting.json', 'w', encoding = 'utf8') as f:
            f.write('{ "db_name" : "' + setting_json[1] + '", "db_type" : "' + setting_json[0] + '", "host" : "' + setting_json[2] + '", "port" : "' + setting_json[3] + '" }')

    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
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
        db_create['dis_log'] = ['id', 'data', 'date', 'ip', 'block', 'top', 'code']
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
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data_get = await db.execute("select data from wiki_set where name = ?", ['frontpage'])
    data_get = await data_get.fetchall()

    if data_get:
        return response.redirect('/w/' + data_get[0][0])
    else:
        return response.redirect('/w/FrontPage')

@app.route("/w/<name:string>")
async def wiki_read(request, name):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')
        
    data = await db.execute("select data from doc where title = ?", [name])
    data = await data.fetchall()

    if data:    
        return jinja.render("index.html", request, wiki_set = await wiki_set(name),
            data = await namumark(data[0][0]),
            title = name,
            sub = 0,
            menu = [['edit/' + name, '편집'], ['discuss/' + name, '토론'], ['backlink/' + name, '역링크'], ['history/' + name, '역사'], ['acl/' + name, 'ACL']]
        )
    else:
        return jinja.render("index.html", request, wiki_set = await wiki_set(name),
            data = "해당 문서를 찾을 수 없습니다.", 
            title = name,
            sub = 0,
            menu = [['edit/' + name, '편집'], ['discuss/' + name, '토론'], ['backlink/' + name, '역링크'], ['history/' + name, '역사'], ['acl/' + name, 'ACL']]
        )
        
@app.route("/edit/<name:string>", methods=['POST', 'GET'])
async def wiki_edit(request, name):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data_get = await db.execute("select data from doc where title = ? ", [name])
    data_get = await data_get.fetchall()
    
    data = ""

    if data_get:
        data = data_get[0][0]

    if request.method == 'POST':
        data = request.form.get('wiki_textarea_edit_1', '')
        send = request.form.get('wiki_textbox_edit_1', '')
        
        if data_get:
            if data_get[0][0] == data:
                return response.redirect("/w/" + name)
            
            else:
                data = re.sub('\n', '<br>', data)
                await db.execute("update doc set data = ? where title = ?", [data, name])
                await db.commit()
                await history_add(name, data, await date_time(), '0', send, '0')
                return response.redirect("/w/" + name)
                
        else:
            data = re.sub('\n', '<br>', data)
            await db.execute("insert into doc (title, data) values (?, ?)", [name, data])
            await db.commit()
            await history_add(name, data, await date_time(), '0', send, '0')
            return response.redirect("/w/" + name)
            
    return jinja.render("index.html", request, wiki_set = await wiki_set(name),
            data = '''
                <form method="post">
                    <textarea rows="25" class="wiki_textarea" name="wiki_textarea_edit_1">''' + html.escape(re.sub('<br>', '\n', data)) + '''</textarea>
                    <input type="text" placeholder="요약" class="wiki_textbox" name="wiki_textbox_edit_1">
                    <button type="submit" class="wiki_button" name="wiki_button_edit_1">저장</button>
                </form>
            ''',
            title = name,
            sub = '편집',
            menu = [['delete/' + name, '삭제'], ['move/' + name, '이동'], ['w/' + name, '문서']]
        )
        
@app.route("/history/<name:string>")
async def wiki_history(request, name):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')
    
    data = ''
    data_get = await db.execute("select id, title, date, ip, send, leng from doc_his where title = ? order by id + 0 desc limit 30", [name])
    data_get = await data_get.fetchall()

    # if request.method == 'POST': 비교 기능 등
        
    if data_get:
        data += '<li>' + data_get[0][2] + ' ' + data_get[0][3] + '</li>'

    return jinja.render("index.html", request, wiki_set = await wiki_set(name),
            data = data,
            title = name,
            sub = '역사',
            menu = [['w/' + name, '문서']]
    )

@app.route("/delete/<name:string>", methods=['POST', 'GET'])
async def wiki_delete(request, name):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data_get = await db.execute("select data from doc where title = ? ", [name])
    data_get = await data_get.fetchall()

    if request.method == 'POST':
            send = request.form.get('wiki_textbox_delete_1', '')
            await db.execute("delete from doc where title = ?", [name])
            await db.commit()
            await history_add(name, '', await date_time(), '0', send, '0')
            return response.redirect("/w/" + name)
            
    if data_get:
        return jinja.render("index.html", request, wiki_set = await wiki_set(name),
            data = '''
                <form method="post">
                    <input type="text" placeholder="요약" class="wiki_textbox" name="wiki_textbox_delete_1">
                    <button type="submit" class="wiki_button" name="wiki_button_delete_1">확인</button>
                </form>
            ''',
            title = name,
            sub = '삭제',
            menu = [['w/' + name, '문서']]
        )
    else:
        return response.redirect("/error/") # 오류 페이지 구현 필요

setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())

@app.route("/move/<name:string>", methods=['POST', 'GET'])
async def wiki_move(request, name):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data_get = await db.execute("select data from doc where title = ? ", [name])
    data_get = await data_get.fetchall()

    if request.method == 'POST':
            change_name = request.form.get('wiki_textbox_move_1', '')
            send = request.form.get('wiki_textbox_move_2', '')
            await db.execute("update doc set title = ? where title = ?", [change_name, name])
            await db.execute("update doc_his set title = ? where title = ?", [change_name, name])
            await db.commit()
            await history_add(change_name, '', await date_time(), '0', send, '0')
            return response.redirect("/w/" + change_name)
            
    if data_get:
        return jinja.render("index.html", request, wiki_set = await wiki_set(name),
            data = '''
                <form method="post">
                    <input type="text" value="''' + name + '''" class="wiki_textbox" name="wiki_textbox_move_1">
                    <input type="text" placeholder="요약" class="wiki_textbox" name="wiki_textbox_move_2">
                    <button type="submit" class="wiki_button" name="wiki_button_move_1">확인</button>
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
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    args = RequestParameters()
    num = request.args.get('num', '1')

    data_get = await db.execute("select data from doc_his where id = ?", [num])
    data_get = await data_get.fetchall()
    data_get = data_get[0][0]

    if request.method == 'POST':
        send = request.form.get('wiki_textbox_revert_1', '')
        data_get = re.sub('\n', '<br>', data_get)
        await db.execute("update doc set data = ? where title = ?", [data_get, name])
        await db.commit()
        await history_add(name, data_get, await date_time(), '0', send, '0')
        return response.redirect("/w/" + name)

    if data_get:
        return jinja.render("index.html", request, wiki_set = await wiki_set(name),
            data = '''
                <form method="post">
                    <textarea rows="25" class="wiki_textarea" name="wiki_textarea_revert_1" readonly>''' + data_get + '''</textarea>
                    <input type="text" placeholder="요약" class="wiki_textbox" name="wiki_textbox_revert_2">
                    <button type="submit" class="wiki_button" name="wiki_button_revert_1">확인</button>
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
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    if request.ctx.session.get('id') == 1:
        return response.redirect('/')

    if request.method == 'POST':
        signup_id = request.form.get('wiki_textbox_signup_1', '')
        signup_password_1 = request.form.get('wiki_textbox_signup_2', '')
        signup_password_2 = request.form.get('wiki_textbox_signup_2', '')

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
        await db.execute("insert into mbr (id, pw, acl, date, email) values (?, ?, ?, ?, ?)", [signup_id, encode_password, 'member', await date_time(), '']) # 추후 권한 기본 설정과 이메일 구현되면 수정 필요, mbr_log 기록 필요.
        await db.commit()
        return response.redirect("/member/login")

    return jinja.render("index.html", request, wiki_set = await wiki_set(0),
        data = '''
            <form method="post">
                <input type="text" placeholder="아이디" class="wiki_textbox" name="wiki_textbox_signup_1">
                <input type="password" placeholder="비밀번호" class="wiki_textbox" name="wiki_textbox_signup_2">
                <input type="password" placeholder="비밀번호 확인" class="wiki_textbox" name="wiki_textbox_signup_3">
                <button type="submit" class="wiki_button" name="wiki_button_signup_1">확인</button>
            </form>
        ''',
        title = '계정 만들기',
        sub = 0,
        menu = 0
    )

@app.route("/member/login", methods=['POST', 'GET'])
async def wiki_login(request):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    if request.ctx.session.get('id') == 1:
        return response.redirect('/')

    if request.method == 'POST':
        wiki_id = request.form.get('wiki_textbox_login_1', '')
        wiki_password = request.form.get('wiki_textbox_login_2', '')

        wiki_pass_check = await VerifyAuth(wiki_id, wiki_password, 0)
        if wiki_pass_check == 1:
            request.ctx.session['id'] = 1
            return response.redirect("/")
        else:
            return response.redirect('/error/') # 오류 페이지 구현 필요

    return jinja.render("index.html", request, wiki_set = await wiki_set(0),
        data = '''
            <form method="post">
                <input type="text" placeholder="아이디" class="wiki_textbox" name="wiki_textbox_login_1">
                <input type="password" placeholder="비밀번호" class="wiki_textbox" name="wiki_textbox_login_2">
                <button type="submit" class="wiki_button" name="wiki_button_login_1">확인</button>
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
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')

    data = ''
    discuss_get = await db.execute("select title, id, state, date, agree from dis where doc = ?", [name])
    discuss_get = await discuss_get.fetchall()

    for discuss in discuss_get:
        data += '<li>' + discuss[0] + discuss[1] + discuss[2] + discuss[3] + discuss[4] + '</li>'

    if request.method == "POST":
        discuss_title = request.form.get('wiki_textbox_discuss_1', '')
        discuss_data = request.form.get('wiki_textarea_discuss_1', '')
        
        title_get = await db.execute("select title from dis where title = ?", [discuss_title])
        title_get = await title_get.fetchall()

        if discuss_title or discuss_data == '':
            return response.redirect("/error/") # 오류 구현 필요

        if title_get:
            return response.redirect("/error/") # 오류 구현 필요

        

    return jinja.render("index.html", request, wiki_set = await wiki_set(name),
        data = data + '''
            <form method="post">
                <input type="text" class="wiki_textbox" name="wiki_textbox_discuss_1">
                <textarea class="wiki_textarea" name="wiki_textarea_discuss_1"></textarea>
                <button type="submit" class="wiki_button" name="wiki_button_discuss_1">
            </form>
        ''',
        title = name,
        sub = '토론',
        menu = [['w/' + name, '문서']]
    )

## Blind = ?blind=num
## delete = ?delete=1
## change_name = textbox
## change_doc = textbox

@app.route("/discuss/<name:string>/<num:int>")
async def wiki_discuss_thread(request, name, num):
    setting_data = json.loads(open('data/setting.json', encoding = 'utf8').read())
    db = await aiosqlite.connect(setting_data['db_name'] + '.db')
    
    data = ''
    thread_list = await db.execute("select data, date, ip, block, top, code from dis_log where id = ?", [num])
    thread_list = await thread_list.fetchall()

    if not thread_list:
        return response.redirect("/error/") # 오류 구현 필요

    for thread_data in thread_list:
        if thread_data[3] != '1':
            data += '''
                <div class="wiki_thread_table">
                    <div class="wiki_thread_table_top">
                        ''' + thread_data[5] + ''' ''' + thread_data[2] + ''' ''' + thread_data[1] + '''
                    </div>
                    <div class="wiki_thread_table_bottom">
                        ''' + thread_data[0] + '''
                </div>
            '''
        else:
            data += '''
                <div class="wiki_thread_table">
                    <div class="wiki_thread_table_top">
                        ''' + thread_data[5] + ''' ''' + thread_data[2] + ''' ''' + thread_data[1] + '''
                    </div>
                    <div class="wiki_thread_table_bottom">
                        블라인드된 스레드입니다.
                </div>
            '''

    if request.method == "POST":
        return 0

    return jinja.render("index.html", request, wiki_set = await wiki_set(name),
        data = data + '''
            <form method="post">
                <textarea class="wiki_textarea" name="wiki_textarea_thread_1"></textarea>
                <button type="submit" class="wiki_button" name="wiki_button_thread_1">
            </form>
        ''',
        title = name,
        sub = '토론',
        menu = [['w/' + name, '문서']]
    )

## API
## 문서 내용, 문서 RAW, 토론 내용, 최근 변경, 최근 토론, 이미지

if __name__ == "__main__":
  app.run(debug=False, access_log=False, host=setting_data['host'], port=setting_data['port'])
