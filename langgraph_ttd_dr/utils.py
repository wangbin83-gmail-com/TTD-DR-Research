"""
TTD-DR Utilities Module
Utility functions for data processing and formatting
"""

import re
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

def clean_reasoning_tags(text: str) -> str:
    """
    Clean AI response text by removing reasoning tags and formatting
    
    Args:
        text: Raw AI response text
        
    Returns:
        Cleaned text with tags removed
    """
    
    # Remove common reasoning tags
    patterns = [
        r'\[REASONING\][\s\S]*?\[/REASONING\]',
        r'\[THINKING\][\s\S]*?\[/THINKING\]',
        r'\[ANALYSIS\][\s\S]*?\[/ANALYSIS\]',
        r'\[EVALUATION\][\s\S]*?\[/EVALUATION\]',
        r'\[SCORES\][\s\S]*?\[/SCORES\]',
        r'\[RECOMMENDATIONS\][\s\S]*?\[/RECOMMENDATIONS\]',
        r'\[DEBUG_ANALYSIS\][\s\S]*?\[/DEBUG_ANALYSIS\]',
        r'\[ISSUES_FOUND\][\s\S]*?\[/ISSUES_FOUND\]',
        r'\[CLARIFICATION_QUESTIONS\][\s\S]*?\[/CLARIFICATION_QUESTIONS\]',
        r'\[RESEARCH_AREAS\][\s\S]*?\[/RESEARCH_AREAS\]',
        r'\[SUB_TOPICS\][\s\S]*?\[/SUB_TOPICS\]',
        r'\[INFORMATION_SOURCES\][\s\S]*?\[/INFORMATION_SOURCES\]',
        r'\[RESEARCH_STRATEGY\][\s\S]*?\[/RESEARCH_STRATEGY\]',
        r'\[SUCCESS_CRITERIA\][\s\S]*?\[/SUCCESS_CRITERIA\]',
        r'\[RESEARCH_DRAFT\][\s\S]*?\[/RESEARCH_DRAFT\]',
        r'\[GAP_ANALYSIS\][\s\S]*?\[/GAP_ANALYSIS\]',
        r'\[SPECIFIC_GAPS\][\s\S]*?\[/SPECIFIC_GAPS\]',
        r'\[ENHANCED_DRAFT\][\s\S]*?\[/ENHANCED_DRAFT\]',
        r'\[FINAL_REPORT\][\s\S]*?\[/FINAL_REPORT\]'
    ]
    
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned

def parse_gap_analysis(text: str) -> List[Dict[str, Any]]:
    """
    Parse gap analysis text into structured gap objects
    
    Args:
        text: Raw gap analysis text
        
    Returns:
        List of structured gap objects
    """
    
    gaps = []
    
    # Extract specific gaps section
    gaps_match = re.search(
        r'\[SPECIFIC_GAPS\]([\s\S]*?)(?:\[|$)',
        text,
        re.IGNORECASE
    )
    
    if not gaps_match:
        return gaps
    
    gaps_text = gaps_match.group(1)
    
    # Parse individual gaps
    gap_pattern = r'-\s*Gap\s+ID:\s*(\w+)\s*\n\s*-?\s*Section:\s*(.*?)\s*\n\s*-?\s*Type:\s*(.*?)\s*\n\s*-?\s*Description:\s*(.*?)\s*\n\s*-?\s*Priority:\s*(\w+)\s*\n\s*-?\s*Search\s+Query:\s*(.*?)\s*(?=\n-|\n\[|$)'
    
    matches = re.findall(gap_pattern, gaps_text, re.IGNORECASE | re.MULTILINE)
    
    for match in matches:
        gap_id, section, gap_type, description, priority, search_query = match
        
        gaps.append({
            "id": gap_id.strip(),
            "section": section.strip(),
            "gap_type": gap_type.strip(),
            "specific_need": description.strip(),
            "search_query": search_query.strip(),
            "priority": priority.strip().lower(),
            "status": "pending"
        })
    
    return gaps

def create_fallback_gap(query: str) -> List[Dict[str, Any]]:
    """
    Create fallback gap when parsing fails
    
    Args:
        query: Original research query
        
    Returns:
        Basic gap structure for fallback
    """
    
    return [{
        "id": str(uuid.uuid4())[:8],
        "section": "general",
        "gap_type": "missing_information",
        "specific_need": "Additional research needed for comprehensive coverage",
        "search_query": f"comprehensive research {query}",
        "priority": "medium",
        "status": "pending"
    }]

