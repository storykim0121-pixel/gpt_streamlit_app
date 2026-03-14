import streamlit as st
import openai

# OpenAI API 키 입력 (나중에 환경변수로도 가능)
openai.api_key = "YOUR_API_KEY"

st.title("GPT 사진+질문 앱")

# 이미지 업로드
uploaded_file = st.file_uploader("사진 업로드", type=["jpg", "png"])

# 질문 입력
question = st.text_input("질문을 입력하세요:")

if uploaded_file and question:
    # 이미지를 GPT에게 보내는 과정 (실제 API 호출은 예시)
    # 여기서는 단순 텍스트 질문만 GPT에 전달
    st.image(uploaded_file, caption="업로드한 사진", use_column_width=True)
    response = openai.ChatCompletion.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "사진 관련 질문에 답변해줘"},
            {"role": "user", "content": question}
        ]
    )
    st.write("GPT 답변:")
    st.write(response['choices'][0]['message']['content'])