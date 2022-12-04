#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

REASON_IN_CONTROL = 1
REASON_OUT_CONTROL = 2

DISTRICTS = ["罗湖区", "福田区", "南山区", "宝安区", "龙岗区", "盐田区", "龙华区", "坪山区", "光明区", "大鹏新区", "外省"]

def init():
    return {}, 0, 0, ""

def parse_patient(line):
    num, loc = line.split(":")
    start, end = 0, 0
    if "-" not in num:
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
    left = ""
    if "中发现" in loc:
        left = loc
    return int(start), int(end), hit_district, left

def parse_reason(left):
    if "主动就诊" in left:
        return REASON_OUT_CONTROL
    elif "社区筛查" in left:
        return REASON_OUT_CONTROL
    elif "跨区域协查" in left:
        return REASON_OUT_CONTROL
    elif "非闭环管理" in left:
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
    with open('daily_shenzhen.txt', 'r') as daily:
        lines = daily.readlines()

    total_map, in_control_map, out_control_map = {}, {}, {}
    round_map, start, end, reason = init()
    csv = []

    for line in lines:
        line = line.strip()
        if line.startswith("病例") and ":" in line:
            start, end, district, left = parse_patient(line)
            if district not in round_map:
                round_map[district] = 0
            round_map[district] += (end - start + 1)
            if left != "":
                reason = parse_reason(left)
                assign_map(round_map, total_map)
                if reason == REASON_IN_CONTROL:
                    assign_map(round_map, in_control_map)
                else:
                    assign_map(round_map, out_control_map)
                round_map, start, end, reason = init()
        elif "中发现" in line:
            reason = parse_reason(line)
            assign_map(round_map, total_map)
            if reason == REASON_IN_CONTROL:
                assign_map(round_map, in_control_map)
            else:
                assign_map(round_map, out_control_map)
            round_map, start, end, reason = init()

    output(csv, total_map)
    output(csv, in_control_map)
    output(csv, out_control_map)

    csv_full = "\r\n".join(csv)
    with open('shenzhen.csv', 'w') as s:
        s.write(csv_full)
main()