class SearchResultFormatter:
    """Utility class for formatting search results"""
    
    @staticmethod
    def format_results_for_llm(
        results: List[Dict[str, Any]],
        original_query: str
    ) -> str:
        """
        Format search results for LLM consumption
        
        Args:
            results: Raw search results
            original_query: Original search query
            
        Returns:
            Formatted string for LLM
        """
        
        if not results:
            return f"No relevant results found for: {original_query}"
        
        formatted_parts = []
        formatted_parts.append(f"Search Results for: {original_query}\n")
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "No Title")
            content = result.get("content", "No Content")
            url = result.get("url", "No URL")
            date = result.get("published_date", "Unknown Date")
            
            # Truncate content if too long
            if len(content) > 800:
                content = content[:800] + "..."
            
            formatted_parts.append(f"{i}. {title}")
            formatted_parts.append(f"   URL: {url}")
            formatted_parts.append(f"   Date: {date}")
            formatted_parts.append(f"   Content: {content}")
            formatted_parts.append("")
        
        return "\n".join(formatted_parts)
    
    @staticmethod
    def format_sources_for_citations(sources: List[Dict[str, Any]]) -> str:
        """
        Format sources for citation in final report
        
        Args:
            sources: Source data objects
            
        Returns:
            Formatted citations string
        """
        
        if not sources:
            return "No sources used in this research."
        
        citations = []
        citations.append("## References")
        citations.append("")
        
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Untitled")
            url = source.get("url", "No URL")
            date = source.get("published_date", "No date")
            
            citation = f"{i}. {title}. {date}. Available at: {url}"
            citations.append(citation)
        
        return "\n".join(citations)

def calculate_component_fitness(
    search_results: List[Dict[str, Any]],
    gaps_addressed: List[str],
    quality_scores: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate fitness scores for system components
    
    Args:
        search_results: List of search results
        gaps_addressed: List of gap IDs that were addressed
        quality_scores: Quality evaluation scores
        
    Returns:
        Component fitness scores
    """
    
    # Base scores
    fitness = {
        "search_strategy": 0.8,
        "synthesis_quality": 0.7,
        "integration_ability": 0.7,
        "gap_identification": 0.8,
        "enhancement_effectiveness": 0.7
    }
    
    # Adjust based on results
    if search_results:
        fitness["search_strategy"] = min(1.0, 0.8 + len(search_results) * 0.05)
    
    if gaps_addressed:
        fitness["gap_identification"] = min(1.0, 0.8 + len(gaps_addressed) * 0.1)
    
    # Adjust based on quality scores
    if quality_scores:
        overall_quality = quality_scores.get("overall_quality", 0.7)
        fitness["synthesis_quality"] = overall_quality
        fitness["enhancement_effectiveness"] = overall_quality
        
        # Use individual scores
        fitness["integration_ability"] = (
            quality_scores.get("structure", 0.7) * 0.4 +
            quality_scores.get("accuracy", 0.7) * 0.6
        )
    
    return fitness

def validate_state(state: Dict[str, Any]) -> List[str]:
    """
    Validate research state for completeness
    
    Args:
        state: Research state to validate
        
    Returns:
        List of validation issues found
    """
    
    issues = []
    
    # Required fields
    required_fields = ["query", "client", "search_tool"]
    for field in required_fields:
        if not state.get(field):
            issues.append(f"Missing required field: {field}")
    
    # Validate types
    if state.get("max_iterations") is not None:
        if not isinstance(state["max_iterations"], int) or state["max_iterations"] < 1:
            issues.append("max_iterations must be positive integer")
    
    if state.get("quality_threshold") is not None:
        if not isinstance(state["quality_threshold"], (int, float)):
            issues.append("quality_threshold must be numeric")
        elif not 0 <= state["quality_threshold"] <= 1:
            issues.append("quality_threshold must be between 0 and 1")
    
    # Validate lists
    list_fields = ["research_gaps", "search_results", "sources", "previous_drafts"]
    for field in list_fields:
        if field in state and not isinstance(state[field], list):
            issues.append(f"{field} must be a list")
    
    return issues

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    
    # Remove or replace unsafe characters
    unsafe_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(unsafe_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    # Ensure not empty
    if not sanitized:
        sanitized = "research_output"
    
    return sanitized

def format_timestamp_for_display(timestamp: str) -> str:
    """
    Format ISO timestamp for display
    
    Args:
        timestamp: ISO format timestamp
        
    Returns:
        Formatted timestamp string
    """
    
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return str(timestamp)