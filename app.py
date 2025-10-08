import streamlit as st
import requests
import google.generativeai as genai
from io import BytesIO
import time
import json
import yt_dlp
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

# --- API FUNCTIONS ---
HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
model = genai.GenerativeModel('gemini-1.5-flash')

def transcribe_audio(audio_buffer, content_type):
    """
    Sends audio to Hugging Face API with the correct content type.
    """
    # Create headers with the specific content type
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": content_type
    }
    
    response = requests.post(HF_API_URL, headers=headers, data=audio_buffer)
    
    try:
        result = response.json()
    except json.JSONDecodeError:
        st.error(f"Failed to decode response from Hugging Face. Raw response: {response.text}")
        return None

    if "error" in result and "is currently loading" in result["error"]:
        wait_time = result.get("estimated_time", 20)
        st.info(f"Model is loading, please wait. Retrying in {wait_time:.0f} seconds...")
        time.sleep(wait_time)
        
        response = requests.post(HF_API_URL, headers=headers, data=audio_buffer)
        try:
            result = response.json()
        except json.JSONDecodeError:
            st.error(f"Failed to decode response on retry. Raw response: {response.text}")
            return None

    if "text" in result:
        return result["text"]
    else:
        st.error(f"Transcription Error: {result.get('error', 'Could not process audio.')}")
        return None

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

def process_audio(audio_buffer, content_type):
    with st.spinner('Transcribing audio... This may take a moment.'):
        transcript_text = transcribe_audio(audio_buffer, content_type)
    
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
                buffer = BytesIO()
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': '-',
                    'logtostderr': True,
                    'quiet': True,
                }
                
                with contextlib.redirect_stdout(buffer):
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtube_url])
                
                buffer.seek(0)
                st.success(f"Successfully loaded audio.")
                # For YouTube, we know it's an audio format, often mpeg (mp3)
                process_audio(buffer, 'audio/mpeg')

            except Exception as e:
                st.error(f"Error downloading from YouTube: {e}")

# File Upload Tab
with tab2:
    st.header("Generate Notes from an Audio File")
    uploaded_file = st.file_uploader("Choose an audio file...", type=['mp3', 'm4a', 'wav'])

    if uploaded_file is not None:
        # Get the content type from the uploaded file itself
        process_audio(uploaded_file, uploaded_file.type)