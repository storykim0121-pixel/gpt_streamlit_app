import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

# OpenAI 연결
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="나만의 AI 친구", page_icon="🤖")

st.title("🤖 나만의 AI 친구")
st.caption("아무 질문이나 해보세요! 사진도 분석해 드려요 📷")

# 대화 기록 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 이미지 업로드
uploaded_files = st.file_uploader(
    "사진 업로드 (선택)",
    type=["png","jpg","jpeg"],
    accept_multiple_files=True
)

# 질문 입력
prompt = st.chat_input("궁금한 걸 물어보세요!")

if prompt:

    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)

    # 메시지 구성
    content = [{"type":"text","text":prompt}]

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

    # 시스템 프롬프트 (ChatGPT 스타일)
    system_prompt = {
        "role":"system",
        "content":"""
너는 친근하고 재미있는 AI 친구야.

대화 스타일:
- 친구처럼 자연스럽게 대화
- 너무 딱딱하지 않게
- 이모지 적당히 사용 😊
- 설명은 이해하기 쉽게
- 사용자가 올린 사진이 있으면 분석

가능한 것:
- 일반 질문 답변
- 고민 상담
- 패션/코디 분석
- 사진 분석
- 정보 설명
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

    # AI 응답
    with st.chat_message("assistant"):

        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True
        )

        response = st.write_stream(stream)

    # 대화 기록 저장
    st.session_state.messages.append({"role":"user","content":prompt})
    st.session_state.messages.append({"role":"assistant","content":response})
