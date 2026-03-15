if uploaded_files:

    st.write("📷 업로드된 사진")

    cols = st.columns(len(uploaded_files))

    for i, file in enumerate(uploaded_files):

        image = Image.open(file)

        # 가로로 정렬
        with cols[i]:
            st.image(image, caption=f"{i+1}번", use_container_width=True)

        # GPT 전달용 저장 (처음만)
        if len(st.session_state.images) < len(uploaded_files):

            image.thumbnail((1024,1024))

            buf = io.BytesIO()
            image.save(buf, format="JPEG")

            img_base64 = base64.b64encode(buf.getvalue()).decode()

            st.session_state.images.append(img_base64)
