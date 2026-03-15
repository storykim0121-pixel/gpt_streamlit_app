import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

# OpenAI 연결
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI 스타일 챗봇", page_icon="🤖")

st.title("🤖 나만의 AI 스타일 & 질문 챗봇")
st.caption("사진을 올리면 분석하고 ChatGPT처럼 대화합니다!")

# 대화 기록
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사진 업로드
uploaded_files = st.file_uploader(
    "사진 업로드 (여러 장 가능)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 채팅 입력
prompt = st.chat_input("궁금한 걸 물어보세요!")

if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

        # 👇 업로드한 사진 화면에 표시
        if uploaded_files:
            cols = st.columns(len(uploaded_files))

            for i, file in enumerate(uploaded_files):
                image = Image.open(file)
                cols[i].image(image, caption=f"{i+1}번 사진", use_container_width=True)

    content = [{"type": "text", "text": prompt}]

    # GPT에 이미지 전달
    if uploaded_files:
        for file in uploaded_files:

            image = Image.open(file)
            image.thumbnail((1024,1024))

            buf = io.BytesIO()
            image.save(buf, format="JPEG")

            img_base64 = base64.b64encode(buf.getvalue()).decode()

            content.append({
                "type":"image_url",
                "image_url":{
                    "url":f"data:image/jpeg;base64,{img_base64}"
                }
            })

    system_prompt = {
        "role":"system",
        "content":"""
너는 친근한 스타일 상담 AI이자 ChatGPT 같은 대화 파트너다.

사진이 여러 장 올라오면
반드시 '1번 사진', '2번 사진' 기준으로 설명한다.

예시:

사진을 보면 이런 색이 있습니다 👀

1️⃣ 1번 사진 — 카멜
2️⃣ 2번 사진 — 다크브라운
3️⃣ 3번 사진 — 블랙

이후 어울리는 순위를 설명한다.

말투는 친구처럼 자연스럽게 하고
이모지를 적당히 사용한다.
"""
    }

    messages = [system_prompt]

    for m in st.session_state.messages:
        messages.append({
            "role":m["role"],
            "content":m["content"]
        })

    messages.append({
        "role":"user",
        "content":content
    })

    with st.chat_message("assistant"):

        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.9,
            stream=True
        )

        response = st.write_stream(stream)

    st.session_state.messages.append({"role":"user","content":prompt})
    st.session_state.messages.append({"role":"assistant","content":response})
