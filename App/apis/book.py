from flask_restful import Resource, abort, fields, marshal, reqparse, request
from App.extension import cache
from App.models.LibraryManagementSystem import User, Books, Book_borrow, Chinese_library_classification_base
from flask import redirect, url_for
from App.apis.tool.abuser import permission_validation

parser_base = reqparse.RequestParser()
parser_base.add_argument('book_name', type=str,
                         required=True, help=" book_name cannot be blank!")
# 添加图书部分
parser_Book_add = parser_base.copy()
parser_Book_add.add_argument('Author', type=str,
                             required=True, help=" Author cannot be blank!")
parser_Book_add.add_argument('publishing_house', type=str,
                             required=True, help=" publishing_house cannot be blank!")
parser_Book_add.add_argument('book_classification', type=str,
                             required=True, help=" book_classification cannot be blank!")
parser_Book_add.add_argument('book_quantity', type=int,
                             required=True, help=" book_quantity cannot be blank!")
# 删除图书
parser_Book_delete = parser_base.copy()

# 更新图书信息
parser_Book_upgrade = parser_base.copy()
parser_Book_upgrade.add_argument('Author', type=str)
parser_Book_upgrade.add_argument('publishing_house', type=str)
parser_Book_upgrade.add_argument('book_classification', type=str)
parser_Book_upgrade.add_argument('change_quantity', type=int)
# 获取单独一本图书详细信息
parser_Book_one = parser_base.copy()

# 添加借书数据
parser_Book_borrow = parser_base.copy()

resource_fields = {
    "data": {'book_name': fields.String,
             "Author": fields.String,
             'publishing_house': fields.String,
             'book_classification': fields.String,
             'book_quantity': fields.Integer
             },
    "status": fields.Integer

}


class Book(Resource):
    def put(self):
        args = parser_Book_add.parse_args()
        if permission_validation() > 1:
            abort(400, msg="你没有权限添加图书")
        book_name = args.get("book_name")  # 书名
        Author = args.get("Author")  # 作者
        publishing_house = args.get("publishing_house")  # 出版社
        book_classification = args.get("book_classification")  # 图书类别
        all_quantity = args.get("book_quantity")  # 图书数量
        now_quantity = all_quantity
        if book_name == '' and Author == '' and publishing_house == '' and book_classification == '':
            abort(404, msg="图书信息不能为空")
        books = Books()
        books.book_name = book_name
        books.Author = Author
        books.publishing_house = publishing_house
        chinese_library_classification_base = Chinese_library_classification_base.query.filter(
            Chinese_library_classification_base.id == book_classification).first()
        if chinese_library_classification_base is None:
            abort(404, msg="图书类别不存在")
        books.book_classification = book_classification
        books.all_quantity = all_quantity
        books.now_quantity = now_quantity
        if not books.save():
            abort(400, status=400, msg="创建失败")

        data = {
            'book_name': book_name,
            "Author": Author,
            'publishing_house': publishing_house,
            'book_classification': book_classification,
            'book_quantity': all_quantity,
            "status": 201
        }
        return marshal(data, resource_fields), 201

    def delete(self):
        if permission_validation() > 1:
            abort(400, msg="你没有权限删除图书")
        args = parser_Book_delete.parse_args()
        book_name = args.get("book_name")
        if book_name == '':
            abort(404, msg="书名不能为空")
        books = Books.query.filter(Books.book_name == book_name).first()
        if not books.delete():
            abort(400, status=400, msg="删除失败")

        data = {
            'book_name': books.book_name,
            "Author": books.Author,
            'publishing_house': books.publishing_house,
            'book_classification': books.book_classification,
            'book_quantity': books.all_quantity,
            "status": 200
        }
        return marshal(data, resource_fields)

    def post(self):
        if permission_validation() > 1:
            abort(400, msg="你没有权限更新图书信息")
        args = parser_Book_upgrade.parse_args()
        book_name = args.get("book_name")  # 书名
        if book_name == '':
            abort(404, msg="书名不能为空")
        books = Books.query.filter(Books.book_name == book_name).first()

        Author = args.get("Author")  # 作者
        if Author is not None and Author != '':
            books.Author = Author

        publishing_house = args.get("publishing_house")  # 出版社
        if publishing_house is not None and publishing_house != '':
            books.publishing_house = publishing_house

        book_classification = args.get("book_classification")  # 图书类别
        if book_classification is not None and book_classification != '':
            books.book_classification = book_classification

        change_quantity = args.get("change_quantity")  # 图书数量
        if change_quantity is not None:
            if (books.now_quantity+change_quantity) < 0:
                abort(400, msg="当前图书数量不够减少")
            books.all_quantity = books.all_quantity+change_quantity
            books.now_quantity = books.now_quantity+change_quantity

        if not books.upgrade():
            abort(400, msg='修改失败')
        books = Books.query.filter(Books.book_name == book_name).first()
        data = {
            'book_name': books.book_name,
            "Author": books.Author,
            'publishing_house': books.publishing_house,
            'book_classification': books.book_classification,
            'book_quantity': books.all_quantity,
            "status": 200
        }
        return marshal(data, resource_fields)

    def get(self):
        args = parser_Book_one.parse_args()
        book_name = args.get("book_name")
        if book_name == '':
            abort(404, msg="书名不能为空")
        books = Books.query.filter(Books.book_name == book_name).first()
        chinese_library_classification_base = Chinese_library_classification_base.query.filter(Chinese_library_classification_base.id == books.book_classification).first()
        data = {
            'book_name': books.book_name,
            "Author": books.Author,
            'publishing_house': books.publishing_house,
            'book_classification':chinese_library_classification_base.base_type,
            'book_quantity': books.all_quantity,
            "status": 200
        }
        return marshal(data, resource_fields)


