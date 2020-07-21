 

第一次启动使用get访问 / 会创建一个root账户默认密码123456

所有返回值都是json数据

### 注册新用户使用put请求 /api/user/registered

​	如果携带管理员权限的token请求头可以直接设定用户权限（0最高权限，1只能修改图书，2只能借书还书）

​	请求携带参数

```
name 用户名
password 密码
authority 权限代码（0-2）只有携带权限为零的token才可以指定
```

请求返回值有2种

```json
1管理员替别人注册
请求值
headers 
token:6e74141aff6a42348ed0a8cc9a107509

form
name:chen
password:123456
authority:1

返回值
{
    "data": {
        "name": "chen",
        "password": "123456"
        "authority":1
    },
    "status": 201
}
2普通注册
请求值
form
name:wang
password:123456

返回值
{
    "data": {
        "name": "wang",
        "password": "123456"
    },
    "status": 201
}
```

### 修改密码使用post请求 /api/user/registered

​	如果携带权限为0的token可以指定修改所有用户的密码

```
请求需要的数据
headers token 用户需要登入才能修改密码
name 用户名 普通用户可指定也可以不指定
password 修改后的密码
```

返回值

```json
普通用户
请求值
headers
token

from
password:123456

返回值
{
    "data": {
        "name": "chen",
        "password": "123456"
    },
    "status": 200
}

管理员
请求值
headers 
token

from
name:chen
password:123456

返回值
{
    "data": {
        "name": "chen",
        "password": "123456"
    },
    "status": 200
}
```

### 登入 post请求 /api/user/login

需要的数据

绝大部分接口都需要使用token

token有效期为7天

```
name 用户名
password 密码
```

返回值

```json
{
    "msg": "success",
    "status": 200,
    "token": "b4c1384b087d447ca64b80f3d8fa9624",
    "authority": 0
}
```

### 管理员修改用户权限 post请求 /api/user/Authority

需要的数据

```
from
name 需要修改的用户名
authority 修改后权限（0-2）
headers
token
```

返回值

```json
请求值
headers
token

from
name:chen
authority:1

返回值
{
    "msg": "success",
    "authority": 1
}
```

### 获取所有用户列表get请求/api/user/list

只有管理员有权限获取所有用户列表

请求值

```
headers
token 必须要有管理员权限
```

返回值

```json
{
    "user": {
        "cxk": 1,
        "nmsl": 1,
        "chen": 1,
        "wang": 1
    }
}
1是权限
```

### 添加图书使用put请求/api/book

需要有权限小于2的账户也就是（0-1）

请求值

```
header
token

from
book_name:高等数学(第二版)
Author:蔡徐坤
publishing_house:2年半出版社
book_classification:G（中国图书馆分类法详细自行百度）
book_quantity:10
```

返回值

```json
{
    "data": {
        "book_name": "高等数学(第二版)",
        "Author": "蔡徐坤",
        "publishing_house": "2年半出版社",
        "book_classification": "G",
        "book_quantity": 10
    },
    "status": 201
}
```

### 修改图书数据但是不能修改书名post请求/api/book

请求值

需要有权限小于2的账户也就是（0-1）

```
headers
token 

from
book_name:高等数学(第二版)
Author:蔡徐坤
publishing_house:2年半出版社
book_classification:G
change_quantity:20（减少使用负整数，增加只有正整数）
```

返回值

```json
{
    "data": {
        "book_name": "高等数学(第二版)",
        "Author": "蔡徐坤",
        "publishing_house": "2年半出版社",
        "book_classification": "G",
        "book_quantity": 30
    },
    "status": 200
}
```

### 删除图书使用delete请求/api/book

请求值

需要有权限小于2的账户也就是（0-1）

```
headers
token

from
book_name:高等数学(第二版)
```

返回值

```
{
    "data": {
        "book_name": "高等数学(第二版)",
        "Author": "蔡徐坤",
        "publishing_house": "2年半出版社",
        "book_classification": "G",
        "book_quantity": 30
    },
    "status": 200
}
```

### 获取单本图书数据get请求/api/book

请求值

```
from
book_name:高等数学

或者也可以这样
/api/book?book_name=高等数学
```

返回值

```json
{
    "data": {
        "book_name": "高等数学",
        "Author": "蔡徐坤",
        "publishing_house": "高等教育出版社",
        "book_classification": "文化、科学、教育、体育",
        "book_quantity": 10
    },
    "status": 200
}
```

### 获取一页也就是10条数据get请求/api/book/\<int:page>

请求值

```
/api/book/0 从0开始，0是第一页
/api/book/1
```

返回值

```json
{
    "data": [
        {
            "book_name": "高等数学",
            "Author": "蔡徐坤",
            "publishing_house": "高等教育出版社",
            "book_classification": "G",
            "now_quantity": 9
        },
        {
            "book_name": "偶像练习生",
            "Author": "蔡徐坤",
            "publishing_house": "2年半出版社",
            "book_classification": "G",
            "now_quantity": 10
        }
    ],
    "all_page": 1,
    "msg": "page start zero"
}
```

### 添加借书数据put请求/api/book/borrow

请求数据

```
herders
tooken

from
book_name:高等数学
```

返回值

```json
{
    "name": "chen",
    "book_name": "高等数学"
}
```

### 删除也就是还书delete请求/api/book/borrow

请求数据

```
headers
token

from
book_name:高等数学
```

返回值

```json
{
    "book_name": "高等数学",
    "name": "chen"
}
```

### 查看借书数据混合了管理员和普通用户查询使用get请求/api/book/borrow

查看所有人的借书数据需要管理员账户权限0

请求值

```
headers
token
```

返回值

```json
{
    "data": [
        {
            "chen": "高等数学"
        }
    ],
    "status": 200
}
```

普通用户查看自己借的所有书

请求值

```
headers
token
```

返回值

```json
{
    "name": "chen",
    "book_name": [
        "高等数学"
    ],
    "status": 200
}
```

