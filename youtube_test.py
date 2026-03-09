import requests

API_KEY = "AIzaSyDvKuBS1S5qcdVNRChcMvP0W_-NXlJPq98"

video_id = "dQw4w9WgXcQ"

url = "https://www.googleapis.com/youtube/v3/videos"

params = {
    "part": "snippet,statistics",
    "id": video_id,
    "key": API_KEY
}

response = requests.get(url, params=params)
data = response.json()

video = data["items"][0]

title = video["snippet"]["title"]
views = video["statistics"]["viewCount"]
likes = video["statistics"].get("likeCount", "N/A")
comments = video["statistics"].get("commentCount", "N/A")

print("Title:", title)
print("Views:", views)
print("Likes:", likes)
print("Comments:", comments)