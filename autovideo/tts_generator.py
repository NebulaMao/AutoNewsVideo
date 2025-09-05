import asyncio
import edge_tts
import os
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from pathlib import Path
from openai import OpenAI

logger = logging.getLogger(__name__)

class TTSProvider:
    EDGE_TTS = "edge_tts"
    SILICONFLOW = "siliconflow"

class TTSGenerator:
    def __init__(self, 
                 provider: str = TTSProvider.EDGE_TTS,
                 voice: str = "zh-CN-XiaoxiaoNeural", 
                 rate: str = "+0%", 
                 volume: str = "+0%",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None):
        self.provider = provider
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # Initialize client based on provider
        if provider == TTSProvider.SILICONFLOW:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url or "https://api.siliconflow.cn/v1"
            )
        
        # Create output directory if it doesn't exist
        os.makedirs("output/audio", exist_ok=True)
    
    async def _generate_audio(self, text: str, output_path: str) -> str:
        """Generate audio from text using selected TTS provider"""
        try:
            if self.provider == TTSProvider.EDGE_TTS:
                return await self._generate_edge_tts_audio(text, output_path)
            elif self.provider == TTSProvider.SILICONFLOW:
                return self._generate_siliconflow_audio(text, output_path)
            else:
                raise ValueError(f"Unsupported TTS provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise
    
    async def _generate_edge_tts_audio(self, text: str, output_path: str) -> str:
        """Generate audio using edge-tts"""
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume
        )
        
        await communicate.save(output_path)
        logger.info(f"Successfully generated audio with edge-tts: {output_path}")
        return output_path
    
    def _generate_siliconflow_audio(self, text: str, output_path: str) -> str:
        """Generate audio using SiliconFlow TTS"""
        try:
            with self.client.audio.speech.with_streaming_response.create(
                model=self.model or "FunAudioLLM/CosyVoice2-0.5B",
                voice=self.voice,
                input=text,
                response_format="mp3"
            ) as response:
                response.stream_to_file(output_path)
            
            logger.info(f"Successfully generated audio with SiliconFlow: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating SiliconFlow audio: {str(e)}")
            raise
    
    def generate_summary_audio(self, summary: str, output_path: str = None) -> str:
        """Generate audio for news summary"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/audio/summary_{timestamp}.mp3"
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._generate_audio(summary, output_path))
        finally:
            loop.close()
    
    def generate_item_audio(self, text: str, item_number: int, output_path: str = None) -> str:
        """Generate audio for individual news item"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/audio/item_{item_number}_{timestamp}.mp3"
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._generate_audio(text, output_path))
        finally:
            loop.close()
    
    def generate_all_audio(self, summary: str, news_items: List[Dict[str, Any]], introductions: List[str]) -> Dict[str, str]:
        """Generate audio for summary and all news items"""
        audio_files = {}
        
        # Generate summary audio
        try:
            summary_audio = self.generate_summary_audio(summary)
            audio_files['summary'] = summary_audio
            logger.info("Generated summary audio")
        except Exception as e:
            logger.error(f"Failed to generate summary audio: {str(e)}")
        
        # Generate individual item audio
        for i, introduction in enumerate(introductions, 1):
            try:
                item_audio = self.generate_item_audio(introduction, i)
                audio_files[f'item_{i}'] = item_audio
                logger.info(f"Generated audio for news item {i}")
            except Exception as e:
                logger.error(f"Failed to generate audio for news item {i}: {str(e)}")
                continue
        
        return audio_files
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds"""
        try:
            communicate = edge_tts.Communicate("", voice=self.voice)
            # This is a workaround to get duration
            # In a real implementation, you might want to use a library like pydub
            import subprocess
            result = subprocess.run(
                ['ffprobe', '-i', audio_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'],
                capture_output=True,
                text=True
            )
            return float(result.stdout.strip())
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            return 5.0  # Default duration