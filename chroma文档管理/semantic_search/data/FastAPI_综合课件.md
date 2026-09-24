# Python FastAPI 综合课件

## 📚 课程目标

从 HTTP 基础知识入手，全面掌握 FastAPI 框架的使用，并能够开发基于 FastAPI 的 RESTful 数据 API。

---

# 第一部分：HTTP 基础知识

## 第一章：什么是 HTTP？

### 1.1 HTTP 定义

**HTTP（HyperText Transfer Protocol）超文本传输协议**是一种用于传输超文本（网页）的应用层协议。它是 Web 的基础，定义了客户端（如浏览器）和服务器之间如何通信。

**简单理解：** HTTP 就像是浏览器和服务器之间的"对话规则"。

### 1.2 客户端-服务器模型

```
┌──────────┐                    ┌──────────┐
│  客户端   │  ───── 请求 ─────>  │  服务器   │
│ (浏览器)  │                    │ (FastAPI) │
│          │  <──── 响应 ──────  │          │
└──────────┘                    └──────────┘
```

**工作流程：**

1. 客户端发送 HTTP 请求
2. 服务器处理请求
3. 服务器返回 HTTP 响应

---

## 第二章：HTTP 请求（Request）

### 2.1 HTTP 请求的组成部分

一个完整的 HTTP 请求包含：

#### **1. 请求行（Request Line）**

```
GET /index.html HTTP/1.1
```

- **方法（Method）**: GET
- **路径（Path）**: /index.html
- **协议版本**: HTTP/1.1

#### **2. 请求头（Request Headers）**

```
Host: www.example.com
User-Agent: Mozilla/5.0
Accept: text/html
Content-Type: application/json
Cookie: session_id=abc123
```

#### **3. 空行**

分隔请求头和请求体

#### **4. 请求体（Request Body）**

```json
{
  "username": "zhangsan",
  "password": "123456"
}
```

### 2.2 HTTP 请求方法（重点）

| 方法        | 用途             | 是否有请求体 | 示例场景           |
| ----------- | ---------------- | ------------ | ------------------ |
| **GET**     | 获取资源         | 否           | 查看文章列表、搜索 |
| **POST**    | 创建资源         | 是           | 提交表单、注册用户 |
| **PUT**     | 更新资源（完整） | 是           | 修改用户全部信息   |
| **PATCH**   | 更新资源（部分） | 是           | 修改用户部分信息   |
| **DELETE**  | 删除资源         | 否           | 删除文章           |
| **HEAD**    | 获取资源头信息   | 否           | 检查文件是否存在   |
| **OPTIONS** | 查询支持的方法   | 否           | CORS 预检请求      |

**FastAPI 中最常用：GET、POST、PUT、DELETE**

### 2.3 GET vs POST 详细对比

#### **GET 请求示例**

```
GET /search?keyword=python&page=1 HTTP/1.1
Host: www.example.com
```

**特点：**

- 参数在 URL 中（查询字符串）
- 可以被浏览器缓存
- 可以被收藏为书签
- 参数有长度限制（约 2KB）
- 不安全，参数暴露在 URL 中

#### **POST 请求示例**

```
POST /login HTTP/1.1
Host: www.example.com
Content-Type: application/json

{
  "username": "zhangsan",
  "password": "123456"
}
```

**特点：**

- 参数在请求体中
- 不能被缓存
- 不能被收藏为书签
- 参数无长度限制
- 相对安全（密码等敏感信息）

### 2.4 常见请求头详解

```python
# Host: 指定服务器域名
Host: www.example.com

# User-Agent: 客户端信息（浏览器类型）
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)

# Accept: 客户端接受的内容类型
Accept: text/html, application/json

# Content-Type: 请求体的数据格式
Content-Type: application/json          # JSON 数据
Content-Type: application/x-www-form-urlencoded  # 表单数据
Content-Type: multipart/form-data       # 文件上传

# Cookie: 存储在客户端的数据
Cookie: session_id=abc123; user=zhangsan

# Authorization: 身份验证信息
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 第三章：HTTP 响应（Response）

### 3.1 HTTP 响应的组成部分

#### **1. 状态行（Status Line）**

```
HTTP/1.1 200 OK
```

- **协议版本**: HTTP/1.1
- **状态码**: 200
- **状态描述**: OK

#### **2. 响应头（Response Headers）**

```
Content-Type: application/json; charset=utf-8
Content-Length: 1234
Set-Cookie: session_id=xyz789
Server: uvicorn
```

#### **3. 空行**

#### **4. 响应体（Response Body）**

```json
{
  "message": "你好，世界！"
}
```

### 3.2 HTTP 状态码（重点）

#### **1xx 信息性状态码**

```
100 Continue - 继续请求
```

#### **2xx 成功状态码**

```
200 OK - 请求成功
201 Created - 资源创建成功（POST 常用）
204 No Content - 成功但无返回内容（DELETE 常用）
```

#### **3xx 重定向状态码**

```
301 Moved Permanently - 永久重定向
302 Found - 临时重定向
304 Not Modified - 资源未修改（缓存）
```

#### **4xx 客户端错误**

```
400 Bad Request - 请求语法错误
401 Unauthorized - 未授权（需要登录）
403 Forbidden - 禁止访问（没有权限）
404 Not Found - 资源不存在
405 Method Not Allowed - 请求方法不允许
422 Unprocessable Entity - 参数校验失败（FastAPI 常用）
```

#### **5xx 服务器错误**

```
500 Internal Server Error - 服务器内部错误
502 Bad Gateway - 网关错误
503 Service Unavailable - 服务不可用
```

### 3.3 常见响应头详解

```python
# Content-Type: 响应体的数据格式
Content-Type: text/html; charset=utf-8      # HTML 页面
Content-Type: application/json              # JSON 数据
Content-Type: image/png                     # PNG 图片

# Content-Length: 响应体长度（字节）
Content-Length: 1234

