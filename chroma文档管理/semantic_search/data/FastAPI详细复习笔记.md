# FastAPI 详细复习笔记

> 仿照《集成学习详细笔记》写法：直觉 → 概念 → 对照表 → 逐行注释代码 → 易错点 → 自测。  
> 材料对齐：`FastAPI_综合课件.md`、`ecommerce_insight_360`（路由分层、Pydantic、部署）。  
> 代码风格：**几乎每行末尾都有中文注释**。  
> 姊妹篇：`Docker详细复习笔记.md`、`HTML详细复习笔记.md`。

---

## 〇、这份笔记怎么用

一句话抓住全篇：

> **FastAPI = 用类型注解写 API：自动校验入参、自动生成文档、默认返回 JSON，适合做高性能数据接口。**

| 章 | 核心问题 |
| --- | --- |
| 一 | HTTP 与为什么选 FastAPI |
| 二 | 第一个应用、路由、请求响应 |
| 三 | Pydantic 模型与统一响应 |
| 四 | 工程结构、依赖注入、静态/模板 |
| 五 | 文档、异常、CORS、部署要点 |
| 六 | 综合实战代码 |
| 七 | 易错点、自测、练习 |

环境：

```python
# pip install fastapi uvicorn[standard] pydantic python-multipart jinja2
# 可选：pip install httpx  # 写测试时常用
```

---

## 一、总地图：HTTP + FastAPI 定位

### 1.1 HTTP 最小必备

客户端发请求，服务器回响应：

```
浏览器 / 前端 / 脚本  ----请求---->  FastAPI 服务器
                     <----响应----
```

请求四件套：请求行、请求头、空行、请求体。  
响应四件套：状态行、响应头、空行、响应体。

| 方法 | 用途 | 是否常有 Body | 场景 |
| --- | --- | --- | --- |
| GET | 读资源 | 否 | 列表、详情、搜索 |
| POST | 创建 / 提交 | 是 | 注册、下单、上传 |
| PUT | 整体替换更新 | 是 | 改整份资料 |
| PATCH | 部分更新 | 是 | 只改一个字段 |
| DELETE | 删除 | 否/可选 | 删资源 |
| OPTIONS | 探路 | 否 | CORS 预检 |

常见状态码：

| 码 | 含义 |
| --- | --- |
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 成功但无内容 |
| 400 | 客户端参数坏了 |
| 401 / 403 | 未登录 / 无权限 |
| 404 | 找不到 |
| 422 | 校验失败（FastAPI/Pydantic 很常见） |
| 500 | 服务器内部错误 |

### 1.2 为什么用 FastAPI（对照 Flask）

| 维度 | Flask 常见痛点 | FastAPI 优势 |
| --- | --- | --- |
| 并发 | WSGI 同步为主 | ASGI + uvicorn，I/O 密集更合适 |
| 校验 | 手写 `request.args` | 类型注解 + Pydantic 自动校验 |
| 文档 | 另维护 Postman / Flasgger | 自带 `/docs`、`/redoc` |
| 输出安全 | `jsonify(dict)` 易多吐字段 | `response_model` 过滤输出 |
| 模块化 | Blueprint | `APIRouter` + `Depends` |

底层：`Starlette`（Web）+ `Pydantic`（数据）+ `Uvicorn`（ASGI 服务器）。

### 1.3 概念卡片

| 概念 | 人话 |
| --- | --- |
| 路由 | URL 路径 + 方法 → 某个函数 |
| 路径参数 | `/users/3` 里的 `3` |
| 查询参数 | `?page=1&size=10` |
| 请求体 Body | POST/PUT 里的 JSON |
| Schema / Model | Pydantic 数据契约 |
| `response_model` | 响应字段安检机 |
| 依赖注入 `Depends` | 把公共逻辑（鉴权、DB）注入路由 |
| OpenAPI | 接口说明书标准，Swagger 据此生成 |

---

## 二、第一个应用与路由

### 2.1 Hello FastAPI

```python
from fastapi import FastAPI  # 导入框架
import uvicorn  # ASGI 服务器

app = FastAPI(  # 创建应用
    title="我的第一个API",  # 文档标题
    version="1.0.0",  # 版本号
    description="复习用最小示例",  # 描述
)

@app.get("/")  # 注册 GET /
def read_root():  # 视图函数
    return {"message": "hello fastapi"}  # 自动转成 JSON

if __name__ == "__main__":  # 脚本直接运行时
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)  # 热重载启动
```

访问：

- 接口：`http://127.0.0.1:8000/`
- Swagger：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

命令行等价：

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

`main:app` 意思是：`main.py` 文件里的变量 `app`。

### 2.2 路径参数与查询参数

