import streamlit as st
import requests
import google.generativeai as genai
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Lecture-to-Notes Generator",
    page_icon="📝",
    layout="wide"
)

# --- API KEY SETUP ---
# To deploy, use st.secrets. For local testing, you can paste your keys directly.
try:
    # Attempt to get keys from Streamlit's secrets management
    HF_API_TOKEN = st.secrets["HF_API_TOKEN"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    # Fallback for local development if secrets aren't set
    st.warning("API keys not found in Streamlit secrets. Using placeholders. Please add your keys for the app to work.")
    HF_API_TOKEN = "hf_YOUR_HUGGING_FACE_TOKEN"  # Replace with your Hugging Face token
    GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"      # Replace with your Google API key

genai.configure(api_key=GOOGLE_API_KEY)

# --- API FUNCTIONS ---
HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')

def transcribe_audio(audio_buffer):
    """
    Transcribes audio using Hugging Face's free Whisper API.
    Includes a retry mechanism for when the model is loading.
    """
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    response = requests.post(HF_API_URL, headers=headers, data=audio_buffer)
    result = response.json()

    # Handle the case where the model is loading
    if "error" in result and "is currently loading" in result["error"]:
        wait_time = result.get("estimated_time", 25)
        st.info(f"The transcription model is loading, please wait. Retrying in {wait_time:.0f} seconds...")
        time.sleep(wait_time)
        
        # Retry the request
        response = requests.post(HF_API_URL, headers=headers, data=audio_buffer)
        result = response.json()

    if "text" in result:
        return result["text"]
    else:
        st.error(f"Transcription Error: {result.get('error', 'Could not process audio.')}")
        return None

def generate_study_notes(transcript):
    """
    Generates structured study notes from a transcript using the Google Gemini API.
    """
    prompt = f"""
    Based on the following lecture transcript, generate a comprehensive set of study materials.
    Structure your response with these three distinct sections:
    1.  **Summary:** A concise, bulleted summary of the key points and main topics.
    2.  **Quiz:** 3 multiple-choice questions to test understanding, with the correct answer clearly indicated.
    3.  **Flashcards:** 3 important key terms and their definitions, formatted as 'Term: Definition'.

    Transcript:
    ---
    {transcript}
    ---
    """
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Summarization Error: {e}")
        return None

# --- STREAMLIT APP LAYOUT ---
st.title("AI Lecture-to-Notes Generator 📝")
st.markdown("Upload any lecture audio file (`.wav`, `.mp3`, `.m4a`) to automatically generate a transcript and a complete study guide.")

uploaded_file = st.file_uploader("Choose an audio file...", type=['wav', 'mp3', 'm4a'])

if uploaded_file is not None:
    st.audio(uploaded_file, format=uploaded_file.type)
    
    # Process the audio when the button is clicked
    if st.button("Generate Study Notes"):
        # Display spinners while processing
        with st.spinner('Transcribing audio... This can take a few moments.'):
            transcript_text = transcribe_audio(uploaded_file)
        
        if transcript_text:
            with st.spinner('Generating your study guide with Gemini...'):
                study_notes = generate_study_notes(transcript_text)
            
            st.success("Processing complete!")
            
            # Display results in two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Transcript")
                st.text_area("Full Lecture Transcript", transcript_text, height=400)
                
            with col2:
                st.subheader("AI-Generated Study Materials")
                st.markdown(study_notes)