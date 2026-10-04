# 研招网数据采集器
import requests, json, time, re
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
session = requests.Session()

def get_provinces():
    """Get all province codes from the main page"""
    r = session.get('https://yz.chsi.com.cn/zsml/dw.do', timeout=10, headers=headers)
    # Extract province codes from Vue template
    matches = re.findall(r'\'(\d{2})\'[^,]+[\'"]([^"\']+省[^"\']*|[^"\']+市|[^"\']+自治区)[\'"]', r.text)
    provinces = []
    for code, name in matches:
        if name and len(code)==2:
            provinces.append((code, name))
    if not provinces:
        # Fallback to common provinces
        provinces = [
            ('11', '北京市'), ('12', '天津市'), ('13', '河北省'), ('14', '山西省'),
            ('15', '内蒙古自治区'), ('21', '辽宁省'), ('22', '吉林省'), ('23', '黑龙江省'),
            ('31', '上海市'), ('32', '江苏省'), ('33', '浙江省'), ('34', '安徽省'),
            ('35', '福建省'), ('36', '江西省'), ('37', '山东省'), ('41', '河南省'),
            ('42', '湖北省'), ('43', '湖南省'), ('44', '广东省'), ('45', '广西壮族自治区'),
            ('46', '海南省'), ('50', '重庆市'), ('51', '四川省'), ('52', '贵州省'),
            ('53', '云南省'), ('54', '西藏自治区'), ('61', '陕西省'), ('62', '甘肃省'),
            ('63', '青海省'), ('64', '宁夏回族自治区'), ('65', '新疆维吾尔自治区')
        ]
    return provinces

def search_schools(ssdm='', dwmc='', xxfs=''):
    """Search for schools via queryAction API"""
    url = 'https://yz.chsi.com.cn/zsml/queryAction.do'
    params = {'ssdm': ssdm, 'dwmc': dwmc, 'xxfs': xxfs, 'pageno': '1'}
    r = session.get(url, params=params, timeout=15, headers=headers)
    r.encoding = 'utf-8'
    return r.text

def parse_school_search(html):
    """Parse school search results to extract schools"""
    soup = BeautifulSoup(html, 'html.parser')
    schools = []
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 3:
            links = tds[1].find_all('a')
            for a in links:
                href = a.get('href', '')
                name = a.get_text(strip=True)
                if href and name:
                    sch_id = ''
                    m = re.search(r'schId-(\d+)', href)
                    if m: sch_id = m.group(1)
                    code = tds[0].get_text(strip=True) if tds else ''
                    if sch_id:
                        schools.append({
                            'schId': sch_id, 'name': name, 'code': code,
                            'detailUrl': href if href.startswith('http') else 'https://yz.chsi.com.cn' + href
                        })
    return schools

def get_school_programs(sch_id, year='2026'):
    """Get all programs for a specific school"""
    url = 'https://yz.chsi.com.cn/zsml/queryAction.do'
    all_programs = []
    for page in range(1, 20):
        params = {'pageno': str(page), 'dwmc': '', 'ssdm': '', 'xxfs': '', 'schId': sch_id}
        r = session.get(url, params=params, timeout=15, headers=headers)
        r.encoding = 'utf-8'
        html = r.text
        programs = parse_programs(html)
        if not programs:
            break
        all_programs.extend(programs)
        time.sleep(0.3)
    return all_programs

def parse_programs(html):
    """Parse ZSML program listing"""
    soup = BeautifulSoup(html, 'html.parser')
    programs = []
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 8:
            cells = [td.get_text(strip=True) for td in tds]
            programs.append({
                'major_code': cells[0] if cells[0] else '',
                'major_name': cells[1] if len(cells) > 1 else '',
                'degree_type': cells[2] if len(cells) > 2 else '',
                'study_mode': cells[3] if len(cells) > 3 else '',
                'direction': cells[4] if len(cells) > 4 else '',
                'exam_subjects': cells[5:9] if len(cells) > 8 else cells[5:]
            })
    return programs

def extract_sch_ids_from_search(html):
    """Extract school IDs from search results"""
    ids = []
    for m in re.finditer(r'schId-(\d+)', html):
        ids.append(m.group(1))
    return list(set(ids))

if __name__ == '__main__':
    # Quick test
    print('Testing queryAction API...')
    result = search_schools(dwmc='清华')
    ids = extract_sch_ids_from_search(result)
    print(f'School IDs found for 清华: {ids[:5]}')
    
    if ids:
        print(f'Getting programs for school ID {ids[0]}...')
        progs = get_school_programs(ids[0])
        print(f'Programs found: {len(progs)}')
        for p in progs[:3]:
            print(f'  {p}')
    print('Done')
    print('Response sample:', result[:500])
