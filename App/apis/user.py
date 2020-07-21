from flask_restful import Resource, abort, fields, marshal, reqparse, request
from App.models.LibraryManagementSystem import User
import uuid
from App.extension import cache
from flask import redirect,url_for

parser_base = reqparse.RequestParser()
parser_base.add_argument('password', type=str,
                         required=True, help=" Password cannot be blank!")
parser_base.add_argument('name', type=str, required=True,
                         help=" Password cannot be blank!")
parser_base.add_argument('authority')

parser_register = parser_base.copy()

parser_login = parser_base.copy()


parser_change = reqparse.RequestParser()
# parser_change.add_argument('change_password', type=str,
#                            required=True, help=" change_password cannot be blank!")
parser_change.add_argument('password', type=str,
                         required=True, help=" Password cannot be blank!")
parser_change.add_argument('name', type=str)



parser_authority = reqparse.RequestParser()
parser_authority.add_argument('name', type=str, required=True,
                         help=" Password cannot be blank!")
parser_authority.add_argument('authority', type=int,
                              required=True, help=" Password cannot be blank!")


resource_fields = {
    "data": {'name': fields.String,
             "password": fields.String
             },
    "status": fields.Integer

}

class First_start(Resource):
    def get(self):
        user = User.query.filter(User.name == "root").first()
        if user is None:
            user = User()
            user.name = "root"
            user.a_passwd = "123456"
            user.authority= 0
            user.save()
            # return redirect(url_for("static",filename="login.html"))
            return "ok"
        # return redirect(url_for("static",filename="login.html"))
        return "已经存在root用户"

class UserRegistered(Resource):
    # 注册用户
    def put(self):
        args = parser_register.parse_args()
        name = args.get("name")
        password = args.get("password")
        token = request.headers.get('token')
        token_name = cache.get(token)
        if token_name is None:
            if name == '' and password == '':
                abort(400, status=400, msg="用户名密码不能为空")
            if User.query.filter(User.name == name).first() is not None:
                abort(400, status=400, msg="已存在相同用户名")
            user = User()
            user.name = name
            user.a_passwd = password
            if not user.save():
                abort(400, status=400, msg="创建失败")
            data = {
                "name": name,
                "status": 201,
                "password": password
            }
            return marshal(data, resource_fields), 201
        else:
            user = User.query.filter(User.name == token_name).first()
            if user.authority != 0:
                abort(400, msg="你没有这个权限，请不要继续尝试。")
            if name == '' and password == '':
                abort(400, status=400, msg="用户名密码不能为空")
            if User.query.filter(User.name == name).first() is not None:
                abort(400, status=400, msg="已存在相同用户名")
            user = User()
            user.name = name
            user.a_passwd = password
            if args.get("authority") != '' and args.get("authority") is not None:
                    user.authority = args.get("authority")
            if not user.save():
                abort(400, status=400, msg="创建失败")
            data = {
                "name": name,
                "status": 201,
                "password": password,
                "authority":authority
            }
            return marshal(data, resource_fields), 201

    # 修改用户密码可由管理员修改也可由用户修改
    def post(self):
        args = parser_change.parse_args()
        name = args.get("name")
        password = args.get("password")
        if password == '':
            abort(400, status=400, msg="密码不能为空")
        token = request.headers.get('token')
        if token == '' or token is None:
            abort(400, msg="token is not null")
        token_name = cache.get(token)
        if token_name is None:
            abort(404, msg="token is invalid")
        if name == '' or name is None:
            name = token_name
        else:
            if name != token_name:
                user = User.query.filter(User.name == token_name).first()
                if user.authority != 0:
                    abort(400, msg="你没有修改其他用户密码的权限")
        user = User.query.filter(User.name == name).first()
        user.a_passwd = password
        if not user.upgrade():
            abort(400, status=400, msg="修改失败")
        data = {
            "name": user.name,
            "status": 200,
            "password": password
        }
        return marshal(data, resource_fields)


class UserLogin(Resource):
    #登入操作
    def post(self):
        args = parser_login.parse_args()
        name = args.get("name")
        password = args.get("password")
        if name == '' and password == '':
            abort(400, status=400, msg="用户名密码不能为空")
        user = User.query.filter(User.name == name).first()
        if user is None:
            abort(404, status=404, msg="用户不存在")
        if not user.check_password(password):
            abort(401, status=401, msg="密码错误")
        token = uuid.uuid4().hex
        cache.set(token, user.name, timeout=60*60*24)
        data = {
            "msg": "success",
            "status": 200,
            "token": token,
            "authority": user.authority
        }
        return data


class Authority(Resource):
    #修改用户权限只有管理员有权限修改
    def post(self):
        args = parser_authority.parse_args()
        authority = args.get("authority")
        token = request.headers.get('token')
        username= args.get("name")
        if token == '' or token is None:
            abort(400, msg="token is not null")
        name = cache.get(token)
        if name is None:
            abort(404, msg="token is invalid")

        if not authority < 3:
            abort(400, msg="authority is too big")
        user = User.query.filter(User.name == username).first()
        user.authority = authority
        if not user.upgrade():
            abort(400, status=400, msg="修改失败")

        data = {
            "msg": "success",
            "authority": authority
        }
        return data
    #获取当前用户权限
    def get(self):
        token = request.headers.get('token')
        if token == '' or token is None:
            abort(400, msg="token is not null")
        name = cache.get(token)
        if name is None:
            abort(404, msg="token is invalid")
        user = User.query.filter(User.name == name).first()
        data = {
            "msg": "success",
            "authority": user.authority,
            "name": user.name
        }
        return data

#获取用户及权限列表只有管理员才能获取
class UserList(Resource):
    def get(self):
        token = request.headers.get('token')
        if token == '' or token is None:
            abort(400, msg="token is not null")
        name = cache.get(token)
        if name is None:
            abort(404, msg="token is invalid")
        user = User.query.filter(User.name == name).first()
        if user.authority != 0:
            abort(400, msg="你没有这个权限，请不要继续尝试。")
        users = User.query.filter(User.authority > 0).all()
        name = []
        authority = []
        for user in users:
            name.append(user.name)
            authority.append(user.authority)
        data = {
            "user": dict(zip(name, authority))
        }
        return data
