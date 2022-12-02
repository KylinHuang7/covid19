#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

REASON_IN_CONTROL = 1
REASON_OUT_CONTROL = 2
DISTRICTS = ["万州区", "涪陵区", "渝中区", "大渡口区", "江北区", "沙坪坝区", "九龙坡区", "南岸区",
             "北碚区", "綦江区", "大足区", "渝北区", "巴南区", "黔江区", "长寿区", "江津区",
             "合川区", "永川区", "南川区", "璧山区", "铜梁区", "潼南区", "荣昌区", "开州区",
             "梁平区", "武隆区", "城口县", "丰都县", "垫江县", "忠县", "云阳县", "奉节县",
             "巫山县", "巫溪县", "石柱县", "秀山县", "酉阳县", "彭水县", "万盛经开区"]

def init():
    return "", 0, 0, ""

def parse_total(line):
    map = {}
    pieces = line.split("、")
    for piece in pieces:
        for district in DISTRICTS:
            if district in piece:
                pos = piece.find(district)
                left = piece[pos + len(district):]
                num = re.findall(r"\d+", left)[0]
                map[district] = num
    return map


def parse_patient(line):
    num, left = line.split("，", 1)
    start, end = 0, 0
    if "－" not in num:
        start = end = re.findall(r"\d+", num)[0]
    else:
        p = re.findall(r"\d+", num)
        start = p[0]
        end = p[1]
    reason = REASON_IN_CONTROL
    if "区域核酸检测" in left:
        reason = REASON_OUT_CONTROL
    elif "扩面核酸检测" in left:
        reason = REASON_OUT_CONTROL
    return int(start), int(end), reason

def output(csv, map):
    stack = []
    for district in DISTRICTS:
        if district in map:
            stack.append(map[district])
        else:
            stack.append(0)
    csv.append(",".join([str(x) for x in stack]))

def main():
    with open('daily_chongqing.txt', 'r') as daily:
        lines = daily.readlines()

    district, start, end, reason = init()
    level1_map, level2_map, in_control_map, out_control_map = {}, {}, {}, {}
    csv = []

    for line in lines:
        line = line.strip()
        if "重庆市新增本土确诊病例" in line:
            level1_map = parse_total(line)
            continue
        elif "新增本土无症状感染者" in line:
            level2_map = parse_total(line)
            continue
        hit = False
        for d in DISTRICTS:
            if line.endswith("、" + d):
                district = d
                hit = True
        if hit:
            continue
        if district != "" and line != "":
            start, end, reason = parse_patient(line)
            if district not in in_control_map:
                in_control_map[district] = 0
            if district not in out_control_map:
                out_control_map[district] = 0
            if reason == REASON_IN_CONTROL:
                in_control_map[district] += end - start + 1
            else:
                out_control_map[district] += end - start + 1

    output(csv, level1_map)
    output(csv, level2_map)
    output(csv, in_control_map)
    output(csv, out_control_map)

    csv_full = "\r\n".join(csv)
    with open('chongqing.csv', 'w') as s:
        s.write(csv_full)

main()
