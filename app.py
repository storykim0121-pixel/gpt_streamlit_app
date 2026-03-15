import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

# API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())

st.title("👕 나의 퍼스널 스타일 분석기")

# 대화 기록 유지
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 이미지 업로드 및 질문 입력
uploaded_files = st.file_uploader("사진을 올려주세요 (비교할 사진을 여러 장 선택해도 좋아요)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
prompt = st.chat_input("사진을 분석하고 순위를 매겨줘!")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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

    # [핵심] 스타일을 결정짓는 시스템 명령
    system_instruction = {
        "role": "system", 
        "content": """당신은 패션 및 이미지 분석 전문가입니다. 사용자가 사진을 올리면 반드시 다음 규칙을 따라 답변하세요.
        1. 첫 줄: 사진 속 대상(색상, 스타일 등)을 먼저 정의하고 리스트화 하세요.
        2. 순위 매기기: [1️⃣, 2️⃣, 3️⃣] 번호를 사용해 가장 추천하는 순서대로 정렬하세요.
        3. 상세 분석: 각 항목마다 장점과 단점을 불렛 포인트로 명확히 작성하세요.
        4. 최종 결론: 마지막에 '👉 개인적으로 ~가 제일 좋아 보였습니다'와 같이 결론을 내리세요.
        5. 말투: 친구에게 조언하듯 친근하고 상냥하게 하세요. (👍, 👕, 👖 같은 이모지 적극 활용)
        6. 가독성: 중요한 내용은 볼드체(**텍스트**)로 강조하고, 전체적으로 구조화하여 작성하세요."""
    }

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[system_instruction] + st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
