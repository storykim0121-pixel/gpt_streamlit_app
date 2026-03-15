import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

# OpenAI 연결
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI 친구 챗봇", page_icon="🤖")

st.title("🤖 나만의 AI 친구")
st.caption("사진 분석도 하고 자유롭게 대화할 수 있어요!")

# 대화 기록
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], str):
            st.markdown(message["content"])

# 사진 업로드
uploaded_files = st.file_uploader(
    "사진 업로드 (선택 / 여러 장 가능)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 채팅 입력
prompt = st.chat_input("궁금한 걸 물어보세요!")

if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

        # 업로드한 사진 표시
        if uploaded_files:
            cols = st.columns(len(uploaded_files))
            for i, file in enumerate(uploaded_files):
                img = Image.open(file)
                cols[i].image(img, caption=f"{i+1}번 사진", use_container_width=True)

    # GPT에 보낼 메시지
    content = [{"type": "text", "text": prompt}]

    # 이미지 처리
    if uploaded_files:
        for file in uploaded_files:

            image = Image.open(file)
            image.thumbnail((1024, 1024))

            buf = io.BytesIO()
            image.save(buf, format="JPEG")

            img_base64 = base64.b64encode(buf.getvalue()).decode()

            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}"
                }
            })

    # ChatGPT 스타일 시스템 프롬프트
    system_prompt = {
        "role": "system",
        "content": """
너는 친근하고 자연스럽게 대화하는 AI 친구다.

대화 스타일:
- 친구처럼 자연스럽게 말한다
- 너무 딱딱하게 설명하지 않는다
- 필요하면 질문도 한다
- 의견을 솔직하게 말한다
- 이모지를 가끔 사용한다 😊

사진이 올라오면:
- 사진을 먼저 설명한다
- 여러 장이면 '1번 사진', '2번 사진' 기준으로 말한다
- 비교가 필요하면 순위를 매긴다

보고서처럼 딱딱하게 말하지 말고
사람처럼 자연스럽게 대화한다.
"""
    }

    messages = [system_prompt]

    for m in st.session_state.messages:
        messages.append({
            "role": m["role"],
            "content": m["content"]
        })

    messages.append({
        "role": "user",
        "content": content
    })

    with st.chat_message("assistant"):

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=1.0,
            top_p=0.95,
            stream=True
        )

        response = st.write_stream(stream)

    # 대화 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})
