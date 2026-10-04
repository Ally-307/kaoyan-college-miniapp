# 考研院校通 —— 考研信息查询小程序

微信小程序原生前端 + 零第三方依赖 Node.js API（原生 http/sqlite）。目标院校/专业/分数线/
复录比/参考书目一站式查询；已完成国家线与自划线数据采集入库，前端保留本地数据兜底。

- `miniapp/` 微信小程序原生前端
- `server/` 零依赖 Node.js API（`node import_data.js` 重建 SQLite，`node server.js` 启动，默认 127.0.0.1:8010）
