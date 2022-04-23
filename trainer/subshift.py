import os

filename = "사이코지만 괜찮아 1"
result_filename = "Save me 11_fixed.srt"
src_path = os.path.join(f'D:\\langapp\\langapp\\media\\auto_convert', filename)
dest_path = os.path.join(f'D:\\langapp\\langapp\\media\\auto_convert', result_filename)

f = open(src_path, "r", encoding='utf-8')
lines = f.readlines()
result_lines = [line for line in lines]

for i, l in enumerate(lines):
    if i % 4 == 1 and i + 4 < len(lines) - 1:
        result_lines[i + 4] = lines[i]

f.close()
f = open(dest_path, "w+", encoding='utf-8')
f.writelines(result_lines)
f.close()
