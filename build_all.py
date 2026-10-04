import json, re, random
random.seed(42)
FP = r'C:\Users\lenovo\Desktop\workspace\project_003_kaoyan-miniapp\miniapp\data\schools.json'
with open(FP, 'r', encoding='utf-8') as f: data = json.load(f)

# ---- Category rules ----
RULES = [
    ('中医药', ['医学']),
    ('财经|经济|金融|经贸|贸易|财政|税务|商', ['经济学', '管理学', '法学']),
    ('工商', ['管理学', '经济学']),
    ('邮电', ['工学', '理学']),
    ('政法|法学|警察|公安|法院', ['法学', '管理学']),
    ('师范|教育|教师', ['教育学', '文学', '理学']),
    ('农业|农林|农学|林业|畜牧|水产', ['农学', '工学', '理学']),
    ('艺术|音乐|美术|戏剧|影视|传媒|新闻|出版', ['艺术学', '文学']),
    ('外语|语言', ['文学', '管理学']),
    ('体育|运动', ['教育学']),
    ('民族', ['法学', '文学', '教育学']),
    ('医|药|临床|护理|口腔|公共卫生|健康|医学', ['医学', '理学']),
    ('海洋|海事', ['工学', '理学']),
    ('石油|化工|地质|矿业|冶金|材料|能源|煤炭', ['工学', '理学']),
    ('航空|航天|民航', ['工学']),
    ('交通|运输|铁道|航海', ['工学', '管理学']),
    ('建筑|土木|水利|测绘|规划|园林', ['工学', '艺术学']),
    ('科技|技术|工业|理工|工程|机械|电力|电子|信息|计算机|自动化|通信', ['工学', '理学', '管理学']),
]
DEFAULT = ['工学', '理学', '管理学', '文学', '经济学']
def get_cats(name, max_c):
    for pat, cats in RULES:
        if re.search(pat, name):
            r = cats[:max_c]
            while len(r) < max_c:
                for c in DEFAULT:
                    if c not in r: r.append(c)
                    if len(r) >= max_c: break
            return r
    return DEFAULT[:max_c]

ALL_985 = {'北京大学','清华大学','浙江大学','复旦大学','上海交通大学','南京大学','武汉大学','华中科技大学','中山大学','四川大学','西安交通大学','哈尔滨工业大学','中国科学技术大学','北京师范大学','中国人民大学','南开大学','天津大学','厦门大学','同济大学','吉林大学','东南大学','山东大学','北京航空航天大学','北京理工大学','国防科技大学','中国农业大学','中央民族大学','西北工业大学','西北农林科技大学','兰州大学','重庆大学','电子科技大学','大连理工大学','东北大学','中南大学','湖南大学','华南理工大学'}
ALL_211 = {'北京交通大学','北京工业大学','北京科技大学','北京化工大学','北京邮电大学','北京林业大学','北京中医药大学','北京外国语大学','中国传媒大学','中央财经大学','对外经济贸易大学','北京体育大学','中国政法大学','华北电力大学','中国矿业大学','中国石油大学','中国地质大学','河海大学','江南大学','南京理工大学','南京航空航天大学','南京农业大学','中国药科大学','郑州大学','武汉理工大学','华中农业大学','华中师范大学','中南财经政法大学','暨南大学','华南师范大学','西南交通大学','西南大学','西南财经大学','西北大学','西安电子科技大学','长安大学','陕西师范大学','上海外国语大学','上海财经大学','华东理工大学','东华大学','上海大学','哈尔滨工程大学','东北师范大学','东北林业大学','辽宁大学','大连海事大学','安徽大学','合肥工业大学','福州大学','南昌大学','中国海洋大学','湖南师范大学','广西大学','海南大学','四川农业大学','贵州大学','云南大学','西藏大学','青海大学','宁夏大学','石河子大学','新疆大学','内蒙古大学','太原理工大学','河北工业大学','天津医科大学'}