# Set-Cookie: 设置客户端 Cookie
Set-Cookie: session_id=xyz789; Path=/; HttpOnly

# Location: 重定向地址
Location: https://www.example.com/new-page

# Cache-Control: 缓存控制
Cache-Control: no-cache
Cache-Control: max-age=3600

# Server: 服务器信息
Server: uvicorn
```

---

## 第四章：URL 详解

### 4.1 URL 结构

```
https://www.example.com:8080/path/to/page?key1=value1&key2=value2#section
  │       │               │      │            │                      │
协议    域名/主机        端口   路径        查询字符串              片段标识符
```

**各部分说明：**

- **协议（Scheme）**: https（加密）或 http（不加密）
- **域名（Host）**: www.example.com
- **端口（Port）**: 8080（默认 HTTP=80，HTTPS=443）
- **路径（Path）**: /path/to/page
- **查询字符串（Query String）**: ?key1=value1&key2=value2
- **片段（Fragment）**: #section（仅客户端使用）

### 4.2 查询字符串详解

```python
# URL 示例
http://example.com/search?keyword=python&page=2&sort=date

# 解析后的参数
keyword = "python"
page = "2"
sort = "date"

# 特殊字符需要编码
http://example.com/search?keyword=%E4%B8%AD%E6%96%87
# %E4%B8%AD%E6%96%87 是 "中文" 的 URL 编码
```

---

## 第五章：Cookie 和 Session

### 5.1 Cookie

**定义：** Cookie 是服务器发送到客户端并存储在客户端的小段数据。

#### **工作流程**

```
1. 客户端首次请求
   GET /login HTTP/1.1

2. 服务器设置 Cookie
   HTTP/1.1 200 OK
   Set-Cookie: user_id=123

3. 客户端后续请求自动带上 Cookie
   GET /profile HTTP/1.1
   Cookie: user_id=123
```

#### **Cookie 属性**

```python
Set-Cookie: name=value; 
            Domain=example.com;     # 作用域名
            Path=/;                 # 作用路径
            Expires=Wed, 21 Oct 2026 07:28:00 GMT;  # 过期时间
            Max-Age=3600;          # 有效期（秒）
            Secure;                # 仅 HTTPS 传输
            HttpOnly;              # 禁止 JavaScript 访问
            SameSite=Strict        # 跨站请求控制
```

### 5.2 Session

**定义：** Session 是服务器端存储的用户会话数据。

#### **工作流程**

```
1. 用户登录成功
   → 服务器创建 Session（存储在服务器）
   → 返回 Session ID 给客户端（通过 Cookie）

2. 客户端后续请求
   → 自动携带 Session ID（Cookie）
   → 服务器根据 Session ID 查找对应的 Session 数据
```

#### **Cookie vs Session**

| 特性     | Cookie                | Session            |
| -------- | --------------------- | ------------------ |
| 存储位置 | 客户端（浏览器）      | 服务器端           |
| 安全性   | 较低（可被查看/篡改） | 较高               |
| 存储容量 | 小（约 4KB）          | 大（取决于服务器） |
| 有效期   | 可设置长期有效        | 通常关闭浏览器失效 |

---

## 第六章：Content-Type 详解

### 6.1 常见的 Content-Type

#### **1. 表单数据（默认）**

```
Content-Type: application/x-www-form-urlencoded

# 数据格式
username=zhangsan&password=123456
```

#### **2. JSON 数据**

```
Content-Type: application/json

# 数据格式
{
  "username": "zhangsan",
  "password": "123456"
}
```

#### **3. 文件上传**

```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

# 数据格式
------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="photo.jpg"
Content-Type: image/jpeg

[二进制文件数据]
------WebKitFormBoundary--
```

#### **4. 纯文本**

```
Content-Type: text/plain

# 数据格式
这是一段纯文本
```

#### **5. HTML**

```
Content-Type: text/html; charset=utf-8

# 数据格式
<!DOCTYPE html>
<html>...</html>
```

---

# 第二部分：FastAPI 框架基础

## 一、FastAPI 框架概述

### 1.1 什么是 FastAPI

FastAPI 是一个现代、快速（高性能）的 Python Web 框架，用于构建 API，基于标准的 Python 类型提示。它具有以下特点：

- **高性能**：性能可与 NodeJS 和 Go 相媲美（得益于 Starlette 和 Pydantic）
- **快速开发**：开发效率提升约 200% 到 300%
- **减少 Bug**：减少约 40% 的人为错误
- **智能提示**：出色的编辑器支持，自动补全无处不在
- **易于使用**：API 设计直观，上手快
- **简洁**：代码简洁，最小化重复
- **自动文档**：自动生成交互式 API 文档（Swagger UI 和 ReDoc）
- **基于标准**：完全兼容 OpenAPI 和 JSON Schema

### 1.2 Web 应用基本架构

```
Web应用架构：
┌─────────────┐    HTTP请求    ┌──────────────┐
│   浏览器     │ ────────────► │ FastAPI 应用  │
│  (前端)     │ ◄──────────── │  (后端)      │
└─────────────┘    HTTP响应    └──────────────┘
                                      │
                                      ▼
                              ┌─────────────┐
                              │   数据库     │
                              └─────────────┘
```

### 1.3 安装 FastAPI

```bash
# 使用pip安装 FastAPI 和 ASGI 服务器 uvicorn
pip install fastapi uvicorn[standard]

# 验证安装
python -c "import fastapi; print(fastapi.__version__)"
```

---

## 二、第一个 FastAPI 应用

### 2.1 最简单的应用

```python
from fastapi import FastAPI

# 创建 FastAPI 应用实例
app = FastAPI()

# 定义路由和视图函数
@app.get('/')
def hello():
    return {'message': 'Hello, World!'}

# 运行应用
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
```

**代码解释**：
1. `FastAPI()` - 创建应用实例
2. `@app.get('/')` - 装饰器定义 GET 请求路由
3. `def hello()` - 视图函数处理请求，返回的 dict 会自动转换为 JSON
4. `uvicorn.run()` - 启动 ASGI 服务器

### 2.2 运行应用

```bash
# 方式1：直接运行 Python 脚本
python app.py

