import streamlit as st
from openai import OpenAI

# OpenAI API 연결
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="My ChatGPT", layout="wide")

SYSTEM_PROMPT = """
You are an assistant similar to ChatGPT.

Response style:
- Give a clear conclusion first.
- Then explain the reasons in structured sections.
- Use short paragraphs or bullet points.
- Provide practical tips when helpful.
- Speak naturally like a human conversation.
- If the user writes in Korean, respond in Korean.
"""

# 대화 기록 초기화
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

uploaded_file = st.file_uploader(
    "파일 업로드",
    type=["pdf", "txt", "docx", "png", "jpg"]
)

if uploaded_file:
    st.write("업로드된 파일:", uploaded_file.name)
    
# 기존 대화 표시
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
user_input = st.chat_input("메시지를 입력하세요")

if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 사용자 질문 표시
    with st.chat_message("user"):
        st.markdown(user_input)

    # GPT 응답 생성
    with st.chat_message("assistant"):

        placeholder = st.empty()
        full_response = ""

        stream = client.chat.completions.create(
            model="gpt-4.1",
            messages=st.session_state.messages,
            temperature=0.5,
            max_tokens=1200,
            presence_penalty=0.3,
            frequency_penalty=0.2,
            stream=True
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_response += delta
            placeholder.markdown(full_response)

    # GPT 답변 저장
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
