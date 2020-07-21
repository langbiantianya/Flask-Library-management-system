from flask_restful import Resource, abort, fields, marshal, reqparse, request
from App.extension import cache
from App.models.LibraryManagementSystem import User, Books, Book_borrow, Chinese_library_classification_base

def permission_validation():
    token = request.headers.get('token')
    if token == '' or token is None:
        abort(400, msg="token is not null")
    name = cache.get(token)
    if name is None:
        abort(404, msg="token is invalid")
    user = User.query.filter(User.name == name).first()
    return user.authority
    