# 方式2：使用 uvicorn 命令
uvicorn app:app --reload

# 访问 http://127.0.0.1:8000/
# 交互式文档 http://127.0.0.1:8000/docs
# 备用文档 http://127.0.0.1:8000/redoc
```

### 2.3 调试模式（热重载）

```python
# 通过 uvicorn 命令行开启热重载
# uvicorn app:app --reload

# 或在代码中开启
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app', host='127.0.0.1', port=8000, reload=True)

# 热重载模式特点：
# 1. 代码修改后自动重载
# 2. 出错时显示详细错误信息
# 3. 自动生成 /docs 交互式文档，可直接调试
```

---

## 三、路由系统

### 3.1 基本路由

```python
# 根路由
@app.get('/')
def index():
    return {'message': '首页'}

# 固定路由
@app.get('/about')
def about():
    return {'message': '关于我们'}

# 多级路由
@app.get('/user/profile')
def user_profile():
    return {'message': '用户资料'}
```

### 3.2 动态路由（路径参数）

FastAPI 通过 Python 类型提示自动完成参数解析和校验：

```python
# 字符串参数（默认）
@app.get('/user/{username}')
def show_user(username: str):
    return {'user': username}

# 整数参数
@app.get('/order/{order_id}')
def show_order(order_id: int):
    return {'order_id': order_id}

# 浮点数参数
@app.get('/price/{amount}')
def show_price(amount: float):
    return {'price': amount}

# 路径参数（包含斜杠）
@app.get('/path/{subpath:path}')
def show_path(subpath: str):
    return {'path': subpath}
```

> **提示**：FastAPI 会根据类型注解自动完成参数转换与校验。如果传入的类型无法转换（如把字符串传给 int），会自动返回 422 错误。

### 3.3 HTTP 方法

FastAPI 为每种 HTTP 方法提供了独立的装饰器：

```python
from fastapi import FastAPI, Form
from pydantic import BaseModel

app = FastAPI()

# GET 请求（查询参数）
@app.get('/search')
def search(q: str = ''):
    return {'keyword': q}

# POST 请求（表单数据）
@app.post('/login')
def login(username: str = Form(...)):
    return {'user': username}

# POST 请求（JSON Body）
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post('/login-json')
def login_json(payload: LoginRequest):
    return {'user': payload.username}

# 多种方法（POST 处理创建，GET 处理读取）
@app.get('/data')
def get_data():
    return {'message': '获取数据'}

@app.post('/data')
def create_data():
    return {'message': '创建数据'}
```

---

## 四、请求与响应

### 4.1 构建响应

FastAPI 默认将返回值序列化为 JSON，无需手动调用 jsonify：

```python
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

# 普通文本响应
@app.get('/text', response_class=PlainTextResponse)
def text_response():
    return '纯文本响应'

# JSON 响应（默认）
@app.get('/api/json')
def json_response():
    return {'name': 'goodA', 'price': 99.9}
```

### 4.2 状态码

```python
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

app = FastAPI()

# 装饰器指定默认状态码
@app.post('/items', status_code=status.HTTP_201_CREATED)
def create_item():
    return {'message': '创建成功'}

# 主动抛出异常返回特定状态码
@app.get('/not-found')
def not_found():
    raise HTTPException(status_code=404, detail='页面不存在')

# 全局错误处理
from fastapi.requests import Request

@app.exception_handler(404)
async def page_not_found(request: Request, exc: HTTPException):
    return JSONResponse(status_code=404, content={'message': '页面不存在404'})
```

---

## 五、模板渲染

### 5.1 Jinja2 模板基础

FastAPI 本身不内置模板引擎，但可以通过 `Jinja2Templates` 集成 Jinja2，模板文件放在 `templates` 目录下。

```bash
pip install jinja2
```

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory='templates')

@app.get("/hello/{name}")
def hello(request: Request, name: str):
    return templates.TemplateResponse(
        request=request,
        name="hello.html",
        context={"name": name}
    )
```

**templates/hello.html**:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Hello</title>
</head>
<body>
    <h1>Hello, {{ name }}!</h1>
</body>
</html>
```

## 六、数据传递

### 6.1 向模板传递数据

```python
@app.get('/dashboard')
def dashboard(request: Request):
    # 准备数据
    stats = {
        'total_sales': 125000,
        'total_orders': 450,
        'total_users': 1200
    }

    products = [
        {'name': '商品A', 'price': 99.9, 'stock': 100},
        {'name': '商品B', 'price': 199.9, 'stock': 50},
        {'name': '商品C', 'price': 299.9, 'stock': 30}
    ]

    # 传递给模板
    return templates.TemplateResponse('dashboard.html', {
        'request': request,
        'stats': stats,
        'products': products
    })
```

### 6.2 模板中使用数据

```html
<!-- 访问字典 -->
<p>总销售额: {{ stats.total_sales }}</p>
<p>总订单数: {{ stats['total_orders'] }}</p>

<!-- 遍历列表 -->
<table>
    <tr>
        <th>商品名</th>
        <th>价格</th>
        <th>库存</th>
    </tr>
    {% for product in products %}
    <tr>
        <td>{{ product.name }}</td>
        <td>¥{{ product.price }}</td>
        <td>{{ product.stock }}</td>
    </tr>
    {% endfor %}
</table>
```

---

## 七、应用配置

### 7.1 配置方式

FastAPI 推荐使用 `pydantic-settings`（或 `pydantic.BaseSettings`）来管理配置：

```bash
pip install pydantic-settings
```

```python
# 方式1：直接在 FastAPI 实例化时传参
app = FastAPI(
    title='我的 API',
    description='FastAPI 应用示例',
    version='1.0.0',
    debug=True
)

