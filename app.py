import streamlit as st
import openai
from PIL import Image

# OpenAI API 키 가져오기
openai.api_key = st.secrets["OPENAI_API_KEY"]  # 나중에 Streamlit Cloud용

st.title("GPT-4 이미지 업로드 테스트")

# 사진 업로드 위젯
uploaded_file = st.file_uploader("사진을 업로드하세요", type=["png","jpg","jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지", use_column_width=True)
    
    # GPT API 호출 예시
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 이미지 설명 AI야."},
            {"role": "user", "content": "이 사진을 설명해줘."}
        ]
    )
    st.write(response['choices'][0]['message']['content'])