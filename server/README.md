# kaoyan-api

零依赖 Node.js API 服务，使用内置 `node:http` 和 `node:sqlite`。

## 使用

```bash
node import_data.js   # 从 ../miniapp/data/schools.json 重建 SQLite
node server.js        # 启动服务，默认 http://127.0.0.1:8010
```

## 环境变量

| 变量 | 说明 | 默认 |
|------|------|------|
| `PORT` | 服务端口 | `8010` |
| `CACHE_TTL` | 接口缓存秒数 | `30` |

## 说明

- 数据库文件：`data/kaoyan.db`，由 `import_data.js` 生成。
- 接口缓存为内存缓存，服务重启即清空。
- 数据更新后必须重新执行 `node import_data.js`。
