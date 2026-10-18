# Chat UI
import streamlit as st
# with st.spinner("Loading libraries..."):
import os
from datetime import datetime
from agent import Agent
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import bs4
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from validator_collection import checkers
from docx import Document
import tempfile
import io
import datetime

st.set_page_config(page_title='Document Agent', layout='wide')

if 'agent' not in st.session_state:
    with st.spinner('Please wait, Loading Data Sources...'):
        st.session_state.agent = Agent(st.secrets['GeminiAPI'])
if 'language' not in st.session_state:
    st.session_state.language = 'English'
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
if "resources" not in st.session_state:
    st.session_state.resources = []

def add_resources(name, tp, summary, date):
    st.session_state.resources.append(
        {
            "name":name, 
            "type":tp,
            "summary":summary,
            "date":date
        }
    )
    
# uploaded files -> (pdf, txt, docs), images of pdf of images, YouTube video, web link
# def summarize(text):
#     pass

def add_message(sender, message):
    """stor message from human or ai into the message history"""
    if sender=='ai':
        st.session_state.messages['messages'].append(('ai',message))
    elif sender=='human':
        st.session_state.messages['messages'].append(('human',message))
    else:
        st.error(f"Value Error '{sender}': Sender must be either 'ai' or 'human' not {sender}!")

def web_scrap(url):
  response = requests.get(url)
  soup = bs4.BeautifulSoup(response.content, "html.parser")
  paragraphs = soup.find_all("p")
  doc = ""
  for p in paragraphs:
      doc += p.text
  return doc

# def file_scrap(path):
#   if path.split('.')[1] == "pdf":
#     loader = PyPDFLoader(path)
#   else:
#     loader = TextLoader(path)
#   doc = loader.load()
#   d = ""
#   for i in doc:
#     d += i.page_content
#   return d

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    return None

def youtube_scrapper(url):
  video_id = extract_video_id(url)
  try:
      ty_api = YouTubeTranscriptApi()
      transcript = ty_api.fetch(video_id, languages=['ar','en'])
      with open("subtitles.txt", "w", encoding='utf-8') as f:
          for entry in transcript:
              f.write(entry.text)
      with open("subtitles.txt", "r", encoding='utf-8') as f:
          return f.read(), 'sucess'
  except Exception as e:
     return f"Error: {e}", 'error'

def file_scrap(file):
    extention = file.name.split('.')[-1].lower()
    if extention=='txt':
        text = file.getvalue().decode("utf-8")
        
    elif extention=='pdf':
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extention}") as tmp_file:
            tmp_file.write(f.getvalue())
            tmp_file_path = tmp_file.name
        try:
            # text = file_scrap(tmp_file_path)
            loader = PyPDFLoader(tmp_file_path)
            text = loader.load()
            # text = ""
            # for i in doc:
            #     text += i.page_content
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
    elif extention == "docx":
        doc = Document(io.BytesIO(file.getvalue()))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


col2, col1 = st.columns([2,0.8])
# chat history
with col2:
    # with st.container(border=True):
        if len(st.session_state.messages['messages'])>1:
            for message in st.session_state.messages['messages']:
                if message[0]=="human":
                    st.chat_message("user", avatar='media/user avatar.png').markdown(message[-1], text_alignment="right" if st.session_state.language =='Arabic' else 'left')
                elif message[0]=="ai":
                    st.chat_message("assistant", avatar='media/bot avatar.png').markdown(message[-1], text_alignment="right" if st.session_state.language =='Arabic' else 'left')   
            mt = st.empty()
            mt2 = st.empty()
        else:
            greeting_en = "Hello 👋, I am Octobot, your documents summarizer and researcher assistant.  \nTo start conversation can you please add your data resources?"
            greeting_ar = "أهلا بيك 👋, انا, أقدر اساعدك ازاي النهاردة؟"
            st.chat_message("assistant", avatar='media/bot avatar.png').info(greeting_ar if st.session_state.language=='Arabic' else greeting_en)
            mt = st.empty()
            mt2 = st.empty()
            # st.file_uploader("Upload your data resourcess:", accept_multiple_files=True, type=['csv', 'pdf', 'txt', 'docx'])

