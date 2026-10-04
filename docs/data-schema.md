# 考研院校通 - 数据模型文档

## 数据文件位置

`miniapp/data/schools.json`

## 顶层结构

```json
{
  "schools": [ School ]
}
```

## School（院校）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | ✅ | 院校唯一标识 |
| name | string | ✅ | 院校名称 |
| nameEn | string | ❌ | 英文名称 |
| logo | string | ❌ | Logo 图片路径（小程序可用路径） |
| province | string | ✅ | 所在省份 |
| city | string | ✅ | 所在城市 |
| region | string | ✅ | 地区：华北/东北/华东/华中/华南/西南/西北 |
| type | string[] | ✅ | 标签数组，可选值：985/211/双一流/省部共建/普通 |
| department | string | ❌ | 主管单位，如"教育部直属" |
| level | string | ❌ | 办学层次：本科/研究生院 |
| website | string | ❌ | 学校官网 |
| yjsWebsite | string | ❌ | 研究生院官网 |
| phone | string | ❌ | 研招办电话 |
| address | string | ❌ | 地址 |
| intro | string | ❌ | 简介（支持换行） |
| tags | string[] | ❌ | 自定义标签 |
| majors | Major[] | ✅ | 该院校招生专业列表 |

## Major（招生专业/方向）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | ✅ | 专业唯一标识（建议 schoolId_majorCode） |
| name | string | ✅ | 专业名称 |
| code | string | ✅ | 专业代码，如 081200 |
| category | string | ✅ | 学科门类：哲学/经济学/法学/教育学/文学/历史学/理学/工学/农学/医学/军事学/管理学/艺术学/交叉学科 |
| level1Subject | string | ❌ | 一级学科名称 |
| degreeType | string | ✅ | 学术学位 / 专业学位 |
| studyMode | string | ❌ | 全日制 / 非全日制 / 全日制与非全日制 |
| direction | string | ❌ | 研究方向说明 |
| initialExam | object | ✅ | 初试信息 |
| initialExam.subjects | ExamSubject[] | ✅ | 初试科目列表 |
| initialExam.totalScore | number | ❌ | 初试总分，默认 500 |
| reexam | object | ❌ | 复试信息 |
| reexam.subjects | string[] | ❌ | 复试科目/内容 |
| reexam.ratio | string | ❌ | 复录比，如"1.2:1" |
| reexam.method | string | ❌ | 复试方式：笔试+面试/仅面试/笔试+面试+上机等 |
| reexam.scoreWeight | string | ❌ | 复试权重，如"50%" |
| additionalExam | object | ❌ | 加试信息（通常针对同等学力） |
| additionalExam.subjects | string[] | ❌ | 加试科目 |
| additionalExam.note | string | ❌ | 加试说明 |
| references | Reference[] | ❌ | 参考书目/资料 |
| admissionData | YearlyData[] | ❌ | 历年招生数据 |
| duration | string | ❌ | 学制，如"3年" |
| tuition | string | ❌ | 学费，如"8000元/年" |
| scholarship | string | ❌ | 奖学金说明 |
| crossMajorPolicy | string | ❌ | 跨考政策：接受/限制/不接受 |
| equivalentEducationPolicy | string | ❌ | 同等学力报考政策 |
| accommodation | string | ❌ | 住宿情况 |
| contact | object | ❌ | 院系联系方式 |
| contact.department | string | ❌ | 院系名称 |
| contact.phone | string | ❌ | 联系电话 |
| contact.email | string | ❌ | 联系邮箱 |
| contact.website | string | ❌ | 院系网站 |
| notes | string[] | ❌ | 注意事项列表 |
| tags | string[] | ❌ | 自定义标签，如"热门""竞争激烈" |

## ExamSubject（考试科目）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | ✅ | 科目代码，如 101 |
| name | string | ✅ | 科目名称 |
| type | string | ✅ | 考试类型：统考/自命题/全国统考/联考 |
| score | number | ✅ | 科目满分 |
| order | number | ✅ | 考试顺序（第1天上午/下午等） |

## Reference（参考书目）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 书名 |
| author | string | ❌ | 作者 |
| publisher | string | ❌ | 出版社 |
| edition | string | ❌ | 版次 |
| isbn | string | ❌ | ISBN |
| isRequired | boolean | ❌ | 是否必读，默认 true |
| type | string | ❌ | 类型：教材/辅导书/习题集/真题/其他 |

## YearlyData（历年招生数据）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| year | number | ✅ | 年份 |
| reexamLine | number | ❌ | 复试分数线 |
| reexamLineNote | string | ❌ | 分数线说明（如院线/校线区别） |
| minAdmissionScore | number | ❌ | 最低录取分数 |
| maxAdmissionScore | number | ❌ | 最高录取分数 |
| avgAdmissionScore | number | ❌ | 平均录取分数 |
| reexamCount | number | ❌ | 进复试人数 |
| admissionCount | number | ❌ | 录取人数 |
| applicationCount | number | ❌ | 报名人数 |
| note | string | ❌ | 备注 |
| source | string | ✅ | 数据来源 URL，只有带来源的记录才能导入 |
| updatedAt | string | ✅ | 数据更新时间，只有带来源的记录才能导入 |

## 示例

见 `miniapp/data/schools.json` 中的完整示例数据。
