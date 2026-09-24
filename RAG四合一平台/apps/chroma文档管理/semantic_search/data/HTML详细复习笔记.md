# HTML 详细复习笔记

> 仿照《集成学习详细笔记》写法：直觉 → 标签体系 → 结构模板 → 与 FastAPI/Jinja 结合 → 易错点 → 自测。  
> 材料对齐：Web 基础 + `ecommerce_insight_360` 模板页常见写法。  
> 示例代码尽量逐行中文注释（HTML 注释用 `<!-- -->`）。  
> 姊妹篇：`FastAPI详细复习笔记.md`、`Docker详细复习笔记.md`。

---

## 〇、这份笔记怎么用

一句话抓住全篇：

> **HTML 是网页的骨架：用标签描述标题、段落、链接、表格、表单；浏览器负责显示，CSS 管颜值，JS 管互动。**

| 章 | 核心问题 |
| --- | --- |
| 一 | HTML 是什么、文档结构 |
| 二 | 常用文本与语义标签 |
| 三 | 链接、图片、列表、表格 |
| 四 | 表单与常见控件 |
| 五 | 布局相关、多媒体、元信息 |
| 六 | 与 FastAPI / Jinja2 联调 |
| 七 | 可访问性与易错点 |
| 八 | 综合页面 + 自测练习 |

建议：用 VS Code / Typora 旁开浏览器直接打开 `.html` 看效果；接 FastAPI 时放到 `templates/`。

---

## 一、总地图

### 1.1 前端三件套

| 技术 | 角色 | 类比 |
| --- | --- | --- |
| HTML | 结构 / 内容 | 房子的梁柱与房间划分 |
| CSS | 样式 | 装修粉刷 |
| JavaScript | 行为 | 水电开关、自动化 |

本笔记聚焦 HTML；在数据大屏项目里常：HTML 搭骨架 → CSS 美化 → JS（如 ECharts）拉 FastAPI 数据。

### 1.2 元素、标签、属性

```html
<a href="https://example.com" target="_blank">官网</a>
```

- 元素：整段 `<a>...</a>`  
- 标签：开始标签 `<a>`、结束标签 `</a>`  
- 属性：`href`、`target`  
- 内容：`官网`  

有的标签自闭合（虚元素）：`<img>`、`<br>`、`<hr>`、`<input>`。

### 1.3 标准文档骨架

```html
<!DOCTYPE html>  <!-- 声明 HTML5 文档 -->
<html lang="zh-CN">  <!-- 根元素，语言简体中文 -->
<head>  <!-- 头部：给浏览器/搜索引擎看的元信息 -->
  <meta charset="UTF-8">  <!-- 字符编码，防中文乱码 -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">  <!-- 移动端适配 -->
  <title>页面标题</title>  <!-- 浏览器标签标题 -->
  <link rel="stylesheet" href="/static/css/style.css">  <!-- 外链 CSS -->
</head>
<body>  <!-- 用户看得见的内容 -->
  <h1>你好，HTML</h1>  <!-- 一级标题 -->
  <p>这是一个段落。</p>  <!-- 段落 -->
  <script src="/static/js/app.js"></script>  <!-- 外链 JS，常放下边加快首屏 -->
</body>
</html>
```

### 1.4 概念卡片

| 概念 | 人话 |
| --- | --- |
| 语义化 | 用恰当标签表达含义，不只全是 `div` |
| 块级元素 | 默认独占一行，如 `div`/`p`/`h1`/`section` |
| 行内元素 | 挤在一行，如 `span`/`a`/`strong` |
| 路径 | 相对路径 `./img/a.png`；绝对路径 `/static/...` |
| DOM | 浏览器把 HTML 解析成的树，JS 可操作它 |

---

## 二、文本与语义结构

### 2.1 标题与段落

```html
<h1>站点主标题（一页通常一个）</h1>  <!-- 权重最高 -->
<h2>章节标题</h2>  <!-- 二级 -->
<h3>小节标题</h3>  <!-- 三级，可继续到 h6 -->
<p>普通段落。段落之间会有间距。</p>  <!-- 段落 -->
<br>  <!-- 换行，少用；结构换行优先用块元素 -->
<hr>  <!-- 主题分隔线 -->
```

