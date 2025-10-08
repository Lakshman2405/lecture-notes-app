import streamlit as st
import openai
import yt_dlp
from io import BytesIO
import requests

# --- PAGE SETUP ---
st.set_page_config(page_title="Notes Generator", page_icon="📝")

# --- API KEY SETUP ---
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.warning("API key not found. Please set it in Streamlit secrets.")

# --- APP TITLE AND DESCRIPTION ---
st.title("AI-Powered Notes Generator 📝")
st.markdown("Get a transcript and study notes from a YouTube video or an audio file.")

# --- TABS FOR INPUT METHOD ---
tab1, tab2 = st.tabs(["▶️ YouTube URL", "📁 File Upload"])

# --- YOUTUBE URL TAB ---
with tab1:
    st.header("Generate Notes from a YouTube Video")
    youtube_url = st.text_input("Enter YouTube URL:")

    if youtube_url:
        with st.spinner('Processing your video... This might take a moment.'):
            try:
                # --- Get Audio from YouTube using yt-dlp ---
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '%(title)s.%(ext)s'
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(youtube_url, download=False)
                    video_title = info_dict.get('title', 'Untitled Video')
                    # Find the best audio URL from the formats
                    audio_url = None
                    for f in info_dict['formats']:
                        if f['acodec'] != 'none' and f['vcodec'] == 'none':
                            audio_url = f['url']
                            break
                    if not audio_url:
                         # Fallback if no audio-only stream is found
                         audio_url = info_dict['url']


                # Download the audio content from the URL into memory
                response = requests.get(audio_url)
                buffer = BytesIO(response.content)
                buffer.name = 'audio.mp3'  # Name the buffer for the API

                st.success(f"Successfully loaded audio from: '{video_title}'")
                
                # --- Transcription ---
                st.subheader("Transcript")
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1", 
                    file=buffer
                )
                st.text_area("Full Transcript", transcript.text, height=200, key="yt_transcript")

                # --- Summarization ---
                st.subheader("Study Notes")
                prompt = f"Generate concise, well-organized study notes from the following transcript: {transcript.text}"
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates study notes from transcripts."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.markdown(response.choices[0].message.content, key="yt_notes")

            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- FILE UPLOAD TAB ---
with tab2:
    st.header("Generate Notes from an Audio File")
    uploaded_file = st.file_uploader("Choose an audio file (.mp3, .m4a, .wav)...", type=['mp3', 'm4a', 'wav'])

    if uploaded_file is not None:
        with st.spinner('Processing your audio file... This might take a moment.'):
            try:
                # --- Transcription ---
                st.subheader("Transcript")
                transcript = openai.audio.transcriptions.create(
                    model="whisper-1", 
                    file=uploaded_file
                )
                st.text_area("Full Transcript", transcript.text, height=200, key="file_transcript")

                # --- Summarization ---
                st.subheader("Study Notes")
                prompt = f"Generate concise, well-organized study notes from the following transcript: {transcript.text}"
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates study notes from transcripts."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.markdown(response.choices[0].message.content, key="file_notes")

            except Exception as e:
                st.error(f"An error occurred: {e}")