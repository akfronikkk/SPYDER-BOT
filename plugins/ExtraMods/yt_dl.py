import os
import requests
import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

def get_text(message: Message) -> [None, str]:
    text_to_return = message.text
    if message.text is None:
        return None
    if " " not in text_to_return:
        return None
    try:
        return message.text.split(None, 1)[1]
    except IndexError:
        return None

@Client.on_message(filters.command(["video", "mp4", "download"]) & filters.private)
async def download_video(client, message: Message):
    query = get_text(message)
    if not query:
        return await message.reply("Please provide a video name or URL.")
    
    m = await message.reply(f"Searching for {query}...")
    
    try:
        # Searching for the video
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        video_id = results[0]["id"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        thumb_name = f'thumb_{video_id}.jpg'
        
        # Download thumbnail
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
        
        await m.edit("Downloading your video...")
        
        # Download the video
        ydl_opts = {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
            "outtmpl": "%(id)s.%(ext)s",
            "quiet": True,
            "logtostderr": False,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_file = ydl.prepare_filename(info_dict)

        # Send the video
        await client.send_video(
            chat_id=message.chat.id,
            video=video_file,
            caption=f"Title: [{title}]({video_url})\nRequested by: {message.from_user.mention}",
            duration=int(info_dict["duration"]),
            thumb=thumb_name,
            supports_streaming=True,
            reply_to_message_id=message.id,
        )
        
        await m.delete()
    
    except Exception as e:
        await m.edit(f"Error: {str(e)}")
        print(e)
    
    finally:
        # Cleanup
        if os.path.exists(video_file):
            os.remove(video_file)
        if os.path.exists(thumb_name):
            os.remove(thumb_name)

# Run the bot
app = Client("my_bot")
app.run()