### 2.2 强调与标记

```html
<strong>重要强调（语义更重）</strong>  <!-- 重要 -->
<em>语气强调</em>  <!-- 强调 -->
<mark>高亮标记</mark>  <!-- 高亮 -->
<code>print("hi")</code>  <!-- 行内代码 -->
<pre>预格式
  保留空格与换行</pre>  <!-- 预格式块 -->
<blockquote>引用别人的话</blockquote>  <!-- 块引用 -->
```

### 2.3 页面分区（语义化布局）

```html
<header>顶部导航 / 品牌区</header>  <!-- 页头 -->
<nav>导航链接区域</nav>  <!-- 导航 -->
<main>  <!-- 一页一个 main，主内容 -->
  <section>  <!-- 主题分块 -->
    <h2>KPI 概览</h2>  <!-- 区块标题 -->
    <article>可独立成篇的内容卡片</article>  <!-- 文章/卡片 -->
  </section>  <!-- 结束区块 -->
  <aside>侧边栏：相关链接/说明</aside>  <!-- 侧栏 -->
</main>  <!-- 主区结束 -->
<footer>页脚：版权、备案</footer>  <!-- 页脚 -->
```

对照电商大屏：`header.navbar` + `main.dashboard-container` + 多个 `section`。

---

## 三、链接、图片、列表、表格

### 3.1 链接

```html
<a href="https://www.yuque.com">语雀</a>  <!-- 外链 -->
<a href="/docs" target="_blank" rel="noopener noreferrer">API 文档</a>  <!-- 新标签打开 -->
<a href="#kpi">跳到本页锚点</a>  <!-- 页内跳转 -->
<a href="mailto:admin@example.com">发邮件</a>  <!-- 邮件 -->
```

`target="_blank"` 建议加 `rel="noopener noreferrer"` 更安全。

### 3.2 图片

```html
<img
  src="/static/img/logo.png"  <!-- 图片地址 -->
  alt="项目 Logo"  <!-- 替代文本，无障碍与图挂了时用 -->
  width="120"  <!-- 显示宽，正式项目更推荐 CSS 控制 -->
  height="40"  <!-- 显示高 -->
>
```

### 3.3 列表

```html
<ul>  <!-- 无序列表 -->
  <li>苹果</li>  <!-- 项 -->
  <li>香蕉</li>  <!-- 项 -->
</ul>

<ol>  <!-- 有序列表 -->
  <li>注册</li>  <!-- 1 -->
  <li>登录</li>  <!-- 2 -->
  <li>下单</li>  <!-- 3 -->
</ol>

<dl>  <!-- 定义列表 -->
  <dt>GMV</dt>  <!-- 术语 -->
  <dd>成交总额</dd>  <!-- 解释 -->
</dl>
```

### 3.4 表格（报表页常用）

```html
<table>  <!-- 表格 -->
  <thead>  <!-- 表头区 -->
    <tr>  <!-- 行 -->
      <th>日期</th>  <!-- 表头单元格 -->
      <th>订单数</th>  <!-- 表头 -->
      <th>GMV</th>  <!-- 表头 -->
    </tr>
  </thead>
  <tbody>  <!-- 表体 -->
    <tr>  <!-- 数据行 -->
      <td>2026-09-01</td>  <!-- 单元格 -->
      <td>128</td>  <!-- 单元格 -->
      <td>35600</td>  <!-- 单元格 -->
    </tr>
  </tbody>
</table>
```

复杂表可用 `colspan` / `rowspan` 合并单元格；样式交给 CSS。

---

## 四、表单（前后端联调重点）

### 4.1 表单骨架

```html
<form action="/api/login" method="post">  <!-- 提交地址与方法 -->
  <label for="username">用户名</label>  <!-- 点击文字聚焦输入框 -->
  <input id="username" name="username" type="text" required>  <!-- 文本框，必填 -->

  <label for="password">密码</label>  <!-- 密码标签 -->
  <input id="password" name="password" type="password" minlength="6" required>  <!-- 密码框 -->

  <button type="submit">登录</button>  <!-- 提交 -->
  <button type="reset">重置</button>  <!-- 清空 -->
</form>
```

