import json

def get_config():
    file = open("./configs/configs.json", "r")
    data = file.read()
    file.close()
    return json.loads(data)