# 方式2：使用 Pydantic Settings 从环境变量/配置文件加载
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = 'MyApp'
    debug: bool = True
    secret_key: str = 'your-secret-key'

    class Config:
        env_file = '.env'

settings = Settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

# 方式3：从环境变量
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-key')
```

### 7.2 常用配置项

| 配置项       | 说明                        | 默认值 |
| ------------ | --------------------------- | ------ |
| debug        | 调试模式                    | False  |
| title        | API 文档标题                | FastAPI |
| description  | API 描述                    | ''     |
| version      | API 版本                    | 0.1.0  |
| docs_url     | Swagger 文档路径            | /docs  |
| redoc_url    | ReDoc 文档路径              | /redoc |

```python
# 推荐配置
app = FastAPI(
    title='电商数据 API',
    description='RESTful API for e-commerce data analytics',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc'
)
```

> **提示**：FastAPI 返回 JSON 默认支持中文（使用 UTF-8 编码），无需像 Flask 那样手动设置 `ensure_ascii=False`。

---

## 八、项目结构

### 8.1 简单项目结构

```
simple_project/
├── main.py             # 应用入口
├── config.py           # 配置文件
├── static/             # 静态文件
│   ├── css/
│   ├── js/
│   └── images/
├── templates/          # 模板文件
│   ├── base.html
│   └── index.html
└── requirements.txt    # 依赖清单
```

### 8.2 中型项目结构

```
medium_project/
├── app/
│   ├── __init__.py     # 应用工厂
│   ├── main.py         # FastAPI 实例
│   ├── routers/        # 路由模块（APIRouter）
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── products.py
│   ├── models.py       # 数据模型
│   ├── schemas.py      # Pydantic 模型
│   ├── utils.py        # 工具函数
│   ├── static/
│   └── templates/
├── config.py           # 配置
├── run.py              # 启动脚本
└── requirements.txt
```

---

## 九、实战练习

### 练习1：创建简单页面

```python
# 目标：创建一个返回商品列表的 API
# 要求：
# 1. 创建路由 GET /products
# 2. 准备商品数据（至少5个）
# 3. 返回 JSON 数据
```

### 练习2：JSON API

```python
# 目标：创建返回JSON数据的API
# 要求：
# 1. 创建路由 GET /api/stats
# 2. 返回销售统计数据
# 3. 支持查询参数过滤
```

---

# 第三部分：FastAPI 数据 API 开发

## 一、RESTful API 概述

### 1.1 什么是 RESTful API

REST（Representational State Transfer）是一种软件架构风格，RESTful API是遵循REST原则设计的Web API。

**核心原则**：
- 使用HTTP方法表示操作类型
- 使用URL表示资源
- 使用JSON格式传输数据
- 无状态通信

### 1.2 HTTP方法与CRUD操作

| HTTP方法 | 操作 | 说明     | 示例                     |
| -------- | ---- | -------- | ------------------------ |
| GET      | 读取 | 获取资源 | GET /api/products        |
| POST     | 创建 | 新建资源 | POST /api/products       |
| PUT      | 更新 | 完整更新 | PUT /api/products/1      |
| PATCH    | 修改 | 部分更新 | PATCH /api/products/1    |
| DELETE   | 删除 | 删除资源 | DELETE /api/products/1   |

### 1.3 API URL设计规范

```
良好的URL设计：
├── /api/products           # 商品列表
├── /api/products/1         # 单个商品
├── /api/products/1/reviews # 商品的评论
├── /api/users              # 用户列表
├── /api/users/1/orders     # 用户的订单
└── /api/stats/sales        # 销售统计

避免的设计：
├── /api/getProducts        # 动词放URL中
├── /api/product_list       # 使用下划线
└── /api/Products           # 大写
```

---

## 二、FastAPI API 基础

### 2.1 返回JSON数据

FastAPI 中所有返回的 dict / list / Pydantic 模型都会自动转换为 JSON，无需 `jsonify`：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get('/api/data')
def get_data():
    return {
        'name': '商品A',
        'price': 99.9,
        'stock': 100
    }
```

### 2.2 处理请求参数

FastAPI 通过函数参数的类型注解自动解析查询参数：

```python
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

ALL_PRODUCTS = [
    {"id": 1, "name": "iPhone 15", "category": "electronics", "price": 7999},
    {"id": 2, "name": "MacBook Pro", "category": "electronics", "price": 15999},
    {"id": 3, "name": "Nike Running Shoes", "category": "sports", "price": 899},
    {"id": 4, "name": "Adidas T-Shirt", "category": "clothing", "price": 199},
    {"id": 5, "name": "Basketball", "category": "sports", "price": 129},
]

@app.get('/api/products')
def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None
):
    # 筛选数据
    products = ALL_PRODUCTS
    if category:
        products = [p for p in products if p['category'] == category]

    # 分页处理
    start = (page - 1) * limit
    end = start + limit

    return {
        "data": products[start:end],
        "total": len(products),
        "page": page,
        "limit": limit
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=9000)
```

####  获取所有商品（分页）

```
GET /api/products?page=1&limit=2
```

#### 按分类筛选

```
GET /api/products?category=sports
```

#### 分类 + 分页

```
GET /api/products?category=electronics&page=1&limit=1
```

## 三、API响应格式规范

### 3.1 统一响应格式

```python
from datetime import datetime
from typing import Any, Optional
from fastapi.responses import JSONResponse

def api_response(data: Any = None, success: bool = True, message: str = '', code: int = 200):
    """统一API响应格式"""
    content = {
        'success': success,
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    return JSONResponse(status_code=code, content=content)
```

也可以使用 Pydantic 模型定义响应结构，让 FastAPI 自动生成文档：

```python
from pydantic import BaseModel
from typing import Any, Optional

class APIResponse(BaseModel):
    success: bool = True
    code: int = 200
    message: str = ''
    data: Optional[Any] = None
    timestamp: str
```

### 3.2 成功响应示例

