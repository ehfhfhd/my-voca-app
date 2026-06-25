import PyPDF2
import google.generativeai as genai
import os
import time

# 1. API 키 설정
genai.configure(api_key="") 
model = genai.GenerativeModel('gemini-flash-lite-latest')

def extract_and_save_all_files(input_folder, output_csv):
    # CSV 파일 초기화 (맨 윗줄 헤더만 먼저 작성)
    with open(output_csv, "w", encoding="utf-8-sig") as f:
        f.write("단어,뜻,예문\n")

    # 폴더 내 모든 PDF 파일 목록 가져오기
    file_list = [f for f in os.listdir(input_folder) if f.endswith(('.pdf', '.PDF'))]
    
    if not file_list:
        print(f"❌ '{input_folder}' 폴더 안에 PDF 파일이 없습니다. 파일을 넣고 다시 실행해주세요.")
        return

    print(f"📂 총 {len(file_list)}개의 PDF 파일을 발견했습니다. 일괄 처리를 시작합니다...\n")

    # 각 파일별로 반복 작업 시작
    for filename in file_list:
        pdf_path = os.path.join(input_folder, filename)
        print(f"\n▶ [{filename}] 파일 작업 시작...")

        try:
            reader = PyPDF2.PdfReader(pdf_path)
            total_pages = len(reader.pages)
        except Exception as e:
            print(f"❌ 오류: {filename} 파일을 읽을 수 없습니다. ({e})")
            continue

        chunk_size = 2 # 한 번에 처리할 페이지 수 
        
        for i in range(0, total_pages, chunk_size):
            raw_text = ""
            start_page = i
            end_page = min(i + chunk_size, total_pages)
            
            # 지정된 2페이지 분량의 텍스트만 먼저 읽기
            for page_num in range(start_page, end_page):
                raw_text += reader.pages[page_num].extract_text() + "\n"
                
            print(f"  🔄 {start_page + 1} ~ {end_page} 페이지 AI 변환 중...")
            
            prompt = f"""
            당신은 영어 교육 전문가입니다. 아래 텍스트는 단어장 PDF 텍스트입니다.
            불필요한 노이즈를 제거하고 영단어와 뜻만 추출하세요.
            추출한 영단어에 맞는 짧은 영어 예문을 직접 작성하세요.
            
            반드시 '단어,"뜻",예문' 형태의 CSV 포맷으로만 출력하세요. 뜻은 무조건 큰따옴표(" ")로 감싸세요.
            첫 줄에 컬럼명(단어,뜻,예문)은 절대 쓰지 마세요. 데이터만 바로 출력하세요.

            [원본 텍스트]
            {raw_text}
            """
            
            try:
                response = model.generate_content(prompt)
                cleaned_csv = response.text.replace('```csv\n', '').replace('```', '').strip()
                
                # 기존 CSV 파일 밑에 계속 이어붙이기 (Append 모드 'a')
                with open(output_csv, "a", encoding="utf-8-sig") as f:
                    f.write(cleaned_csv + "\n")
                    
            except Exception as e:
                print(f"  ⚠️ {start_page + 1}~{end_page} 페이지 처리 중 오류 발생: {e}")
                
            # API 과부하 방지를 위해 3초 대기
            time.sleep(3)

    print(f"\n✅ 완료! 모든 파일의 단어가 '{output_csv}' 파일 1개에 통합 저장되었습니다.")

# --- 메인 실행 로직 ---
if __name__ == "__main__":
    input_folder_name = "voca_files" # 처리할 파일들을 모아둘 폴더 이름
    output_filename = "total_words_auto.csv" # 최종 완성될 하나의 CSV 파일
    
    # 폴더가 없으면 자동으로 생성해주는 안전장치
    if not os.path.exists(input_folder_name):
        os.makedirs(input_folder_name)
        print(f"'{input_folder_name}' 폴더를 새로 만들었습니다. 이 폴더 안에 PDF 파일들을 넣고 다시 실행해주세요!")
    else:
        extract_and_save_all_files(input_folder_name, output_filename)
