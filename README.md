# discord_tweetsub

注意事项：

- 使用前需在 `dc.py` 里配置bot的token
- `sub.json` 需和 `dc.py` 在同一目录下
- python需安装依赖库 `requests` 和 `discord.py`

使用方法：直接 `python3 dc.py`

# 指令

- `/添加订阅 {频道ID} {推特账号} [[{筛选条件},{关键词}]]` (e.g: `/添加订阅 111 nezumiironyanko` `/添加订阅 222 Rezero_official [blacklist,MF,J] [media,iv]`)
  - 注1：添加订阅时的筛选条件有 `whitelist` , `blacklist` 和 `media` 三种，关键词之间用逗号 `,` 分隔，若筛选条件和关键词为空则默认不进行筛选
  - 注2：若筛选条件为 `media`，则只需要填入一个关键词，关键词 `iv` `!iv` `i` `!i` `v` `!v` 分别对应 `包含图片或视频` `不包含图片和视频` `包含图片` `不包含图片` `包含视频` `不包含视频`
- `/删除订阅 {订阅ID}` (e.g: `/删除订阅 1`)
- `/订阅列表` (注: 删除订阅的订阅ID在这里获取)
