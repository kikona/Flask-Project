import re

# 校验功能
from App.models import User


class BaseForm():


    def check(self, requsest):
        # 请求的数据都在 request 中
        # status 保存请求状态，error保存错误信息
        status = True
        error = {}

        for key, value in self.__dict__.items():
            post_value = requsest.form.get(key)
            # 校验
            if not re.match(value, post_value):
                status = False
                error['massage'] = '用户名或密码错误'
        return status, error


# 用于验证登录
class LoginForm(BaseForm):


    def __init__(self):
        # 账号不低于1位，不超过10位，只能是字母
        self.username = '[a-zA-Z]{2,10}'
        # 密码至少6位，不超过10位，可以是字母和数字
        self.userpwd = '[0-9a-zA-Z]{6,10}'


# 用于校验注册
class RegisterForm(BaseForm):

    def __init__(self):
        self.username = '[a-zA-Z]{2,10}'
        # 密码
        self.userpwd = '[0-9a-zA-Z]{6,10}'
        # 确认密码
        self.userpwd2 = '[0-9a-zA-Z]{6,10}'

    def check(self, requsest):
        # 配置接口
        status, error = super().check(requsest)
        # 取输入的用户名
        name = requsest.form.get('username')
        # 在数据库中查找是否有存在的
        user = User.query.filter_by(name=name)
        if user.count() > 0:
            status = False
            error['massage'] = '用户名已存在'

        return status, error

