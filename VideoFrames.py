import base64
import requests
import asyncio
import httpx
import os
from pytube import YouTube
from pymongo import MongoClient
import cv2
from dotenv import load_dotenv


load_dotenv()

# Retrieve environment variables
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")  # Assuming it's already URL-encoded
cluster_address = os.getenv("MONGO_CLUSTER_ADDRESS")
database = os.getenv("MONGO_DATABASE")  # Assuming 'test' is your database name
options = "retryWrites=true&w=majority"  # Your connection options

# Construct the MongoDB URI
mongo_uri = f"mongodb+srv://{username}:{password}@{cluster_address}/{database}?{options}"

# Initialize the MongoDB client
client = MongoClient(mongo_uri)
db = client['Database']
collection = db['FrameCollection']
print("Connection is Successfull!")

def download_youtube_video(url, path):
    attempts = 0
    max_attempts = 5  # Maximum number of attempts
    while attempts < max_attempts:
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            video_id = yt.video_id
            stream.download(output_path=path, filename='video.mp4')
            print('Video downloaded successfully.')
            return video_id
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempts + 1} failed with IncompleteRead: {e}")
            attempts += 1
            if attempts == max_attempts:
                raise  # Reraise the last exception if all attempts fail


def extract_frames(video_path, frame_rate):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    extracted_frames = []
    fps = vidcap.get(cv2.CAP_PROP_FPS)  # Get the frames per second of the video
    
    while success:
        if count % frame_rate == 0:
            frame_path = f"frame_{count/fps:.2f}.jpg"
            cv2.imwrite(frame_path, image)  # Save frame as JPEG file
            extracted_frames.append((frame_path, count / fps))  # Append frame path and timestamp
            print(f"Extracted frame {count} at {count/fps:.2f} seconds")
        success, image = vidcap.read()
        count += 1
    return extracted_frames

async def encode_frame_to_base64(frame_path):
    with open(frame_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def send_frame_to_api(frame,time, video_id, api_endpoint):
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
            data['video_id'] = video_id
            data['timestamp'] = int(time)
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
        asyncio.run(send_frame_to_api(frame[0],frame[1], video_id, API_ENDPOINT))

    # Cleanup: Remove downloaded video and extracted frames
    os.remove(video_path)
    for frame in extracted_frames:
        os.remove(frame[0])
    for doc in collection.find():
        print(doc)
    client.close()





