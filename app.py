import streamlit as st
import requests
import google.generativeai as genai
import time
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Lecture-to-Notes Generator",
    page_icon="📝",
    layout="wide"
)

# --- API KEY SETUP ---
# It is best practice to use st.secrets for deployment.
try:
    # Attempt to get keys from Streamlit's secrets management
    HF_API_TOKEN = st.secrets["HF_API_TOKEN"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    # Fallback for local development if secrets aren't set
    st.error("API keys not found in Streamlit secrets. Please ensure .streamlit/secrets.toml is configured.")
    # WARNING: These are placeholders. The app will only work with real keys in secrets.toml.
    HF_API_TOKEN = "hf_YOUR_HUGGING_FACE_TOKEN"  
    GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"       

genai.configure(api_key=GOOGLE_API_KEY)

# --- API CONFIGURATION ---
HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')

def transcribe_audio(audio_buffer):
    """
    Transcribes audio using Hugging Face's Whisper API.
    Sends the raw binary data of the audio file to the API.
    """
    # CRITICAL FIX: Explicitly reads the file bytes to avoid the "Content type None" error.
    # Reset the stream position to the start before reading.
    audio_buffer.seek(0)
    # Read the content into raw bytes
    audio_bytes = audio_buffer.read()

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    # Send the raw audio bytes as the request data
    response = requests.post(HF_API_URL, headers=headers, data=audio_bytes)
    result = response.json()

    # Handle the case where the model is loading (common with free tier APIs)
    if "error" in result and "is currently loading" in result["error"]:
        wait_time = result.get("estimated_time", 25)
        st.info(f"The transcription model is loading, please wait. Retrying in {wait_time:.0f} seconds...")
        
        # Wait time + 2 seconds buffer
        time.sleep(wait_time + 2) 
        
        # Retry the request
        response = requests.post(HF_API_URL, headers=headers, data=audio_bytes)
        result = response.json()

    if "text" in result:
        return result["text"]
    else:
        st.error(f"Transcription Error (API Response): {result.get('error', 'Could not process audio.')}")
        st.caption("Double-check your Hugging Face API Token and the file size/format.")
        return None

def generate_study_notes(transcript):
    """
    Generates structured study notes (Summary, Quiz, Flashcards) 
    from a transcript using the Google Gemini API.
    """
    prompt = f"""
    Based on the following lecture transcript, generate a comprehensive set of study materials.
    Structure your response using Markdown with these three distinct sections:
    1.  **Summary:** A concise, bulleted summary of the key points and main topics. Use Markdown lists.
    2.  **Quiz:** 3 multiple-choice questions to test understanding, with the correct answer clearly indicated (e.g., in bold).
    3.  **Flashcards:** 3 important key terms and their definitions, formatted as 'Term: Definition' and separated by a horizontal rule (---).

    Transcript:
    ---
    {transcript}
    ---
    """
    
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Summarization Error with Gemini: {e}")
        st.caption("Ensure your Google API Key is correct.")
        return None

# --- STREAMLIT APP LAYOUT ---
st.title("AI Lecture-to-Notes Generator 📝")
st.markdown("Upload any lecture audio file (`.wav`, `.mp3`, `.m4a`) to automatically generate a transcript and a complete study guide.")

# Max file size set to 200MB 
uploaded_file = st.file_uploader("Choose an audio file...", type=['wav', 'mp3', 'm4a'], help="Max size 200MB.")

if uploaded_file is not None:
    # Display the audio player
    st.audio(uploaded_file, format=uploaded_file.type)
    
    # Process the audio when the button is clicked
    if st.button("Generate Study Notes", type="primary"):
        
        # Check if API keys are likely invalid (based on placeholders)
        if "YOUR_GOOGLE_API_KEY" in GOOGLE_API_KEY or "YOUR_HUGGING_FACE_TOKEN" in HF_API_TOKEN:
             st.error("Configuration Error: Please provide valid API keys in your Streamlit secrets (`.streamlit/secrets.toml`).")
        else:
            # Step 1: Transcribe Audio
            with st.spinner('Transcribing audio... This can take a few moments depending on file size.'):
                transcript_text = transcribe_audio(uploaded_file)
            
            if transcript_text:
                st.success("Transcription complete!")
                
                # Step 2: Generate Study Materials
                with st.spinner('Generating your study guide with Gemini...'):
                    study_notes = generate_study_notes(transcript_text)
                
                if study_notes:
                    st.success("Study materials generated successfully!")
                    
                    # Display results in two columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Transcript")
                        st.text_area("Full Lecture Transcript", transcript_text, height=450)
                        
                    with col2:
                        st.subheader("AI-Generated Study Materials")
                        # Use st.markdown to properly render the structured output from Gemini
                        st.markdown(study_notes)