```json
{
    "success": true,
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "name": "商品A",
        "price": 99.9
    },
    "timestamp": "2024-01-15T10:30:00"
}
```

### 3.3 错误响应示例

```json
{
    "success": false,
    "code": 404,
    "message": "商品不存在",
    "data": null,
    "timestamp": "2024-01-15T10:30:00"
}
```

### 3.4 分页响应示例

```json
{
    "success": true,
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [],
        "pagination": {
            "page": 1,
            "limit": 10,
            "total": 100,
            "pages": 10
        }
    },
    "timestamp": "2024-01-15T10:30:00"
}
```

---

## 四、电商数据 API 设计

### 4.1 统计数据API

```python
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

@app.get('/api/stats/overview')
def stats_overview():
    """获取业务概览数据"""
    stats = {
        'gmv': calculate_gmv(),
        'orders': count_orders(),
        'users': count_users(),
        'aov': calculate_aov()
    }
    return api_response(stats)

@app.get('/api/stats/sales')
def stats_sales(
    start: Optional[str] = Query(None, description='开始日期'),
    end: Optional[str] = Query(None, description='结束日期'),
    group: str = Query('day', regex='^(day|week|month)$')
):
    """获取销售统计"""
    sales_data = get_sales_data(start, end, group)
    return api_response(sales_data)
```

### 4.2 用户分析API

```python
@app.get('/api/stats/users')
def stats_users():
    """获取用户统计"""
    stats = {
        'total': count_total_users(),
        'new_today': count_new_users_today(),
        'active_today': count_active_users_today(),
        'by_channel': get_users_by_channel(),
        'by_type': get_users_by_type()
    }
    return api_response(stats)

@app.get('/api/stats/rfm')
def stats_rfm():
    """获取RFM分群数据"""
    rfm_data = calculate_rfm()
    return api_response({
        'segments': rfm_data['segment_counts'],
        'avg_values': rfm_data['segment_values']
    })
```

### 4.3 商品分析API

```python
@app.get('/api/stats/products')
def stats_products(limit: int = Query(10, ge=1, le=100)):
    """获取商品统计"""
    stats = {
        'top_selling': get_top_products('sales', limit),
        'top_revenue': get_top_products('revenue', limit),
        'low_stock': get_low_stock_products(limit),
        'by_category': get_sales_by_category()
    }
    return api_response(stats)
```

### 4.4 趋势数据API

```python
from datetime import datetime, timedelta

@app.get('/api/trends/sales')
def trends_sales(days: int = Query(30, ge=1, le=365)):
    """获取销售趋势"""
    trends = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        trends.append({
            'date': date,
            'sales': get_daily_sales(date),
            'orders': get_daily_orders(date)
        })

    return api_response(trends[::-1])  # 按日期正序

@app.get('/api/trends/users')
def trends_users(days: int = Query(30, ge=1, le=365)):
    """获取用户趋势"""
    trends = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        trends.append({
            'date': date,
            'new_users': get_new_users(date),
            'active_users': get_active_users(date)
        })

    return api_response(trends[::-1])
```

---

## 五、数据聚合与计算

### 5.1 使用Pandas处理数据

```python
import pandas as pd
import numpy as np

def calculate_sales_stats(orders_df, start_date=None, end_date=None):
    """计算销售统计"""
    df = orders_df.copy()

    # 日期筛选
    if start_date:
        df = df[df['order_date'] >= start_date]
    if end_date:
        df = df[df['order_date'] <= end_date]

    # 计算统计指标
    stats = {
        'total_sales': float(df['amount'].sum()),
        'total_orders': len(df),
        'avg_order_value': float(df['amount'].mean()),
        'max_order': float(df['amount'].max()),
        'min_order': float(df['amount'].min())
    }

    return stats
```

### 5.2 时间序列聚合

```python
def get_sales_by_period(orders_df, period='D'):
    """按周期聚合销售数据"""
    df = orders_df.copy()
    df['order_date'] = pd.to_datetime(df['order_date'])
    df.set_index('order_date', inplace=True)

    # 重采样
    agg_data = df.resample(period).agg({
        'amount': 'sum',
        'order_id': 'count',
        'user_id': 'nunique'
    }).reset_index()

    agg_data.columns = ['date', 'sales', 'orders', 'customers']

    # 转换为可JSON序列化的格式
    result = []
    for _, row in agg_data.iterrows():
        result.append({
            'date': row['date'].strftime('%Y-%m-%d'),
            'sales': float(row['sales']),
            'orders': int(row['orders']),
            'customers': int(row['customers'])
        })

    return result
```

### 5.3 分类统计

```python
def get_category_stats(orders_df, products_df):
    """获取分类统计"""
    # 合并订单和商品数据
    merged = orders_df.merge(products_df[['product_id', 'category']], on='product_id')

    # 按分类聚合
    category_stats = merged.groupby('category').agg({
        'amount': 'sum',
        'order_id': 'count',
        'user_id': 'nunique'
    }).reset_index()

    category_stats.columns = ['category', 'sales', 'orders', 'customers']

    # 计算占比
    total_sales = category_stats['sales'].sum()
    category_stats['percentage'] = (category_stats['sales'] / total_sales * 100).round(2)

    return category_stats.to_dict('records')
```

---

## 六、API文档

### 6.1 API文档规范

FastAPI 会根据代码和类型注解自动生成 OpenAPI 文档，访问 `/docs`（Swagger UI）或 `/redoc` 即可查看。

```
API: 获取销售统计
URL: /api/stats/sales
方法: GET

请求参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start | string | 否 | 开始日期 (YYYY-MM-DD) |
| end | string | 否 | 结束日期 (YYYY-MM-DD) |
| group | string | 否 | 分组方式 (day/week/month) |

响应示例：
{
    "success": true,
    "data": {
        "total_sales": 125000,
        "total_orders": 450,
        "trends": []
    }
}

错误码：
| 码 | 说明 |
|-----|------|
| 400 | 参数错误 |
| 422 | 参数校验失败 |
| 500 | 服务器错误 |
```