# uploading (add resources)
with col1:
    with st.container(border=True):
        st.subheader(":material/add_circle: **Add Resources**", divider='blue')
        web_link = st.text_input(":blue[:material/link:] Web Page", placeholder='www.test-article.com', icon=':material/link:')
        if web_link and not checkers.is_url(web_link):
            st.error("Error: Invalid Link!")
        st.space('xxsmall')
        youtube_link = st.text_input(":red[:material/smart_display:] YouTube Video", placeholder='https://www.youtube.com/watch?v=x', icon=':material/smart_display:')
        if youtube_link and not checkers.is_url(youtube_link):
            st.error("Error: Invalid Link!")
        # elif youtube_link and 'youtube.com' not in youtube_link:
        #     st.error("Error: Invalid YouTube Video Link!")
        st.space('xxsmall')
        files = st.file_uploader(":orange[:material/attachment:] Upload Files", type=["pdf", "txt", "docx"], accept_multiple_files=True, max_upload_size=20)
        st.space('xxsmall')

        if st.button("Summarize", type='primary'):
            if not files and not web_link and not youtube_link:
                st.error("Please add a data resource!")
            # Files
            if files:
                with st.spinner("Please wait while extracting your files text..."):
                    for f in files:
                        found = False
                        for r in st.session_state.resources:
                            if f.name==r['name']:
                                found=True
                        if not found:
                            text = file_scrap(f)
                            # def summarize(self, text, source_type, source_name, language)
                            source_name = f.name
                            source_type = f.name.split('.')[-1].lower()
                            summary = st.session_state.agent.summarize(text, source_type, source_name, st.session_state.language)
                            st.session_state.messages['messages'].append(('human', f"""attached "{f.name}" file to summarize"""))
                            st.session_state.messages['messages'].append(('ai',summary))
                            st.session_state.agent.add_resources(text, source_type, source_name)
                            add_resources(f.name, f.name.split('.')[-1].lower(), summary, datetime.date.today())
                            st.success("Your document file added to resources successfully!")
                            # st.rerun()
                        else:
                            st.error("File is exist already!")
            # Web link
            if web_link and checkers.is_url(web_link):
                found = False
                for r in st.session_state.resources:
                    if web_link==r['name']:
                        found=True
                if not found:
                    text = web_scrap(web_link)
                    if text:
                        with st.spinner("Please wait while geting the web text..."):
                            summary = st.session_state.agent.summarize(text, 'web_page', web_link, st.session_state.language)
                            st.session_state.messages['messages'].append(('human', f"""attached "{web_link}" web link to summarize"""))
                            st.session_state.messages['messages'].append(('ai',summary))
                            st.session_state.agent.add_resources(text, 'web_page', web_link)
                            add_resources(web_link, 'web-page', summary, datetime.date.today())
                            st.success("Your web article added to resources successfully!")
                            # st.rerun()
                    else:
                        st.error("Error: cann't access this web page!") 
                else:
                    st.error("Web link is exist already!")
            # Youtube video
            if youtube_link and checkers.is_url(youtube_link):
                found = False
                for r in st.session_state.resources:
                    if youtube_link==r['name']:
                        found=True
                if not found:
                    text, case = youtube_scrapper(youtube_link)
                    if case=='error':
                        st.error(text)
                    else:
                        with st.spinner("Please wait while geting the video's subtitles..."):
                            summary = st.session_state.agent.summarize(text, 'youtube video', youtube_link, st.session_state.language)
                            st.session_state.messages['messages'].append(('human', f"""attached "{youtube_link}" video link to summarize"""))
                            st.session_state.messages['messages'].append(('ai',summary))
                            st.session_state.agent.add_resources(text, 'youtube video', youtube_link)
                            add_resources(youtube_link, 'youtube', summary, datetime.date.today())
                            st.success("Your Youtube video added to resources successfully!!")
                            # st.rerun()
                else:
                    st.error("Youtube video is exist already!")
            st.rerun()
            st.space('xxsmall')
        # st.divider()
    
    # view resources 
    if st.session_state.resources:
        with st.container(border=True):
            st.subheader(":material/database: **Your Resources**", divider='blue')
            types = ['pdf', 'docx','txt', 'web-page', 'youtube']
            icons = {'web-page':":blue[:material/link:]", 'youtube':":red[:material/smart_display:]", 'pdf':":orange[:material/attachment:]", 'docx':":orange[:material/attachment:]", 'txt':":orange[:material/attachment:]"}
            if st.session_state.resources:
                for r in st.session_state.resources:
                    # tp = "Web-Page" if r['type'] == 'web-page' else "Attached file"
                    if r['type']=='web-page':
                        tp = 'Web-Page'
                    elif r['type']=='youtube':
                        tp = 'Youtube Video'
                    else:
                        tp = 'Attached File'
                    col11, col22 = st.columns([2,1], vertical_alignment='center')
                    with col11:
                        st.markdown(f"{icons[r['type']]} {tp}")
                    with col22:
                        st.caption(r['date'], text_alignment='right')
                    # st.markdown(f"{icons[r['type']]} {tp}")
                    st.markdown(r['name'])
                    # col11, col22 = st.columns([2,1], vertical_alignment='center')
                    # with col11:
                    with st.popover("Summary", type='tertiary'):
                        st.markdown(r['summary'])
                    # with col22:
                        # st.caption(r['date'], text_alignment='right')
                    st.divider()
            else:
                # st.space()
                st.warning("You haven't uploaded any data resources!")




if st.session_state.resources:
    message = st.chat_input("Say Something...", accept_audio=True, accept_file='multiple', file_type=['csv', 'pdf', 'txt', 'docx'], max_upload_size=20)
else:
    message = st.chat_input("Say Something...", accept_audio=True, accept_file='multiple', file_type=['csv', 'pdf', 'txt', 'docx'], max_upload_size=20, disabled=True)
# st.write(st.session_state.resources)

# for m in st.session_state.messages