EXAM_101 = {'code':'101','name':'思想政治理论','type':'统考','score':100,'order':1}
EXAM_201 = {'code':'201','name':'英语(一)','type':'统考','score':100,'order':2}
EXAM_204 = {'code':'204','name':'英语(二)','type':'统考','score':100,'order':2}
EXAM_301 = {'code':'301','name':'数学(一)','type':'统考','score':150,'order':3}
EXAM_302 = {'code':'302','name':'数学(二)','type':'统考','score':150,'order':3}
EXAM_303 = {'code':'303','name':'数学(三)','type':'统考','score':150,'order':3}
EXAM_396 = {'code':'396','name':'经济类综合能力','type':'统考','score':150,'order':3}
EXAM_199 = {'code':'199','name':'管理类综合能力','type':'统考','score':200,'order':1}

MAJORS = [
    ('081200','计算机科学与技术','工学',[EXAM_101,EXAM_201,EXAM_301],'计算机专业基础综合'),
    ('085400','电子信息','工学',[EXAM_101,EXAM_204,EXAM_302],'电子与通信工程综合'),
    ('080200','机械工程','工学',[EXAM_101,EXAM_201,EXAM_301],'机械设计基础'),
    ('081400','土木工程','工学',[EXAM_101,EXAM_201,EXAM_301],'结构力学'),
    ('081700','化学工程与技术','工学',[EXAM_101,EXAM_201,EXAM_302],'化工原理'),
    ('083500','软件工程','工学',[EXAM_101,EXAM_201,EXAM_301],'软件工程专业基础'),
    ('081100','控制科学与工程','工学',[EXAM_101,EXAM_201,EXAM_301],'自动控制原理'),
    ('080800','电气工程','工学',[EXAM_101,EXAM_201,EXAM_301],'电路原理'),
    ('080500','材料科学与工程','工学',[EXAM_101,EXAM_201,EXAM_302],'材料科学基础'),
    ('083000','环境科学与工程','工学',[EXAM_101,EXAM_201,EXAM_302],'环境工程原理'),
    ('070100','数学','理学',[EXAM_101,EXAM_201],'数学分析'),
    ('070200','物理学','理学',[EXAM_101,EXAM_201],'普通物理'),
    ('070300','化学','理学',[EXAM_101,EXAM_201],'无机化学'),
    ('071000','生物学','理学',[EXAM_101,EXAM_201],'生物化学'),
    ('071400','统计学','理学',[EXAM_101,EXAM_201,EXAM_303],'概率论与数理统计'),
    ('070500','地理学','理学',[EXAM_101,EXAM_201],'自然地理学'),
    ('120200','工商管理','管理学',[EXAM_101,EXAM_201,EXAM_303],'管理学'),
    ('120400','公共管理','管理学',[EXAM_101,EXAM_201,EXAM_303],'公共管理学'),
    ('125100','工商管理硕士(MBA)','管理学',[EXAM_199],'无'),
    ('120100','管理科学与工程','管理学',[EXAM_101,EXAM_201,EXAM_301],'管理信息系统'),
    ('020200','应用经济学','经济学',[EXAM_101,EXAM_201,EXAM_303],'经济学综合'),
    ('025100','金融','经济学',[EXAM_101,EXAM_204,EXAM_396],'金融学综合'),
    ('025200','应用统计','经济学',[EXAM_101,EXAM_204,EXAM_303],'统计学综合'),
    ('030100','法学','法学',[EXAM_101,EXAM_201],'法学综合'),
    ('035101','法律(非法学)','法学',[EXAM_101,EXAM_201],'法律硕士综合'),
    ('030500','马克思主义理论','法学',[EXAM_101,EXAM_201],'马克思主义基本原理'),
    ('030200','政治学','法学',[EXAM_101,EXAM_201],'政治学原理'),
    ('030300','社会学','法学',[EXAM_101,EXAM_201],'社会学理论'),
    ('050200','外国语言文学','文学',[EXAM_101,EXAM_201],'综合外语'),
    ('050300','新闻传播学','文学',[EXAM_101,EXAM_201],'新闻传播实务'),
    ('055200','新闻与传播','文学',[EXAM_101,EXAM_204],'新闻与传播专业基础'),
    ('050100','中国语言文学','文学',[EXAM_101,EXAM_201],'文学综合'),
    ('040100','教育学','教育学',[EXAM_101,EXAM_201],'教育学综合'),
    ('045100','教育','教育学',[EXAM_101,EXAM_204],'教育综合'),
    ('040200','心理学','教育学',[EXAM_101,EXAM_201],'心理学专业综合'),
    ('045400','应用心理','教育学',[EXAM_101,EXAM_204],'心理学专业综合'),
    ('100200','临床医学','医学',[EXAM_101,EXAM_201],'临床医学综合'),
    ('100700','药学','医学',[EXAM_101,EXAM_201],'药学综合'),
    ('105500','药学(专硕)','医学',[EXAM_101,EXAM_204],'药学综合'),
    ('130400','美术学','艺术学',[EXAM_101,EXAM_204],'中外美术史'),
    ('135100','艺术','艺术学',[EXAM_101,EXAM_204],'艺术基础'),
    ('130500','设计学','艺术学',[EXAM_101,EXAM_204],'设计史论'),
    ('090100','作物学','农学',[EXAM_101,EXAM_201],'植物生理学'),
    ('095100','农业','农学',[EXAM_101,EXAM_204],'农业知识综合'),
]
CAT_MAJORS = {}
for m in MAJORS:
    cat = m[2]
    if cat not in CAT_MAJORS: CAT_MAJORS[cat] = []
    CAT_MAJORS[cat].append(m)
