#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

sp = [
    {
        'line': 0,
        'level': 1,
        'keyword': '病例',
        'source_from': '本市闭环隔离管控人员',
        'isolation': '即被隔离管控',
    }, {
        'line': 0,
        'level': 1,
        'keyword': '病例',
        'source_from': '在社区核酸筛查中发现异常',
        'isolation': '即被隔离管控',
    }, {
        'line': 0,
        'level': 1,
        'keyword': '病例',
        'source_from': '此前报告的本土无症状感染者',
        'isolation': '',
    }, {
        'line': 0,
        'level': 2,
        'keyword': '无症状感染者',
        'source_from': '本市闭环隔离管控人员',
        'isolation': '即被隔离管控',
    }, {
        'line': 0,
        'level': 2,
        'keyword': '无症状感染者',
        'source_from': '在社区核酸筛查中发现异常',
        'isolation': '即被隔离管控',
    },
]

with open('daily.txt', 'r') as daily:
    lines = daily.readlines()

for line_no, line in enumerate(lines):
    for i, x in enumerate(sp):
        if x['line'] == 0 and x['source_from'] in line:
            sp[i]['line'] = line_no
            break

sql_prefix = "INSERT INTO daily_input (`level`, district, start_id, end_id, source_from, `isolation`) VALUES\n"
sql = []
for line_no, line in enumerate(lines):
    for i, x in enumerate(sp):
        if line_no < x['line']:
            regex_num = re.compile(r"{0}(\d+)".format(x['keyword']))
            regex_district = re.compile(r"居住于(.*区)")
            match_obj_num = regex_num.findall(line)
            match_obj_district = regex_district.findall(line)
            if match_obj_num and match_obj_district:
                if len(match_obj_num) >= 2:
                    sql.append("""({0}, '{1}', {2}, {3}, '{4}', '{5}')""".format(
                        x['level'], match_obj_district[0], match_obj_num[0], match_obj_num[1],
                        x['source_from'], x['isolation']))
                else:
                    sql.append("""({0}, '{1}', {2}, {3}, '{4}', '{5}')""".format(
                        x['level'], match_obj_district[0], match_obj_num[0], match_obj_num[0],
                        x['source_from'], x['isolation']))
            break

sql_full = sql_prefix + ",\n".join(sql) + ";\n"
with open('daily.sql', 'w') as s:
    s.write(sql_full)