```python
from typing import Optional  # 可选类型
from fastapi import FastAPI, Path, Query  # 路径与查询增强

app = FastAPI()  # 应用

@app.get("/products/{product_id}")  # 路径参数
def get_product(
    product_id: int = Path(..., ge=1, description="商品ID，至少为1"),  # ... 表示必填
    q: Optional[str] = Query(None, min_length=1, max_length=50, description="搜索词"),  # 可选查询
    page: int = Query(1, ge=1),  # 页码默认 1
):
    return {  # 返回字典
        "product_id": product_id,  # 路径里拿到的 id
        "q": q,  # 查询词
        "page": page,  # 页码
    }
```

| 位置 | 例子 | 典型用途 |
| --- | --- | --- |
| 路径参数 | `/users/5` | 唯一资源定位 |
| 查询参数 | `?status=paid` | 过滤、分页、排序 |

### 2.3 请求体：JSON + Pydantic

```python
from pydantic import BaseModel, Field  # 数据模型
from fastapi import FastAPI  # 框架

app = FastAPI()  # 应用

class UserCreate(BaseModel):  # 入参契约
    username: str = Field(..., min_length=2, max_length=32, description="用户名")  # 必填字符串
    age: int = Field(..., ge=0, le=150, description="年龄")  # 年龄范围
    email: str  # 简单必填；更严可用 EmailStr

@app.post("/users", status_code=201)  # 创建成功常用 201
def create_user(user: UserCreate):  # Body 自动解析并校验
    return {  # 业务里通常会入库再返回
        "id": 1,  # 模拟主键
        "username": user.username,  # 回显
        "age": user.age,  # 回显
        "email": user.email,  # 回显
    }
```

校验失败时 FastAPI 自动返回 **422**，并说明哪个字段错了。

### 2.4 多种 HTTP 方法

```python
from fastapi import APIRouter  # 路由模块化

router = APIRouter(prefix="/items", tags=["Items"])  # 统一前缀与文档分组

@router.get("")  # GET /items
def list_items():  # 列表
    return [{"id": 1, "name": "A"}]  # 示例数据

@router.get("/{item_id}")  # GET /items/1
def get_item(item_id: int):  # 详情
    return {"id": item_id, "name": "A"}  # 示例

@router.post("")  # POST /items
def create_item(name: str):  # 简化演示；正式应用请用 Model
    return {"id": 2, "name": name}  # 创建结果

@router.delete("/{item_id}", status_code=204)  # 删除常返回 204
def delete_item(item_id: int):  # 删除
    return None  # 无内容
```

在 `main.py` 里挂载：

```python
app.include_router(router)  # 把子路由挂到应用上
```

---

## 三、Pydantic 与统一响应格式

### 3.1 为什么要 Schema

没有契约时：前端不知道字段、后端容易多返回内部字段。  
有 `response_model` 时：文档自动生成 + 输出字段过滤。

### 3.2 统一响应壳（项目常用）

```python
from typing import Generic, Optional, TypeVar  # 泛型
from pydantic import BaseModel  # 基类

T = TypeVar("T")  # 数据类型占位

class BaseResponse(BaseModel, Generic[T]):  # 统一外壳
    code: int = 200  # 业务码
    message: str = "ok"  # 提示
    data: Optional[T] = None  # 真正数据

def success_response(data=None, message: str = "成功"):  # 成功助手
    return {"code": 200, "message": message, "data": data}  # 也可直接返回 BaseResponse
```

路由示例：

```python
from fastapi import APIRouter  # 路由
from pydantic import BaseModel  # 模型

class UserGrowthSchema(BaseModel):  # 出参结构
    dates: list[str]  # 日期列表
    counts: list[int]  # 人数列表

router = APIRouter(prefix="/users", tags=["Users"])  # 用户模块

@router.get("/growth", response_model=BaseResponse[UserGrowthSchema], summary="用户增长")  # 声明出参
def get_user_growth(start_date: Optional[str] = None):  # 可选开始日期
    payload = UserGrowthSchema(  # 构造符合契约的数据
        dates=["2026-01-01", "2026-01-02"],  # 示例日期
        counts=[10, 15],  # 示例计数
    )
    return success_response(data=payload, message="获取成功")  # 统一成功响应
```

### 3.3 入参位置小结

| 来源 | 写法直觉 |
| --- | --- |
| Path | `item_id: int` 出现在路径里 |
| Query | 函数参数且不在路径中，默认当 Query |
| Body | Pydantic 模型参数 |
| Header / Cookie | `Header(...)` / `Cookie(...)` |
| Form / File | `Form` / `File`（要装 `python-multipart`） |

---

## 四、工程结构、依赖注入、静态与模板

### 4.1 推荐目录（对齐电商项目）

```
app/
  main.py           # 创建 app、挂载路由、中间件
  routers/          # 只放路由函数
  schemas/          # Pydantic 入参出参
  services/         # 业务逻辑
  models/           # ORM / 表结构（若有数据库）
  core/             # 配置、统一响应、数据库连接
  static/           # css/js/图片
  templates/        # Jinja2 HTML
```

原则：**路由薄、服务厚、Schema 管契约。**

### 4.2 依赖注入 `Depends`

```python
from fastapi import Depends, HTTPException  # 依赖与异常

def get_token_header(x_token: str = Header(...)):  # 假装鉴权依赖
    if x_token != "secret":  # 校验失败
        raise HTTPException(status_code=401, detail="无效令牌")  # 抛 401
    return x_token  # 返回给路由使用

@app.get("/private", dependencies=[Depends(get_token_header)])  # 路由级依赖
def private_data():  # 业务
    return {"ok": True}  # 通过鉴权才到这里
```

也可以把依赖结果当作参数：

```python
def get_db():  # 模拟数据库会话
    db = {"conn": "sqlite"}  # 假对象
    try:  # 正常提供
        yield db  # 注入给路由
    finally:  # 请求结束
        pass  # 这里关闭连接

@app.get("/db-check")  # 检查
def db_check(db=Depends(get_db)):  # 自动注入
    return db  # 返回连接信息
```

### 4.3 静态文件与 Jinja2 模板

```python
from pathlib import Path  # 路径
from fastapi import FastAPI, Request  # 请求对象给模板用
from fastapi.staticfiles import StaticFiles  # 静态资源
from fastapi.templating import Jinja2Templates  # 模板引擎
from fastapi.responses import HTMLResponse  # HTML 响应

app = FastAPI()  # 应用
BASE = Path(__file__).resolve().parent  # 当前目录
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")  # 挂载静态
templates = Jinja2Templates(directory=str(BASE / "templates"))  # 模板目录

@app.get("/", response_class=HTMLResponse)  # 返回网页
def index(request: Request):  # 模板必须传 request
    return templates.TemplateResponse(  # 渲染
        "index.html",  # 模板名
        {"request": request, "project_name": "电商洞察", "version": "1.0"},  # 上下文
    )
```

模板里用 `{{ project_name }}` 插值；静态资源用 `/static/css/style.css`。

---

## 五、文档、异常、CORS、部署

### 5.1 自动文档

- `/docs`：Swagger UI，可直接试接口  
- `/redoc`：更适合阅读的文档页  
- 写好 `summary`、`description`、`Field(description=...)`、`response_model`，文档就好看  

### 5.2 主动抛错与全局处理

```python
from fastapi import HTTPException, Request  # 异常与请求
from fastapi.responses import JSONResponse  # JSON 响应
from fastapi.exceptions import RequestValidationError  # 校验异常

@app.get("/orders/{order_id}")  # 订单详情
def get_order(order_id: int):  # 路径参数
    if order_id <= 0:  # 业务校验
        raise HTTPException(status_code=400, detail="order_id 必须为正整数")  # 400
    if order_id == 999:  # 模拟不存在
        raise HTTPException(status_code=404, detail="订单不存在")  # 404
    return {"order_id": order_id, "status": "paid"}  # 正常返回

@app.exception_handler(RequestValidationError)  # 自定义 422 外观
async def validation_exception_handler(request: Request, exc: RequestValidationError):  # 处理器
    return JSONResponse(  # 统一 JSON
        status_code=422,  # 状态码
        content={"code": 422, "message": "参数校验失败", "detail": exc.errors()},  # 细节
    )
```

### 5.3 CORS（前后端分离常开）

```python
from fastapi.middleware.cors import CORSMiddleware  # 跨域中间件

app.add_middleware(  # 注册中间件
    CORSMiddleware,  # CORS
    allow_origins=["http://localhost:5173"],  # 允许的前端源；生产勿用 *
    allow_credentials=True,  # 是否允许携带 cookie
    allow_methods=["*"],  # 允许方法
    allow_headers=["*"],  # 允许头
)
```

### 5.4 启动与生产要点

开发：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

生产常见：

```bash
gunicorn -c gunicorn.conf.py app.main:app
# worker_class = "uvicorn.workers.UvicornWorker"
```

或：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

前面常再挂 Nginx 做反向代理与静态加速。完整容器化见 Docker 姊妹篇。

---

## 六、综合实战（逐行注释最小 API）

```python
from typing import List, Optional  # 类型
from fastapi import FastAPI, HTTPException, Query  # 框架与异常
from pydantic import BaseModel, Field  # 数据模型
import uvicorn  # 服务器

app = FastAPI(title="商品复习API", version="1.0.0")  # 应用

class ProductIn(BaseModel):  # 创建入参
    name: str = Field(..., min_length=1, max_length=64)  # 名称
    price: float = Field(..., gt=0, description="价格必须大于0")  # 价格
    stock: int = Field(0, ge=0)  # 库存默认 0

class ProductOut(ProductIn):  # 出参多一个 id
    id: int  # 主键

class BaseResp(BaseModel):  # 统一响应
    code: int = 200  # 业务码
    message: str = "ok"  # 消息
    data: Optional[object] = None  # 数据

DB: List[ProductOut] = []  # 内存假数据库
_next_id = 1  # 自增 id

@app.get("/health")  # 健康检查
def health():  # 运维探针常用
    return {"status": "up"}  # 存活

@app.get("/products", response_model=BaseResp)  # 列表
def list_products(
    keyword: Optional[str] = Query(None, description="名称关键词"),  # 可选搜索
    min_price: Optional[float] = Query(None, ge=0),  # 最低价
):
    items = DB  # 先拿全部
    if keyword:  # 有关键词
        items = [p for p in items if keyword in p.name]  # 过滤名称
    if min_price is not None:  # 有最低价
        items = [p for p in items if p.price >= min_price]  # 过滤价格
    return {"code": 200, "message": "ok", "data": items}  # 统一壳

@app.post("/products", response_model=BaseResp, status_code=201)  # 创建
def create_product(body: ProductIn):  # Body 校验
    global _next_id  # 修改全局计数
    product = ProductOut(id=_next_id, **body.model_dump())  # 组装出参
    _next_id += 1  # 自增
    DB.append(product)  # 入库
    return {"code": 201, "message": "created", "data": product}  # 返回

@app.get("/products/{product_id}", response_model=BaseResp)  # 详情
def get_product(product_id: int):  # 路径参数
    for p in DB:  # 线性查找（演示用）
        if p.id == product_id:  # 找到
            return {"code": 200, "message": "ok", "data": p}  # 返回
    raise HTTPException(status_code=404, detail="商品不存在")  # 找不到

@app.delete("/products/{product_id}", response_model=BaseResp)  # 删除
def delete_product(product_id: int):  # 路径参数
    global DB  # 准备改列表
    before = len(DB)  # 原长度
    DB = [p for p in DB if p.id != product_id]  # 过滤掉目标
    if len(DB) == before:  # 没删掉任何东西
        raise HTTPException(status_code=404, detail="商品不存在")  # 404
    return {"code": 200, "message": "deleted", "data": None}  # 成功

if __name__ == "__main__":  # 入口
    uvicorn.run(app, host="127.0.0.1", port=8000)  # 启动
```

建议自测顺序：打开 `/docs` → POST 创建 → GET 列表 → GET 详情 → DELETE → 再查 404。

---

## 七、易错点、自测、练习

### 7.1 易错点

1. 把 `uvicorn main:app` 写成 `main.py:app`。  
2. 路径参数类型写错，却怪 422。  
3. POST JSON 却用 Form 方式提交。  
4. 忘记 `response_model`，把内部字段泄露出去。  
5. 模板渲染忘传 `request`。  
6. 生产环境 `reload=True` 或不限制 CORS `*`。  
7. 同步阻塞大计算塞满事件循环还不加进程/队列。  
8. 业务错误全返回 500，不区分 400/404/422。  
9. 路由里堆 SQL，不分层。  
10. 改代码不重启，又没开 `--reload`。  

### 7.2 自测

1. FastAPI 默认文档地址？  
2. 查询参数和路径参数差别？  
3. Pydantic 校验失败默认状态码？  
4. `response_model` 的两个作用？  
5. `APIRouter` 解决什么问题？  
6. ASGI 服务器常用哪个？  
7. 为什么说 FastAPI 适合数据 API？  

答案：`/docs` 与 `/redoc`；`?a=1` vs `/users/1`；422；文档 + 输出过滤；模块化路由；uvicorn；类型校验与自动文档省事且性能好。

### 7.3 练习

1. 给商品 API 增加 PATCH 改库存。  
2. 增加统一异常处理器，把 `HTTPException` 也包进 `code/message`。  
3. 用 `APIRouter` 拆成 `products.py` / `health.py`。  
4. 对照 `ecommerce_insight_360` 读一条真实路由与 schema。  

---

## 八、速查卡

```text
安装: pip install fastapi uvicorn[standard] pydantic
启动: uvicorn app.main:app --reload
文档: /docs  /redoc
路径参数: /items/{id}
查询参数: ?page=1
Body: Pydantic BaseModel
模块化: APIRouter + include_router
出参安检: response_model=...
鉴权/DB: Depends(...)
静态: app.mount("/static", StaticFiles(...))
模板: Jinja2Templates + TemplateResponse
跨域: CORSMiddleware
生产: gunicorn + UvicornWorker 或 uvicorn --workers N
```

---

## 九、一句话收束

> FastAPI 用类型注解把「校验、文档、序列化」自动化；把 HTTP 方法、参数位置、Pydantic 契约和工程分层吃透，就能稳定写出可维护的数据 API，再配合 Docker 部署上线。
