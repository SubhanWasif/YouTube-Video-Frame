# YouTube-Video-Frame

This project is designed to download YouTube videos, extract frames at a specified rate, and analyze these frames by sending them to an API endpoint. The analysis results are then stored in a MongoDB database management<br/>

## Installation<br/>
### Python Dependencies<br/>
First, install the required Python libraries using pip. You can do this by running the following command in your terminal:
```
pip install pytube opencv-python pymongo httpx asyncio
```

`pytube` is used for downloading videos from YouTube, opencv-python for frame extraction,<br/> `pymongo` for interacting with MongoDB, and httpx alongside asyncio for asynchronous HTTP requests.
 

## MongoDB Setup
Follow these steps to install and set up MongoDB on your system:<br/>
1. **Download MongoDB:** Visit the [MongoDB official website](https://www.mongodb.com/cloud/atlas/lp/try4?utm_source=google&utm_campaign=search_gs_pl_evergreen_atlas_core_prosp-brand_gic-null_emea-pk_ps-all_desktop_eng_lead&utm_term=mongodb&utm_medium=cpc_paid_search&utm_ad=e&utm_ad_campaign_id=12212624545&adgroup=115749718983&cq_cmp=12212624545&gad_source=1&gclid=CjwKCAiA0bWvBhBjEiwAtEsoW16AnJ6k_9ObgQM8wwLPIZ17AoXc4wA9pmvmo7F69L1hJHJO7spwNxoCDDwQAvD_BwE) and download the MongoDB Community Server for your operating system.<br/>
2. **Install MongoDB:** Follow the installation guide specific to your operating system provided in the [MongoDB documentation](https://www.mongodb.com/docs/).<br/>
3. **Start MongoDB:** Once installed, start the MongoDB service. The method to start MongoDB depends on your operating system. Refer to the official documentation for detailed instructions.<br/>
4. **Create a Database and Collection:** You can create a database and collection using the MongoDB shell or GUI tools like MongoDB Compass. For this project, you will need a database named Database and a collection named FrameCollection.<br/>
To create them using the MongoDB shell, follow these steps:<br/>
	* Open the MongoDB shell by typing mongo in your terminal.<br/>
	* Create a new database by running use Database.<br/>
	* Create a collection by running db.createCollection('FrameCollection').<br/>

## Running the Script
To run the script, simply execute the Python file from your terminal:
```
python your_script_name.py
```
## Customization
You can customize the script by modifying the following variables at the beginning of the script:<br/>
1. **VIDEO_URL:** The URL of the YouTube video you wish to download and analyze.
2. **DOWNLOAD_PATH:** The directory where the video will be downloaded. By default, it's set to the current directory (.).
3. **FRAME_RATE:** The frequency at which frames are extracted from the video. For example, a FRAME_RATE of 30 will extract one frame every second for a video with a frame rate of 30 FPS.
4. **API_ENDPOINT:** The endpoint where frame data will be sent for analysis.

## Cleanup
The script automatically cleans up downloaded videos and extracted frames after processing. Ensure you have adequate permissions in your file system for these operations.
