import googleapiclient.discovery
import pandas as pd

def search_youtube_videos(api_key, query, max_results=50):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=max_results,
        type="video"
    )
    response = request.execute()
    return response

def main(api_key, query, max_results=50, output_file="C:/Users/soo/Desktop/soo/2024/env_capstone/youtubeAPI_list.xlsx"):
    # "환경" 키워드로 검색
    videos = search_youtube_videos(api_key, query, max_results)

    # 동영상 정보 추출
    video_data = {
        "Title": [item['snippet']['title'] for item in videos['items']],
        "Description": [item['snippet']['description'] for item in videos['items']],
        "Video ID": [item['id']['videoId'] for item in videos['items']],
        "Channel Title": [item['snippet']['channelTitle'] for item in videos['items']],
        "Published At": [item['snippet']['publishedAt'] for item in videos['items']]
    }
    df = pd.DataFrame(video_data)

    # Excel 파일로 저장
    df.to_excel(output_file, index=False)

    print(f"Data has been written to {output_file}")

# YouTube Data API 키를 여기에 입력하세요
api_key = "AIzaSyDjGoXBcmSVy8Ohh4OSJbDHdAMV_0yXLbc"

# 검색할 키워드
query = "환경"

# 메인 함수 실행
main(api_key, query)
