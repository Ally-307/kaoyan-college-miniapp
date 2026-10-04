import hashlib, struct, os, sys
sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', closefd=False)

path = r'C:\Users\lenovo\Documents\WeChat Files\Applet\wxdcd3d073e47d1742\287\__APP__.wxapkg'
out_dir = r'C:\Users\lenovo\Desktop\workspace\project_003_kaoyan-miniapp\unpacked_miniapp'

with open(path, 'rb') as f:
    data = f.read()
print('File size:', len(data))

keys = [
    b'The-ether-queen-uplink-version-one!',
    hashlib.md5(b'wxdcd3d073e47d1742').digest(),
]

for key in keys:
    dec = bytearray(len(data))
    for i in range(len(data)):
        dec[i] = data[i] ^ key[i % len(key)]
    count = dec[0]
    if count < 100 and count > 0:
        print('Key OK: count=' + str(count))
        pos = 1
        files = []
        for _ in range(count):
            nl = dec[pos]; pos += 1
            name = bytes(dec[pos:pos+nl]); pos += nl
            off = struct.unpack('<I', bytes(dec[pos:pos+4]))[0]
            sz = struct.unpack('<I', bytes(dec[pos+4:pos+8]))[0]
            pos += 8
            files.append((name, off, sz, nl))
        print('Files:', len(files))
        # Try to extract with filename XOR key offset
        os.makedirs(out_dir, exist_ok=True)
        for name, off, sz, nl in files:
            found = False
            for ko in range(20):
                fname = bytes([b ^ key[(ko + i) % len(key)] for i, b in enumerate(name)])
                try:
                    fname_s = fname.decode('utf-8')
                    if '/' in fname_s or '.js' in fname_s or '.json' in fname_s or '.wxss' in fname_s or '.wxml' in fname_s or '.html' in fname_s:
                        content = bytes([data[off + i] ^ key[(off + i) % len(key)] for i in range(min(sz, len(data) - off))])
                        fp = os.path.join(out_dir, fname_s.lstrip('/').replace('\\', '/'))
                        os.makedirs(os.path.dirname(fp), exist_ok=True)
                        with open(fp, 'wb') as fw: fw.write(content)
                        print('  OK: ' + fname_s + ' (' + str(sz) + 'B)')
                        found = True
                        break
                except:
                    pass
            if not found:
                print('  FAIL: ' + name.hex() + ' (tried ' + str(len(key)) + ' offsets)')
        break
    else:
        print('Key fail: first_byte=' + str(count))
print('Done')
