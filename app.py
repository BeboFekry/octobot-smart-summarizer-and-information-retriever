import streamlit as st
import base64
st.set_page_config(page_title="Octobot", page_icon='media/iconNationAi.png', initial_sidebar_state='collapsed', layout='centered')
st.logo('media/Logo.png', size='large')

if 'messages' not in st.session_state:
    with open('data/prompt.txt', 'rb') as f:
        st.session_state.prompt = f.read()
    st.session_state.messages = {
        "messages": [
            ("system", st.session_state.prompt),
        ]
    }
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = 0


def set_bg_video(video_file):
  with open(video_file, "rb") as f:
    encoded_video = base64.b64encode(f.read()).decode()

  html_code = f"""
    <style>
    MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    # header {{visibility: hidden;}}

    .video-background {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        z-index: -1;
        object-fit: cover;
    }}

    .stApp {{
        background: transparent !important;
    }}
    </style>

    <video autoplay muted loop class="video-background">
        <source src="data:video/mp4;base64,{encoded_video}" type="video/mp4">
        Error: your browser does't support loading background video!
    </video>
    """
  st.markdown(html_code, unsafe_allow_html=True)

# set_bg_video(r"media\bg video.webm")


home = st.Page("home.py", title="Home", icon=":material/home:", default=True)
chat = st.Page("chat.py", title="Chatbot", icon=":material/smart_toy:")

pg = st.navigation([home, chat])

pg.run()