### 6.2 在代码中添加文档

FastAPI 支持通过 docstring、`summary`、`description` 和 `response_model` 等参数丰富自动生成的文档：

```python
@app.get(
    '/api/stats/sales',
    summary='获取销售统计',
    description='根据日期范围和分组方式返回销售统计数据',
    tags=['统计']
)
def api_stats_sales(
    start: Optional[str] = Query(None, description='开始日期，格式 YYYY-MM-DD'),
    end: Optional[str] = Query(None, description='结束日期，格式 YYYY-MM-DD'),
    group: str = Query('day', description='分组方式，可选 day/week/month')
):
    """
    获取销售统计数据

    - **start**: 开始日期，格式 YYYY-MM-DD
    - **end**: 结束日期，格式 YYYY-MM-DD
    - **group**: 分组方式，可选 day/week/month
    """
    # 实现代码...
```

---

## 七、完整API示例

### 7.1 电商数据API完整代码结构

```python
# api.py
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(
    title='电商数据 API',
    description='RESTful API for e-commerce data analytics',
    version='1.0.0'
)

# ========== 辅助函数 ==========

def api_response(data=None, success=True, message='', code=200):
    """统一响应格式"""
    return JSONResponse(status_code=code, content={
        'success': success,
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

# ========== 统计API ==========

@app.get('/api/stats/overview')
def stats_overview():
    """业务概览"""
    pass

@app.get('/api/stats/sales')
def stats_sales():
    """销售统计"""
    pass

@app.get('/api/stats/users')
def stats_users():
    """用户统计"""
    pass

@app.get('/api/stats/products')
def stats_products():
    """商品统计"""
    pass

# ========== 趋势API ==========

@app.get('/api/trends/sales')
def trends_sales():
    """销售趋势"""
    pass

@app.get('/api/trends/users')
def trends_users():
    """用户趋势"""
    pass

# ========== 列表API ==========

@app.get('/api/products')
def list_products():
    """商品列表"""
    pass

@app.get('/api/orders')
def list_orders():
    """订单列表"""
    pass

# ========== 错误处理 ==========

@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    return api_response(None, False, '资源不存在', 404)

@app.exception_handler(500)
async def server_error(request: Request, exc: HTTPException):
    return api_response(None, False, '服务器错误', 500)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
```

---

