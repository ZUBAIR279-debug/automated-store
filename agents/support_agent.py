"""
SupportAgent – Customer conversation and real‑time inventory queries.
Uses Gemini with custom system instructions and database lookups.
"""

import logging
import re
from typing import List, Dict, Any

import google.generativeai as genai
from sqlalchemy.exc import SQLAlchemyError

from app import db, Product
from config import Config

logger = logging.getLogger(__name__)

class SupportAgent:
    """Handles customer queries via chat widget or WhatsApp."""

    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            'gemini-1.5-pro',
            system_instruction=(
                "You are the elite digital manager of an automated tech boutique. "
                "You help customers with product inquiries, stock availability, "
                "specifications, and ordering assistance. Always be friendly and professional. "
                "If you don't know the answer, say so and offer to connect the customer with human support."
            )
        )
        self.chat = self.model.start_chat(history=[])

    def fetch_available_stock(self, product_name: str) -> int:
        """Query database for stock count of a product (case-insensitive)."""
        try:
            product = Product.query.filter(Product.name.ilike(f"%{product_name}%")).first()
            if product:
                return product.stock_count
            return 0
        except SQLAlchemyError as e:
            logger.error(f"Stock query error: {e}")
            return 0

    def fetch_product_specs(self, product_name: str) -> Dict[str, Any]:
        """Retrieve full product details for a given name."""
        try:
            product = Product.query.filter(Product.name.ilike(f"%{product_name}%")).first()
            if product:
                return {
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'image_url': product.image_url,
                    'stock': product.stock_count
                }
            return {}
        except SQLAlchemyError as e:
            logger.error(f"Specs query error: {e}")
            return {}

    def generate_response(self, user_message: str) -> str:
        """
        Process user message, optionally check DB for stock/specs, and return AI response.
        """
        # Intercept common patterns to inject real data
        lower_msg = user_message.lower()
        response = ""
        
        # Check if asking about stock
        if "stock" in lower_msg or "availability" in lower_msg:
            # Extract product name: simplistic approach
            words = user_message.split()
            for i, word in enumerate(words):
                if word.lower() in ['stock', 'available', 'availability'] and i+1 < len(words):
                    potential_name = ' '.join(words[i+1:])
                    stock = self.fetch_available_stock(potential_name)
                    if stock > 0:
                        response = f"The {potential_name} is currently in stock with {stock} units available."
                    else:
                        response = f"Sorry, {potential_name} is currently out of stock."
                    # Then let Gemini refine the message
                    user_message = f"{user_message}\n[FACT]: {response}"
                    break
        
        # Check if asking for specs
        if "spec" in lower_msg or "feature" in lower_msg or "detail" in lower_msg:
            words = user_message.split()
            for i, word in enumerate(words):
                if word.lower() in ['specs', 'specifications', 'features', 'details'] and i+1 < len(words):
                    potential_name = ' '.join(words[i+1:])
                    specs = self.fetch_product_specs(potential_name)
                    if specs:
                        fact = f"Product: {specs['name']}\nDescription: {specs['description']}\nPrice: ${specs['price']}\nStock: {specs['stock']}"
                        response = f"\n[FACT]: {fact}"
                    break
        
        # Send full context to Gemini
        try:
            if not response:
                # No fact injected, just use the message
                full_prompt = user_message
            else:
                full_prompt = f"{user_message}\n{response}"
            
            # Use chat context
            self.chat.send_message(full_prompt)
            reply = self.chat.last.text
            return reply
        except Exception as e:
            logger.error(f"Gemini response error: {e}")
            return "I'm having trouble processing your request right now. Please try again later."

    def reset_chat(self):
        """Reset the conversation history."""
        self.chat = self.model.start_chat(history=[])