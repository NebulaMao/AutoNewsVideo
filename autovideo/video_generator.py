import subprocess
import os
import tempfile
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self, fps: int = 30, video_width: int = 1920, video_height: int = 1080):
        self.fps = fps
        self.video_width = video_width
        self.video_height = video_height
        
        # Create output directory if it doesn't exist
        os.makedirs("output/video", exist_ok=True)
    
    def _run_ffmpeg_command(self, command: List[str]) -> str:
        """Run FFmpeg command and return the output path"""
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"FFmpeg command executed successfully")
            return command[-1]  # Return the output file path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg command failed: {e.stderr}")
            raise
        except FileNotFoundError:
            logger.error("FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
            raise
    
    def create_video_segment(self, image_path: str, audio_path: str, output_path: str, duration: float = None) -> str:
        """Create a video segment from image and audio"""
        if duration is None:
            duration = self._get_audio_duration(audio_path)
        
        command = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', image_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            '-vf', f'scale={self.video_width}:{self.video_height},fps={self.fps}',
            '-t', str(duration),
            '-pix_fmt', 'yuv420p',
            output_path
        ]
        
        return self._run_ffmpeg_command(command)
    
    def create_video_from_images(self, image_paths: List[str], audio_paths: List[str], 
                               output_path: str = None, durations: List[float] = None) -> str:
        """Create video from multiple images and audio files"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/video/news_video_{timestamp}.mp4"
        
        if durations is None:
            durations = [self._get_audio_duration(audio_path) for audio_path in audio_paths]
        
        # Create temporary video files for each segment
        temp_videos = []
        try:
            for i, (image_path, audio_path, duration) in enumerate(zip(image_paths, audio_paths, durations)):
                temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                temp_video.close()
                
                self.create_video_segment(image_path, audio_path, temp_video.name, duration)
                temp_videos.append(temp_video.name)
            
            # Concatenate all videos
            if len(temp_videos) == 1:
                # If only one video, copy with explicit audio encoding
                command = [
                    'ffmpeg', '-y',
                    '-i', temp_videos[0],
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-pix_fmt', 'yuv420p',
                    output_path
                ]
            else:
                # Create concat file
                concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
                for temp_video in temp_videos:
                    concat_file.write(f"file '{temp_video}'\n")
                concat_file.close()
                
                # Concatenate videos
                command = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_file.name,
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-pix_fmt', 'yuv420p',
                    output_path
                ]
                
                result = self._run_ffmpeg_command(command)
                os.unlink(concat_file.name)
            
            logger.info(f"Video created successfully: {output_path}")
            return output_path
            
        finally:
            # Clean up temporary files
            for temp_video in temp_videos:
                if os.path.exists(temp_video):
                    os.unlink(temp_video)
    
    def add_transition(self, video_path: str, output_path: str, transition_type: str = "fade") -> str:
        """Add transition effects to video"""
        if transition_type == "fade":
            # Add fade in and fade out
            command = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vf', f'fade=in:0:30,fade=out:st={self._get_video_duration(video_path)-1}:d=1',
                '-c:a', 'copy',
                output_path
            ]
        else:
            # Just copy the video if no transition specified
            command = ['ffmpeg', '-y', '-i', video_path, '-c', 'copy', output_path]
        
        return self._run_ffmpeg_command(command)
    
    def create_final_video(self, overview_image: str, overview_audio: str,
                          news_images: List[str], news_audios: List[str],
                          output_path: str = None) -> str:
        """Create final news video with overview and individual items"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/video/final_news_{timestamp}.mp4"
        
        # Combine all images and audio
        all_images = [overview_image] + news_images
        all_audios = [overview_audio] + news_audios
        
        # Create video
        video_path = self.create_video_from_images(all_images, all_audios)
        
        # Add transitions
        final_video = self.add_transition(video_path, output_path)
        
        # Clean up intermediate file
        if os.path.exists(video_path):
            os.unlink(video_path)
        
        logger.info(f"Final video created: {final_video}")
        return final_video
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds"""
        try:
            command = [
                'ffprobe', '-i', audio_path,
                '-show_entries', 'format=duration',
                '-v', 'quiet', '-of', 'csv=p=0'
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            logger.warning(f"Could not get duration for {audio_path}, using default 5 seconds")
            return 5.0
    
    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds"""
        try:
            command = [
                'ffprobe', '-i', video_path,
                '-show_entries', 'format=duration',
                '-v', 'quiet', '-of', 'csv=p=0'
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            logger.warning(f"Could not get duration for {video_path}, using default 10 seconds")
            return 10.0
    
    def add_background_music(self, video_path: str, music_path: str, output_path: str, volume: float = 0.3) -> str:
        """Add background music to video"""
        command = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', music_path,
            '-filter_complex', f'[1:a]volume={volume}[bgm];[0:a][bgm]amix=inputs=2:duration=shortest',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '192k',
            output_path
        ]
        
        return self._run_ffmpeg_command(command)