关键：`name` 才会作为字段名发给后端；只有 `id` 不够。

### 4.2 常见 input 类型

| type | 用途 |
| --- | --- |
| text | 普通文本 |
| password | 密码 |
| email | 邮箱（带基础格式提示） |
| number | 数字 |
| date | 日期 |
| checkbox | 多选 |
| radio | 单选（同名一组） |
| file | 上传文件 |
| hidden | 隐藏字段 |
| submit | 提交按钮（也可用 button） |

```html
<label><input type="radio" name="pay" value="wechat" checked> 微信</label>  <!-- 单选默认微信 -->
<label><input type="radio" name="pay" value="alipay"> 支付宝</label>  <!-- 单选 -->

<label><input type="checkbox" name="agree" value="1" required> 同意协议</label>  <!-- 多选/同意 -->

<select name="city">  <!-- 下拉框 -->
  <option value="bj">北京</option>  <!-- 选项 -->
  <option value="sh" selected>上海</option>  <!-- 默认选中 -->
</select>

<textarea name="remark" rows="4" cols="40" placeholder="备注"></textarea>  <!-- 多行文本 -->
```

### 4.3 GET 表单 vs POST 表单

| method | 数据去哪 | 适合 |
| --- | --- | --- |
| GET | 拼到 URL 查询串 | 搜索、筛选 |
| POST | 请求体 | 登录、创建、上传 |

FastAPI 侧：JSON API 多用 `fetch` 发 JSON；传统表单可能是 `Form(...)` 或模板页提交。

---

## 五、布局容器、多媒体、元信息

### 5.1 div 与 span

```html
<div class="kpi-card">  <!-- 块级盒子，布局主力，但别滥用替代语义标签 -->
  <span class="kpi-title">累计订单</span>  <!-- 行内片段 -->
  <div class="kpi-value" id="kpiOrders">--</div>  <!-- 给 JS 填数预留 id -->
</div>
```

### 5.2 多媒体

```html
<video src="/static/demo.mp4" controls width="480"></video>  <!-- 视频，controls 显示控件 -->
<audio src="/static/notify.mp3" controls></audio>  <!-- 音频 -->
<iframe src="https://example.com" width="600" height="300" title="嵌入页"></iframe>  <!-- 内嵌页 -->
```

### 5.3 有用的 head 元信息

```html
<meta charset="UTF-8">  <!-- 编码 -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">  <!-- 响应式视口 -->
<meta name="description" content="电商数据洞察平台">  <!-- SEO 描述 -->
<link rel="icon" href="/static/favicon.ico">  <!-- 网站图标 -->
```

---

## 六、和 FastAPI / Jinja2 一起用

### 6.1 模板变量

FastAPI 传入：

```python
return templates.TemplateResponse(
    "index.html",
    {"request": request, "project_name": "电商洞察", "version": "1.0"},
)
```

模板：

```html
<title>{{ project_name }} - 数据平台</title>  <!-- 插入变量 -->
<h1 class="brand-title">{{ project_name }}</h1>  <!-- 品牌名 -->
<span>版本 v{{ version }}</span>  <!-- 版本号 -->
```

### 6.2 条件与循环（Jinja）

```html
{% if user %}  <!-- 条件：已登录 -->
  <p>你好，{{ user.name }}</p>  <!-- 显示用户名 -->
{% else %}  <!-- 否则 -->
  <a href="/login">请登录</a>  <!-- 登录入口 -->
{% endif %}  <!-- 结束条件 -->

<ul>  <!-- 列表 -->
  {% for item in products %}  <!-- 循环商品 -->
    <li>{{ item.name }} - ¥{{ item.price }}</li>  <!-- 一项 -->
  {% endfor %}  <!-- 结束循环 -->
</ul>
```

### 6.3 静态资源路径

```html
<link rel="stylesheet" href="/static/css/style.css">  <!-- CSS -->
<script src="/static/js/dashboard.js"></script>  <!-- JS -->
<img src="/static/img/logo.png" alt="logo">  <!-- 图片 -->
```

对应 FastAPI：

```python
app.mount("/static", StaticFiles(directory="app/static"), name="static")
```

