import re


with open("scammer_data.txt", "r", encoding="utf-8") as f:
    scammer_data = f.read()


scammer_ids = list(set(map(int, re.findall(r'\b\d{9,10}\b', scammer_data))))

pattern = re.compile(r'ID (\b\d{9,10}\b) @([^\s]+)')

scammer_ids_and_usernames = []

for input_string in scammer_data.splitlines():
    match = pattern.search(input_string)
    if match:
        user_id = int(match.group(1))
        username = match.group(2)

        exists = False

        for scammer_id_and_username in scammer_ids_and_usernames:
            if scammer_id_and_username["id"] == user_id:
                exists = True
                break

        if exists:
            continue
        else:
            scammer_ids_and_usernames.append(
                {
                    "id": user_id,
                    "username": username,
                    "number_requests": 1,
                    "is_scam": True
                }
            )

