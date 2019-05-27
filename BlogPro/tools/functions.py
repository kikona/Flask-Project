from functools import wraps
from datetime import datetime

from flask import session, render_template, redirect, url_for, request

from App.models import User, Article, UserToken


def login_required(fn):
    @wraps(fn)  # 避免反向解析出问题，flask里必须加
    def inner(*args, **kwargs):
        # 判断UserToken中是否有对应数据
        token = session.get('token', '')
        user_token = UserToken.query.filter_by(token=token).first()
        if user_token:
            # 有登录信息，查看是否已过期
            if user_token.out_time > datetime.now():
                # 如果没有过期，就返回用户名
                request.username = User.query.get(user_token.user_id).name
                return fn(*args, **kwargs)
        # 未登录
        return redirect(url_for('blue.admin_login'))

    return inner


def check_all_articles(fn):

    @wraps(fn)
    def check(*args, **kwargs):
        articles = Article.query.filter_by(kindid=1)
        # 找出所有分类
        article_kind = Article.query.group_by('kindid')
        # 统计每个类的数量
        num_list = []
        for article in article_kind:
            num = Article.query.filter_by(kindid=article.kindid).count()
            kid = article.kindid
            num_list.append((article.my_kind.name, num, kid))

        request.data = {
            'articles': articles,
            'num_list': num_list
        }
        return fn(*args, **kwargs)

    return check