### 7.2 完整可运行示例：data_api.py

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件名称：data_api.py
功能描述：电商数据分析 API 服务（基于 FastAPI）
创建日期：2024年1月
运行方式：python data_api.py  或  uvicorn data_api:app --reload
访问地址：http://127.0.0.1:5002/
交互式文档：http://127.0.0.1:5002/docs
"""

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

# 创建 FastAPI 应用
app = FastAPI(
    title='E-Commerce Data API',
    description='RESTful API for e-commerce data analytics',
    version='1.0.0'
)

# ============================================================
# 数据生成
# ============================================================

def generate_sample_data():
    """生成示例数据"""
    np.random.seed(42)

    # 日期范围
    end_date = datetime(2024, 1, 15)
    start_date = end_date - timedelta(days=365)

    # 用户数据
    n_users = 1000
    users = pd.DataFrame({
        'user_id': range(1, n_users + 1),
        'register_date': pd.to_datetime([
            start_date + timedelta(days=np.random.randint(0, 365))
            for _ in range(n_users)
        ]),
        'user_type': np.random.choice(['Normal', 'Member', 'VIP'], n_users, p=[0.7, 0.2, 0.1]),
        'channel': np.random.choice(['Organic', 'SEM', 'Social', 'Referral'], n_users)
    })

    # 订单数据
    n_orders = 8000
    categories = ['Electronics', 'Clothing', 'Home', 'Food', 'Beauty']

    orders = pd.DataFrame({
        'order_id': range(1, n_orders + 1),
        'user_id': np.random.randint(1, n_users + 1, n_orders),
        'order_date': pd.to_datetime([
            start_date + timedelta(days=np.random.randint(0, 365))
            for _ in range(n_orders)
        ]),
        'amount': np.random.exponential(200, n_orders) + 50,
        'category': np.random.choice(categories, n_orders),
        'status': np.random.choice(['Completed', 'Cancelled', 'Returned'], n_orders, p=[0.88, 0.08, 0.04])
    })

    # 商品数据
    products = [
        {'id': 1, 'name': 'Smartphone', 'category': 'Electronics', 'price': 599, 'stock': 100},
        {'id': 2, 'name': 'Laptop', 'category': 'Electronics', 'price': 999, 'stock': 50},
        {'id': 3, 'name': 'Headphones', 'category': 'Electronics', 'price': 149, 'stock': 200},
        {'id': 4, 'name': 'T-Shirt', 'category': 'Clothing', 'price': 29, 'stock': 500},
        {'id': 5, 'name': 'Jeans', 'category': 'Clothing', 'price': 59, 'stock': 300},
        {'id': 6, 'name': 'Sofa', 'category': 'Home', 'price': 499, 'stock': 30},
        {'id': 7, 'name': 'Table Lamp', 'category': 'Home', 'price': 39, 'stock': 150},
        {'id': 8, 'name': 'Coffee', 'category': 'Food', 'price': 15, 'stock': 1000},
        {'id': 9, 'name': 'Lipstick', 'category': 'Beauty', 'price': 25, 'stock': 400},
        {'id': 10, 'name': 'Perfume', 'category': 'Beauty', 'price': 89, 'stock': 200},
    ]

    return users, orders, pd.DataFrame(products)


# 全局数据
USERS, ORDERS, PRODUCTS = generate_sample_data()


# ============================================================
# 辅助函数
# ============================================================

def api_response(data=None, success=True, message='', code=200):
    """统一API响应格式"""
    return JSONResponse(status_code=code, content={
        'success': success,
        'code': code,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })


def parse_date(date_str, default=None):
    """解析日期字符串"""
    if not date_str:
        return default
    try:
        return pd.to_datetime(date_str)
    except Exception:
        return default


# ============================================================
# 首页
# ============================================================

@app.get('/', response_class=HTMLResponse)
def index():
    """API首页"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>E-Commerce Data API</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
            .container { max-width: 900px; margin: 0 auto; }
            h1 { color: #00d9ff; }
            h2 { color: #ff6b6b; border-bottom: 1px solid #333; padding-bottom: 10px; }
            .endpoint { background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #00d9ff; }
            .method { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 12px; margin-right: 10px; }
            .get { background: #27ae60; }
            .post { background: #f39c12; }
            .url { color: #00d9ff; font-family: monospace; }
            .desc { color: #aaa; margin-top: 5px; }
            a { color: #00d9ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 E-Commerce Data API (FastAPI)</h1>
            <p>RESTful API for e-commerce data analytics. Try <a href="/docs">/docs</a> for interactive Swagger UI.</p>

            <h2>📊 Statistics APIs</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a class="url" href="/api/stats/overview">/api/stats/overview</a>
                <p class="desc">Get business overview statistics</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a class="url" href="/api/stats/sales">/api/stats/sales</a>
                <p class="desc">Get sales statistics (params: start, end)</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a class="url" href="/api/stats/users">/api/stats/users</a>
                <p class="desc">Get user statistics</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a class="url" href="/api/stats/categories">/api/stats/categories</a>
                <p class="desc">Get category breakdown</p>
            </div>

            <h2>📈 Trends APIs</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a class="url" href="/api/trends/daily">/api/trends/daily</a>
                <p class="desc">Get daily sales trends (params: days)</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a class="url" href="/api/trends/monthly">/api/trends/monthly</a>
                <p class="desc">Get monthly sales trends</p>
            </div>

            <h2>👥 User Analysis APIs</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a class="url" href="/api/analysis/rfm">/api/analysis/rfm</a>
                <p class="desc">Get RFM segmentation data</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a class="url" href="/api/analysis/retention">/api/analysis/retention</a>
                <p class="desc">Get user retention data</p>
            </div>

            <h2>📦 Products APIs</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a class="url" href="/api/products">/api/products</a>
                <p class="desc">Get product list (params: category, limit)</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span>
                <a class="url" href="/api/products/1">/api/products/{id}</a>
                <p class="desc">Get single product</p>
            </div>
        </div>
    </body>
    </html>
    '''


# ============================================================
# 统计API
# ============================================================

@app.get('/api/stats/overview')
def stats_overview():
    """业务概览统计"""
    completed = ORDERS[ORDERS['status'] == 'Completed']

    stats = {
        'gmv': round(float(completed['amount'].sum()), 2),
        'total_orders': len(completed),
        'total_customers': int(completed['user_id'].nunique()),
        'total_users': len(USERS),
        'aov': round(float(completed['amount'].mean()), 2),
        'completion_rate': round(len(completed) / len(ORDERS) * 100, 2)
    }

    return api_response(stats, message='Success')


@app.get('/api/stats/sales')
def stats_sales(
    start: Optional[str] = Query(None, description='开始日期 YYYY-MM-DD'),
    end: Optional[str] = Query(None, description='结束日期 YYYY-MM-DD')
):
    """销售统计"""
    start_dt = parse_date(start)
    end_dt = parse_date(end)

    df = ORDERS[ORDERS['status'] == 'Completed'].copy()

    if start_dt is not None:
        df = df[df['order_date'] >= start_dt]
    if end_dt is not None:
        df = df[df['order_date'] <= end_dt]

    stats = {
        'total_sales': round(float(df['amount'].sum()), 2),
        'total_orders': len(df),
        'avg_order_value': round(float(df['amount'].mean()), 2) if len(df) > 0 else 0,
        'max_order': round(float(df['amount'].max()), 2) if len(df) > 0 else 0,
        'min_order': round(float(df['amount'].min()), 2) if len(df) > 0 else 0,
        'customers': int(df['user_id'].nunique())
    }

    return api_response(stats, message='Success')


@app.get('/api/stats/users')
def stats_users():
    """用户统计"""
    # 用户类型分布
    type_dist = USERS['user_type'].value_counts().to_dict()

    # 渠道分布
    channel_dist = USERS['channel'].value_counts().to_dict()

    # 活跃用户（过去30天有订单）
    thirty_days_ago = ORDERS['order_date'].max() - timedelta(days=30)
    active_users = ORDERS[ORDERS['order_date'] >= thirty_days_ago]['user_id'].nunique()

    stats = {
        'total_users': len(USERS),
        'active_users_30d': int(active_users),
        'by_type': type_dist,
        'by_channel': channel_dist
    }

    return api_response(stats, message='Success')


@app.get('/api/stats/categories')
def stats_categories():
    """分类统计"""
    completed = ORDERS[ORDERS['status'] == 'Completed']

    category_stats = completed.groupby('category').agg({
        'amount': 'sum',
        'order_id': 'count',
        'user_id': 'nunique'
    }).reset_index()

    category_stats.columns = ['category', 'sales', 'orders', 'customers']
    total_sales = category_stats['sales'].sum()
    category_stats['percentage'] = (category_stats['sales'] / total_sales * 100).round(2)

    data = category_stats.sort_values('sales', ascending=False).to_dict('records')

    # 转换为JSON可序列化格式
    for item in data:
        item['sales'] = round(float(item['sales']), 2)
        item['orders'] = int(item['orders'])
        item['customers'] = int(item['customers'])
        item['percentage'] = float(item['percentage'])

    return api_response(data, message='Success')


# ============================================================
# 趋势API
# ============================================================

@app.get('/api/trends/daily')
def trends_daily(days: int = Query(30, ge=1, le=365)):
    """日销售趋势"""
    completed = ORDERS[ORDERS['status'] == 'Completed'].copy()
    completed['date'] = completed['order_date'].dt.date

    # 获取最近N天数据
    max_date = completed['order_date'].max()
    min_date = max_date - timedelta(days=days)

    daily = completed[completed['order_date'] >= min_date].groupby('date').agg({
        'amount': 'sum',
        'order_id': 'count',
        'user_id': 'nunique'
    }).reset_index()

    daily.columns = ['date', 'sales', 'orders', 'customers']

    data = []
    for _, row in daily.iterrows():
        data.append({
            'date': str(row['date']),
            'sales': round(float(row['sales']), 2),
            'orders': int(row['orders']),
            'customers': int(row['customers'])
        })

    return api_response(sorted(data, key=lambda x: x['date']), message='Success')


@app.get('/api/trends/monthly')
def trends_monthly():
    """月销售趋势"""
    completed = ORDERS[ORDERS['status'] == 'Completed'].copy()
    completed['month'] = completed['order_date'].dt.to_period('M')

    monthly = completed.groupby('month').agg({
        'amount': 'sum',
        'order_id': 'count',
        'user_id': 'nunique'
    }).reset_index()

    monthly.columns = ['month', 'sales', 'orders', 'customers']

    data = []
    for _, row in monthly.iterrows():
        data.append({
            'month': str(row['month']),
            'sales': round(float(row['sales']), 2),
            'orders': int(row['orders']),
            'customers': int(row['customers'])
        })

    return api_response(data, message='Success')


# ============================================================
# 用户分析API
# ============================================================

@app.get('/api/analysis/rfm')
def analysis_rfm():
    """RFM分析"""
    completed = ORDERS[ORDERS['status'] == 'Completed'].copy()
    analysis_date = completed['order_date'].max() + timedelta(days=1)

    rfm = completed.groupby('user_id').agg({
        'order_date': lambda x: (analysis_date - x.max()).days,
        'order_id': 'count',
        'amount': 'sum'
    }).reset_index()

    rfm.columns = ['user_id', 'recency', 'frequency', 'monetary']

    # RFM评分
    rfm['R_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop').astype(int)
    rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)
    rfm['M_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)

    # 分群
    def segment(row):
        r, f, m = row['R_score'], row['F_score'], row['M_score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 4 and f >= 4:
            return 'Loyal'
        elif r >= 4:
            return 'Recent'
        elif f >= 4 or m >= 4:
            return 'At Risk'
        else:
            return 'Hibernating'

    rfm['segment'] = rfm.apply(segment, axis=1)

    # 分群统计
    segment_stats = rfm.groupby('segment').agg({
        'user_id': 'count',
        'monetary': 'mean'
    }).reset_index()

    segment_stats.columns = ['segment', 'count', 'avg_monetary']

    data = {
        'segments': segment_stats.to_dict('records'),
        'rfm_summary': {
            'avg_recency': round(float(rfm['recency'].mean()), 1),
            'avg_frequency': round(float(rfm['frequency'].mean()), 2),
            'avg_monetary': round(float(rfm['monetary'].mean()), 2)
        }
    }

    # 格式化数值
    for seg in data['segments']:
        seg['count'] = int(seg['count'])
        seg['avg_monetary'] = round(float(seg['avg_monetary']), 2)

    return api_response(data, message='Success')


@app.get('/api/analysis/retention')
def analysis_retention():
    """用户留存分析"""
    completed = ORDERS[ORDERS['status'] == 'Completed'].copy()
    completed['cohort_month'] = completed.groupby('user_id')['order_date'].transform('min').dt.to_period('M')
    completed['order_month'] = completed['order_date'].dt.to_period('M')

    # 计算月份差
    completed['months_since'] = (completed['order_month'] - completed['cohort_month']).apply(lambda x: x.n if hasattr(x, 'n') else 0)

    # 构建留存矩阵
    cohort_data = completed.groupby(['cohort_month', 'months_since'])['user_id'].nunique().unstack(fill_value=0)

    # 取最近6个月
    cohort_data = cohort_data.tail(6).iloc[:, :7]

    # 计算留存率
    cohort_sizes = cohort_data.iloc[:, 0]
    retention = cohort_data.divide(cohort_sizes, axis=0) * 100

    data = {
        'retention_matrix': {str(k): v for k, v in retention.round(1).to_dict().items()},
        'avg_retention': {f'month_{i}': round(float(retention[i].mean()), 1) for i in range(min(7, len(retention.columns)))}
    }

    return api_response(data, message='Success')


# ============================================================
# 商品API
# ============================================================

@app.get('/api/products')
def list_products(
    category: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100)
):
    """商品列表"""
    df = PRODUCTS.copy()

    if category:
        df = df[df['category'] == category]

    data = df.head(limit).to_dict('records')

    return api_response(data, message='Success')


@app.get('/api/products/{product_id}')
def get_product(product_id: int):
    """获取单个商品"""
    product = PRODUCTS[PRODUCTS['id'] == product_id]

    if len(product) == 0:
        return api_response(None, False, 'Product not found', 404)

    return api_response(product.iloc[0].to_dict(), message='Success')


# ============================================================
# 错误处理
# ============================================================

@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    return api_response(None, False, 'Resource not found', 404)


@app.exception_handler(500)
async def server_error(request: Request, exc: HTTPException):
    return api_response(None, False, 'Internal server error', 500)


# ============================================================
# 主函数
# ============================================================

if __name__ == '__main__':
    import uvicorn

    print("=" * 50)
    print("E-Commerce Data API Server (FastAPI)")
    print("=" * 50)
    print(f"\nData loaded:")
    print(f"  - Users: {len(USERS)}")
    print(f"  - Orders: {len(ORDERS)}")
    print(f"  - Products: {len(PRODUCTS)}")
    print("\nAccess URL: http://127.0.0.1:5002/")
    print("Interactive docs: http://127.0.0.1:5002/docs")
    print("\nPress Ctrl+C to stop\n")

    uvicorn.run(app, host='0.0.0.0', port=5002)
```

---

**教程结束**
