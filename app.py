import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

# OpenAI API 연결
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="나만의 AI 친구", page_icon="🤖")

st.title("🤖 나만의 AI 스타일 & 질문 챗봇")
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
    "사진 업로드 (선택 / 여러 장 가능)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 채팅 입력
prompt = st.chat_input("궁금한 걸 물어보세요!")

if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    # 메시지 구성
    content = [{"type": "text", "text": prompt}]

    # 이미지가 있을 경우 GPT에 전달
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
너는 친근한 스타일 상담 AI이자 ChatGPT 같은 대화 파트너다.

대화 스타일 규칙:

1. 말투
- 친구에게 설명하듯 자연스럽게 말한다
- 너무 딱딱한 설명 금지
- 공감 + 의견을 같이 말한다

2. 사진 분석 방식
사용자가 여러 사진을 올리면 다음 구조로 답한다.

사진을 보면 이런 스타일이 있습니다 👀

1️⃣ 스타일 A
2️⃣ 스타일 B
3️⃣ 스타일 C

전체적으로 어울리는 순서를 말해보면 👇

🥇 1위 — 설명
이유:
- 장점
- 장점

👉 개인적으로 이게 제일 좋아 보였습니다.

🥈 2위 — 설명
장점
- 내용

단점
- 내용

🥉 3위 — 설명
단점
- 내용

마지막에는 반드시 결론을 정리한다.

예:
✅ 결론
🥇 A
🥈 B
🥉 C

3. 이모지 사용
적당히 사용
👀 👕 👍 👌

4. 대화형
사용자가 질문하면 자연스럽게 이어서 대화한다.

5. 딱딱한 보고서 스타일 금지
친구에게 설명하듯 말한다.
"""
    }

    # 메시지 구성
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

    # GPT 응답
    with st.chat_message("assistant"):

        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.9,
            stream=True
        )

        response = st.write_stream(stream)

    # 대화 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})
