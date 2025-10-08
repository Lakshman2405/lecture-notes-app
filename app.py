import streamlit as st
import requests
import google.generativeai as genai
from io import BytesIO
import time
import json

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
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
model = genai.GenerativeModel('gemini-pro')

def transcribe_audio(audio_buffer):
    """
    Sends audio to Hugging Face API, handles model loading, and safely decodes JSON.
    """
    response = requests.post(HF_API_URL, headers=headers, data=audio_buffer)
    
    # Try to decode the JSON response
    try:
        result = response.json()
    except json.JSONDecodeError:
        st.error(f"Failed to decode response from Hugging Face. Raw response: {response.text}")
        return None

    # Handle the case where the model is loading
    if "error" in result and "is currently loading" in result["error"]:
        wait_time = result.get("estimated_time", 20)
        st.info(f"Model is loading, please wait. Retrying in {wait_time:.0f} seconds...")
        time.sleep(wait_time)
        
        # Retry the request
        response = requests.post(HF_API_URL, headers=headers, data=audio_buffer)
        try:
            result = response.json()
        except json.JSONDecodeError:
            st.error(f"Failed to decode response on retry. Raw response: {response.text}")
            return None

    # Final check for text or error
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
st.markdown("Upload an audio file to get a transcript and study notes.")

uploaded_file = st.file_uploader("Choose an audio file (.mp3, .m4a, .wav)...", type=['mp3', 'm4a', 'wav'])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/mp3')
    
    with st.spinner('Transcribing audio... This may take a moment for large files.'):
        transcript_text = transcribe_audio(uploaded_file)
    
    if transcript_text:
        st.subheader("Transcript")
        st.text_area("Full Transcript", transcript_text, height=200)
        
        with st.spinner('Generating study notes...'):
            study_notes = summarize_text(transcript_text)
        
        if study_notes:
            st.subheader("Study Notes")
            st.markdown(study_notes)