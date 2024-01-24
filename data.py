import re


with open("scammer_data.txt", "r", encoding="utf-8") as f:
    scammer_data = f.read()
    print(scammer_data)


scammer_ids = list(set(map(int, re.findall(r'\b\d{9,10}\b', scammer_data))))
