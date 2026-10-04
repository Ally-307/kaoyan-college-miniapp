import re
c = open('C:\\Users\\lenovo\\Desktop\\workspace\\project_003_kaoyan-miniapp\\bing.html', 'r', encoding='utf-8').read()
# Find all href URLs
idx = 0
count = 0
while True:
    s = c.find('href="http', idx)
    if s < 0: break
    e = c.find('"', s + 6)
    if e < 0: break
    url = c[s+6:e]
    # Skip common junk
    if not any(k in url for k in ['bing', 'microsoft', 'twitter', 'google', 'facebook', 'instagram']):
        # Get context text
        ctx_end = c.find('<', s)
        ctx_start = c.rfind('>', max(0, s-200), s)
        text = c[ctx_start+1:ctx_end].strip()[:80] if ctx_start > 0 else ''
        print(text + ': ' + url)
        count += 1
    idx = e + 1
print('---')
print('Total links:', count)