class BookDetailed(Resource):
    def get(self, page):
        length = len(Books.query.all())
        if length % 10 == 0:
            h_page = length/10
        else:
            h_page = length//10+1
        if page is not None:
            if page < h_page:
                s_page = page*10
            else:
                if length < 10:
                    s_page = 0
                else:
                    s_page = int(length-10)
        else:
            s_page = 0
        c_page = 10
        books = Books.query.limit(c_page).offset(s_page).all()
        base_data = []
        for book in books:
            base_data.append({'book_name': book.book_name,
                              'Author': book.Author,
                              'publishing_house': book.publishing_house,
                              'book_classification': book.book_classification,
                              'now_quantity': book.now_quantity})
        data = {
            'data': base_data,
            'all_page': h_page,
            'msg': 'page start zero'
        }
        return data


class Borrow(Resource):
    def put(self):
        token = request.headers.get('token')
        if token == '' or token is None:
            abort(400, msg="token not null")
        name = cache.get(token)
        if name is None or name == '':
            abort(400, msg="token 无效")
        user = User.query.filter(User.name == name).first()
        args = parser_Book_borrow.parse_args()
        book_name = args.get("book_name")
        if book_name == '':
            abort(404, msg="书名 not null")
        books = Books.query.filter(Books.book_name == book_name).first()
        book_borrow = Book_borrow()
        book_borrow.book_id = books.id
        book_borrow.user_id = user.id

        books.now_quantity = books.now_quantity-1

        if not book_borrow.save():
            abort(400, msg="保存失败")

        if not books.upgrade():
            book_borrow = Book_borrow.query.filter(
                Book_borrow.book_id == books.id).first()
            book_borrow.delete()
            abort(400, msg="更新保存失败")
        data = {
            'name': name,
            'book_name': book_name
        }
        return data, 201

    def delete(self):
        token = request.headers.get('token')
        if token == '' or token is None:
            abort(400, msg="token not null")
        name = cache.get(token)
        if name is None or name == '':
            abort(400, msg="token 无效")
        args = parser_Book_borrow.parse_args()
        book_name = args.get("book_name")
        if book_name == '':
            abort(404, msg="书名 not null")
        user = User.query.filter(User.name == name).first()
        books = Books.query.filter(Books.book_name == book_name).first()
        book_borrow = Book_borrow.query.filter(
            Book_borrow.book_id == books.id and Book_borrow.user_id == user.id).first()
        books.now_quantity = books.now_quantity+1
        if book_borrow == None:
            abort(400, msg="你没有权限替别人还书")
        if not book_borrow.delete():
            abort(400, msg='还书异常')
        if not books.upgrade():
            book_borrow.book_id = books.id
            book_borrow.user_id = user.id
            book_borrow.save()
            abort(400, msg='还书异常')
        data = {
            "book_name": book_name,
            "name": name
        }
        return data

    def get(self):
        if permission_validation() < 1:
            book_borrows = Book_borrow.query.all()
            book_ids=[]
            user_ids=[]
            for book_borrow in book_borrows:
                book_ids.append(book_borrow.book_id)
                user_ids.append(book_borrow.user_id)
            base_data=[]
            for (user_id,book_id) in zip(user_ids,book_ids):
                user = User.query.filter(User.id == user_id).first()
                books = Books.query.filter(Books.id == book_id).first()
                base_data.append({user.name:books.book_name})
            data = {
                'data':base_data,
                'status':200
            }
            return data
        else:
            token = request.headers.get('token')
            if token == '' or token is None:
                abort(400, msg="token not null")
            name = cache.get(token)
            if name is None or name == '':
                abort(400, msg="token 无效")
            user = User.query.filter(User.name == name).first()
            book_borrows = Book_borrow.query.filter(
                Book_borrow.user_id == user.id).all()
            book_ids=[]
            for book_borrow in book_borrows:
                book_ids.append(book_borrow.book_id)
            book_names=[]
            for book_id in book_ids:
                books = Books.query.filter(Books.id == book_id).first()
                book_names.append(books.book_name)
            data = {
                "name":name,
                "book_name":book_names,
                'status':200
            }
        return data
