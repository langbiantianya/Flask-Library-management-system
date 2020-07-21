from App.models.LibraryManagementSystem import User
def first_start():
    user = User.query.filter(User.name == "root").first()
    if user is None:
        user = User()
        user.name = "root"
        user.a_passwd = "123456"
        user.authority= 0
        user.save()