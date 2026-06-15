import PyPDF2
import google.generativeai as genai
import time

# 1. API 키 설정
genai.configure(api_key="") 
model = genai.GenerativeModel('gemini-flash-lite-latest')

def extract_and_save_all_pages(pdf_path, output_csv):
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"📄 총 {total_pages}페이지의 PDF를 확인했습니다. 추출을 시작합니다...\n")
    except FileNotFoundError:
        print(f"❌ 오류: {pdf_path} 파일을 찾을 수 없습니다.")
        return

    # CSV 파일 초기화 (맨 윗줄 헤더만 먼저 작성)
    with open(output_csv, "w", encoding="utf-8-sig") as f:
        f.write("단어,뜻,예문\n")

    chunk_size = 2 # 한 번에 처리할 페이지 수 (2페이지씩 안전하게 처리)
    
    for i in range(0, total_pages, chunk_size):
        raw_text = ""
        start_page = i
        end_page = min(i + chunk_size, total_pages)
        
        # 2페이지 분량의 텍스트만 먼저 읽기
        for page_num in range(start_page, end_page):
            raw_text += reader.pages[page_num].extract_text() + "\n"
            
        print(f"🔄 {start_page + 1} ~ {end_page} 페이지 AI 변환 중...")
        
        # AI에게 정제 요청 (헤더 없이 데이터만 출력하도록 프롬프트 수정)
        prompt = f"""
        당신은 영어 교육 전문가입니다. 아래 텍스트는 텝스 단어장 PDF 텍스트입니다.
        불필요한 노이즈('21. 10. 19', '1/2', '단어' 등)를 제거하고 영단어와 뜻만 추출하세요.
        추출한 영단어에 맞는 짧은 영어 예문을 직접 작성하세요.
        
        반드시 '단어,"뜻",예문' 형태의 CSV 포맷으로만 출력하세요. 뜻은 쉼표 오류 방지를 위해 무조건 큰따옴표(" ")로 감싸세요.
        첫 줄에 컬럼명(단어,뜻,예문)은 절대 쓰지 마세요. 데이터만 바로 출력하세요.

        [원본 텍스트]
        {raw_text}
        """
        
        try:
            response = model.generate_content(prompt)
            # 마크다운 기호 제거
            cleaned_csv = response.text.replace('```csv\n', '').replace('```', '').strip()
            
            # 기존 CSV 파일 밑에 계속 이어붙이기 (Append 모드 'a')
            with open(output_csv, "a", encoding="utf-8-sig") as f:
                f.write(cleaned_csv + "\n")
                
        except Exception as e:
            print(f"⚠️ {start_page + 1}~{end_page} 페이지 처리 중 오류 발생: {e}")
            
        # API 과부하 방지를 위해 3초 대기 후 다음 페이지 진행
        time.sleep(3)

    print(f"\n✅ 완료! 모든 단어가 '{output_csv}' 파일에 저장되었습니다.")

# --- 메인 실행 로직 ---
if __name__ == "__main__":
    pdf_filename = "test.pdf" #PDF 파일명
    output_filename = "teps_words_auto.csv"
    
    extract_and_save_all_pages(pdf_filename, output_filename)