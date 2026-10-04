import json
fp = r"C:\Users\lenovo\Desktop\workspace\project_003_kaoyan-miniapp\miniapp\data\schools.json"
d = json.load(open(fp, "r", encoding="utf-8"))
s = d["schools"]
print(f"学校总数: {len(s)}")
print(f"有专业数据的: {sum(1 for x in s if x.get('majors'))}")
print(f"专业总数: {sum(len(x.get('majors',[])) for x in s)}")
types = {}
for x in s:
    for t in x.get("type",[]):
        types[t] = types.get(t,0)+1
print(f"类型分布: {types}")
print(f"前3所: {[(x['name'], x['province']) for x in s[:3]]}")
with_majors = [x for x in s if x.get("majors")]
if with_majors:
    m = with_majors[0]
    print(f"示例学校: {m['name']}, majors数: {len(m['majors'])}")
    print(f"首个专业: {json.dumps(m['majors'][0], ensure_ascii=False)[:200]}")
