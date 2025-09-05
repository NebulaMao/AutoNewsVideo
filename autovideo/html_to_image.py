from playwright.sync_api import sync_playwright
from jinja2 import Environment, FileSystemLoader
from PIL import Image
import os
from typing import Dict, Any, List
import logging
from datetime import datetime
import tempfile
import base64

logger = logging.getLogger(__name__)

class HTMLToImageConverter:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
        # Create output directory if it doesn't exist
        os.makedirs("output/images", exist_ok=True)
    
    def _generate_html_content(self, template_name: str, **kwargs) -> str:
        """Generate HTML content from template"""
        template = self.env.get_template(template_name)
        return template.render(**kwargs)
    
    def _html_to_image(self, html_content: str, output_path: str, width: int = 1920, height: int = 1080) -> str:
        """Convert HTML content to image using Playwright"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # Set viewport size
                page.set_viewport_size({"width": width, "height": height})
                
                # Load HTML content
                page.set_content(html_content, wait_until="networkidle")
                
                # Take screenshot
                page.screenshot(path=output_path, full_page=True)
                
                browser.close()
            
            logger.info(f"Successfully converted HTML to image: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting HTML to image: {str(e)}")
            raise
    
    def generate_overview_image(self, summary: str, news_count: int, date: str = None, output_path: str = None) -> str:
        """Generate overview image from summary"""
        if date is None:
            date = datetime.now().strftime("%Y年%m月%d日")
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/images/overview_{timestamp}.jpg"
        
        html_content = self._generate_html_content(
            "overview.html",
            date=date,
            summary=summary,
            news_count=news_count
        )
        
        return self._html_to_image(html_content, output_path)
    
    def generate_news_item_image(self, news_item: Dict[str, Any], item_number: int, total_items: int, output_path: str = None) -> str:
        """Generate individual news item image"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/images/news_item_{item_number}_{timestamp}.jpg"
        
        html_content = self._generate_html_content(
            "news_item.html",
            title=news_item.get('title', ''),
            summary=news_item.get('summary', ''),
            category=news_item.get('category', '未分类'),
            importance=news_item.get('importance', 3),
            keywords=news_item.get('keywords', []),
            created_at=news_item.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            item_number=item_number,
            total_items=total_items
        )
        
        return self._html_to_image(html_content, output_path)
    
    def generate_all_news_images(self, news_items: List[Dict[str, Any]]) -> List[str]:
        """Generate images for all news items"""
        image_paths = []
        
        for i, news_item in enumerate(news_items, 1):
            try:
                image_path = self.generate_news_item_image(
                    news_item, 
                    item_number=i, 
                    total_items=len(news_items)
                )
                image_paths.append(image_path)
                logger.info(f"Generated image for news item {i}")
            except Exception as e:
                logger.error(f"Failed to generate image for news item {i}: {str(e)}")
                continue
        
        return image_paths
    
    def resize_image(self, input_path: str, output_path: str, width: int = 1920, height: int = 1080) -> str:
        """Resize image to specified dimensions"""
        try:
            with Image.open(input_path) as img:
                resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                resized_img.save(output_path, quality=95)
                logger.info(f"Successfully resized image to {output_path}")
                return output_path
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            raise