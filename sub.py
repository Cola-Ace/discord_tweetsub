import json

file_url = "./configs/sub.json"

def get_subs():
    file = open(file_url, mode="r")
    data = file.read()
    file.close()
    return json.loads(data)


def add_sub(channel_id: str, guild: str, tweetor: str, filters=[]):
    file = open(file_url, mode="r")
    data = json.loads(file.read())
    file.close()

    if guild not in data:
        data[guild] = []

    repeat = False
    for i in data[guild]:
        if i["channel_id"] == channel_id and i["tweetor"] == tweetor:
            repeat = True
            break

    if repeat != True:
        file = open(file_url, mode="w")
        data[guild].append({"channel_id": channel_id, "tweetor": tweetor, "latest_tweeted": "", "filters": filters})
        json.dump(data, file)
        file.close()

    
def del_sub(id: int, guild_id: str):
    file = open(file_url, mode="r")
    data = json.loads(file.read())
    file.close()

    if (guild_id not in data) or (id > len(data[guild_id])): # 频道不存在 或 id 超出范围
        return False
    
    del data[guild_id][id - 1]
    
    file = open(file_url, mode="w")
    json.dump(data, file)
    file.close()

    return True


def set_latest_tweeted(guild_id: str, index: int, date: str):
    file = open(file_url, mode="r")
    data = json.loads(file.read())
    file.close()

    data[guild_id][index]["latest_tweeted"] = date

    file = open(file_url, mode="w")
    json.dump(data, file)
    file.close()