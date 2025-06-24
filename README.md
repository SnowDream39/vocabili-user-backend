FastAPI Users + Alembic

.env：

```
APP_ENV=development
API_HOST=localhost
PORT=8000
DEBUG=false
ROOT=""
```

## 跨域 Cookies 问题

跨域 Cookies 是一个极其复杂的问题。这里是一套方案，在开发环境下基本可用，使用步骤如下：

1. 在生产环境中（实际网站上）登录，取得 `.vocabili.top` 域下的 Cookie。注意 `CookieTransport` 类的写法。
2. 在开发环境中（任意域名）使用该 Cookie，注意需要配置 axios 的 `withCrediential: true`。

