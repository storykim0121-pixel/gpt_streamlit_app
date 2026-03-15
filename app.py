import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())

st.title("🤖 GPT 다중 이미지 분석기")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 여러 장 업로드 설정 (accept_multiple_files=True 추가)
uploaded_files = st.file_uploader("사진을 여러 장 선택하세요", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
prompt = st.chat_input("질문을 입력하세요...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    content_payload = [{"type": "text", "text": prompt}]
    
    # 여러 장 반복 처리
    if uploaded_files:
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            image.thumbnail((1024, 1024))
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            content_payload.append({
                "type": "image_url", 
                "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
            })

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content_payload}],
            stream=True,
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
