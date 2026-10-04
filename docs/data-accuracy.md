# 数据准确性路线

当前数据状态：**不包含随机生成的分数线数据**。

## 现状

- 522 所院校、6752 个专业来自 `collect_data.py` / `build_v2.py` / `final_build.py`。
- 复试线、录取分、报名人数目前**全部为空**，不再随机生成。
- 只有通过 `server/import_verified.py` 导入、且带 `source_url` 和 `updated_at` 的记录才会写入 `admissionData`。

## 要达到“准确”需要做的事

1. 确定权威数据源：
   - 研招网（学校、专业、招生计划）
   - 各校研究生院官网（复试线、拟录取名单）
   - 教育部公开文件（学科评估、双一流名单）
2. 建立采集与清洗流程：
   - 定时抓取 + 人工抽查
   - 数据校验：年份、分数范围、专业代码
   - 每条数据补充 `source`（来源 URL）和 `updatedAt`（更新时间），否则导入会被拒绝
3. 前端标注来源：
   - 专业详情页显示“数据来源：XX官网，更新于 YYYY-MM-DD”
   - 无法确认的数据不要标成官方数据
4. 提供纠错入口：
   - 用户发现错误后提交反馈，后台人工核对后修正

## 导入已验证数据（当前）

1. 在 `data/verified/reexam_lines.csv` 中填写真实数据，格式见表头。
2. 运行导入：

```bash
python server/import_verified.py
```

3. 重新导入数据库并启动服务：

```bash
cd server
node import_data.js
node server.js
```

CSV 模板位于 `data/verified/reexam_lines.csv`。学校按名称、专业按代码匹配；找不到对应院校/专业、缺少 `source_url` 或 `updated_at` 的记录会被跳过并打印原因。

## 后续

- 接入真实数据源后，`/api/meta` 的 `dataStatus` 会变为 `verified-partial`。
- 建议增加数据版本号、增量更新接口和管理后台。
