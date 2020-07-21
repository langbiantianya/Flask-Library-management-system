from flask_restful import Api
from . import user,book

api = Api()
def init_api(app):
    api.init_app(app)

api.add_resource(user.First_start,'/')
api.add_resource(user.UserRegistered,'/api/user/registered')
api.add_resource(user.UserLogin,'/api/user/login')
api.add_resource(user.Authority,'/api/user/Authority')
api.add_resource(user.UserList,'/api/user/list')
api.add_resource(book.Book,'/api/book')
api.add_resource(book.BookDetailed,'/api/book/<int:page>')
api.add_resource(book.Borrow,'/api/book/borrow')
