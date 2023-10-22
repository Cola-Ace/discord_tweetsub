import requests
import json
import discord
from discord.ext import commands, tasks

# 自定义模块
from config import *
from logger import logger
from sub import *
from tweet import *

# 配置文件部分
configs = get_config()

dc_token = configs["token"] # discord机器人的token
guild_id = configs["guild_id"] # 频道ID
permission_roles = configs["permission_roles"] # 拥有此权限组的用户视为管理员
nitter_url = configs["nitter_url"] # nitter 源
loop_min = int(configs["loop_min"]) # 检测间隔, 以分钟为间隔

# 权限
def is_admin(roles: list):
    admin = False

    for role in roles:
        if str(role).lstrip().rstrip() in permission_roles:
            admin = True
            break
    
    return admin

# Bot部分
def main():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.command(name="添加订阅")
    async def _sub_add(ctx, *args):
        if not is_admin(ctx.author.roles):
            await ctx.send("权限不足")
            return
        
        if len(args) < 2:
            await ctx.send("命令格式错误")
            return
        
        channel_id = args[0]
        tweetor = args[1]

        channel = bot.get_channel(int(channel_id))
        if channel == None:
            await ctx.send("找不到对应频道")
            return

        status_code = is_tweetor_exist(tweetor, nitter_url)
        if status_code != 200:
            await ctx.send(f"输入推特号有误或订阅服务不可用, 状态码: {status_code}")
            return
        
        filters = []
        if len(args) >= 3:
            for i in range(2, len(args)):
                filter = {}
                keywords = []

                arg = args[i].split(",")
                filter["status"] = arg[0].lstrip("[")
                for k in range(1, len(arg)):
                    keywords.append(arg[k].rstrip("]"))
                filter["keywords"] = keywords

                filters.append(filter)
        
        add_sub(str(channel_id), str(channel.guild.id), tweetor, filters)
        await ctx.send("添加成功")

    @bot.command(name="删除订阅")
    async def _sub_del(ctx, *args):
        if not is_admin(ctx.author.roles):
            await ctx.send("权限不足")
            return
        
        if len(args) != 1:
            await ctx.send("命令格式错误")
            return

        if del_sub(int(args[0]), str(ctx.message.guild.id)) != True:
            await ctx.send("删除订阅失败")
            return

        await ctx.send("已删除订阅")

    @bot.command(name="订阅列表")
    async def _sub_list(ctx):
        if not is_admin(ctx.author.roles):
            await ctx.send("权限不足")
            return
        
        data = get_subs()
        output = ""

        guild_id = str(ctx.message.guild.id) # 过滤非本服务器订阅
        if (guild_id not in data) or (len(data[guild_id]) == 0):
            await ctx.send("当前服务器无订阅")
            return
        
        for i in range(0, len(data[guild_id])):
            channel = bot.get_channel(int(data[guild_id][i]["channel_id"]))
            
            if channel == None:
                continue
            filters = "("
            for filter in data[guild_id][i]["filters"]:
                filters += f'{filter["status"]}: ['
                keywords = ""
                for keyword in filter["keywords"]:
                    keywords += f'{keyword},'
                keywords = keywords.rstrip(",") # 清除多余逗号
                keywords += "]"
                filters += f'{keywords};'

            filters = filters.rstrip(";") # 清除多余分号
            filters += ")"

            output += f'{i + 1}. [@{data[guild_id][i]["tweetor"]}](https://twitter.com/{data[guild_id][i]["tweetor"]}): https://discord.com/channels/{guild_id}/{data[guild_id][i]["channel_id"]} {filters}\n'
        
        embed = discord.Embed(title="Subscriptions", color=0x00FFFF, description=output)
        await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        logger.info(f"当前已登录机器人用户 {bot.user}")
        _detect.start()

    @tasks.loop(minutes=loop_min)
    async def _detect():
        data = get_subs()
        for guild_id in data.keys():
            logger.info(f'正在获取 {guild_id} 的 {len(data[guild_id])} 个订阅')
            for i in range(0, len(data[guild_id])):
                channel = bot.get_channel(int(data[guild_id][i]["channel_id"]))

                if channel == None:
                    logger.warning("获取频道失败")
                    continue

                tweet = get_latest_tweet(data[guild_id][i]["tweetor"], nitter_url)

                if tweet == False:
                    logger.error(f'获取 {data[guild_id][i]["tweetor"]} 的推文失败')
                    continue

                # logger.info(f'tweetor: {data[guild_id][i]["tweetor"]} | 最新推文: {tweet["pubDate"]} | 上次推文: {data[guild_id][i]["latest_tweeted"]}')

                if tweet != False and tweet["pubDate"] != data[guild_id][i]["latest_tweeted"]: # 为最新的推文
                    next_loop = True # 不符合筛选条件的就continue (值为 False 时代表满足所有筛选条件)

                    if len(data[guild_id][i]["filters"]) == 0: # 无筛选条件
                        logger.info(f'tweet: {data[guild_id][i]["tweetor"]} with no filter')

                    no_pass_filter = False # 未满足的筛选条件
                    for filter in data[guild_id][i]["filters"]: # 一个或多个筛选条件 (没有筛选条件时不执行, 默认满足所有筛选条件)
                        if no_pass_filter: # 如果有未满足的筛选条件则直接跳过
                            logger.info("有未满足的筛选条件")
                            next_loop = True
                            break

                        keywords = filter["keywords"] # 关键词提取

                        # whitelist
                        if filter["status"] == "whitelist":
                            logger.info(f'tweet: {data[guild_id][i]["tweetor"]} with a whitelist {json.dumps(keywords)}')
                            find = False
                            for keyword in keywords:
                                if tweet["content"].find(keyword) != -1: # 找到白名单关键词
                                    find = True
                                    break
                            
                            if not find:
                                no_pass_filter = True

                        # blacklist
                        elif filter["status"] == "blacklist":
                            logger.info(f'tweet: {data[guild_id][i]["tweetor"]} with a blacklist {json.dumps(keywords)}')
                            find = False # 是否找到黑名单关键词
                            for keyword in keywords:
                                if tweet["content"].find(keyword) != -1: # 找到黑名单关键词
                                    find = True
                                    break
                                
                            if find: # 如果存在黑名单关键词
                                logger.info(f'twwet: {data[guild_id][i]["tweetor"]} no pass blacklist')
                                no_pass_filter = True
                                
                        # media
                        elif filter["status"] == "media":
                            logger.info(f'tweet: {data[guild_id][i]["tweetor"]} with a media {json.dumps(keywords)}')
                            keyword = filter["keywords"][0]
                            has_image = tweet["full_content"].find("img") != -1
                            has_video = is_tweet_has_video(tweet["src_link"])
                            # 以下筛选条件都与实际代码相反
                            # include image or video
                            # doesn't include image or video
                            # include image
                            # doesn't include image
                            # include video
                            # doesn't include video
                            if ( keyword == "iv" and not has_image and not has_video ):
                                logger.info(f'tweet: {data[guild_id][i]["tweetor"]} no pass media {keyword}')
                                no_pass_filter = True
                            elif ( keyword == "!iv" and (has_image or is_tweet_has_video(tweet["src_link"])) ):
                                logger.info(f'tweet: {data[guild_id][i]["tweetor"]} no pass media {keyword}')
                                no_pass_filter = True
                            elif ( keyword == "i" and not has_image ):
                                logger.info(f'tweet: {data[guild_id][i]["tweetor"]} no pass media {keyword}')
                                no_pass_filter = True
                            elif ( keyword == "!i" and has_image ):
                                logger.info(f'tweet: {data[guild_id][i]["tweetor"]} no pass media {keyword}')
                                no_pass_filter = True
                            elif ( keyword == "v" and not has_video ):
                                logger.info(f'tweet: {data[guild_id][i]["tweetor"]} no pass media {keyword}')
                                no_pass_filter = True
                            elif ( keyword == "!v" and has_video ):
                                logger.info(f'tweet: {data[guild_id][i]["tweetor"]} no pass media {keyword}')
                                no_pass_filter = True
                    
                    if no_pass_filter == False:
                        next_loop = False

                    if next_loop:
                        continue

                    set_latest_tweeted(guild_id, i, tweet["pubDate"])

                    webhook = await channel.create_webhook(name="TweetSub")
                    await webhook.send(f"{tweet['link']}", username=tweet["name"], avatar_url=tweet["avatar"])
                    await webhook.delete()
    
    @_detect.after_loop
    async def _restart_loop():
        _detect.start()

    bot.run(dc_token)


if __name__ == "__main__":
    main()