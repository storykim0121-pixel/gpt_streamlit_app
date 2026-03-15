import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

# API 클라이언트 초기화
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🤖 나만의 GPT 챗봇")

# 대화 기록 유지 (앱이 새로고침되어도 대화가 사라지지 않게 함)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 내용을 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 이미지 업로드 버튼
uploaded_file = st.file_uploader("사진을 분석하고 싶다면 여기 올리세요 (선택)", type=["png", "jpg", "jpeg"])

# 채팅 입력창
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 1. 사용자의 질문을 저장하고 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 이미지 처리 준비
    content_payload = [{"type": "text", "text": prompt}]
    if uploaded_file:
        image = Image.open(uploaded_file)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}})

    # 3. GPT 호출 (스트리밍 방식 적용 - 더 빠릿함)
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o", # 성능 좋은 모델
            messages=[{"role": "user", "content": content_payload}],
            stream=True,
        )
        response = st.write_stream(stream)
    
    # 4. AI의 답변을 저장
    st.session_state.messages.append({"role": "assistant", "content": response})
