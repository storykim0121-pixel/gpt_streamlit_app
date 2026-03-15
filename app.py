import streamlit as st
from openai import OpenAI

# OpenAI API 연결
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 시스템 프롬프트 (ChatGPT 스타일)
SYSTEM_PROMPT = """
You are a friendly and natural conversational AI.

Rules:
- Speak naturally like chatting with a friend.
- Be warm, helpful, and clear.
- Avoid sounding robotic or overly formal.
- Keep answers concise but informative.
- If the user speaks Korean, respond in Korean.
"""

# 세션에 대화 기록 저장
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요? 🙂"}
    ]

# 제목
st.title("My GPT Chat")

# 기존 채팅 출력
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])

    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])

# 사용자 입력
user_input = st.chat_input("메시지를 입력하세요")

if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # GPT 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        temperature=0.7,
        max_tokens=800
    )

    reply = response.choices[0].message.content

    # GPT 답변 저장
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # 화면에 출력
    with st.chat_message("assistant"):
        st.write(reply)