# message = st.chat_input("Say Something...", accept_audio=True, accept_file='multiple', file_type=['csv', 'pdf', 'txt', 'docx'], max_upload_size=20)
if message:
    # if message.files:
    #     pass
    # mt.chat_message("assistant", avatar='media/bot avatar.png').
    # mt.chat_message("user", avatar='media/user avatar.png').markdown(message.text, text_alignment="right" if st.session_state.language =='Arabic' else 'left')
    # with mt2.chat_message("assistant", avatar='media/bot avatar.png').spinner():
    if message.text:
        mt.chat_message("user", avatar='media/user avatar.png').markdown(message.text, text_alignment="right" if st.session_state.language =='Arabic' else 'left')
        with mt2.chat_message("assistant", avatar='media/bot avatar.png').spinner():
            st.session_state.messages['messages'].append(('human', message.text))
            response = st.session_state.agent.predict(st.session_state.messages['messages'], st.session_state.language)
            # st.write(response.content)
            st.session_state.messages['messages'].append(('ai',response))
            st.rerun()
    if message.audio:
        mt.chat_message("user", avatar='media/user avatar.png').audio(message.audio)
        with mt2.chat_message("assistant", avatar='media/bot avatar.png').spinner('listening...'):
            with open("user_voice.mp3", "wb") as f:
                f.write(message.audio.read())
            text = st.session_state.agent.STT("user_voice.mp3", language=st.session_state.language)
            st.session_state.messages['messages'].append(('human', message.text))
            response = st.session_state.agent.predict(st.session_state.messages, st.session_state.language)
            st.session_state.messages['messages'].append(('ai',response))
            st.rerun()
    if message.files:
        
        for f in message.files:
            with st.spinner("Please wait while extracting your files text..."):
                # for f in files:
                found = False
                for r in st.session_state.resources:
                    if f.name==r['name']:
                        found=True
                if not found:
                    text = file_scrap(f)
                    # def summarize(self, text, source_type, source_name, language)
                    source_name = f.name
                    source_type = f.name.split('.')[-1].lower()
                    summary = st.session_state.agent.summarize(text, source_type, source_name, st.session_state.language)
                    st.session_state.messages['messages'].append(('human', f"""attached "{f.name}" file to summarize"""))
                    st.session_state.messages['messages'].append(('ai',summary))
                    st.session_state.agent.add_resources(text, source_type, source_name)
                    add_resources(f.name, f.name.split('.')[-1].lower(), summary, datetime.date.today())
                    st.success("Your document file added to resources successfully!")
                    st.rerun()
                else:
                    st.error("File is exist already!")

if st.session_state.resources:
    with st.columns([2,0.8])[0].expander(":green[:material/database:] Your Resources"):
        st.subheader("**Your Resources**", divider='blue')
        types = ['pdf', 'docx','txt', 'web-page', 'youtube']
        icons = {'web-page':":blue[:material/link:]", 'youtube':":red[:material/smart_display:]", 'pdf':":orange[:material/attachment:]", 'docx':":orange[:material/attachment:]", 'txt':":orange[:material/attachment:]"}
        if st.session_state.resources:
            for r in st.session_state.resources:
                # tp = "Web-Page" if r['type'] == 'web-page' else "Attached file"
                if r['type']=='web-page':
                    tp = 'Web-Page'
                elif r['type']=='youtube':
                    tp = 'Youtube Video'
                else:
                    tp = 'Attached File'
                col11, col22 = st.columns([2,1], vertical_alignment='center')
                with col11:
                    st.markdown(f"{icons[r['type']]} {tp}")
                with col22:
                    st.caption(r['date'], text_alignment='right')
                # st.markdown(f"{icons[r['type']]} {tp}")
                st.markdown(r['name'])
                # col11, col22 = st.columns([2,1], vertical_alignment='center')
                # with col11:
                with st.popover("Summary", type='tertiary'):
                    st.markdown(r['summary'])
                # with col22:
                    # st.caption(r['date'], text_alignment='right')
                st.divider()
        else:
            # st.space()
            st.warning("You haven't uploaded any data resources!")
        
# Settings
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
                st.rerun()
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
                    st.rerun()
            with col22:
                if st.button(":material/delete:", width='stretch', type='tertiary', key=c):
                    if st.session_state.chat_id == c:
                        st.session_state.messages = {"messages": [("system", st.session_state.prompt)]}
                        st.session_state.chat_id = len(st.session_state.chat_history)
                        # st.session_state.agent = Agent(st.secrets['GeminiAPI'])
                    del st.session_state.chat_history[c]
                    st.rerun()
    # st.button("New Chat", icon=':material/add:', width='stretch', type='tertiary')

    st.divider()
    st.header(":material/settings: Settings")
    new_lang = st.selectbox(f"**Voice Language** (current is {st.session_state.language})", ('Arabic', 'English'), placeholder='Language..', index=None)
    if new_lang and new_lang != st.session_state.language:
        st.write(f"Language will be change into :blue[{new_lang}]")
        if st.button("Save changes", type='primary'):
            st.session_state.language = new_lang
            st.rerun()

