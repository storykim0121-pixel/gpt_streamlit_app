import streamlit as st
import base64
import io
from openai import OpenAI
from PIL import Image

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI 친구", page_icon="🤖")

st.title("🤖 나만의 AI 친구")
st.caption("사진 분석도 하고 자유롭게 대화해보세요!")

# 대화 기록
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이미지 저장
if "images" not in st.session_state:
    st.session_state.images = []

# 기존 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 질문 입력
prompt = st.chat_input("궁금한 걸 물어보세요!")

# 👇 질문 입력 아래에 사진 업로드
uploaded_files = st.file_uploader(
    "사진 업로드 (선택 / 여러 장 가능)",
    type=["png","jpg","jpeg"],
    accept_multiple_files=True
)

if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    content = [{"type":"text","text":prompt}]

    # 처음 업로드 시만 사진 표시
    if uploaded_files and len(st.session_state.images) == 0:

        st.write("📷 업로드된 사진")

        for i, file in enumerate(uploaded_files):

            image = Image.open(file)

            # 세로 표시
            st.image(image, caption=f"{i+1}번 사진", use_container_width=True)

            image.thumbnail((1024,1024))

            buf = io.BytesIO()
            image.save(buf, format="JPEG")

            img_base64 = base64.b64encode(buf.getvalue()).decode()

            st.session_state.images.append(img_base64)

    # GPT 전달
    for img in st.session_state.images:
        content.append({
            "type":"image_url",
            "image_url":{
                "url":f"data:image/jpeg;base64,{img}"
            }
        })

    system_prompt = {
        "role":"system",
        "content":"""
너는 친근하고 분석을 잘하는 AI 친구다.

대화 스타일
- 친구처럼 자연스럽게 말한다
- 설명은 충분히 자세하게 한다
- 의견을 솔직하게 말한다
- 도움이 되는 추가 조언도 한다
- 이모지를 적당히 사용한다 👀👍

사진이 여러 장 올라오면

1️⃣ 사진별 특징 설명  
2️⃣ 색상 / 스타일 분석  
3️⃣ 가장 어울리는 순위  
4️⃣ 장점과 단점  
5️⃣ 최종 결론  

형식 예시

사진을 보면 이런 특징이 있습니다 👀

1️⃣ 1번 사진 — 설명  
2️⃣ 2번 사진 — 설명  

전체적으로 어울리는 순서를 말해보면 👇

🥇 1위 — 이유  
🥈 2위 — 이유  
🥉 3위 — 이유  

👉 개인적인 추천을 말한다.

보고서처럼 딱딱하게 말하지 말고
ChatGPT처럼 자연스럽게 대화한다.
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
            temperature=1.1,
            top_p=0.95,
            stream=True
        )

        response = st.write_stream(stream)

    st.session_state.messages.append({"role":"user","content":prompt})
    st.session_state.messages.append({"role":"assistant","content":response})
