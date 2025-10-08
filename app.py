import streamlit as st
import openai
from pytube import YouTube
import os
from io import BytesIO

# --- PAGE SETUP ---
st.set_page_config(page_title="YT-to-Notes", page_icon="▶️")

# --- API KEY SETUP ---
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.warning("API key not found. Please set it in Streamlit secrets.")

# --- APP TITLE AND DESCRIPTION ---
st.title("YouTube Video to Study Notes Generator ▶️➡️📝")
st.markdown("Enter a YouTube video URL, and I'll transcribe and summarize it into study notes for you!")

# --- URL INPUT ---
youtube_url = st.text_input("Enter YouTube URL:")

if youtube_url:
    # Display a spinner while processing
    with st.spinner('Processing your video... This might take a moment.'):
        try:
            # --- 1. GET AUDIO FROM YOUTUBE ---
            st.subheader("1. Getting Audio from YouTube")
            yt = YouTube(youtube_url)
            
            # Filter for audio-only streams and get the best one
            audio_stream = yt.streams.filter(only_audio=True).first()
            
            # Download the audio into an in-memory buffer (no file is saved)
            buffer = BytesIO()
            audio_stream.stream_to_buffer(buffer)
            # IMPORTANT: Reset buffer's pointer to the beginning for Whisper API
            buffer.seek(0)
            
            st.success(f"Successfully loaded audio from: '{yt.title}'")

            # --- 2. TRANSCRIPTION ---
            st.subheader("2. Video Transcript")
            # We need to give the file a name for the API, even though it's in memory
            buffer.name = 'audio.mp3' 
            
            # Call the Whisper API to transcribe the audio
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", 
                file=buffer
            )
            st.success("Transcription complete!")
            st.text_area("Full Transcript", transcript.text, height=200)

            # --- 3. SUMMARIZATION & NOTE GENERATION ---
            st.subheader("3. Your Study Notes")
            prompt = f"""
            Based on the following video transcript, please generate a set of concise study notes.
            The notes should be well-organized, highlighting the key concepts, definitions, and important examples mentioned.
            Use bullet points for clarity.

            Transcript:
            "{transcript.text}"
            """
            
            # Call the GPT-4 API to generate notes
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates study notes from video transcripts."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            study_notes = response.choices[0].message.content
            st.success("Study notes generated!")
            st.markdown(study_notes)

        except Exception as e:
            st.error(f"An error occurred: {e}")