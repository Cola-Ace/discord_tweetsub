import requests
import json
import xml.etree.ElementTree as ET
import datetime
import discord
from discord.ext import commands, tasks

# 配置文件部分
dc_token = "" # discord机器人的token
guild_id = "914821735788974120" # 频道ID
loop_min = 1 # 检测间隔, 以分钟为间隔

# 下面的部分不要动

def get_subs():
    file = open("./sub.json", mode="r")
    data = file.read()
    file.close()
    return json.loads(data)

def add_sub(channel_id, tweetor):
    file = open("./sub.json", mode="r")
    data = json.loads(file.read())
    file.close()

    repeat = False
    for i in data:
        if i["channel_id"] == channel_id and i["tweetor"] == tweetor:
            repeat = True
            break

    if repeat != True:
        file = open("./sub.json", mode="w")
        data.append({"channel_id": channel_id, "tweetor": tweetor, "latest_tweeted": ""})
        file.write(json.dumps(data))
        file.close()
    
def del_sub(id):
    file = open("./sub.json", mode="r")
    data = json.loads(file.read())
    file.close()

    if int(id) > len(data):
        return False
    
    del data[int(id) - 1]
    
    file = open("./sub.json", mode="w")
    file.write(json.dumps(data))
    file.close()

    return True

def set_latest_tweeted(index, date):
    file = open("./sub.json", mode="r")
    data = json.loads(file.read())
    file.close()

    data[index]["latest_tweeted"] = date

    file = open("./sub.json", mode="w")
    file.write(json.dumps(data))
    file.close()

# 杂项
class logger:
    def info(msg):
        print(getNowtime() + " [Info] " + msg)
    def error(msg):
        print(getNowtime() + " [Error] " + msg)
    def warning(msg):
        print(getNowtime() + " [Warning] " + msg)

def getNowtime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 获取推文部分
def xml_to_json(xml_string):
    root = ET.fromstring(xml_string)
    return json.dumps({root.tag: xml_to_dict(root)})

def xml_to_dict(element):
    d = {}
    if element.attrib:
        d["@attributes"] = element.attrib
    if element.text:
        d[element.tag] = element.text
    for child in element:
        child_data = xml_to_dict(child)
        if child.tag in d:
            if type(d[child.tag]) is list:
                d[child.tag].append(child_data)
            else:
                d[child.tag] = [d[child.tag], child_data]
        else:
            d[child.tag] = child_data
    return d

def get_latest_tweet(account):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43"
    }
    r = requests.get(f"https://nitter.poast.org/{account}/rss", headers=headers)
    if r.status_code != 200:
        return False
    
    data = json.loads(xml_to_json(r.text))["rss"]["channel"]
    tweet = {
        "pubDate": data["item"][0]["pubDate"]["pubDate"],
        "link": data["item"][0]["link"]["link"].replace("#m", "").replace("nitter.poast.org", "vxtwitter.com"),
        "status": "Tweeted",
        "name": data["title"]["title"].split(" / @")[0],
        "avatar": data["image"]["url"]["url"]
    }
    if data["item"][0]["title"]["title"][0:2] == "RT":
        tweet["status"] = "Retweeted"
    return tweet

def is_tweetor_exist(account):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43"
    }
    r = requests.get(f"https://nitter.poast.org/{account}/rss", headers=headers)
    return r.status_code

# Bot部分
def main():
    # print(get_latest_tweet("Rezero_official"))

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.command(name="添加订阅")
    async def _sub_add(ctx, *args):
        if len(args) != 2:
            await ctx.send("命令格式错误")
            return
        
        channel_id = args[0]
        tweetor = args[1]

        status_code = is_tweetor_exist(tweetor)
        if status_code != 200:
            await ctx.send(f"输入推特号有误或订阅服务不可用, 状态码: {status_code}")
            return
        
        add_sub(channel_id, tweetor)
        await ctx.send("添加成功")

    @bot.command(name="删除订阅")
    async def _sub_del(ctx, *args):
        if len(args) != 1:
            await ctx.send("命令格式错误")
            return

        if del_sub(args[0]) != True:
            await ctx.send("删除订阅失败")
            return

        await ctx.send("已删除订阅")

    @bot.command(name="订阅列表")
    async def _sub_list(ctx):
        data = get_subs()
        output = f"当前订阅如下 (共 {len(data)} 个订阅):\n"
        for i in range(0, len(data)):
            channel = bot.get_channel(int(data[i]["channel_id"]))
            if channel == None:
                continue
            output += f"{i + 1}: 频道: {channel.name} | 订阅ID: {data[i]['tweetor']}\n"
        
        await ctx.send(output)

    @bot.event
    async def on_ready():
        logger.info(f"当前已登录机器人用户 {bot.user}")
        _detect.start()

    @tasks.loop(minutes=loop_min)
    async def _detect():
        data = get_subs()
        for i in range(0, len(data)):
            channel = bot.get_channel(int(data[i]["channel_id"]))

            if channel == None:
                logger.warning("获取频道失败")
                continue

            tweet = get_latest_tweet(data[i]["tweetor"])
            if tweet["pubDate"] != data[i]["latest_tweeted"]:
                logger.info("新推")
                set_latest_tweeted(i, tweet["pubDate"])

                webhook = await channel.create_webhook(name="TweetSub")
                await webhook.send(f"{tweet['link']}", username=tweet["name"], avatar_url=tweet["avatar"])
                await webhook.delete()

    bot.run(dc_token)


if __name__ == "__main__":
    main()