### 6.4 页面先出骨架，JS 再填数（大屏常见）

```html
<div class="kpi-value" id="kpiGmv">¥ --</div>  <!-- 占位 -->
<script>  <!-- 简化示例：真实项目常写在独立 js 文件 -->
  // 向 FastAPI 拉 KPI
  fetch("/api/sales/overview")  // 请求后端
    .then(r => r.json())  // 转 JSON
    .then(res => {  // 成功回调
      document.getElementById("kpiGmv").textContent = "¥ " + res.data.gmv;  // 填数
    });
</script>
```

HTML 负责坑位（带 `id`），JS 负责把 API 数据塞进去。

---

## 七、可访问性、语义、易错点

### 7.1 好习惯

1. 图片写有意义的 `alt`。  
2. 表单控件配 `<label for=...>`。  
3. 标题按层级，不要为了「字大」乱跳 `h1→h4`。  
4. 按钮用 `<button>`，链接用 `<a>`，别混用语义。  
5. 颜色对比度足够（偏 CSS，但结构别只靠颜色表达状态）。  

### 7.2 易错点

1. 中文乱码：忘了 `<meta charset="UTF-8">`。  
2. 标签没闭合，结构错乱。  
3. 表单控件没有 `name`，后端收不到。  
4. 路径写错：相对路径在嵌套路由下失效，静态资源优先用 `/static/...`。  
5. 块级元素塞进 `<p>` 等非法嵌套。  
6. 把全部布局只堆 `div`，失去语义与可维护性。  
7. Jinja 变量当普通 HTML 写，忘了 `{{ }}`。  
8. 外链 JS 放 head 又阻塞渲染（可 `defer` 或改到 body 末尾）。  
9. `id` 重复，JS 只找得到第一个。  
10. 直接拼接用户输入进 HTML 造成 XSS（模板自动转义别乱用 `|safe`）。  

---

## 八、综合页面示例（可保存为 `demo.html`）

