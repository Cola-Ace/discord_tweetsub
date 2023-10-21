import requests
import json
from xml_convert import xml_to_json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43"
}

def get_latest_tweet(account, nitter_url):
    r = requests.get(f"https://{nitter_url}/{account}/rss", headers=headers)
    if r.status_code != 200:
        return False
    
    data = json.loads(xml_to_json(r.text))["rss"]["channel"]
    tweet = {
        "pubDate": data["item"][0]["pubDate"]["pubDate"],
        "link": data["item"][0]["link"]["link"].replace("#m", "").replace(nitter_url, "vxtwitter.com"),
        "name": data["title"]["title"].split(" / @")[0],
        "avatar": data["image"]["url"]["url"],
        "content": data["item"][0]["title"]["title"],
        "full_content": data["item"][0]["description"]["description"],
        "src_link": data["item"][0]["link"]["link"].replace("#m", "")
    }
    if data["item"][0]["title"]["title"][0:2] == "RT":
        tweet["status"] = "Retweeted"
    return tweet

def is_tweetor_exist(account, nitter_url):
    r = requests.get(f"https://{nitter_url}/{account}/rss", headers=headers)
    return r.status_code

def is_tweet_has_video(src_link):
    r = requests.get(src_link, headers=headers)
    result = str(r.content)
    return result.find("<video") != -1