#!/usr/bin/python
# -*- coding: utf-8 -*-

STATUS_UNKNOWN = 0
STATUS_DISTRICT = 1
STATUS_ADDR = 2
DISTRICTS = ["黄浦区", "徐汇区", "长宁区", "静安区", "普陀区", "虹口区", "杨浦区", "闵行区", "宝山区", "嘉定区",
                     "浦东新区", "金山区", "松江区", "青浦区", "奉贤区", "崇明区"]
def init():
    return "", []

def output(csv, district, addrs):
    for addr in addrs:
        csv.append("""{0},{1}""".format(district, addr))

def main():
    with open('address.txt', 'r') as address:
        lines = address.readlines()
    status = STATUS_UNKNOWN
    csv_prefix = "district,address"
    district_map = {}
    district, addrs = init()

    for line in lines:
        line = line.strip()
        if line in DISTRICTS and line not in district_map:
            district = line
            district_map[district] = []
            status = STATUS_DISTRICT
            continue
        if status == STATUS_DISTRICT and line != "" and not line.startswith("202") and "消毒" not in line:
            addrs.append(line.strip("，；、。"))
        elif "消毒" in line:
            status = STATUS_ADDR
            output(district_map[district], district, addrs)
            district, addrs = init()

    csv_full = csv_prefix
    for district in DISTRICTS:
        if district in district_map and len(district_map[district]) > 0:
            csv_full += "\r\n" + "\r\n".join(district_map[district])
        else:
            csv_full += "\r\n{0},".format(district)
    with open('address.csv', 'w') as s:
        s.write(csv_full)

main()
