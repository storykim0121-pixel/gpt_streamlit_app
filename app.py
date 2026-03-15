import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
You are a helpful conversational AI similar to ChatGPT.

Rules:
- Speak naturally like chatting with a person.
- Be friendly and clear.
- Avoid robotic responses.
- Maintain context from previous messages.
- If the user writes Korean, respond in Korean.
"""

st.set_page_config(page_title="My ChatGPT", layout="wide")

# 대화 저장
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요? 🙂"}
    ]

# 사이드바
with st.sidebar:
    st.title("ChatGPT")

    if st.button("➕ 새 대화"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요? 🙂"}
        ]
        st.rerun()

st.title("My ChatGPT")

# 기존 채팅 표시
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 입력창
user_input = st.chat_input("메시지를 입력하세요")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # GPT 응답
    with st.chat_message("assistant"):

        placeholder = st.empty()
        full_response = ""

        stream = client.chat.completions.create(
            model="gpt-5",
            messages=st.session_state.messages,
            temperature=0.7,
            stream=True
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            placeholder.markdown(full_response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
