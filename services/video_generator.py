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
        """Resize video with letterboxing/pillarboxing to prevent stretching"""
        # First trim to target duration to reduce memory footprint
        if clip.duration > self.target_duration:
            clip = clip.subclipped(0, self.target_duration)
            
        # Target aspect ratio (9:16 for vertical video)
        target_ratio = target_size[0] / target_size[1]  # width/height = 9/16
        clip_ratio = clip.w / clip.h
        
        logger.info(f"Input video ratio: {clip_ratio:.3f}, target ratio: {target_ratio:.3f}")
        
        # Create a black background of the target size
        background = ColorClip(size=target_size, color=(0, 0, 0))
        background = background.with_duration(clip.duration)
        
        # Calculate the size that preserves aspect ratio while fitting within the target
        if clip_ratio > target_ratio:  # Wider than target (landscape video)
            # Scale based on width, will have black bars top and bottom
            scale_factor = target_size[0] / clip.w
            new_width = target_size[0]
            new_height = int(clip.h * scale_factor)
            
            logger.info(f"Adding letterboxing (black bars on top/bottom): new size {new_width}x{new_height}")
            
            # Resize while maintaining aspect ratio
            resized_clip = clip.resized(width=new_width, height=new_height)
        else:  # Taller than target or equal (portrait video)
            # Scale based on height, will have black bars on sides
            scale_factor = target_size[1] / clip.h
            new_height = target_size[1]
            new_width = int(clip.w * scale_factor)
            
            logger.info(f"Adding pillarboxing (black bars on sides): new size {new_width}x{new_height}")
            
            # Resize while maintaining aspect ratio
            resized_clip = clip.resized(width=new_width, height=new_height)
        
        # Position in the center of the frame - this creates the letterboxing/pillarboxing effect
        positioned_clip = resized_clip.with_position(("center", "center"))
        
        # Composite the resized video over the black background
        final = CompositeVideoClip([background, positioned_clip], size=target_size)
        
        # Clean up intermediate clips to free memory
        if hasattr(resized_clip, 'close'):
            resized_clip.close()
        
        return final

    def generate_video(self, quote: str, author: str, video_url: str) -> Optional[str]:
        """Memory-optimized video generation"""
        temp_video_path = None
        preview_clip = None
        video = None
        text_clip = None
        final_video = None
        
        try:
            # Download video
            temp_video_path = self._download_video(video_url)

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
                print(f"Quote is {quote} and author is {author}")
                # Create text overlay and final composition
                text_clip = self._create_text_clip(quote, author, video.duration)
                
                final_video = CompositeVideoClip(
                    [video, text_clip],
                    size=self.target_size
                )
                pbar.update(1)
                
                # Generate output path
                output_path = self.output_dir / f"quote_video_{int(time.time())}.mp4"
                
                # Memory-optimized encoding
                with tqdm.tqdm(
                    total=int(final_video.duration * self.target_fps),
                    desc="Encoding video",
                    unit="frames"
                ) as t:
                    def write_progress(frame):
                        t.update(1)
                    
                    # Write video with memory-optimized settings
                    final_video.write_videofile(
                        str(output_path),
                        fps=self.target_fps,  # Set output FPS here
                        codec="libx264",
                        preset="ultrafast",  # Even faster encoding, lower quality but less RAM
                        audio_codec="aac",
                        audio=False,  # Skip audio processing
                        threads=4,
                        ffmpeg_params=["-tile-columns", "6", "-frame-parallel", "1"]  # Parallelization
                    )
                
                logger.info(f"Video generated at: {output_path}")
                return str(output_path)  # Return the path as a string, not a jsonify response
                
        except Exception as e:
            logger.error("Error generating video", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())  # Print full stack trace
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

