"""
BrainAgent – Uses Groq API (Free, Fast, Reliable)
"""

import json
import logging
import re
import os
from typing import Dict, Any

from groq import Groq
from config import Config

logger = logging.getLogger(__name__)

class BrainAgent:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        self.model = "llama-3.3-70b-versatile"
        self.admin_whatsapp = Config.OWNER_WHATSAPP_NUMBER

    def process_command(self, raw_text: str) -> Dict[str, Any]:
        prompt = f"""
        Extract structured product data from this command.
        Return ONLY valid JSON with keys: name, description, image_url, cost_price, price, stock_count.
        If any field missing, use reasonable defaults.
        Use Unsplash URLs for images.
        Command: {raw_text}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw_json = response.choices[0].message.content.strip()
            raw_json = re.sub(r'```json\s*', '', raw_json)
            raw_json = re.sub(r'```\s*', '', raw_json)
            return json.loads(raw_json)
        except Exception as e:
            logger.error(f"Groq parse error: {e}")
            raise ValueError(f"Failed to parse command: {e}")

    def handle_command(self, raw_text: str) -> Dict[str, Any]:
        try:
            # AI sirf JSON data nikal kar wapas bhej dega (Database saving app.py karegi)
            product_data = self.process_command(raw_text)
            return {
                'success': True,
                'product': product_data,
                'message': 'AI successfully parsed product data'
            }
        except Exception as e:
            logger.error(f"handle_command error: {e}")
            return {'success': False, 'error': str(e)}