import logging
from typing import Dict, Any, List, Callable
from datetime import datetime
import os

from .config import Config
from .llm_client import LLMClient
from .html_to_image import HTMLToImageConverter
from .tts_generator import TTSGenerator
from .video_generator import VideoGenerator

logger = logging.getLogger(__name__)

class AutoVideoGenerator:
    def __init__(self, config: Config = None):
        self.config = config or Config.from_env()
        
        # Initialize components
        self.llm_client = LLMClient(self.config.llm)
        self.html_converter = HTMLToImageConverter()
        self.tts_generator = TTSGenerator(
            provider=self.config.tts.provider,
            voice=self.config.tts.voice,
            rate=self.config.tts.rate,
            volume=self.config.tts.volume,
            api_key=self.config.tts.api_key,
            base_url=self.config.tts.base_url,
            model=self.config.tts.model
        )
        self.video_generator = VideoGenerator(
            fps=self.config.video.fps,
            video_width=self.config.video.width,
            video_height=self.config.video.height
        )
        
        # Create output directory
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def generate_news_video(self, news_data_fetcher: Callable, output_path: str = None) -> str:
        """
        Generate complete news video from news data
        
        Args:
            news_data_fetcher: Function that returns news data
            output_path: Optional output path for the final video
        
        Returns:
            Path to the generated video file
        """
        try:
            logger.info("Starting news video generation")
            
            # Step 1: Fetch news data
            logger.info("Fetching news data...")
            raw_news_data = news_data_fetcher()
            
            # Step 2: Process news data with LLM
            logger.info("Processing news data with LLM...")
            processed_news = self._process_news_data(raw_news_data)
            
            # Step 3: Generate summary
            logger.info("Generating news summary...")
            summary = self.llm_client.generate_summary(processed_news)
            
            # Step 4: Generate individual item introductions
            logger.info("Generating item introductions...")
            introductions = []
            for news_item in processed_news:
                introduction = self.llm_client.generate_item_introduction(news_item)
                introductions.append(introduction)
            
            # Step 5: Generate images
            logger.info("Generating images...")
            overview_image = self.html_converter.generate_overview_image(
                summary=summary,
                news_count=len(processed_news)
            )
            
            news_images = self.html_converter.generate_all_news_images(processed_news)
            
            # Step 6: Generate audio
            logger.info("Generating audio...")
            audio_files = self.tts_generator.generate_all_audio(
                summary=summary,
                news_items=processed_news,
                introductions=introductions
            )
            
            # Step 7: Generate video
            logger.info("Generating final video...")
            final_video = self.video_generator.create_final_video(
                overview_image=overview_image,
                overview_audio=audio_files['summary'],
                news_images=news_images,
                news_audios=[audio_files[f'item_{i+1}'] for i in range(len(processed_news))],
                output_path=output_path
            )
            
            logger.info(f"News video generated successfully: {final_video}")
            return final_video
            
        except Exception as e:
            logger.error(f"Error generating news video: {str(e)}")
            raise
    
    def _process_news_data(self, raw_news_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw news data using LLM"""
        processed_news = []
        
        for news_item in raw_news_data:
            try:
                # Use LLM to format news data
                formatted_news = self.llm_client.generate_news_json(news_item)
                
                # Add timestamp if not present
                if 'created_at' not in formatted_news:
                    formatted_news['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                processed_news.append(formatted_news)
                
            except Exception as e:
                logger.error(f"Error processing news item: {str(e)}")
                continue
        
        return processed_news
    
    def generate_from_news_list(self, news_items: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Generate video from pre-formatted news items
        
        Args:
            news_items: List of formatted news items
            output_path: Optional output path for the final video
        
        Returns:
            Path to the generated video file
        """
        try:
            logger.info("Starting news video generation from pre-formatted items")
            
            # Step 1: Generate summary
            logger.info("Generating news summary...")
            summary = self.llm_client.generate_summary(news_items)
            
            # Step 2: Generate individual item introductions
            logger.info("Generating item introductions...")
            introductions = []
            for news_item in news_items:
                introduction = self.llm_client.generate_item_introduction(news_item)
                introductions.append(introduction)
            
            # Step 3: Generate images
            logger.info("Generating images...")
            overview_image = self.html_converter.generate_overview_image(
                summary=summary,
                news_count=len(news_items)
            )
            
            news_images = self.html_converter.generate_all_news_images(news_items)
            
            # Step 4: Generate audio
            logger.info("Generating audio...")
            audio_files = self.tts_generator.generate_all_audio(
                summary=summary,
                news_items=news_items,
                introductions=introductions
            )
            
            # Step 5: Generate video
            logger.info("Generating final video...")
            final_video = self.video_generator.create_final_video(
                overview_image=overview_image,
                overview_audio=audio_files['summary'],
                news_images=news_images,
                news_audios=[audio_files[f'item_{i+1}'] for i in range(len(news_items))],
                output_path=output_path
            )
            
            logger.info(f"News video generated successfully: {final_video}")
            return final_video
            
        except Exception as e:
            logger.error(f"Error generating news video from items: {str(e)}")
            raise