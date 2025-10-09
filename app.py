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
try:
    HF_API_TOKEN = st.secrets["HF_API_TOKEN"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("API keys not found in Streamlit secrets. Please ensure .streamlit/secrets.toml is configured.")
    HF_API_TOKEN = "hf_YOUR_HUGGING_FACE_TOKEN"  
    GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"       

genai.configure(api_key=GOOGLE_API_KEY)

# --- API CONFIGURATION ---
HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
GEMINI_MODEL = genai.GenerativeModel('gemini-2.5-flash')

def transcribe_audio(audio_buffer):
    """
    Transcribes audio using Hugging Face's Whisper API.
    Uses the final, confirmed method: raw bytes with manual Content-Type header.
    """
    audio_buffer.seek(0)
    audio_bytes = audio_buffer.read()
    
    # 🌟 FINAL FIX: Use raw data + manual Content-Type header (not the 'files=' parameter)
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": audio_buffer.type # Use the file's detected mime type
    }
    
    # Send the raw audio bytes as the request data
    response = requests.post(HF_API_URL, headers=headers, data=audio_bytes)

    # 1. Check status code first
    if response.status_code != 200:
        st.error(f"Transcription API Error (Status {response.status_code}): Could not process request.")
        # Attempt to display the error text for debugging
        st.caption(f"Raw Response Text (Non-JSON): {response.text[:200]}...")
        return None

    try:
        result = response.json()
    except requests.exceptions.JSONDecodeError:
        st.error("Transcription API returned a non-JSON response.")
        st.caption(f"The server is likely down or the API token is invalid. Raw status: {response.status_code}")
        return None

    # Handle the case where the model is loading
    if isinstance(result, dict) and "error" in result and "is currently loading" in result["error"]:
        wait_time = result.get("estimated_time", 25)
        st.info(f"The transcription model is loading, please wait. Retrying in {wait_time:.0f} seconds...")
        time.sleep(wait_time + 2) 
        
        # Retry logic
        response = requests.post(HF_API_URL, headers=headers, data=audio_bytes) # Use data=audio_bytes here too
        
        if response.status_code != 200:
            st.error("Retry failed. Status was not 200.")
            return None
            
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            st.error("Retry failed. Returned non-JSON.")
            return None

    # Final check for success or failure
    if isinstance(result, dict) and "text" in result and result["text"].strip():
        return result["text"]
    else:
        # Handles empty strings or API-side errors reported in JSON
        error_message = ""
        if isinstance(result, dict) and 'error' in result:
            error_message = result['error']
        
        st.error(f"Transcription failed: {error_message or 'No meaningful text returned.'}")
        st.caption("The audio file may be silent, or the API failed internally.")
        return None

def generate_study_notes(transcript):
    """
    Generates structured study notes (Summary, Quiz, Flashcards) 
    from a transcript using the Google Gemini API.
    """
    if not transcript or not transcript.strip():
        return "**No Content Detected**\n\nThe AI summarization skipped the content as the transcription returned only silence or background noise. Please try a different audio file."

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

uploaded_file = st.file_uploader("Choose an audio file...", type=['wav', 'mp3', 'm4a'], help="Max size 200MB.")

if uploaded_file is not None:
    st.audio(uploaded_file, format=uploaded_file.type)
    
    if st.button("Generate Study Notes", type="primary"):
        
        # Check if API keys are likely invalid (based on placeholders)
        if "YOUR_GOOGLE_API_KEY" in GOOGLE_API_KEY or "YOUR_HUGGING_FACE_TOKEN" in HF_API_TOKEN:
             st.error("Configuration Error: Please provide valid API keys in your Streamlit secrets (`.streamlit/secrets.toml`).")
        else:
            with st.spinner('Transcribing audio... This can take a few moments depending on file size.'):
                transcript_text = transcribe_audio(uploaded_file)
            
            if transcript_text:
                st.success("Transcription complete!")
                
                with st.spinner('Generating your study guide with Gemini...'):
                    study_notes = generate_study_notes(transcript_text)
                
                if study_notes:
                    st.success("Study materials generated successfully!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Transcript")
                        # Display a warning if the content is just the "No Content Detected" message
                        if "No Content Detected" in study_notes:
                            st.warning("Transcript was empty or contained only noise.")
                        st.text_area("Full Lecture Transcript", transcript_text, height=450)
                        
                    with col2:
                        st.subheader("AI-Generated Study Materials")
                        st.markdown(study_notes)
