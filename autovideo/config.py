from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class LLMConfig(BaseModel):
    api_key: Optional[str] = Field(default=None, description="API key for LLM service")
    base_url: Optional[str] = Field(default=None, description="Base URL for custom LLM endpoint")
    model: str = Field(default="gpt-3.5-turbo", description="Model name to use")
    temperature: float = Field(default=0.7, description="Temperature for response generation")
    max_tokens: int = Field(default=1000, description="Maximum tokens for response")

class VideoConfig(BaseModel):
    width: int = Field(default=1920, description="Video width in pixels")
    height: int = Field(default=1080, description="Video height in pixels")
    fps: int = Field(default=30, description="Frames per second")
    image_duration: int = Field(default=5, description="Duration of each image in seconds")
    transition_duration: float = Field(default=0.5, description="Transition duration between images")

class TTSConfig(BaseModel):
    provider: str = Field(default="edge_tts", description="TTS provider: edge_tts or siliconflow")
    voice: str = Field(default="zh-CN-XiaoxiaoNeural", description="Voice for TTS")
    rate: str = Field(default="+0%", description="Speech rate")
    volume: str = Field(default="+0%", description="Speech volume")
    api_key: Optional[str] = Field(default=None, description="API key for TTS service")
    base_url: Optional[str] = Field(default=None, description="Base URL for TTS service")
    model: Optional[str] = Field(default=None, description="Model name for TTS service")

class Config(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    video: VideoConfig = Field(default_factory=VideoConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    output_dir: str = Field(default="output", description="Output directory for generated files")
    whyta_api_key: Optional[str] = Field(default=None, description="API key for Whyta news API")
    
    @classmethod
    def from_env(cls):
        return cls(
            llm=LLMConfig(
                api_key=os.getenv("LLM_API_KEY"),
                base_url=os.getenv("LLM_BASE_URL"),
                model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000"))
            ),
            tts=TTSConfig(
                provider=os.getenv("TTS_PROVIDER", "edge_tts"),
                voice=os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural"),
                rate=os.getenv("TTS_RATE", "+0%"),
                volume=os.getenv("TTS_VOLUME", "+0%"),
                api_key=os.getenv("TTS_API_KEY"),
                base_url=os.getenv("TTS_BASE_URL"),
                model=os.getenv("TTS_MODEL")
            ),
            whyta_api_key=os.getenv("WHYTA_API_KEY"),
        )