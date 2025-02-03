import argparse
import logging
import moviepy
import whisper
from moviepy import CompositeVideoClip, TextClip, VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
from whisper import Whisper

def generate_captions(whisper_model: Whisper, audio_file, captions_file = ""):
    print("transcribing...")
    result = whisper_model.transcribe(audio_file, word_timestamps=True)
    print("transcription results", result)
    for segment in result["segments"]:
        print(f"Start: {segment['start']}, End: {segment['end']}, Text: {segment['text']}")
    return result["segments"]

def add_captions_to_video(caption_segments, video_file):
    # Load the video clip.
    video = VideoFileClip(video_file)
    
    # Convert caption_segments (dicts) into a list of ((start, end), text) tuples.
    subs = [((seg["start"], seg["end"]), seg["text"]) for seg in caption_segments]
    
    # Generator function that returns a styled TextClip for a given subtitle string.
    generator = lambda txt: TextClip(
        text=txt, font='Arial', font_size=24, size=(48, 48), color='white',
        stroke_color='black', method='caption'
    )
    
    # Create the subtitles clip.
    subtitles = SubtitlesClip(subs, make_textclip=generator, encoding="utf-8")
    
    # Composite the video with the subtitles overlay.
    video_with_captions = CompositeVideoClip([video, subtitles])
    
    # Write the final video file.
    video_with_captions.write_videofile(
        "output_video.mp4", fps=video.fps,
        temp_audiofile="temp-audio.m4a", remove_temp=True,
        codec="libx264", audio_codec="aac"
    )


def main(video_file, captions_file):
    try:
        print("trying")
        model = whisper.load_model("base")
        audio_file = VideoFileClip(video_file)
        audio_file.audio.write_audiofile("audio_file.mp3")
        caption_segments = generate_captions(model, "audio_file.mp3")
        add_captions_to_video(caption_segments, video_file)
        return 
    except Exception as e:
        logging.exception(f"Could not load file, {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_file", required=True)
    parser.add_argument("--captions_file", required=False, default=None)
    args = parser.parse_args()
    video_file = args.video_file
    captions_file = args.captions_file
    main(video_file, captions_file)