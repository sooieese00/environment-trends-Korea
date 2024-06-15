import pandas as pd

# 엑셀 파일 경로
file_path = "C:/Users/soo/Desktop/soo/2024/env_capstone/youtubeAPI_soo_00.xlsx"

# 엑셀 파일 읽기
df = pd.read_excel(file_path)

# 중복된 행 제거 (Video ID 열을 기준으로)
df.drop_duplicates(subset="Video ID", keep='last', inplace=True)

# 수정된 DataFrame을 다시 엑셀 파일로 저장
df.to_excel(file_path, index=False)

print("중복된 행이 제거되었습니다.")

