import yt_dlp
import os

def download_audio_from_youtube():
    video_url = input("Please enter the YouTube video URL: ")
    
    # Define the output path to be the same folder as the script
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Downloading and converting audio...")
            ydl.download([video_url])
        print("\nSuccess! Your MP3 file is saved in the YouTube Downloader folder.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    download_audio_from_youtube()