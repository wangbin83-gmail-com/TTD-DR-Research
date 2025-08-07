"""
TTD-DR Workflow Module
LangGraph workflow definition for test-time diffusion research process
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from langgraph_ttd_dr.state import TTDResearchState, create_initial_state
from langgraph_ttd_dr.nodes import (
    ClarificationNode,
    PlanningNode,
    DraftGenerationNode,
    GapAnalyzerNode,
    WebSearchNode,
    EnhancementNode,
    QualityEvaluatorNode,
    FinalReportNode
)

def create_ttd_workflow() -> StateGraph:
    """
    Create the complete TTD-DR research workflow
    
    Returns:
        Configured LangGraph workflow for test-time diffusion research
    """
    
    # Initialize workflow with state schema
    workflow = StateGraph(TTDResearchState)
    
    # Add nodes
    workflow.add_node("clarify", ClarificationNode())
    workflow.add_node("plan", PlanningNode())
    workflow.add_node("generate_draft", DraftGenerationNode())
    workflow.add_node("analyze_gaps", GapAnalyzerNode())
    workflow.add_node("web_search", WebSearchNode())
    workflow.add_node("enhance", EnhancementNode())
    workflow.add_node("evaluate", QualityEvaluatorNode())
    workflow.add_node("finalize", FinalReportNode())
    
    # Define edges and conditional logic
    
    # Entry point
    workflow.set_entry_point("clarify")
    
    # Clarification -> Planning
    workflow.add_edge("clarify", "plan")
    
    # Planning -> Draft Generation
    workflow.add_edge("plan", "generate_draft")
    
    # Draft Generation -> Gap Analysis
    workflow.add_edge("generate_draft", "analyze_gaps")
    
    # Gap Analysis -> Web Search (if gaps found)
    def should_search_gaps(state: TTDResearchState) -> str:
        """Determine if web search is needed based on gaps"""
        if state["research_gaps"] and len(state["research_gaps"]) > 0:
            return "web_search"
        else:
            return "evaluate"
    
    workflow.add_conditional_edges(
        "analyze_gaps",
        should_search_gaps,
        {
            "web_search": "web_search",
            "evaluate": "evaluate"
        }
    )
    
    # Web Search -> Enhancement
    workflow.add_edge("web_search", "enhance")
    
    # Enhancement -> Quality Evaluation
    workflow.add_edge("enhance", "evaluate")
    
    # Quality Evaluation -> Decision point
    def should_continue_research(state: TTDResearchState) -> str:
        """Determine if research should continue based on quality and iteration count"""
        
        # Check if max iterations reached
        if state["current_iteration"] >= state["max_iterations"]:
            return "finalize"
        
        # Check if quality threshold met
        if state["quality_score"] >= state["quality_threshold"]:
            return "finalize"
        
        # Check if significant improvement was made
        if len(state["research_gaps"]) == 0 and state["quality_score"] > 0.7:
            return "finalize"
        
        # Continue research
        return "analyze_gaps"
    
    workflow.add_conditional_edges(
        "evaluate",
        should_continue_research,
        {
            "finalize": "finalize",
            "analyze_gaps": "analyze_gaps"
        }
    )
    
    # Finalization -> END
    workflow.add_edge("finalize", END)
    
    return workflow

def create_debug_workflow() -> StateGraph:
    """
    Create a debug version of the workflow with enhanced logging
    
    Returns:
        Debug workflow with additional logging nodes
    """
    
    workflow = create_ttd_workflow()
    
    # Add debug nodes between each step
    # This would be implemented based on specific debugging needs
    
    return workflow

def create_minimal_workflow() -> StateGraph:
    """
    Create a minimal workflow for testing purposes
    
    Returns:
        Simplified workflow with core functionality
    """
    
    workflow = StateGraph(TTDResearchState)
    
    # Add only essential nodes
    workflow.add_node("generate_draft", DraftGenerationNode())
    workflow.add_node("analyze_gaps", GapAnalyzerNode())
    workflow.add_node("web_search", WebSearchNode())
    workflow.add_node("enhance", EnhancementNode())
    workflow.add_node("finalize", FinalReportNode())
    
    # Simple linear flow
    workflow.set_entry_point("generate_draft")
    workflow.add_edge("generate_draft", "analyze_gaps")
    workflow.add_edge("analyze_gaps", "web_search")
    workflow.add_edge("web_search", "enhance")
    workflow.add_edge("enhance", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow