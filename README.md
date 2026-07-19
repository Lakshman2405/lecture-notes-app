# 📝 AI Lecture-to-Notes Generator

An intelligent application that transforms lecture audio into comprehensive study materials using advanced AI technologies. Upload any lecture recording and automatically generate transcripts, summaries, quizzes, and flashcards!

## 🌟 Features

- **Audio Transcription**: Convert lecture recordings (WAV, MP3, M4A) to text using OpenAI's Whisper API
- **AI-Powered Study Materials**: Generate structured study guides including:
  - **Summary**: Key points and main topics in bulleted format
  - **Quiz**: Multiple-choice questions to test understanding
  - **Flashcards**: Important terms with definitions for memorization
- **YouTube Integration**: Download audio from YouTube videos for transcription
- **Interactive Web Interface**: Built with Streamlit for easy, intuitive use
- **Multi-format Support**: Supports WAV, MP3, and M4A audio formats
- **Real-time Processing**: Spinner animations and status updates during processing

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Hugging Face API token ([Get one here](https://huggingface.co/settings/tokens))
- Google Generative AI API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Lakshman2405/lecture-notes-app.git
   cd lecture-notes-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**
   
   Create a `.streamlit/secrets.toml` file in the project directory:
   ```toml
   HF_API_TOKEN = "your_hugging_face_token_here"
   GOOGLE_API_KEY = "your_google_api_key_here"
   ```

   Alternatively, if deploying on Streamlit Cloud, add these secrets through the app dashboard.

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`

## 📋 Usage

### Generate Notes from Audio File

1. Launch the application using the command above
2. Click "Choose an audio file..." and select your lecture recording
3. Preview the audio using the built-in player
4. Click the "Generate Study Notes" button
5. Wait for transcription and study material generation
6. View the transcript and AI-generated study materials side-by-side

### Download YouTube Audio

To extract audio from YouTube lectures:

```bash
python download.py
```

Follow the prompt to enter a YouTube URL. The audio will be saved as an MP3 file in the project directory, which you can then upload to the main application.

## 📁 Project Structure

```
lecture-notes-app/
├── app.py                 # Main Streamlit application
├── download.py            # YouTube audio downloader utility
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── .devcontainer/        # Development container configuration
```

## 🔧 Technical Details

### Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web application framework for UI |
| `requests` | HTTP library for API calls |
| `google-generativeai` | Google Gemini AI for content generation |
| `yt_dlp` | YouTube video downloading and audio extraction |

### API Services Used

**Hugging Face Whisper API**
- Transcribes audio to text using OpenAI's Whisper model
- Endpoint: `https://api-inference.huggingface.co/models/openai/whisper-large-v3`
- Supports high-accuracy transcription with automatic retry on model loading

**Google Generative AI (Gemini)**
- Generates structured study materials from transcripts
- Model: `gemini-2.5-flash`
- Produces summaries, quizzes, and flashcards in Markdown format

### Error Handling

The application includes robust error handling for:
- Invalid or missing API keys
- Model loading delays (with automatic retry)
- Non-JSON API responses
- Empty or silent audio files
- Network connectivity issues

## 💡 How It Works

```
Audio File Upload
      ↓
Transcription (Whisper)
      ↓
Transcript Generated
      ↓
AI Processing (Gemini)
      ↓
Study Materials Generated
      ↓
Display: Summary, Quiz, Flashcards
```

## 🎓 Use Cases

- **Students**: Transform lecture recordings into organized study guides
- **Educators**: Create study materials from recorded lectures automatically
- **Online Learning**: Extract key information from course videos
- **Content Creation**: Generate quiz questions and flashcards from audio content
- **Accessibility**: Create text transcripts of spoken lectures

## ⚙️ Configuration

### Supported Audio Formats
- `.wav` - WAV audio files
- `.mp3` - MPEG audio files
- `.m4a` - Apple audio files (AAC)

### File Size Limit
- Maximum upload size: 200MB

### Processing Time
- Typical transcription: 1-5 minutes depending on audio length
- Study material generation: 30-60 seconds
- Varies based on server load and audio quality

## 🐛 Troubleshooting

**Issue: "API keys not found in Streamlit secrets"**
- Ensure `.streamlit/secrets.toml` exists with correct API keys
- Check token validity on Hugging Face and Google Cloud Console

**Issue: "Transcription API Error"**
- Verify audio file format (WAV, MP3, or M4A)
- Check internet connection
- Ensure Hugging Face API token is valid

**Issue: "Model is currently loading"**
- The application automatically retries after waiting
- This is normal on first use or after inactivity

**Issue: "Empty transcript generated"**
- Audio may be too silent or contain only background noise
- Try a clearer audio file with better recording quality

## 🔐 Security

- API keys are stored locally in `.streamlit/secrets.toml` (not committed to git)
- All API calls use secure HTTPS connections
- Audio files are processed in-memory and not permanently stored
- Sensitive credentials are never logged or exposed

## 📈 Performance Optimization

- Uses Streamlit's caching mechanisms (where applicable)
- Efficient streaming for large audio files
- Retry logic with exponential backoff for API calls
- Optimized prompts for faster Gemini processing

## 🛠️ Development

### Running in Development Container

The `.devcontainer` folder contains configuration for VS Code Dev Containers:
```bash
# Open in VS Code and reopen in container
# This ensures consistent development environment
```

### Adding New Features

1. Create a new branch
2. Implement your feature
3. Test thoroughly with various audio formats and lengths
4. Submit a pull request

## 📝 Example Output

### Transcript
```
[Full transcribed text of the lecture...]
```

### Study Materials
**Summary**
- Key Point 1: Description
- Key Point 2: Description
- Key Point 3: Description

**Quiz**
1. What is...?
   - Option A
   - Option B ✓ (correct)
   - Option C
   
**Flashcards**
- Term 1: Definition 1
---
- Term 2: Definition 2
---
- Term 3: Definition 3
```

## 📄 License

This project is open source and available for educational and personal use.

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs and issues
- Suggest improvements or new features
- Submit pull requests with enhancements

## 📧 Support

For issues, questions, or suggestions, please open a GitHub issue or contact the repository owner.

## 🎯 Future Enhancements

- [ ] Multiple language transcription support
- [ ] PDF export for study materials
- [ ] Custom prompt templates for different subjects
- [ ] Integration with note-taking apps
- [ ] Batch processing for multiple files
- [ ] Advanced filtering and editing of transcripts
- [ ] Cloud storage integration
- [ ] User authentication and history tracking

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for transcription
- [Google Generative AI](https://ai.google.dev/) for content generation
- [Streamlit](https://streamlit.io/) for the interactive framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube integration

---

Made with ❤️ for students and educators everywhere!
