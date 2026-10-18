# Home Page
import streamlit as st
import streamlit.components.v1 as components
import base64

# st.subheader("AI Medical Agent - NationAI Assesment", divider='blue')

st.set_page_config(page_title="Documents Retreival Agent/Home", initial_sidebar_state='collapsed', layout='wide')
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

set_bg_video(r"media/bg video.webm")
chat = st.Page('chat.py')

# with open('data/html.txt','rb') as f:
#     particles_js = f.read()

col1, col2, col3 = st.columns([1,4,1])

# with col1:
#     components.html(particles_js, height=1600, scrolling=False)
# with col3:
#     components.html(particles_js, height=1600, scrolling=False)
with col2:
    st.header(":gray[The Smartest AI Document Retrieval Assistant]\n\n## :gray[Ready to Chat!]", text_alignment='center')
    st.markdown(":rainbow[Patient's reports assistant and guidelines, medical information retrieval]", text_alignment='center')
    mt = st.empty()
    st.columns([1.47,1,1], vertical_alignment='top')[1].image(r"media\Ai Robot Vector Art.gif")
    if st.columns([2,1,2])[1].button(":material/chat: Chat", type='primary', width='stretch'):
        st.switch_page(chat)
    # st.page_link(chat, label='Chat', )
    # col1, col2, col3, col4 = st.columns([3,1.1,1.1,3])
    # with col2:
    #     st.link_button(":material/play_arrow: Demo", type='secondary', url='https://youtu.be/1qybCcar-vE?si=l1EPUSfeNxKg1uXk', width='stretch')
    # with col3:
    #     if st.button(":material/chat: Chat", type='primary', width='stretch'):
    #         st.switch_page(chat)
    st.divider()


with col2:
    st.subheader(":gray[Introduction]", divider='blue', width='content')
    st.markdown("""
    :gray[**AI Medical Agent key features:**]

    :gray[1. Support text and voice interaction for faster communication (Arabic & English)]
    
    :gray[2. Support patient's reports & informations]
    
    :gray[3. Suuport medical information about healthcare from "The Washington Manual of Medical Therapeutics" book]
    
    :gray[4. Support 3 types of knowledge resources (Patients data frame, medical knowledge base RAG system, Kaggle api access for patient's medical imaging scan images)]
    
    :gray[5. Guard to avoice diagnostic and out of context questions]
    """)
    st.divider()
with col2:
    st.subheader(":gray[:material/settings: Project workflow]", divider='blue', width='content')
    st.image("media/project flow.svg")

st.divider()

# with st.sidebar:
#    st.header(":material/chat: Conversation History", divider='blue')
#    if st.button("New Chat", icon=':material/add:', width='stretch', type='tertiary'):
#       st.switch_page(chat)


with st.sidebar:
    # st.divider()
    st.header(":material/chat: Conversation History", divider='blue')
    col11, col22 = st.columns([2,1], vertical_alignment='center')
    
    with col11:
        if st.button("New Chat", icon=':material/add:', width='stretch', type='tertiary'):
            if len(st.session_state.messages['messages'])>1:
                # Auto saving current chat
                if st.session_state.chat_history:
                    if st.session_state.chat_id < len(st.session_state.chat_history):
                        st.session_state.chat_history[st.session_state.chat_id] = st.session_state.messages
                    else:
                        st.session_state.chat_history.append(st.session_state.messages)
                else:
                    st.session_state.chat_history.append(st.session_state.messages)
                st.session_state.messages = {"messages": [("system", st.session_state.prompt)]}
                st.session_state.chat_id = len(st.session_state.chat_history)
                # st.session_state.agent = Agent(st.secrets['GeminiAPI'])
                st.switch_page(chat)    
            else:
                st.switch_page(chat)
    with col22:
        st.space('medium')
    if st.session_state.chat_history:
        for c in range(len(st.session_state.chat_history)-1, -1,-1):
            with col11:
                if st.button(f"Chat {c+1}", width='stretch', type='tertiary'):
                    if len(st.session_state.messages['messages'])>1:
                        if st.session_state.chat_id < len(st.session_state.chat_history):
                            if st.session_state.chat_history[st.session_state.chat_id] != st.session_state.messages:
                                st.session_state.chat_history[st.session_state.chat_id] = st.session_state.messages
                        else:
                            st.session_state.chat_history.append(st.session_state.messages)
                    st.session_state.chat_id = c
                    st.session_state.messages = st.session_state.chat_history[c]
                    st.switch_page(chat)
            with col22:
                if st.button(":material/delete:", width='stretch', type='tertiary', key=c):
                    if st.session_state.chat_id == c:
                        st.session_state.messages = {"messages": [("system", st.session_state.prompt)]}
                        st.session_state.chat_id = len(st.session_state.chat_history)
                        # st.session_state.agent = Agent(st.secrets['GeminiAPI'])
                    del st.session_state.chat_history[c]
                    st.switch_page(chat)
