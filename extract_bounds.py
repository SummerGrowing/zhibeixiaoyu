import sys

input_file = 'D:/dachuang/4.12_quanwen_qianru.html'

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all template literals (const XXX = `...`)
variables = []
current_var = None
for i, line in enumerate(lines):
    stripped = line.strip()
    if 'const ' in stripped and '= `' in stripped:
        var_name = stripped.split('const ')[1].split(' = ')[0]
        current_var = {'name': var_name, 'start': i, 'end': None}
        variables.append(current_var)
    elif current_var and current_var['end'] is None:
        if stripped == '`;' or stripped == '`':
            current_var['end'] = i

for v in variables:
    if v['name'] in ['KEBIAO_FULL_TEXT', 'GRADE4A_TEACHING_FOCUS_FULL', 'GRADE4A_READING_GUIDE_FULL']:
        print(f"{v['name']}: lines {v['start']+1} to {v['end']+1} ({v['end']-v['start']-1} content lines)")
