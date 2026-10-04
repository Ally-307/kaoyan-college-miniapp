import json
fp = r'C:\Users\lenovo\Desktop\workspace\project_003_kaoyan-miniapp\generate_majors.py'
c = open(fp, 'r', encoding='utf-8').read()
# Replace literal backslash+quote with single quotes for dict keys
c = c.replace('\\"schools\\"', "'schools'")
c = c.replace('\\"name\\"', "'name'")
c = c.replace('\\"majors\\"', "'majors'")
open(fp, 'w', encoding='utf-8').write(c)
print('Fixed')
