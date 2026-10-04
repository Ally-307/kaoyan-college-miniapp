# Explore 研招网 site structure
import requests
from bs4 import BeautifulSoup
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def explore():
    url = 'https://yz.chsi.com.cn/sch/'
    r = requests.get(url, timeout=10, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Find all province/region sections
    provinces = soup.find_all('div', class_='province-item')
    print(f'Province sections: {len(provinces)}')
    
    # Find all school links
    links = soup.find_all('a')
    school_links = []
    for a in links:
        href = a.get('href', '')
        text = a.get_text(strip=True)
        if '/sch/' in href and text and len(text) > 1 and '下一页' not in text:
            if text not in [s[1] for s in school_links]:
                school_links.append((href, text))
    
    print(f'\nSample school links (first 20):')
    for href, name in school_links[:20]:
        print(f'  {name}: {href}')
    print(f'\nTotal school links from main page: {len(school_links)}')
    
    # Check pagination
    pagination = soup.find('div', class_='pagination')
    if pagination:
        pages = pagination.find_all('a')
        print(f'\nPagination pages: {len(pages)}')
        for p in pages:
            print(f'  {p.get_text(strip=True)}: {p.get("href", "")}')

if __name__ == '__main__':
    explore()
