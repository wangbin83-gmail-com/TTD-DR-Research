"""
TTD-DR Prompts Module
Comprehensive prompt templates for research workflow
"""

from typing import Dict, Any, List

def get_clarification_prompt(query: str) -> str:
    """Generate prompt for query clarification analysis"""
    
    return f"""
    Analyze the following research query for clarity and completeness.
    
    RESEARCH QUERY: {query}
    
    TASK:
    1. Identify any ambiguities or unclear aspects
    2. Determine if additional context is needed
    3. Assess if the query is too broad or too narrow
    4. Check for missing specific requirements
    
    Provide a clear assessment and specific clarification questions if needed.
    
    Format your response as:
    [REASONING]
    Your analysis here
    
    [NEEDS_CLARIFICATION]
    YES or NO
    
    [CLARIFICATION_QUESTIONS]
    - Question 1
    - Question 2
    - etc.
    """

def get_planning_prompt(query: str, context: str = "") -> str:
    """Generate prompt for comprehensive research planning"""
    
    context_section = f"\nADDITIONAL CONTEXT: {context}" if context else ""
    
    return f"""
    Create a comprehensive research plan for the following query.
    
    RESEARCH QUERY: {query}
    {context_section}
    
    TASK:
    1. Break down the query into key research areas
    2. Identify specific sub-topics to investigate
    3. Determine information sources needed
    4. Create a systematic research strategy
    5. Define success criteria for each research area
    
    Provide a detailed, structured research plan that can guide systematic investigation.
    
    Format your response as:
    [RESEARCH_AREAS]
    List the main areas to research
    
    [SUB_TOPICS]
    Specific sub-topics for each area
    
    [INFORMATION_SOURCES]
    Types of sources needed
    
    [RESEARCH_STRATEGY]
    Step-by-step approach
    
    [SUCCESS_CRITERIA]
    How to evaluate completeness
    """

def get_draft_generation_prompt(query: str, plan: str, context: str = "") -> str:
    """Generate prompt for creating comprehensive research drafts"""
    
    context_section = f"\nRESEARCH CONTEXT: {context}" if context else ""
    
    return f"""
    Create a comprehensive research draft based on the following specifications.
    
    RESEARCH QUERY: {query}
    {context_section}
    
    RESEARCH PLAN: {plan}
    
    TASK:
    1. Create a well-structured research document
    2. Address all key areas identified in the plan
    3. Provide thorough analysis and synthesis
    4. Include relevant examples and explanations
    5. Ensure logical flow and coherence
    6. Use appropriate terminology and definitions
    
    The draft should be comprehensive and ready for further refinement.
    
    Format your response as:
    [RESEARCH_DRAFT]
    Complete research document with:
    - Executive Summary
    - Introduction
    - Main Body (organized by topics)
    - Key Findings
    - Conclusion
    - References (placeholder)
    """

def get_gap_analysis_prompt(query: str, draft: str) -> str:
    """Generate prompt for identifying research gaps"""
    
    return f"""
    Analyze the following research draft for completeness and identify specific gaps.
    
    ORIGINAL QUERY: {query}
    
    CURRENT DRAFT:
    {draft}
    
    TASK:
    1. Identify missing information or knowledge gaps
    2. Assess depth vs breadth of coverage
    3. Check for outdated information
    4. Look for unaddressed aspects of the query
    5. Identify areas needing more detail or examples
    6. Note any logical inconsistencies or gaps in reasoning
    
    Provide specific, actionable gaps that can be addressed through targeted research.
    
    Format your response as:
    [GAP_ANALYSIS]
    Overall assessment of completeness
    
    [SPECIFIC_GAPS]
    For each gap:
    - Gap ID: [unique identifier]
    - Section: [which part of the draft]
    - Type: [missing_info|outdated|insufficient_detail|inconsistency|etc.]
    - Description: [what's missing or needed]
    - Priority: [high|medium|low]
    - Search Query: [specific search to address this gap]
    """

