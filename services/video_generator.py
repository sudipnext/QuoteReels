import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Optional, Tuple
from flask import jsonify
import requests
from moviepy import CompositeVideoClip, TextClip, VideoFileClip, ColorClip, concatenate_videoclips
import tqdm
from api.tts_client import TTSClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoGeneratorError(Exception):
    """Custom exception for video generation errors"""
    pass


class VideoGenerator:
    def __init__(self):
        """Initialize video generator with default settings"""
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        self.temp_dir = Path(tempfile.gettempdir()) / "reels_automator"
        self.temp_dir.mkdir(exist_ok=True)

        self.text_settings = {
            "font": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "fontsize": 70,
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 2
        }

        self.target_duration = 15  # seconds
        self.target_size = (1080, 1920)  # 9:16 aspect ratio
        
        # Memory-saving settings
        self.target_fps = 30
        self.preview_scale = 0.5  # Reduce to 0.25 for more memory savings during preview

    def _create_text_clip(self, quote: str, author: str, duration: float) -> TextClip:
        """Create a text clip with the quote and author."""
        formatted_text = f'"{quote}"\n\n- {author}'

        # Updated for MoviePy v2.0 compatibility
        text_clip = (
            TextClip(
                text=formatted_text,
                font=self.text_settings["font"],
                font_size=self.text_settings["fontsize"],
                color=self.text_settings["color"],
                stroke_color=self.text_settings["stroke_color"],
                stroke_width=self.text_settings["stroke_width"],
                method="caption",
                size=(self.target_size[0] - 100, None),
                text_align="center"
            )
            .with_position("center")
            .with_duration(duration)
        )

        return text_clip

    def _download_video(self, url: str) -> Path:
        """Download a video from a URL and return its temporary path."""
        try:
            temp_path = self.temp_dir / f"temp_video_{int(time.time())}.mp4"

            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            with tqdm.tqdm(
                total=total_size,
                unit="iB",
                unit_scale=True,
                desc="Downloading video"
            ) as progress:
                with open(temp_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            size = f.write(chunk)
                            progress.update(size)

            logger.info(f"Video downloaded to: {temp_path}")
            return temp_path

        except Exception as e:
            raise VideoGeneratorError(f"Failed to download video: {str(e)}")

    def _cleanup_temp_files(self, *files: Path):
        """Remove temporary files."""
        for file in files:
            try:
                if file.exists():
                    file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {file}: {e}")

    def _resize_video(self, clip: VideoFileClip, target_size: Tuple[int, int]) -> VideoFileClip:
        """Resize and crop video to fill the target size (TikTok 9:16) without distortion."""
        if clip.duration > self.target_duration:
            clip = clip.subclipped(0, self.target_duration)

        target_w, target_h = target_size
        target_ratio = target_w / target_h
        clip_ratio = clip.w / clip.h

        logger.info(f"Input video ratio: {clip_ratio:.3f}, target ratio: {target_ratio:.3f}")

        if clip_ratio > target_ratio:
            # Crop width (center)
            new_width = int(clip.h * target_ratio)
            x1 = int((clip.w - new_width) / 2)
            x2 = x1 + new_width
            y1 = 0
            y2 = clip.h
            logger.info(f"Cropping width: x1={x1}, x2={x2}, y1={y1}, y2={y2}")
        else:
            # Crop height (center)
            new_height = int(clip.w / target_ratio)
            y1 = int((clip.h - new_height) / 2)
            y2 = y1 + new_height
            x1 = 0
            x2 = clip.w
            logger.info(f"Cropping height: x1={x1}, x2={x2}, y1={y1}, y2={y2}")

        # Ensure crop box is within bounds
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(clip.w, x2)
        y2 = min(clip.h, y2)

        cropped = clip.cropped(x1=x1, y1=y1, x2=x2, y2=y2)
        resized = cropped.resized(new_size=target_size)
        return resized

    def generate_video(self, quote: str, author: str, video_url: str, tts_voice: str = None) -> Optional[str]:
        """Memory-optimized video generation with optional TTS audio"""
        temp_video_path = None
        temp_audio_path = None
        preview_clip = None
        video = None
        text_clip = None
        final_video = None

        try:
            # Download video
            temp_video_path = self._download_video(video_url)

            # Generate TTS audio if voice is provided
            if tts_voice:
                temp_audio_path = self.temp_dir / f"temp_audio_{int(time.time())}.mp3"
                tts_client = TTSClient()
                tts_client.generate_voice(quote, tts_voice, str(temp_audio_path))

            with tqdm.tqdm(total=5, desc="Generating video") as pbar:
                # Load video at lower resolution first for preview
                preview_size = (
                    int(self.target_size[0] * self.preview_scale),
                    int(self.target_size[1] * self.preview_scale)
                )
                
                # First pass: Check video and generate a small preview
                preview_clip = VideoFileClip(
                    str(temp_video_path),
                    target_resolution=preview_size,
                    fps_source="fps"  # Only read fps, don't decode frames
                )
                
                logger.info(f"Video loaded: {preview_clip.w}x{preview_clip.h} @ {preview_clip.fps}fps")
                
                # Close preview to free memory
                preview_clip.close()
                preview_clip = None
                pbar.update(1)
                
                # Second pass: Load video at target resolution with memory optimization settings
                video = VideoFileClip(
                    str(temp_video_path),
                    target_resolution=self.target_size,
                    audio=False  # Skip audio if not needed
                )
                pbar.update(1)
                
                # Process video
                video = self._resize_video(video, self.target_size)
                pbar.update(1)
                
                # Loop if needed (manual concatenation approach)
                if video.duration < self.target_duration:
                    # Manual looping implementation since loop() is unavailable
                    logger.info(f"Video duration too short ({video.duration}s), extending to {self.target_duration}s")
                    
                    # Calculate how many times we need to loop
                    repetitions = int(self.target_duration / video.duration) + 1
                    
                    # Create a list of repetitions of the same clip
                    clips = [video] * repetitions
                    
                    # Concatenate them
                    looped_video = concatenate_videoclips(clips)
                    
                    # Trim to exact duration
                    video = looped_video.subclipped(0, self.target_duration)
                    
                    # Close the intermediate clip
                    if hasattr(looped_video, 'close'):
                        looped_video.close()
                else:
                    video = video.subclipped(0, self.target_duration)
                pbar.update(1)
                
                # Create text overlay and final composition
                text_clip = self._create_text_clip(quote, author, video.duration)

                final_video = CompositeVideoClip(
                    [video, text_clip],
                    size=self.target_size
                )
                pbar.update(1)

                # Generate output path
                output_path = self.output_dir / f"quote_video_{int(time.time())}.mp4"

                # Write video with audio if available
                final_video.write_videofile(
                    str(output_path),
                    fps=self.target_fps,
                    codec="libx264",
                    preset="ultrafast",
                    audio=str(temp_audio_path) if temp_audio_path else False,
                    audio_codec="aac" if temp_audio_path else None,
                    threads=4,
                    ffmpeg_params=["-tile-columns", "6", "-frame-parallel", "1"]
                )

            logger.info(f"Video generated at: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error("Error generating video", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())
            return None

        finally:
            # Clean up all resources
            for clip in [preview_clip, video, text_clip, final_video]:
                if clip and hasattr(clip, 'close'):
                    try:
                        clip.close()
                    except:
                        pass

            if temp_video_path:
                self._cleanup_temp_files(temp_video_path)
            if temp_audio_path and temp_audio_path.exists():
                temp_audio_path.unlink()

