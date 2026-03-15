import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

# 1. 클라이언트 초기화 (Secrets에 설정한 이름 OPENAI_API_KEY 사용)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("📸 GPT 이미지 분석기")

# 사진 업로드 위젯
uploaded_file = st.file_uploader("이미지를 업로드하세요 (png/jpg/jpeg)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # 업로드된 이미지 표시
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지", use_column_width=True)

    # 이미지를 base64 형식으로 변환 (GPT-4o가 읽기 위한 필수 과정)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # GPT API 호출
    with st.spinner("AI가 이미지를 분석 중입니다..."):
        response = client.chat.completions.create(
            model="gpt-4o", # 더 성능이 좋은 gpt-4o 모델 사용
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "이 이미지를 간단히 설명해줘."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                    ]
                }
            ]
        )

    # GPT 응답 출력
    st.subheader("분석 결과")
    st.write(response.choices[0].message.content)
