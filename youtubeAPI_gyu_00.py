import googleapiclient.discovery
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import pandas as pd
import os
from datetime import datetime

def search_youtube_videos(api_key, query, max_results=50, page_token=None, published_after=None, published_before=None):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=max_results,
        type="video",
        pageToken=page_token,
        publishedAfter=published_after,
        publishedBefore=published_before
    )
    response = request.execute()
    return response

def get_video_transcripts(video_ids):
    transcripts = {}
    for video_id in video_ids:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for transcript in transcript_list:
                if transcript.language_code == 'ko':
                    text_formatter = TextFormatter()
                    transcript_text = transcript.fetch()
                    formatted_text = text_formatter.format_transcript(transcript_text)
                    transcripts[video_id] = formatted_text
                    break
        except Exception as e:
            print(f"Could not retrieve transcript for video {video_id}: {e}")
    return transcripts

def load_processed_video_ids(filename="processed_video_ids.txt"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return set(line.strip() for line in file)
    return set()

def save_processed_video_ids(video_ids, filename="processed_video_ids.txt"):
    with open(filename, "a") as file:
        for video_id in video_ids:
            file.write(f"{video_id}\n")

def load_existing_video_ids_from_excel(output_file):
    if os.path.exists(output_file):
        df_existing = pd.read_excel(output_file)
        return set(df_existing["Video ID"].tolist())
    return set()

def main(api_key, query, max_results=50, filename="processed_video_ids.txt", output_file="C:/Users/soo/Desktop/soo/2024/env_capstone/youtubeAPI_gyu_00.xlsx"):
    processed_video_ids = load_processed_video_ids(filename)
    existing_video_ids = load_existing_video_ids_from_excel(output_file)

    # 날짜 범위 설정
    date_ranges = [
        ("2014-01-01T00:00:00Z", "2014-12-31T23:59:59Z"),
        ("2015-01-01T00:00:00Z", "2015-12-31T23:59:59Z"),
        ("2016-01-01T00:00:00Z", "2016-12-31T23:59:59Z"),
        ("2017-01-01T00:00:00Z", "2017-12-31T23:59:59Z"),
    ]

    for published_after, published_before in date_ranges:
        next_page_token = None

        while True:
            videos = search_youtube_videos(api_key, query, max_results, next_page_token, published_after, published_before)
            
            new_videos = []
            for item in videos['items']:
                video_id = item['id']['videoId']
                if video_id not in processed_video_ids and video_id not in existing_video_ids:
                    new_videos.append(item)

            if not new_videos:
                break

            video_data = {
                "Title": [item['snippet']['title'] for item in new_videos],
                "Description": [item['snippet']['description'] for item in new_videos],
                "Video ID": [item['id']['videoId'] for item in new_videos],
                "Channel Title": [item['snippet']['channelTitle'] for item in new_videos],
                "Published At": [item['snippet']['publishedAt'] for item in new_videos]
            }
            df_new = pd.DataFrame(video_data)

            video_ids = video_data["Video ID"]
            transcripts = get_video_transcripts(video_ids)

            df_new['Transcript'] = df_new['Video ID'].map(transcripts)

            if os.path.exists(output_file):
                df_existing = pd.read_excel(output_file)
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_combined = df_new

            df_combined.drop_duplicates(subset="Video ID", keep='last', inplace=True)

            df_combined.to_excel(output_file, index=False)

            save_processed_video_ids(video_ids, filename)

            print(f"Data has been written to {output_file}")

            next_page_token = videos.get('nextPageToken')

            if not next_page_token:
                break

# YouTube Data API 키를 여기에 입력하세요
api_key = "AIzaSyBp8l2fByWapMmAtJUjpCTXAsEGDTv7ZBM"

# 검색할 키워드
query = "환경"

# 메인 함수 실행
main(api_key, query)