def get_enhancement_prompt(
    query: str,
    current_draft: str,
    new_information: str,
    specific_gaps: List[Dict[str, Any]]
) -> str:
    """Generate prompt for enhancing draft with new information"""
    
    gaps_text = "\n".join([
        f"- {gap['section']}: {gap['description']}"
        for gap in specific_gaps
    ])
    
    return f"""
    Enhance the following research draft using the new information provided.
    
    ORIGINAL QUERY: {query}
    
    CURRENT DRAFT:
    {current_draft}
    
    NEW RESEARCH INFORMATION:
    {new_information}
    
    SPECIFIC GAPS TO ADDRESS:
    {gaps_text}
    
    TASK:
    1. Integrate relevant new information into the draft
    2. Address each identified gap specifically
    3. Maintain logical flow and coherence
    4. Add appropriate citations and references
    5. Ensure accuracy and avoid contradictions
    6. Improve overall quality and completeness
    
    The enhanced draft should be more comprehensive and accurate.
    
    Format your response as:
    [ENHANCED_DRAFT]
    Complete enhanced research document
    """

def get_quality_evaluation_prompt(query: str, draft: str) -> str:
    """Generate prompt for evaluating research quality"""
    
    return f"""
    Evaluate the quality of this research draft against multiple criteria.
    
    RESEARCH QUERY: {query}
    
    DRAFT TO EVALUATE:
    {draft}
    
    EVALUATION CRITERIA (score 0-1):
    1. COMPREHENSIVENESS: How thoroughly does it address all aspects of the query?
    2. ACCURACY: Is the information factually correct and reliable?
    3. DEPTH: Does it provide sufficient analysis and detail?
    4. STRUCTURE: Is it well-organized and logically structured?
    5. CURRENCY: Is the information current and up-to-date?
    
    TASK:
    1. Score each criterion from 0 to 1
    2. Provide specific feedback for each score
    3. Calculate overall quality score
    4. Identify specific areas for improvement
    5. Determine if additional iterations are needed
    
    Format your response as:
    [EVALUATION]
    Detailed assessment for each criterion
    
    [SCORES]
    COMPREHENSIVENESS: [score]
    ACCURACY: [score]
    DEPTH: [score]
    STRUCTURE: [score]
    CURRENCY: [score]
    OVERALL_QUALITY: [average_score]
    
    [RECOMMENDATIONS]
    Specific suggestions for improvement
    """

def get_final_report_prompt(query: str, final_draft: str, sources: List[Dict[str, Any]]) -> str:
    """Generate prompt for creating final polished report"""
    
    sources_text = "\n".join([
        f"- {source['title']} ({source['url']})"
        for source in sources[:10]  # Limit to prevent token overflow
    ])
    
    return f"""
    Create a polished final research report from the completed research.
    
    ORIGINAL QUERY: {query}
    
    RESEARCH DRAFT:
    {final_draft}
    
    KEY SOURCES:
    {sources_text}
    
    TASK:
    1. Create a professional, publication-ready report
    2. Add proper introduction and conclusion
    3. Format with clear section headings
    4. Add executive summary
    5. Include properly formatted references
    6. Ensure consistent formatting and style
    7. Remove any placeholder content or tags
    8. Add table of contents if appropriate
    
    The final report should be comprehensive, well-structured, and ready for presentation.
    
    Format your response as:
    [FINAL_REPORT]
    Complete polished research report with:
    - Title
    - Executive Summary
    - Table of Contents (if needed)
    - Introduction
    - Main Body (organized sections)
    - Conclusion
    - References
    - Appendices (if needed)
    """

def get_debug_prompt(query: str, state_info: str) -> str:
    """Generate debug prompt for troubleshooting"""
    
    return f"""
    Debug the following research workflow state.
    
    RESEARCH QUERY: {query}
    
    CURRENT STATE:
    {state_info}
    
    TASK:
    1. Identify any issues or problems
    2. Analyze workflow progress
    3. Check for missing data or errors
    4. Provide debugging recommendations
    
    Format your response as:
    [DEBUG_ANALYSIS]
    Systematic analysis of current state
    
    [ISSUES_FOUND]
    List of identified issues
    
    [RECOMMENDATIONS]
    Specific debugging steps
    """