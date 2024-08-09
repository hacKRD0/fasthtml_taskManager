from fasthtml.common import *

db = database('data/dashboard.db')
tasks, users = db.t.tasks, db.t.users
print("Users list: ", users())
print("tasks list: ", tasks())
if tasks not in db.t:
    tasks.create(id=int, title=str, status=int, due_date=str, created_at=str, pk='id')
if users not in db.t:
    users.create(name=str, role=str, pwd=str, pk='name')
User, Task = users.dataclass(), tasks.dataclass()

@dataclass
class Login: name:str; pwd:str

@dataclass
class Register: name:str; pwd:str

login_redir = RedirectResponse('/login', status_code=303)
register_redir = RedirectResponse('/register', status_code=303)

def before(req, sess):
    auth = req.scope['auth'] = sess.get('auth', None)
    if not auth: return login_redir
    tasks.xtra(name=auth)

bware = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', '/login', '/register', '/users'])

def _not_found(req, exc): return Titled('Oh no!', Div('We could not find that page :('))

app, rt = fast_app(live=true, debug=true, before=bware, exception_handlers={404: _not_found})

@rt('/')
def get(req, auth):
    title = f"{auth}'s task management"
    top = Grid(H1(title), Div(A('Logout', href='/logout'), style='text-align: right'))
    # column1 = Form(*tasks())
    new_inp = Input(id="new-title", name="title", placeholder="New Task")
    add = Form(Group(new_inp, Button("Add")), hx_post="/", target_id='tasks-not-started-list', hx_swap="afterbegin")
    card = Card(Ul(tasks(), id='task-list'), header=add)
    return Titled(top), Main(card)

@rt('/')
async def post(task: Task):
    new_inp = Input(id="new-title", name="title", placeholder="New Task")
    task.status = 0
    return tasks.insert(task), new_inp

@rt('/users')
async def get():
    frm = Form(users(),
               id='users-list', cls='sortable', hx_post="/reorder", hx_trigger="end")
    card = Card(Ul(frm), header=add, footer=Div(id='users'))
    return Container(card)


@rt('/login')
def get():
    frm = Form(
        Input(id='name', placeholder='Username'),
        Input(id='pwd', type='password', placeholder='Password'),
        Button('Login'),
        action='/login', method='post'
    )

    return Titled('Login', frm, A('Not Registered? Sign Up Here!', href='/register'))

@rt('/register')
def get():
    frm = Form(
        Input(id='name', placeholder='Username'),
        Input(id='pwd', type='password', placeholder='Password'),
        Button('Register'),
        action='/register', method='post'
    )

    return Titled('Register', frm)

@rt('/login')
def post(login: Login, sess):
    if not login.name or not login.pwd:
        return login_redir
    
    try: u = users[login.name]
    except NotFoundError: return register_redir

    if not compare_digest(u.pwd.decode('utf-8'), login.pwd): return login_redir

    sess['auth'] = u.name 

    return RedirectResponse('/', status_code=303)

@app.get("/logout")
def logout(sess):
    del sess['auth']
    return login_redir

@rt('/register')
async def post(register: Register, sess):
    if not register.name or not register.pwd: return register_redir

    newUser = User(name=register.name, pwd=register.pwd.encode('utf-8'))

    try: users.insert(newUser)
    except Exception as e: 
        print ("Excpetion: ", e)
        return register_redir 



    return RedirectResponse('/', status_code=303)


serve()