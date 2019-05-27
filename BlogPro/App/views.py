import hashlib
import random
import uuid

from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, make_response
from App.models import *
from tools.forms import LoginForm, RegisterForm
from tools.functions import login_required, check_all_articles

blue = Blueprint('blue', __name__)


data = {}

@blue.route('/')
@check_all_articles
def index():
    return render_template('web/index.html', data=request.data)


@blue.route('/kinddetail/<int:kid>/')
@check_all_articles
def kind_detail(kid):

    kinds = Kind.query.all()
    for kind in kinds:
        if kid == kind.id:
            articles = Article.query.filter_by(kindid=kid)
            request.data['articles'] = articles
    return render_template('web/index.html', data=request.data)


@blue.route('/articledetail/<int:aid>/')
@check_all_articles
def article_detail(aid):

    arti = Article.query.get(aid)
    return render_template('web/art_detail.html', arti=arti, data=request.data)


@blue.route('/list/')
@check_all_articles
def list():
    page = int(request.args.get('page', 1))
    num = int(request.args.get('num', 5))

    articles = Article.query.offset((page-1)*num)
    request.data['articles'] = articles

    p = Article.query.paginate(page, num, False)
    article_list = p.items

    return render_template('web/list.html', p=p, article_list=article_list, data=request.data)

@blue.route('/about/')
@check_all_articles
def about():
    return render_template('web/about.html', data=request.data)




# md5加密
def md5_passwd(pwd):
    m = hashlib.md5()
    m.update(pwd.encode())
    return m.hexdigest()

