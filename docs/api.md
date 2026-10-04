# API 文档

服务默认地址：`http://127.0.0.1:8010/api`

所有接口返回统一结构：

```json
{
  "code": 0,
  "message": "ok",
  "data": {},
  "meta": {
    "serverTime": 0,
    "dataVersion": ""
  }
}
```

## 健康检查

`GET /health`

返回服务状态、运行时间和端口。

## 数据元信息

`GET /meta`

返回数据版本、导入时间、院校数、专业数、数据状态提示。

## 筛选选项

`GET /filters`

返回：

- `types`：院校类型及数量
- `regions`：地区及数量
- `provinces`：省份及数量
- `totalSchools`、`totalMajors`

## 院校搜索

`GET /schools/search`

参数：

| 参数 | 说明 |
|------|------|
| `q` | 关键词，匹配院校名/省份/城市 |
| `type` | 院校类型，可传多个，如 `type=985&type=211` |
| `region` | 地区，可传多个 |
| `province` | 省份，可传多个 |
| `page` | 页码，默认 1 |
| `pageSize` | 每页数量，默认 20，最大 100 |

返回 `{ items, total, page, pageSize, hasMore }`。

## 热门院校

`GET /schools/hot?limit=6`

返回 `{ items }`。

## 院校详情

`GET /schools/:id`

返回完整院校对象，包含 `majors` 数组。

## 专业搜索

`GET /majors/search`

参数：

| 参数 | 说明 |
|------|------|
| `q` | 关键词，匹配专业名/代码/学科门类 |
| `schoolId` | 限定院校 |
| `page`、`pageSize` | 分页参数 |

返回 `{ items, total, page, pageSize, hasMore }`。

## 专业详情

`GET /majors/:schoolId/:majorId`

返回 `{ major, school }`。
