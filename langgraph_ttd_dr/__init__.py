"""
TTD-DR: Test-Time Diffusion Deep Research
Advanced AI-powered research system with test-time diffusion methodology
"""

__version__ = "1.0.0"
__author__ = "Bin Wang"
__email__ = "wangbin83@gmail.com"
__description__ = "Test-Time Diffusion Deep Research system with Kimi API integration"

from .interface import TTDResearcher
from .workflow import create_ttd_workflow
from .state import TTDResearchState, create_initial_state

__all__ = [
    "TTDResearcher",
    "create_ttd_workflow", 
    "TTDResearchState",
    "create_initial_state"
]