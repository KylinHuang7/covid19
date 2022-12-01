#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

STATUS_UNKNOWN = 0
STATUS_LEVEL_1 = 1 # 确诊
STATUS_LEVEL_2 = 2 # 无症状

REASON_IN_CONTROL = 1
REASON_OUT_CONTROL = 2

DISTRICTS = ["荔湾区", "越秀区", "海珠区", "天河区", "白云区", "黄埔区", "番禺区",
             "花都区", "南沙区", "从化区", "增城区", "集中隔离场所"]

def init():
    return {}, 0, 0, ""

def parse_patient(line):
    num, loc = line.split("：")
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
    pos = loc.find("。")
    left = loc[pos + 1:].strip()
    return int(start), int(end), hit_district, left

def parse_reason(left):
    if "主动就诊" in left:
        return REASON_OUT_CONTROL
    elif "社区筛查" in left:
        return REASON_OUT_CONTROL
    elif "跨区域协查" in left:
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
    with open('daily_guangzhou.txt', 'r') as daily:
        lines = daily.readlines()

    status = STATUS_UNKNOWN
    level1_map, level2_map, in_control_map, out_control_map = {}, {}, {}, {}
    round_map, start, end, reason = init()
    csv = []

    for line in lines:
        line = line.strip()
        if line.startswith("本土确诊病例"):
            status = STATUS_LEVEL_1
            start, end, district, left = parse_patient(line)
            if district not in round_map:
                round_map[district] = 0
            round_map[district] += (end - start + 1)
            if "集中隔离场所" in line or left != "":
                reason = parse_reason(left)
                assign_map(round_map, level1_map)
                if reason == REASON_IN_CONTROL:
                    assign_map(round_map, in_control_map)
                else:
                    assign_map(round_map, out_control_map)
                round_map, start, end, reason = init()
        elif line.startswith("本土无症状感染者"):
            status = STATUS_LEVEL_2
            start, end, district, left = parse_patient(line)
            if district not in round_map:
                round_map[district] = 0
            round_map[district] += (end - start + 1)
            if "集中隔离场所" in line or left != "":
                reason = parse_reason(left)
                assign_map(round_map, level2_map)
                if reason == REASON_IN_CONTROL:
                    assign_map(round_map, in_control_map)
                else:
                    assign_map(round_map, out_control_map)
                round_map, start, end, reason = init()
        elif line.startswith("上述"):
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
    with open('guangzhou.csv', 'w') as s:
        s.write(csv_full)
main()
