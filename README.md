# discord_tweetsub

注意事项：

- 使用前需在 `dc.py` 里配置bot的token
- `sub.json` 需和 `dc.py` 在同一目录下
- python需安装依赖库 `requests` 和 `discord.py`
- 添加订阅时的筛选条件仅有 `whitelist` 和 `blacklist` 两种，关键词之间用空格分隔，若筛选条件和关键词为空则默认不进行筛选

使用方法：直接 `python3 dc.py`

# 指令

- `/添加订阅 {频道ID} {推特账号} [{筛选条件} {关键词}]` e.g: 1./添加订阅 111 nezumiironyanko 2./添加订阅 222 Rezero_official blacklist MF J
- `/删除订阅 {订阅ID}` e.g: /删除订阅 1
- `/订阅列表` (注: 删除订阅的订阅ID在这里获取)
