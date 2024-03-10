import base64
import requests
import asyncio
import httpx
import os
from pytube import YouTube
from pymongo import MongoClient
import cv2



# Connecting to the MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Database']
collection = db['FrameCollection']

def download_youtube_video(url, path):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    video_id = yt.video_id
    stream.download(output_path=path, filename='video.mp4')
    print('Video downloaded successfully.')
    return video_id

def extract_frames(video_path, frame_rate):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    extracted_frames = []
    while success:
        if count % frame_rate == 0:
            frame_path = f"frame_{count}.jpg"
            cv2.imwrite(frame_path, image)
            extracted_frames.append(frame_path)
            print(f"Extracted frame {count}")
        success, image = vidcap.read()
        count += 1
    return extracted_frames

async def encode_frame_to_base64(frame_path):
    with open(frame_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def send_frame_to_api(frame, video_id, api_endpoint):
    frame_base64 = await encode_frame_to_base64(frame)  # await the async function
    payload = {
        'frameData': "data:image/jpeg;base64," + frame_base64,
        'movieName': video_id
    }
    async with httpx.AsyncClient() as client:  # Use httpx.AsyncClient for async requests
        response = await client.post(api_endpoint, json=payload)
        print(f"Frame {frame} sent with status code {response.status_code}")
        # print(response.json())
        if response.json() != []:
            data = response.json()
            data = data[0]
            collection.insert_one(data)
            



if __name__ == "__main__":
    # parameters
    VIDEO_URL = 'https://www.youtube.com/watch?v=GVPzGBvPrzw'  # Replace with the actual video URL
    DOWNLOAD_PATH = '.'  # Current directory
    FRAME_RATE = 30  # Adjust based on how often you want to extract frames
    API_ENDPOINT = 'http://127.0.0.1:5000'  # Replace with your actual API endpoint

    # Download YouTube video and get video ID
    video_id = download_youtube_video(VIDEO_URL, DOWNLOAD_PATH)

    # Extract frames from the downloaded video
    video_path = os.path.join(DOWNLOAD_PATH, 'video.mp4')
    extracted_frames = extract_frames(video_path, FRAME_RATE)

    # Send extracted frames to API
    for frame in extracted_frames:
        asyncio.run(send_frame_to_api(frame, 'GVPzGBvPrzw', API_ENDPOINT))

    # Cleanup: Remove downloaded video and extracted frames
    os.remove(video_path)
    for frame in extracted_frames:
        os.remove(frame)
    for doc in collection.find():
        print(doc)
    client.close()




