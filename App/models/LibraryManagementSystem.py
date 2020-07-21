from App.models.Base import BaseModel,db
from werkzeug.security import generate_password_hash,check_password_hash


class User(BaseModel):
    name = db.Column(db.String(16),nullable=False)
    #权限由0~2组成数字越小权限越大
    authority = db.Column(db.Integer,default='1',nullable=False)
    _a_passwd = db.Column(db.String(256),nullable=False)
    @property
    def a_passwd(self):
        raise Exception("Error Action: Password can't be access")
    @a_passwd.setter
    def a_passwd(self,value):
        self._a_passwd = generate_password_hash(value)
    def check_password(self,password):
        return check_password_hash(self._a_passwd,password)

class Books(BaseModel):
    book_name = db.Column(db.String(256),nullable=False,unique=True)
    Author = db.Column(db.String(256),nullable=False)
    publishing_house = db.Column(db.String(256),nullable=False)
    #中国图书馆分类法
    book_classification = db.Column(db.String(10),db.ForeignKey('chinese_library_classification_base.id'))
    all_quantity = db.Column(db.Integer)
    now_quantity = db.Column(db.Integer)


class Book_borrow(BaseModel):
    book_id = db.Column(db.Integer,db.ForeignKey('books.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

class Chinese_library_classification_base(BaseModel):
    base_type = db.Column(db.String(256),nullable=False,unique=True)
    id = db.Column(db.String(2),primary_key=True)
