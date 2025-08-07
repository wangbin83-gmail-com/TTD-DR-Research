"""
TTD-DR State Management Module
Defines the complete state schema for the research system
"""

from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    """Status of research tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ResearchGap(TypedDict):
    """Structure for identified research gaps"""
    id: str
    section: str
    gap_type: str
    specific_need: str
    search_query: str
    priority: str
    status: TaskStatus

class SourceData(TypedDict):
    """Structure for research sources"""
    id: str
    title: str
    url: str
    content: str
    raw_content: str
    access_date: str
    published_date: str
    relevance_score: float
    search_engine: str
    gap_addressed: Optional[str]
    content_length: int
    extraction_timestamp: str

class ComponentFitness(TypedDict):
    """Fitness scores for system components"""
    search_strategy: float
    synthesis_quality: float
    integration_ability: float
    gap_identification: float
    enhancement_effectiveness: float

class QualityMetrics(TypedDict):
    """Quality evaluation metrics"""
    comprehensiveness: float
    accuracy: float
    depth: float
    structure: float
    currency: float
    overall_quality: float

class TTDResearchState(TypedDict):
    """
    Complete state schema for TTD-DR research system
    
    This defines the complete state structure used throughout the research workflow
    """
    # Core research parameters
    query: str
    research_context: str
    max_iterations: int
    quality_threshold: float
    
    # AI client and tools
    client: Any  # AI client instance
    search_tool: Any  # Web search tool instance
    
    # Research workflow state
    current_iteration: int
    research_complete: bool
    
    # Content and analysis
    clarification_needed: bool
    clarification_questions: List[str]
    query_analysis: str
    research_plan: str
    current_draft: str
    previous_drafts: List[str]
    final_report: str
    
    # Gap analysis
    research_gaps: List[ResearchGap]
    gap_analysis_text: str
    
    # Search and sources
    search_results: List[Dict[str, Any]]
    sources: List[SourceData]
    
    # Quality and evaluation
    quality_score: float
    quality_scores: Dict[str, float]
    quality_evaluation: str
    component_fitness: ComponentFitness
    
    # Timestamps for tracking
    timestamp: str
    planning_timestamp: str
    draft_timestamp: str
    gap_analysis_timestamp: str
    search_timestamp: str
    enhancement_timestamp: str
    quality_timestamp: str
    finalization_timestamp: str

def create_initial_state(
    query: str,
    research_context: str = "",
    max_iterations: int = 3,
    quality_threshold: float = 0.85,
    client: Any = None,
    search_tool: Any = None,
    **kwargs
) -> TTDResearchState:
    """
    Create initial state for research workflow
    
    Args:
        query: Research question or topic
        research_context: Additional context for research
        max_iterations: Maximum refinement iterations
        quality_threshold: Target quality score
        client: AI client instance
        search_tool: Web search tool instance
        **kwargs: Additional configuration options
        
    Returns:
        Initialized research state
    """
    
    now = datetime.now().isoformat()
    
    return {
        # Core parameters
        "query": query,
        "research_context": research_context,
        "max_iterations": max_iterations,
        "quality_threshold": quality_threshold,
        
        # Client and tools
        "client": client,
        "search_tool": search_tool,
        
        # Workflow state
        "current_iteration": 0,
        "research_complete": False,
        
        # Content tracking
        "clarification_needed": False,
        "clarification_questions": [],
        "query_analysis": "",
        "research_plan": "",
        "current_draft": "",
        "previous_drafts": [],
        "final_report": "",
        
        # Gap analysis
        "research_gaps": [],
        "gap_analysis_text": "",
        
        # Search results
        "search_results": [],
        "sources": [],
        
        # Quality metrics
        "quality_score": 0.0,
        "quality_scores": {},
        "quality_evaluation": "",
        "component_fitness": {
            "search_strategy": 1.0,
            "synthesis_quality": 1.0,
            "integration_ability": 1.0,
            "gap_identification": 1.0,
            "enhancement_effectiveness": 1.0
        },
        
        # Timestamps
        "timestamp": now,
        "planning_timestamp": "",
        "draft_timestamp": "",
        "gap_analysis_timestamp": "",
        "search_timestamp": "",
        "enhancement_timestamp": "",
        "quality_timestamp": "",
        "finalization_timestamp": ""
    }

def update_state_with_source_metadata(
    state: TTDResearchState, 
    new_sources: List[SourceData]
) -> TTDResearchState:
    """
    Update state with new source metadata
    
    Args:
        state: Current research state
        new_sources: New sources to add
        
    Returns:
        Updated state with new sources
    """
    
    # Avoid duplicates based on URL
    existing_urls = {source["url"] for source in state["sources"]}
    unique_new_sources = [
        source for source in new_sources 
        if source["url"] not in existing_urls
    ]
    
    state["sources"].extend(unique_new_sources)
    return state

def get_state_summary(state: TTDResearchState) -> Dict[str, Any]:
    """
    Get a summary of the current research state
    
    Args:
        state: Current research state
        
    Returns:
        Summary dictionary with key metrics
    """
    
    return {
        "query": state["query"],
        "current_iteration": state["current_iteration"],
        "max_iterations": state["max_iterations"],
        "quality_score": state["quality_score"],
        "quality_threshold": state["quality_threshold"],
        "research_complete": state["research_complete"],
        "gaps_count": len(state["research_gaps"]),
        "sources_count": len(state["sources"]),
        "draft_length": len(state["current_draft"]) if state["current_draft"] else 0,
        "final_report_length": len(state["final_report"]) if state["final_report"] else 0
    }