# discord_tweetsub

注意事项：

- 使用前需在 `dc.py` 里配置bot的token
- `sub.json` 需和 `dc.py` 在同一目录下
- python需安装依赖库 `requests` 和 `discord.py`

使用方法：直接 `python3 dc.py`

# 指令

- `/添加订阅 {频道ID} {推特账号}` e.g: /添加订阅 111 nezumiironyanko
- `/删除订阅 {订阅ID}` e.g: /删除订阅 1
- `/订阅列表` (注: 删除订阅的订阅ID在这里获取)
