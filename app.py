from flask import Flask, render_template, request
import requests
import re
import matplotlib.pyplot as plt
import os


app = Flask(__name__)

API_KEY = os.getenv("YOUTUBE_API_KEY")

recent_searches = []


# -----------------------------
# Extract Video ID
# -----------------------------
def extract_video_id(url):

    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"

    match = re.search(regex, url)

    if match:
        return match.group(1)

    return None


# -----------------------------
# Get Channel Data
# -----------------------------
def get_channel_data(channel_id):

    url = "https://www.googleapis.com/youtube/v3/channels"

    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    data = response.json()

    if "items" in data and len(data["items"]) > 0:

        channel = data["items"][0]

        name = channel["snippet"]["title"]

        subs = int(channel["statistics"].get("subscriberCount", 0))
        views = int(channel["statistics"].get("viewCount", 0))
        videos = int(channel["statistics"].get("videoCount", 0))

        logo = channel["snippet"]["thumbnails"]["high"]["url"]

        labels = ["Subscribers","Views","Videos"]
        values = [subs,views,videos]
        colors = ["purple","blue","orange"]

        plt.figure(figsize=(8,5))
        plt.bar(labels,values,color=colors)
        plt.title("Channel Analytics")

        chart_path = os.path.join("static","channel_chart.png")

        plt.savefig(chart_path)
        plt.close()

        return {
            "name": name,
            "subs": f"{subs:,}",
            "views": f"{views:,}",
            "videos": f"{videos:,}",
            "logo": logo
        }

    return None


# -----------------------------
# Get Top Videos
# -----------------------------
def get_top_videos(channel_id):

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part":"snippet",
        "channelId":channel_id,
        "order":"viewCount",
        "maxResults":10,
        "type":"video",
        "key":API_KEY
    }

    response = requests.get(url,params=params)

    data = response.json()

    videos=[]

    if "items" in data:

        for item in data["items"]:

            video_id=item["id"]["videoId"]

            title=item["snippet"]["title"]

            stats_url="https://www.googleapis.com/youtube/v3/videos"

            stats_params={
                "part":"statistics",
                "id":video_id,
                "key":API_KEY
            }

            stats_response=requests.get(stats_url,params=stats_params)

            stats_data=stats_response.json()

            if "items" in stats_data:

                stats=stats_data["items"][0]["statistics"]

                views=int(stats.get("viewCount",0))
                likes=int(stats.get("likeCount",0))
                comments=int(stats.get("commentCount",0))

                videos.append({
                    "title":title,
                    "views":f"{views:,}",
                    "likes":f"{likes:,}",
                    "comments":f"{comments:,}"
                })

    return videos


# -----------------------------
# Main Route
# -----------------------------
@app.route("/",methods=["GET","POST"])
def home():

    video_data=None
    channel_data=None
    top_videos=None

    if request.method=="POST":

        url=request.form["url"]
        analysis_type=request.form["type"]

        # Channel analysis
        if analysis_type=="channel":

            channel_name=url.split("@")[-1]

            search_url="https://www.googleapis.com/youtube/v3/search"

            params={
                "part":"snippet",
                "q":channel_name,
                "type":"channel",
                "maxResults":1,
                "key":API_KEY
            }

            response=requests.get(search_url,params=params)

            data=response.json()

            if "items" in data and len(data["items"])>0:

                channel_id=data["items"][0]["snippet"]["channelId"]

                channel_data=get_channel_data(channel_id)

                top_videos=get_top_videos(channel_id)


        # Video analysis
        if analysis_type=="video":

            video_id=extract_video_id(url)

            if video_id:

                api_url="https://www.googleapis.com/youtube/v3/videos"

                params={
                    "part":"snippet,statistics",
                    "id":video_id,
                    "key":API_KEY
                }

                response=requests.get(api_url,params=params)

                data=response.json()

                if "items" in data and len(data["items"])>0:

                    video=data["items"][0]

                    views=int(video["statistics"]["viewCount"])
                    likes=int(video["statistics"].get("likeCount",0))
                    comments=int(video["statistics"].get("commentCount",0))

                    engagement_rate=((likes+comments)/views)*100

                    labels=["Views","Likes","Comments"]
                    values=[views,likes,comments]
                    colors=["blue","green","red"]

                    plt.figure(figsize=(8,5))
                    plt.bar(labels,values,color=colors)
                    plt.title("Video Engagement Analysis")

                    chart_path=os.path.join("static","chart.png")

                    plt.savefig(chart_path)
                    plt.close()

                    recent_searches.append(video["snippet"]["title"])
                    recent_searches[:] = recent_searches[-5:]

                    video_data={
                        "title":video["snippet"]["title"],
                        "views":f"{views:,}",
                        "likes":f"{likes:,}",
                        "comments":f"{comments:,}",
                        "engagement":round(engagement_rate,2),
                        "thumbnail":video["snippet"]["thumbnails"]["high"]["url"],
                        "video_id":video_id
                    }

    return render_template(
        "index.html",
        video=video_data,
        channel=channel_data,
        top_videos=top_videos,
        recent=recent_searches
    )


if __name__=="__main__":
    app.run(debug=True)