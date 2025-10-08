import streamlit as st
import requests
import google.generativeai as genai
import yt_dlp
from io import BytesIO
import sys
import contextlib

# --- PAGE SETUP ---
st.set_page_config(page_title="Free Notes Generator", page_icon="📝")

# --- API KEY SETUP ---
try:
    HF_API_TOKEN = st.secrets["HF_API_TOKEN"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.warning("API key not found. Please set your Hugging Face and Google API keys in Streamlit secrets.")

# --- HUGGING FACE API FUNCTION (FOR TRANSCRIPTION) ---
HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def transcribe_audio(audio_buffer):
    response = requests.post(HF_API_URL, headers=headers, data=audio_buffer)
    result = response.json()
    if "text" in result:
        return result["text"]
    else:
        st.error(f"Transcription Error: {result.get('error', 'Unknown error')}")
        return None

# --- GOOGLE GEMINI API FUNCTION (FOR SUMMARIZATION) ---
model = genai.GenerativeModel('gemini-pro')

def summarize_text(transcript):
    prompt = f"Generate concise, well-organized study notes from the following transcript: {transcript}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Summarization Error: {e}")
        return None

# --- MAIN APP LOGIC ---
st.title("AI-Powered Notes Generator (Free Version) 📝")
st.markdown("Get a transcript and study notes from a YouTube video or an audio file.")

tab1, tab2 = st.tabs(["▶️ YouTube URL", "📁 File Upload"])

def process_audio(audio_buffer):
    with st.spinner('Transcribing audio... This might take a moment.'):
        transcript_text = transcribe_audio(audio_buffer)
    
    if transcript_text:
        st.subheader("Transcript")
        st.text_area("Full Transcript", transcript_text, height=200)
        
        with st.spinner('Generating study notes...'):
            study_notes = summarize_text(transcript_text)
        
        if study_notes:
            st.subheader("Study Notes")
            st.markdown(study_notes)

# YouTube URL Tab
with tab1:
    st.header("Generate Notes from a YouTube Video")
    youtube_url = st.text_input("Enter YouTube URL:")

    if youtube_url:
        with st.spinner('Downloading audio from YouTube...'):
            try:
                # More robust method to download audio directly into a buffer
                buffer = BytesIO()
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': '-', # Directs output to stdout
                    'logtostderr': True,
                    'quiet': True,
                }
                
                # Temporarily redirect stdout to our buffer
                with contextlib.redirect_stdout(buffer):
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtube_url])
                
                buffer.seek(0)
                st.success(f"Successfully loaded audio.")
                process_audio(buffer)

            except Exception as e:
                st.error(f"Error downloading from YouTube: {e}")

# File Upload Tab
with tab2:
    st.header("Generate Notes from an Audio File")
    uploaded_file = st.file_uploader("Choose an audio file...", type=['mp3', 'm4a', 'wav'])

    if uploaded_file is not None:
        process_audio(uploaded_file)