import streamlit as st
import openai
import os

# --- PAGE SETUP ---
# Set the title and icon of the browser tab
st.set_page_config(page_title="Lecture-to-Notes", page_icon="🎙️")

# --- API KEY SETUP ---
# Get the API key from Streamlit's secrets management
# For local testing, you can set this as an environment variable
# For deployment, you will set this in Streamlit Community Cloud's settings
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.warning("API key not found. Please set it in Streamlit secrets.")
    # As a fallback for local development, you might use an environment variable
    # or hardcode it, but be careful not to expose it in public repositories.
    # For example: openai.api_key = "YOUR_API_KEY_HERE" (NOT RECOMMENDED FOR PRODUCTION)

# --- APP TITLE AND DESCRIPTION ---
st.title("AI-Powered Lecture-to-Notes Generator 🎙️➡️📝")
st.markdown("Upload a lecture audio file, and I'll transcribe and summarize it into study notes for you!")

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Choose an audio file (.mp3, .m4a, .wav)...", type=['mp3', 'm4a', 'wav'])

if uploaded_file is not None:
    # Display a spinner while processing
    with st.spinner('Processing your lecture... This might take a moment.'):
        try:
            # --- 1. TRANSCRIPTION ---
            st.subheader("1. Lecture Transcript")
            # Call the Whisper API to transcribe the audio
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", 
                file=uploaded_file
            )
            st.success("Transcription complete!")
            st.text_area("Full Transcript", transcript.text, height=200)

            # --- 2. SUMMARIZATION & NOTE GENERATION ---
            st.subheader("2. Your Study Notes")
            # Create a prompt for the GPT model
            prompt = f"""
            Based on the following lecture transcript, please generate a set of concise study notes.
            The notes should be well-organized, highlighting the key concepts, definitions, and important examples mentioned.
            Use bullet points for clarity.

            Transcript:
            "{transcript.text}"
            """
            
            # Call the GPT-4 API to generate notes
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates study notes from lecture transcripts."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            study_notes = response.choices[0].message.content
            st.success("Study notes generated!")
            st.markdown(study_notes)

        except Exception as e:
            st.error(f"An error occurred: {e}")