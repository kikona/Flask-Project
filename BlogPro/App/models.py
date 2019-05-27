from App.exts import db


class BaseDB():


    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# 模型 => 类
class Kind(db.Model, BaseDB):
    __tablename__ = 'kind'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), unique=True)
    articles = db.relationship('Article', backref='my_kind', lazy=True)

class Article(db.Model, BaseDB):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), unique=True)
    content = db.Column(db.TEXT)
    imags = db.Column(db.Integer)
    kindid = db.Column(db.Integer, db.ForeignKey(Kind.id))


class User(db.Model, BaseDB):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True)
    passwd = db.Column(db.String(200))


class UserToken(db.Model, BaseDB):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(200), unique=True, nullable=False)
    out_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