CATS_ALL = list(CAT_MAJORS.keys())

def build_major(tpl, sid):
    code, name, cat, exams, self_name = tpl
    subjects = [dict(s) for s in exams]
    if self_name != '无':
        subjects.append({'code':str(random.randint(801,899)),'name':self_name,'type':'自命题','score':150,'order':len(exams)+1})
    total = sum(s['score'] for s in subjects)
    return {
        'id': sid[:8] + '_' + code,
        'name': name, 'code': code, 'category': cat,
        'degreeType': '专业学位' if code[0] == '1' else '学术学位',
        'studyMode': '全日制',
        'initialExam': {'subjects': subjects, 'totalScore': total},
        'reexam': {'ratio': '1.2:1', 'method': '面试'},
        'admissionData': [],
        'duration': '3年', 'tuition': '8000元/年',
    }

count = 0
for s in data['schools']:
    n, sid = s['name'], s['id']
    if n in ALL_985: cats = get_cats(n, 5); per_cat = 5
    elif n in ALL_211: cats = get_cats(n, 4); per_cat = 4
    else: cats = get_cats(n, 3); per_cat = 3
    s['majors'] = []
    for cat in cats:
        pool = CAT_MAJORS.get(cat, [])
        for tpl in pool[:per_cat]:
            s['majors'].append(build_major(tpl, sid))
            count += 1

print('Total majors: ' + str(count) + ' for ' + str(len(data['schools'])) + ' schools')
json_str = json.dumps(data, ensure_ascii=False, indent=2)
with open(FP, 'w', encoding='utf-8') as f: f.write(json_str)
with open(FP.replace('.json','.js'), 'w', encoding='utf-8') as f:
    f.write('var schoolData = ' + json_str + ';\nmodule.exports = schoolData;\n')
print('Saved (' + str(len(json_str)) + ' bytes)')
for kw in ['财经','师范','医','政法','外语','农业','邮电','体育','艺术','民族','海洋']:
    for s in data['schools']:
        if kw in s['name']:
            cats = [m['category'] for m in s['majors']]
            from collections import Counter
            uniq = list(dict.fromkeys(cats))
            print(s['name'] + ': ' + str(uniq) + ' (' + str(len(s['majors'])) + ' majors)')
            break
