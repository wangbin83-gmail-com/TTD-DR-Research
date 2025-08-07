"""
TTD-DR Interface Module
Main interface for the Test-Time Diffusion Deep Research system
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from langgraph_ttd_dr.workflow import create_ttd_workflow
from langgraph_ttd_dr.state import create_initial_state, TTDResearchState
from langgraph_ttd_dr.client_factory import create_client
from langgraph_ttd_dr.tools import WebSearchTool

logger = logging.getLogger(__name__)

class TTDResearcher:
    """
    Main interface for Test-Time Diffusion Deep Research system
    
    Provides a high-level API for conducting comprehensive research
    using test-time diffusion methodology with Kimi AI integration.
    """
    
    def __init__(
        self,
        query: str,
        client_type: str = "kimi",
        max_iterations: int = 3,
        quality_threshold: float = 0.85,
        research_context: str = "",
        search_engines: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize the TTD Researcher
        
        Args:
            query: The research question or topic
            client_type: Type of AI client ('kimi', 'openai', 'azure')
            max_iterations: Maximum refinement iterations
            quality_threshold: Quality threshold for stopping
            research_context: Additional context for multi-faceted research
            search_engines: List of search engines to use
            **kwargs: Additional configuration options
        """
        self.query = query
        self.client_type = client_type
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        self.research_context = research_context
        self.search_engines = search_engines or ["tavily", "duckduckgo"]
        self.config = kwargs
        
        # Initialize components
        self.client = create_client(client_type, **kwargs)
        self.search_tool = WebSearchTool(self.search_engines)
        
        logger.info(f"Initialized TTDResearcher for query: {query}")
    
    async def run(self) -> Dict[str, Any]:
        """
        Execute the complete research workflow
        
        Returns:
            Dictionary containing research results and metadata
        """
        try:
            # Create initial state
            initial_state = create_initial_state(
                query=self.query,
                research_context=self.research_context,
                max_iterations=self.max_iterations,
                quality_threshold=self.quality_threshold,
                **self.config
            )
            
            # Create workflow
            workflow = create_ttd_workflow()
            
            # Execute workflow
            logger.info("Starting research workflow...")
            final_state = await workflow.ainvoke(initial_state)
            
            # Process results
            result = self._process_results(final_state)
            
            logger.info(f"Research completed successfully. Quality score: {result['quality_score']}")
            return result
            
        except Exception as e:
            logger.error(f"Research workflow failed: {str(e)}")
            raise
    
    def _process_results(self, final_state: TTDResearchState) -> Dict[str, Any]:
        """
        Process the final state into a structured result
        
        Args:
            final_state: The final research state
            
        Returns:
            Processed research results
        """
        return {
            "final_report": final_state["final_report"],
            "sources": final_state["sources"],
            "quality_score": final_state["quality_score"],
            "iterations": final_state["current_iteration"],
            "gaps_identified": len(final_state["research_gaps"]),
            "metadata": {
                "query": self.query,
                "research_context": self.research_context,
                "client_type": self.client_type,
                "max_iterations": self.max_iterations,
                "quality_threshold": self.quality_threshold,
                "search_engines": self.search_engines,
                "timestamp": final_state["timestamp"],
                "component_fitness": final_state["component_fitness"]
            }
        }
    
    async def run_with_progress(self, callback=None) -> Dict[str, Any]:
        """
        Run research with progress callback support
        
        Args:
            callback: Optional callback function for progress updates
            
        Returns:
            Research results
        """
        # This would implement streaming progress updates
        # For now, delegates to run()
        return await self.run()