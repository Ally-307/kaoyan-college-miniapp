# -*- coding: utf-8 -*-
import requests, json, time, sys, re
from bs4 import BeautifulSoup
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
session = requests.Session()
PROVINCES = [('11','北京'),('12','天津'),('13','河北'),('14','山西'),
('15','内蒙古'),('21','辽宁'),('22','吉林'),('23','黑龙江'),
('31','上海'),('32','江苏'),('33','浙江'),('34','安徽'),
('35','福建'),('36','江西'),('37','山东'),('41','河南'),
('42','湖北'),('43','湖南'),('44','广东'),('45','广西'),
('46','海南'),('50','重庆'),('51','四川'),('52','贵州'),
('53','云南'),('54','西藏'),('61','陕西'),('62','甘肃'),
('63','青海'),('64','宁夏'),('65','新疆')]
ALL_985 = {'北京大学','清华大学','浙江大学','复旦大学','上海交通大学','南京大学',
'武汉大学','华中科技大学','中山大学','四川大学','西安交通大学','哈尔滨工业大学',
'中国科学技术大学','北京师范大学','中国人民大学','南开大学','天津大学','厦门大学',
'同济大学','吉林大学','东南大学','山东大学','北京航空航天大学','北京理工大学',
'国防科技大学','中国农业大学','中央民族大学','西北工业大学','西北农林科技大学',
'兰州大学','重庆大学','电子科技大学','大连理工大学','东北大学','中南大学','湖南大学','华南理工大学'}
ALL_211 = {'北京交通大学','北京工业大学','北京科技大学','北京化工大学','北京邮电大学',
'北京林业大学','北京中医药大学','北京外国语大学','中国传媒大学','中央财经大学',
'对外经济贸易大学','北京体育大学','中国政法大学','华北电力大学','河北工业大学',
'中国矿业大学','中国石油大学','中国地质大学','中央音乐学院','河海大学','江南大学',
'南京理工大学','南京航空航天大学','南京农业大学','中国药科大学','郑州大学',
'武汉理工大学','华中农业大学','华中师范大学','中南财经政法大学','暨南大学',
'华南师范大学','西南交通大学','西南大学','西南财经大学','西北大学','西安电子科技大学',
'长安大学','陕西师范大学','上海外国语大学','上海财经大学','华东理工大学','东华大学',
'上海大学','第二军医大学','哈尔滨工程大学','东北师范大学','东北林业大学',
'延边大学','辽宁大学','大连海事大学','安徽大学','合肥工业大学','福州大学',
'南昌大学','中国海洋大学','湖南师范大学','华南师范大学','广西大学','海南大学',
'四川农业大学','贵州大学','云南大学','西藏大学','青海大学','宁夏大学',
'石河子大学','新疆大学','内蒙古大学','太原理工大学','天津医科大学'}
def get_type(n):
    if n in ALL_985: return ['985','211','双一流']
    if n in ALL_211: return ['211','双一流']
    return ['普通']
def get_region(p):
    if p in ['北京','天津','河北','山西','内蒙古']: return '华北'
    if p in ['辽宁','吉林','黑龙江']: return '东北'
    if p in ['上海','江苏','浙江','安徽','福建','江西','山东']: return '华东'
    if p in ['河南','湖北','湖南']: return '华中'
    if p in ['广东','广西','海南']: return '华南'
    if p in ['重庆','四川','贵州','云南','西藏']: return '西南'
    if p in ['陕西','甘肃','青海','宁夏','新疆']: return '西北'
    return ''
if __name__ == '__main__':
    print('Collecting schools from yz.chsi.com.cn...')
    seen = set(); schools = []
    for code, name in PROVINCES:
        cnt = 0
        for page in range(1, 50):
            url = f'https://yz.chsi.com.cn/sch/search.do?ssdm={code}&pageno={page}'
            r = session.get(url, timeout=15, headers=headers)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            found = 0
            for a in soup.find_all('a', href=True):
                m = re.search(r'/sch/schoolInfo--schId-(\d+)', a['href'])
                if m:
                    txt = a.get_text(strip=True)
                    if txt and len(txt)>1 and txt not in ['招生简章','调剂办法','院校信息']:
                        sid = m.group(1)
                        if sid not in seen:
                            seen.add(sid); schools.append({'schId':sid,'name':txt,'province':name}); cnt+=1; found+=1
            if found == 0: break
            time.sleep(0.2)
        print(f'  {name}: {cnt}')
    print(f'\nTotal: {len(schools)} schools')
    data = {'schools': []}
    for s in schools:
        data['schools'].append({'id':s['schId'],'name':s['name'],'province':s['province'],
            'city':'','region':get_region(s['province']),'type':get_type(s['name']),'intro':'','tags':[],'majors':[]})
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    fp = r"C:\Users\lenovo\Desktop\workspace\project_003_kaoyan-miniapp\miniapp\data\schools.json"
    with open(fp, 'w', encoding='utf-8') as f: f.write(json_str)
    with open(fp.replace('.json','.js'), 'w', encoding='utf-8') as f:
        f.write("var schoolData = " + json_str + ";\nmodule.exports = schoolData;\n")
    types = {}
    for s in data['schools']:
        for t in s['type']: types[t] = types.get(t, 0) + 1
    c985 = types.get('985', 0); c211 = types.get('211', 0); cnormal = types.get('普通', 0)
    print('985: ' + str(c985) + ', 211: ' + str(c211) + ', 普通: ' + str(cnormal))
    print('Saved! ' + str(len(data['schools'])) + ' schools')
    for s in data['schools'][:5]:
        print('  ' + s['name'] + ' | ' + s['province'] + ' | ' + str(s['type']))