```html
<!DOCTYPE html>  <!-- HTML5 -->
<html lang="zh-CN">  <!-- 中文页 -->
<head>  <!-- 头 -->
  <meta charset="UTF-8">  <!-- 编码 -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">  <!-- 视口 -->
  <title>复习用仪表盘骨架</title>  <!-- 标题 -->
  <style>  <!-- 演示用内联样式；正式项目请外链 CSS -->
    body { font-family: sans-serif; margin: 0; background: #f6f8fb; }  /* 页底色 */
    header { background: #0f766e; color: #fff; padding: 16px 24px; }  /* 顶栏 */
    main { padding: 24px; display: grid; gap: 16px; grid-template-columns: repeat(3, 1fr); }  /* 三列卡片 */
    .card { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,.06); }  /* 卡片 */
    table { width: 100%; border-collapse: collapse; background: #fff; }  /* 表 */
    th, td { border: 1px solid #e5e7eb; padding: 8px; text-align: left; }  /* 单元格 */
    footer { padding: 16px 24px; color: #666; }  /* 页脚 */
  </style>  <!-- 样式结束 -->
</head>  <!-- 头结束 -->
<body>  <!-- 体 -->
  <header>  <!-- 页头 -->
    <h1>电商数据复习页</h1>  <!-- 主标题 -->
    <nav>  <!-- 导航 -->
      <a href="#kpi" style="color:#fff;margin-right:12px;">指标</a>  <!-- 锚点 -->
      <a href="#table" style="color:#fff;margin-right:12px;">表格</a>  <!-- 锚点 -->
      <a href="#form" style="color:#fff;">筛选</a>  <!-- 锚点 -->
    </nav>  <!-- 导航结束 -->
  </header>  <!-- 页头结束 -->

  <main id="kpi">  <!-- 主区 KPI -->
    <section class="card">  <!-- 卡片1 -->
      <h2>GMV</h2>  <!-- 标题 -->
      <p id="kpiGmv">¥ --</p>  <!-- JS 可填 -->
    </section>  <!-- 结束 -->
    <section class="card">  <!-- 卡片2 -->
      <h2>订单数</h2>  <!-- 标题 -->
      <p id="kpiOrders">--</p>  <!-- 占位 -->
    </section>  <!-- 结束 -->
    <section class="card">  <!-- 卡片3 -->
      <h2>转化率</h2>  <!-- 标题 -->
      <p id="kpiCvr">--%</p>  <!-- 占位 -->
    </section>  <!-- 结束 -->
  </main>  <!-- 主区结束 -->

  <section id="table" class="card" style="margin:0 24px 16px;">  <!-- 表格区 -->
    <h2>近三日订单</h2>  <!-- 标题 -->
    <table>  <!-- 表 -->
      <thead>  <!-- 头 -->
        <tr><th>日期</th><th>订单</th><th>GMV</th></tr>  <!-- 表头行 -->
      </thead>  <!-- 头结束 -->
      <tbody>  <!-- 体 -->
        <tr><td>2026-09-01</td><td>120</td><td>30000</td></tr>  <!-- 行1 -->
        <tr><td>2026-09-02</td><td>132</td><td>34500</td></tr>  <!-- 行2 -->
        <tr><td>2026-09-03</td><td>128</td><td>33100</td></tr>  <!-- 行3 -->
      </tbody>  <!-- 体结束 -->
    </table>  <!-- 表结束 -->
  </section>  <!-- 表格区结束 -->

  <section id="form" class="card" style="margin:0 24px 24px;">  <!-- 表单区 -->
    <h2>筛选条件</h2>  <!-- 标题 -->
    <form action="/dashboard" method="get">  <!-- GET 筛选 -->
      <label for="start">开始日期</label>  <!-- 标签 -->
      <input id="start" name="start" type="date">  <!-- 日期 -->
      <label for="end">结束日期</label>  <!-- 标签 -->
      <input id="end" name="end" type="date">  <!-- 日期 -->
      <button type="submit">查询</button>  <!-- 提交 -->
    </form>  <!-- 表单结束 -->
  </section>  <!-- 表单区结束 -->

  <footer>  <!-- 页脚 -->
    <small>仅供 HTML 复习演示 · 数据为静态示例</small>  <!-- 说明 -->
  </footer>  <!-- 页脚结束 -->

  <script>  <!-- 演示填数 -->
    document.getElementById("kpiGmv").textContent = "¥ 97,600";  // 填 GMV
    document.getElementById("kpiOrders").textContent = "380";  // 填订单
    document.getElementById("kpiCvr").textContent = "3.2%";  // 填转化
  </script>  <!-- 脚本结束 -->
</body>  <!-- 体结束 -->
</html>  <!-- 文档结束 -->
```

---

## 九、自测与练习

### 9.1 自测

1. `head` 和 `body` 分别放什么？  
2. 为什么要 `charset=UTF-8`？  
3. `ul`/`ol`/`dl` 差别？  
4. 表单字段怎样才能被提交？  
5. `div` 和 `section` 选用直觉？  
6. Jinja 插值语法？  
7. 静态文件在 FastAPI 里通常挂载到哪？  

答案：元信息 vs 可见内容；防乱码；无序/有序/术语定义；靠 `name`；无语义盒子 vs 有主题区块；`{{ var }}`；`/static`。

### 9.2 练习

1. 手写一个「个人简历页」：header、经历列表、技能表格、联系表单。  
2. 把综合示例改成 Jinja 模板，用 FastAPI 传入标题和表格数据。  
3. 给所有图片补 `alt`，给表单补完整 `label`。  
4. 用 `fetch` 调用你写的 FastAPI `/health`，在页面显示状态。  

---

## 十、速查卡

```text
文档声明: <!DOCTYPE html>
根: <html lang="zh-CN">
头: charset / viewport / title / link / script
结构: header nav main section article aside footer
文本: h1~h6 p strong em code pre
链接图片: a img (记得 alt)
列表: ul ol dl
表格: table thead tbody tr th td
表单: form label input select textarea button（关键 name）
布局盒: div span
模板: {{ var }}  {% if %}  {% for %}
静态: /static/...
```

---

## 十一、一句话收束

> HTML 搭的是页面骨架与语义；写清结构、表单与静态资源路径后，再交给 CSS/JS 与 FastAPI 接口，就能做出可维护的数据页与大屏，而不是一堆难读的标签堆砌。
