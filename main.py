import json
import os
from ultralytics import YOLO
import cv2
import json


import os
import cv2
import boto3
import yt_dlp as youtube_dl
from yt_dlp.utils import DownloadError
import uuid
from decimal import Decimal
import math




session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
    aws_session_token='', 
    region_name='us-east-1'
)

dynamodb = session.resource('dynamodb')
table = dynamodb.Table('Adinteractive-DB')
print("Connection is Successfull!")

    
    
def download_youtube_video(url, path):
    attempts = 0
    max_attempts = 5  # Maximum number of attempts
    video_id = None

    while attempts < max_attempts:
        print(f"Attempt {attempts + 1}")
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'video.mp4',  # Save the file as video.mp4 in the specified path
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(url, download=True)
                video_id = result.get('id', None)
            
            print(f"Video downloaded successfully.")
            return video_id

        except DownloadError as e:
            print(f"Attempt {attempts + 1} failed with DownloadError: {e}")
            attempts += 1
            if attempts == max_attempts:
                raise  # Reraise the last exception if all attempts failed



def get_frame_rate(video_url):
     # Define the options
    ydl_opts = {
        'format': 'best',  # We will extract the best quality available
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # Extract information about the video
        info_dict = ydl.extract_info(video_url, download=False)
        
        # yt-dlp stores available formats in 'formats' key
        formats = info_dict.get('formats', [])

        # Initialize variables
        highest_fps = 0
        selected_fps = None

        # First pass: Try to find a format with exactly 24 fps
        for fmt in formats:
            fps = fmt.get('fps')
            if fps == 24:
                return fps  # Immediately return if 24 fps is found

        # Second pass: If 24 fps is not found, find the highest fps available
        for fmt in formats:
            fps = fmt.get('fps')
            if fps and fps > highest_fps:
                highest_fps = fps  # Keep track of the highest fps

        # Return the highest frame rate found (if no 24 fps format was found)
        if highest_fps > 0:
            return highest_fps

    return None


def extract_frames(video_path, frame_skip):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    extracted_frames = []
    
    while success:
        # Get the current timestamp in milliseconds
        timestamp_ms = vidcap.get(cv2.CAP_PROP_POS_MSEC)
        timestamp_seconds = timestamp_ms / 1000.0
        
        frame_path = f"frame_{timestamp_seconds:.2f}.jpg"
        cv2.imwrite(frame_path, image)  # Save frame as JPEG file
        extracted_frames.append((frame_path, timestamp_seconds))  # Append frame path and timestamp
        print(f"Extracted frame at {timestamp_seconds:.2f} seconds")
        
        # Skip frames according to frame_skip. frame_skip=0 means save every frame.
        for _ in range(frame_skip):
            success, image = vidcap.read()
        
        success, image = vidcap.read()
    
    return extracted_frames





# @app.before_first_request
def load_model(movie_name):
    global model, classNames, descriptions, links, labels, images, prevMovieName , product_id

    
    # video_ids = ["GgKmhDaVo48", "granTurismo", "redNotice", "GVPzGBvPrzw"]
    # if movie_name in video_ids:

    with open("granTurismo.json") as json_data_file:
        data = json.load(json_data_file)


    # Load model
    model = YOLO("gran_turismo_m.pt")


    print("Model loaded...", movie_name)
    classNames = model.module.names if hasattr(model, 'module') else model.names

    descriptions = data["descriptions"]
    links = data["links"]
    labels = data["labels"]
    images = data["images"]
    product_id = data["product_id"]

    # prevMovieName = movie_name
    # else:
    #     print("Data not found for this movie...")




def get_predictions(movie_name):
    
    results = model("frame.jpg", stream=False, conf=0.6, iou=0.7)

    for result in results:

        result = result.cpu().numpy()

        # print(result)

        # resultPlotted = result.plot(line_width = 1, show_conf = True, font_size = 1)
        # print(result.boxes.xywhn)

        # resultPlotted = drawBoxes(result.orig_img, result.boxes.xyxy, result.boxes.conf, result.boxes.cls, result.names, corneredBbox = True)
        resultPlotted = result.orig_img
        classIdxs = result.boxes.cls
        # classNames = result.names
        json_response = []
        for i, bbox in enumerate(result.boxes.xyxy):

            object_name = f'{classNames[int(classIdxs[i])]}'

            x1, y1, x2, y2 = [int(b) for b in bbox]
            if object_name == "livingRoomTable":
                center_coordinates = ((int((x1 + x2)/2))/resultPlotted.shape[1], (int((y1 + ((y2-y1)*70/100))))/resultPlotted.shape[0])
            else:
                center_coordinates = ((int((x1 + x2)/2))/resultPlotted.shape[1], (int((y1 + ((y2-y1)*30/100))))/resultPlotted.shape[0])
            # cv2.circle(resultPlotted, center_coordinates, 5, (0,0,255), thickness=-1)

            # resultPlotted = drawCenters(resultPlotted, result.boxes.xyxy)

                    # print(xyxy)

            json_response.append({
                "label":labels[object_name],
                "description":descriptions[object_name],
                "coordinates":list(center_coordinates),
                "link":links[object_name],
                "image": images[object_name],
                "product_id":product_id[object_name]
                }
            )
    print(json_response)
    return json_response



def send_to_db(json_response, timestamp_seconds, movie_name,frame_rate): 
    for i in json_response: 
        id = str(uuid.uuid4())
        product_id = i["product_id"]
        coordinates = i["coordinates"]
        decimal = [Decimal(str(coord)) for coord in coordinates]
        timestamp = str(math.floor(timestamp_seconds*frame_rate))

        
        item = {
                'coordinate_id': id,
                'product_id': product_id,
                'coordinates': decimal,
                'timestamp': timestamp,
                'video_id': movie_name
            }
        print(item)
        table.put_item(
            Item=item
        )




if __name__ == "__main__":
    print("Starting the process...")
    VIDEO_URL = 'https://www.youtube.com/watch?v=GgKmhDaVo48' 
    movie_name = download_youtube_video(VIDEO_URL, 'video.mp4')
    frame_rate = get_frame_rate(VIDEO_URL)
    print(f"Frame rate: {frame_rate} fps")
    extracted_frames = extract_frames('video.mp4', frame_skip=0)
    print(f"Extracted {len(extracted_frames)} frames")
    load_model(movie_name)
    for frame_path, timestamp_seconds in extracted_frames:
        print(frame_path)
        print(f"Processing frame at {timestamp_seconds:.2f} seconds")
        # Load the frame
        
        # Load frame_path and save it as frame.jpg
        frame = cv2.imread(frame_path)        
        cv2.imwrite("frame.jpg", frame)
        
        predictions = get_predictions(movie_name)
        # print(predictions)
        if predictions != []:
            send_to_db(predictions , timestamp_seconds, movie_name,frame_rate)
        # Save the predictions to a JSON file
    os.remove('video.mp4')
    for frame in extracted_frames:
        os.remove(frame[0])