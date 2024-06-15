import googleapiclient.discovery
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import pandas as pd
import os

def search_youtube_videos(api_key, query, max_results=50):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        q=query,  # 여기서 "환경"을 검색
        part="snippet",
        maxResults=max_results,
        type="video"
    )
    response = request.execute()
    return response

def get_video_transcripts(video_ids):
    transcripts = {}
    for video_id in video_ids:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for transcript in transcript_list:
                if transcript.language_code == 'ko':  # 'ko'는 한국어 자막을 의미합니다. 다른 언어 코드도 사용할 수 있습니다.
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

def main(api_key, query, max_results=50, filename="processed_video_ids.txt", output_file="C:/Users/soo/Desktop/soo/2024/env_capstone/youtubeAPI_list.xlsx"):
    # 이미 처리된 동영상 ID 로드
    processed_video_ids = load_processed_video_ids(filename)

    # "환경" 키워드로 검색
    videos = search_youtube_videos(api_key, query, max_results)
    
    # 새로운 동영상 필터링
    new_videos = [item for item in videos['items'] if item['id']['videoId'] not in processed_video_ids]

    # 동영상 정보 추출
    video_data = {
        "Title": [item['snippet']['title'] for item in new_videos],
        "Description": [item['snippet']['description'] for item in new_videos],
        "Video ID": [item['id']['videoId'] for item in new_videos],
        "Channel Title": [item['snippet']['channelTitle'] for item in new_videos],
        "Published At": [item['snippet']['publishedAt'] for item in new_videos]
    }
    df_new = pd.DataFrame(video_data)

    # 동영상 자막 추출
    video_ids = video_data["Video ID"]
    transcripts = get_video_transcripts(video_ids)

    # DataFrame에 자막 추가
    df_new['Transcript'] = df_new['Video ID'].map(transcripts)

    # 기존 엑셀 파일에 새로운 데이터를 추가
    if os.path.exists(output_file):
        df_existing = pd.read_excel(output_file)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_excel(output_file, index=False)

    # 새로운 동영상 ID 저장
    save_processed_video_ids(video_ids, filename)

    print(f"Data has been written to {output_file}")


# YouTube Data API 키를 여기에 입력하세요
api_key = "AIzaSyDjGoXBcmSVy8Ohh4OSJbDHdAMV_0yXLbc"

# 검색할 키워드
query = "환경"

# 메인 함수 실행
main(api_key, query)

