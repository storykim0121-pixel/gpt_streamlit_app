import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

# API 클라이언트 초기화
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())

st.title("🤖 GPT 다중 이미지 분석기")

# 대화 기록 유지
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 이미지 업로드 (여러 장 가능)
uploaded_files = st.file_uploader("사진을 여러 장 선택하세요", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
prompt = st.chat_input("질문을 입력하세요...")

if prompt:
    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # GPT에게 보낼 데이터 구성
    content_payload = [{"type": "text", "text": prompt}]
    
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

    # AI 성격 부여 및 응답 생성
    system_instruction = {
        "role": "system", 
        "content": "당신은 세계 최고의 AI 비서입니다. 답변은 항상 매우 자세하고 친절하며, 전문가 수준의 분석을 제공하세요. 중요한 내용은 불렛 포인트로 정리하고, 시각적 디테일을 꼼꼼하게 설명해 주세요."
    }

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[system_instruction] + st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
