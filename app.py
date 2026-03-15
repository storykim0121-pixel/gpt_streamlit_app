import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🤖 AI 친구")

# 대화 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이미지 저장
if "images" not in st.session_state:
    st.session_state.images = []

# 기존 대화 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------
# 입력 영역
# -------------------

prompt = st.text_input("궁금한 걸 물어보세요")

uploaded_files = st.file_uploader(
    "사진 업로드",
    type=["png","jpg","jpeg"],
    accept_multiple_files=True
)

# 📷 사진 미리보기 (가로 정렬)
if uploaded_files:

    st.write("📷 업로드된 사진")

    cols = st.columns(len(uploaded_files))

    for i, file in enumerate(uploaded_files):

        image = Image.open(file)

        with cols[i]:
            st.image(image, caption=f"{i+1}번", use_container_width=True)

# 보내기 버튼
send = st.button("보내기")

# -------------------
# 질문 처리
# -------------------

if send and prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    content = [{"type":"text","text":prompt}]

    # 이미지 GPT 전달
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
        "content":"친근한 AI 친구처럼 대화하고 사진이 있으면 분석도 해준다."
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
            stream=True
        )

        response = st.write_stream(stream)

    st.session_state.messages.append({"role":"user","content":prompt})
    st.session_state.messages.append({"role":"assistant","content":response})
