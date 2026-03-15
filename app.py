import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

# API 클라이언트 초기화 (공백 제거를 위해 .strip() 추가)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())

st.title("🤖 GPT 대화 & 이미지 분석기")

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 내용 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 이미지 업로드 및 채팅 입력
uploaded_file = st.file_uploader("사진을 분석하려면 먼저 업로드하세요 (선택)", type=["png", "jpg", "jpeg"])
prompt = st.chat_input("메시지를 입력하세요...")

if prompt:
    # 1. 사용자 질문 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. GPT에 보낼 데이터 구성 (텍스트 + 이미지)
    content_payload = [{"type": "text", "text": prompt}]
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        # 이미지 용량 최적화 (GPT 인식을 위해 리사이즈)
        image.thumbnail((1024, 1024))
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        content_payload.append({
            "type": "image_url", 
            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
        })

    # 3. GPT 호출 및 응답 출력
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content_payload}],
            stream=True,
        )
        response = st.write_stream(stream)
    
    # 4. AI 답변 저장
    st.session_state.messages.append({"role": "assistant", "content": response})
