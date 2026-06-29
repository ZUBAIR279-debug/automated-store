"""
AccountantAgent – Payment verification using Gemini Vision.
Accepts a screenshot image and extracts details.
"""

import logging
import base64
import json
import re
from typing import Dict, Any, Optional

import google.generativeai as genai
from config import Config

logger = logging.getLogger(__name__)

class AccountantAgent:
    """
    Verifies payment screenshots (EasyPaisa / JazzCash) via Gemini Vision.
    Extracts Transaction ID, Amount, Account Number, and status.
    """

    def __init__(self):
        # Yahan hum explicitly API key pass kar rahe hain taake Cloud Credentials ka error na aaye
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            logger.error("Config.GEMINI_API_KEY is missing!")
        genai.configure(api_key=api_key)
        
        # Direct client model configuration
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def verify_payment_screenshot(self, image_base64: str) -> Dict[str, Any]:
        """
        Analyze screenshot using Gemini Vision and return extracted JSON data.
        """
        try:
            # Prepare prompt
            prompt = """
            You are a payment verification agent. Analyze the provided payment screenshot.
            Extract the following details with high accuracy:
            - transaction_id (or TID)
            - amount (numeric value only, e.g., 229 or 10)
            - account_number (the receiver's or sender's account number)
            - status (successful, pending, failed)

            Return ONLY a JSON object with keys: transaction_id, amount, account_number, status.
            """
            
            # Decode image safely
            try:
                if image_base64.startswith('data:'):
                    raw_b64 = image_base64.split(',')[1]
                else:
                    raw_b64 = image_base64
                image_bytes = base64.b64decode(raw_b64)
            except Exception as b64_err:
                logger.error(f"Base64 decode error: {b64_err}")
                return {'success': False, 'error': f'Invalid base64 string: {b64_err}'}

            image_part = {
                "mime_type": "image/png",
                "data": image_bytes
            }
            
            # API Call to Gemini
            response = self.model.generate_content([prompt, image_part])
            raw_json = response.text.strip()
            
            # Clean markdown JSON block if present
            raw_json = re.sub(r'```json\s*', '', raw_json)
            raw_json = re.sub(r'```\s*', '', raw_json)
            
            extracted = json.loads(raw_json)
            return {'success': True, 'extracted': extracted}

        except Exception as e:
            logger.error(f"AccountantAgent vision error: {e}")
            return {'success': False, 'error': str(e)}