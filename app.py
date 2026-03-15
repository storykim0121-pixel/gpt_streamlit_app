import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"].strip())

st.title("💡 나의 만능 AI 비서")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_files = st.file_uploader("이미지를 분석하고 싶다면 업로드하세요 (선택)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
prompt = st.chat_input("질문을 입력하세요...")

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

    # [시스템 프롬프트: 모든 분야에 적용되는 전문가 스타일]
    system_instruction = {
        "role": "system", 
        "content": """당신은 다방면에 능통한 전문 AI 어시스턴트입니다. 아래 가이드라인을 엄격히 준수하세요:
        1. 말투: 친근하고 상냥하게, 친구나 가족에게 조언하듯 대하세요. 이모지(👍, ✨, 💡 등)를 적절히 활용해 답변을 생동감 있게 만드세요.
        2. 답변 구조: 결론부터 제시하고, 그 이유를 설명한 뒤, 구체적인 실행 방법(단계별 가이드)을 불렛 포인트로 정리하세요.
        3. 가독성: 중요한 정보는 볼드체(**텍스트**)로 강조하고, 전체적인 답변의 흐름을 논리적으로 구성하세요.
        4. 태도: 사용자가 어렵게 느끼지 않도록 전문 지식을 아주 쉽고 직관적으로 풀어서 설명하세요."""
    }

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[system_instruction] + st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
