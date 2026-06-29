"""
Agent package initializer.
Expose all agent classes for easy import.
"""

from .brain_agent import BrainAgent
from .support_agent import SupportAgent
from .accountant_agent import AccountantAgent
from .fraud_agent import FraudAgent

__all__ = [
    'BrainAgent',
    'SupportAgent',
    'AccountantAgent',
    'FraudAgent'
]