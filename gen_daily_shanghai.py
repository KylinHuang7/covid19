#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

STATUS_UNKNOWN = 0
STATUS_LEVEL_1 = 1 # 确诊
STATUS_LEVEL_2 = 2 # 无症状

SUBSTATUS_UNKNOWN = 0
SUBSTATUS_PATIENT = 1 # 病例
SUBSTATUS_REASON = 2

def init():
    return "", 0, 0, "", "", []
def parse_patient(line, level):
    num, loc = "", ""
    if "居住于" in line:
        num, loc = line.split("居住于")
    elif "暂住于" in line:
        num, loc = line.split("暂住于")
    if num == "" or loc == "":
        raise Exception("parse patient fail 1")
    start, end = 0, 0
    if num.count(level) == 1:
        start = end = re.findall(r"\d+", num)[0]
    elif num.count(level) == 2:
        p = re.findall(r"\d+", num)
        start = p[0]
        end = p[1]
    else:
        raise Exception("parse patient fail 2")
    pos = loc.find("区")
    district = loc[:pos]+"区"
    left = loc[pos+1:].strip("，。；")
    return district, start, end, left

def parse_reason(left):
    if "发现" in left:
        left = left.lstrip("均系").lstrip("系")
        pos = left.find("发现")
        return left[:pos] + "发现"
    elif "阳性" in left:
        left = left.lstrip("以上人员")
        pos = left.find("阳性")
        return left[:pos] + "阳性"

def output(sql, status, tmp, reason):
    for line in tmp:
        district, start, end = line
        sql.append("""({0}, '{1}', {2}, {3}, '{4}', '即被隔离管控')""".format(status, district, start, end, reason))

def main():
    with open('daily_shanghai.txt', 'r') as daily:
        lines = daily.readlines()

    status = STATUS_UNKNOWN
    substatus = SUBSTATUS_UNKNOWN
    district, start, end, left, reason, tmp = init()
    sql_prefix = "INSERT INTO daily_input (`level`, district, start_id, end_id, source_from, `isolation`) VALUES\n"
    sql = []

    for line in lines:
        line = line.strip()
        if line == "本土病例情况":
            status = STATUS_LEVEL_1
            continue
        elif line == "本土无症状感染者情况":
            status = STATUS_LEVEL_2
            continue

        if status == STATUS_LEVEL_1 and line.startswith("病例"):
            district, start, end, left = parse_patient(line, '病例')
            tmp.append([district, start, end])
            substatus = SUBSTATUS_PATIENT
            if left != "":
                reason = parse_reason(left)
                substatus = SUBSTATUS_REASON
                output(sql, status, tmp, reason)
                district, start, end, left, reason, tmp = init()
            continue
        elif status == STATUS_LEVEL_2 and line.startswith("无症状感染者"):
            district, start, end, left = parse_patient(line, "无症状感染者")
            tmp.append([district, start, end])
            substatus = SUBSTATUS_PATIENT
            if left != "":
                reason = parse_reason(left)
                substatus = SUBSTATUS_REASON
                output(sql, status, tmp, reason)
                district, start, end, left, reason, tmp = init()
            continue
        if substatus == SUBSTATUS_PATIENT:
            reason = parse_reason(line)
            substatus = SUBSTATUS_REASON
            output(sql, status, tmp, reason)
            district, start, end, left, reason, tmp = init()

    sql_full = sql_prefix + ",\n".join(sql) + ";\n"
    with open('daily.sql', 'w') as s:
        s.write(sql_full)

main()