# 登录
@blue.route('/login/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        form = LoginForm()
        status, error = form.check(request)

        if status:
            username = request.form.get('username')
            userpwd = request.form.get('userpwd')
            # 把输入的密码加密，和数据库的加密密码对比
            userpwd = md5_passwd(userpwd)
            users = User.query.filter_by(name=username, passwd=userpwd).first()

            if not users:
                error['massage'] = '用户名或密码错误'
                return render_template('admin/login.html', error=error)


            # cookie 中保存 token 信息，而不是用户信息
            # uuid 是一个唯一的数据
            token = uuid.uuid4().hex
            session['token'] = token

            print(session['token'])
            # res.set_cookie('user', '123')

            # 单点登录，数据库存储 user 的 token，保证每个用户不管登录几次都只有一天信息
            old_user_token = UserToken.query.filter_by(user_id=users.id).first()
            if old_user_token:
                # 如果用户已经有 token 信息，就更新信息和时间
                old_user_token.token = token
                old_user_token.out_time = datetime.now() + timedelta(days=1)
                old_user_token.save()
            # 如果是首次登录，还没有 token 信息，就创建一个
            else:
                user_token = UserToken()
                user_token.user_id = users.id
                user_token.token = token
                user_token.out_time = datetime.now() + timedelta(days=1)
                user_token.save()
            return redirect(url_for('blue.admin_index'))

        return render_template('admin/login.html', error=error)

    return render_template('admin/login.html')


# 注册
@blue.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form = RegisterForm()
        status, error = form.check(request)

        if status:
            # 如果通过格式验证，就创建用户
            user = User()
            user.name = request.form.get('username')
            # 密码加密保存
            passwd = request.form.get('userpwd')
            user.passwd = md5_passwd(passwd)
            user.save()

            return redirect(url_for('blue.admin_login'))

        return render_template('admin/register.html', error=error)

    return render_template('admin/register.html')


# 后台首页
@blue.route('/admin/')
@login_required
def admin_index():

    username = request.username

    page = int(request.args.get('page', 1))
    num = int(request.args.get('num', 5))

    articles = Article.query.offset((page - 1) * num)
    data['articles'] = articles

    p = Article.query.paginate(page, num, False)
    count = Article.query.count()

    return render_template('admin/article.html', username=username, count=count,p=p, data=data)



@blue.route('/loginout/')
def admin_loginout():

    session.pop('userid')
    return redirect(url_for('blue.admin_login'))


@blue.route('/addarticle/')
@login_required
def add_article():

    username = request.username

    kinds = Kind.query.order_by('id')
    num = Kind.query.group_by('id').count()
    return render_template('admin/add-article.html', username=username, kinds=kinds, num=num)



# 发布文章
@blue.route('/createarticle/', methods=['GET', 'POST'])
@login_required
def create_article():

    title = request.form.get('title')
    content = str(request.form.get('content'))[3:-4]
    kid = request.form.get('category')

    article = Article()
    article.title = title
    article.content = content
    article.kindid = kid

    image = random.randint(1,9)
    print(image)
    article.imags = image

    try:
        db.session.add(article)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.flush()
        print("添加失败")

    res = redirect(url_for('blue.admin_index'))
    return res



# 修改文章
@blue.route('/changearticle/', methods=['GET', 'POST'])
@login_required
def change():

    username = request.username

    n_id = request.args.get('n_id')
    arti = Article.query.get(n_id)

    kinds = Kind.query.order_by('id')
    num = Kind.query.group_by('id').count()

    return render_template('admin/update-article.html', username=username, arti=arti, kinds=kinds, num=num)



@blue.route('/updatearticle/', methods=['GET', 'POST'])
@login_required
def update_article():
    title = request.form.get('title')
    content = str(request.form.get('content'))[3:-4]
    kid = request.form.get('category')

    n_id = request.args.get('a_id')

    article = Article.query.get(n_id)
    article.title = title
    article.content = content
    article.kindid = kid

    try:
        db.session.add(article)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.flush()
        print("修改失败")

    res = redirect(url_for('blue.admin_index'))
    return res


@blue.route('/deletearticle/', methods=['GET', 'POST'])
@login_required
def delete():

    n_id = request.args.get('a_id')
    article = Article.query.get(n_id)

    try:
        db.session.delete(article)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.flush()
        print("删除文章失败")

    res = redirect(url_for('blue.admin_index'))
    return res



@blue.route('/category/',endpoint='category_index')
@login_required
def category_index():
    username = request.username
    n = Kind.query.group_by('id').count()
    kind = Kind.query.order_by('id')

    # 统计每个类的数量
    num_list = []
    for k in kind:
        num = Article.query.filter_by(kindid=k.id).count()
        name = k.name
        num_list.append((k.id, name, num))
    return render_template('admin/category.html', num_list=num_list, n=n, username=username)



@blue.route('/addcategory/', methods=['GET', 'POST'])
@login_required
def add_category():
    name = request.form.get('name')
    kind = Kind()
    kind.name = name

    try:
        db.session.add(kind)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.flush()
        print("添加kind失败")

    res = redirect(url_for('blue.category_index'))
    return res


@blue.route('/updatecategory/', methods=['GET', 'POST'])
@login_required
def update_category():

    username = request.username

    kid = int(request.args.get('kid'))
    kind = Kind.query.get(kid)
    return render_template('admin/update-category.html', kind=kind, username=username)


@blue.route('/changecategory/', methods=['GET', 'POST'])
@login_required
def change_category():
    kid = request.args.get('kid')
    kind = Kind.query.get(kid)
    kind.name = request.form.get('name')

    try:
        db.session.add(kind)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.flush()
        print("修改kind失败")

    res = redirect(url_for('blue.category_index'))
    return res



@blue.route('/deletecategory/', methods=['GET', 'POST'])
@login_required
def delete_category():
    kid = request.args.get('kid')
    kind = Kind.query.get(kid)

    Article.query.filter_by(kindid=kid).delete()

    try:
        db.session.delete(kind)
        db.session.commit()
    except:
        db.session.rollback()
        db.session.flush()
        print("删除kind失败")

    res = redirect(url_for('blue.category_index'))
    return res