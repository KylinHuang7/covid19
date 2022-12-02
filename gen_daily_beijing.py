#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

STATUS_UNKNOWN = 0
STATUS_LEVEL_1 = 1 # 确诊
STATUS_LEVEL_2 = 2 # 无症状

REASON_IN_CONTROL = 1
REASON_OUT_CONTROL = 2

DISTRICTS = ["东城区", "西城区", "朝阳区", "海淀区", "丰台区", "石景山区", "门头沟区", "房山区",
             "通州区", "顺义区", "昌平区", "大兴区", "怀柔区", "平谷区", "密云区", "延庆区", "经开区"]

def init():
    return {}, 0, 0, ""

def parse_patient(line):
    num, loc = line.split("：")
    start, end = 0, 0
    if "至" not in num:
        start = end = re.findall(r"\d+", num)[0]
    else:
        p = re.findall(r"\d+", num)
        start = p[0]
        end = p[1]
    hit_district = ""
    for district in DISTRICTS:
        if district in loc:
            hit_district = district
            break
    return int(start), int(end), hit_district

def parse_reason(left):
    if "社会面" in left:
        return REASON_OUT_CONTROL
    return REASON_IN_CONTROL

def assign_map(source_map, target_map):
    for k, v in source_map.items():
        if k in target_map:
            target_map[k] += v
        else:
            target_map[k] = v

def output(csv, map):
    stack = []
    for district in DISTRICTS:
        if district in map:
            stack.append(map[district])
        else:
            stack.append(0)
    csv.append(",".join([str(x) for x in stack]))

def main():
    with open('daily_beijing.txt', 'r') as daily:
        lines = daily.readlines()

    status = STATUS_UNKNOWN
    level1_map, level2_map, in_control_map, out_control_map = {}, {}, {}, {}
    round_map, start, end, reason = init()
    csv = []

    for line in lines:
        line = line.strip()
        if line.startswith("确诊病例"):
            status = STATUS_LEVEL_1
            start, end, district = parse_patient(line)
            if district not in round_map:
                round_map[district] = 0
            round_map[district] += (end - start + 1)
        elif line.startswith("无症状感染者"):
            status = STATUS_LEVEL_2
            start, end, district = parse_patient(line)
            if district not in round_map:
                round_map[district] = 0
            round_map[district] += (end - start + 1)
        elif line.startswith("以上"):
            reason = parse_reason(line)
            if status == STATUS_LEVEL_1:
                assign_map(round_map, level1_map)
            else:
                assign_map(round_map, level2_map)
            if reason == REASON_IN_CONTROL:
                assign_map(round_map, in_control_map)
            else:
                assign_map(round_map, out_control_map)
            round_map, start, end, reason = init()

    output(csv, level1_map)
    output(csv, level2_map)
    output(csv, in_control_map)
    output(csv, out_control_map)

    csv_full = "\r\n".join(csv)
    with open('beijing.csv', 'w') as s:
        s.write(csv_full)
main()
