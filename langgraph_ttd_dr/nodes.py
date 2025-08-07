"""
TTD-DR Nodes Module
Implementation of research workflow nodes for LangGraph
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langgraph_ttd_dr.state import TTDResearchState
from langgraph_ttd_dr.prompts import (
    get_clarification_prompt,
    get_planning_prompt,
    get_draft_generation_prompt,
    get_gap_analysis_prompt
)
from langgraph_ttd_dr.utils import (
    clean_reasoning_tags,
    parse_gap_analysis,
    create_fallback_gap,
    SearchResultFormatter
)

logger = logging.getLogger(__name__)

class BaseResearchNode:
    """Base class for research workflow nodes"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def process(self, state: TTDResearchState) -> TTDResearchState:
        """Process the current state and return updated state"""
        raise NotImplementedError
    
    async def __call__(self, state: TTDResearchState) -> TTDResearchState:
        """Make node callable for LangGraph"""
        return await self.process(state)

class ClarificationNode(BaseResearchNode):
    """Node for analyzing research query and determining if clarification is needed"""
    
    async def process(self, state: TTDResearchState) -> TTDResearchState:
        """Analyze query for clarity and completeness"""
        
        self.logger.info("Analyzing query for clarification needs...")
        
        # Generate clarification prompt
        prompt = get_clarification_prompt(state["query"])
        
        # Get clarification analysis from AI
        response = await state["client"].generate(prompt)
        
        # Parse response and update state
        clarification_text = clean_reasoning_tags(response)
        
        # Update state with clarification analysis
        state["clarification_needed"] = "NEEDS_CLARIFICATION: YES" in clarification_text
        state["clarification_questions"] = self._extract_questions(clarification_text)
        state["query_analysis"] = clarification_text
        
        self.logger.info(f"Clarification analysis complete. Needs clarification: {state['clarification_needed']}")
        
        return state
    
    def _extract_questions(self, text: str) -> List[str]:
        """Extract clarification questions from AI response"""
        questions = []
        lines = text.split('\n')
        in_questions = False
        
        for line in lines:
            line = line.strip()
            if 'CLARIFICATION_QUESTIONS:' in line:
                in_questions = True
                continue
            if in_questions and line and not line.startswith('---'):
                if line.startswith('-') or line.startswith('•'):
                    questions.append(line[1:].strip())
                elif line and not line.startswith('['):
                    questions.append(line)
        
        return questions

class PlanningNode(BaseResearchNode):
    """Node for generating comprehensive research plans"""
    
    async def process(self, state: TTDResearchState) -> TTDResearchState:
        """Generate research strategy and plan"""
        
        self.logger.info("Generating research plan...")
        
        # Build planning context
        planning_context = ""
        if state["research_context"]:
            planning_context = f"Research Context: {state['research_context']}"
        
        if state["clarification_questions"]:
            planning_context += f"\n\nUser provided clarification: {state['clarification_questions']}"
        
        # Generate planning prompt
        prompt = get_planning_prompt(state["query"], planning_context)
        
        # Get research plan from AI
        response = await state["client"].generate(prompt)
        
        # Update state with research plan
        state["research_plan"] = clean_reasoning_tags(response)
        state["planning_timestamp"] = datetime.now().isoformat()
        
        self.logger.info("Research plan generated successfully")
        
        return state

class DraftGenerationNode(BaseResearchNode):
    """Node for generating initial research drafts"""
    
    async def process(self, state: TTDResearchState) -> TTDResearchState:
        """Generate comprehensive research draft"""
        
        self.logger.info("Generating initial research draft...")
        
        # Build draft generation context
        draft_context = state["research_context"] if state["research_context"] else ""
        
        # Generate draft prompt
        prompt = get_draft_generation_prompt(
            state["query"],
            state["research_plan"],
            draft_context
        )
        
        # Generate draft
        response = await state["client"].generate(prompt)
        
        # Update state with draft
        state["current_draft"] = clean_reasoning_tags(response)
        state["draft_timestamp"] = datetime.now().isoformat()
        state["current_iteration"] = 1
        
        self.logger.info(f"Initial draft generated (iteration {state['current_iteration']})")
        
        return state

class GapAnalyzerNode(BaseResearchNode):
    """Node for identifying research gaps and areas needing improvement"""
    
    async def process(self, state: TTDResearchState) -> TTDResearchState:
        """Analyze current draft for research gaps"""
        
        self.logger.info("Analyzing research gaps...")
        
        # Generate gap analysis prompt
        prompt = get_gap_analysis_prompt(state["query"], state["current_draft"])
        
        # Get gap analysis from AI
        response = await state["client"].generate(prompt)
        
        # Parse gaps
        try:
            gaps = parse_gap_analysis(response)
            if not gaps:
                gaps = create_fallback_gap(state["query"])
        except Exception as e:
            self.logger.warning(f"Failed to parse gap analysis: {e}")
            gaps = create_fallback_gap(state["query"])
        
        # Update state with gaps
        state["research_gaps"] = gaps
        state["gap_analysis_text"] = response
        state["gap_analysis_timestamp"] = datetime.now().isoformat()
        
        self.logger.info(f"Identified {len(gaps)} research gaps")
        
        return state

class WebSearchNode(BaseResearchNode):
    """Node for conducting targeted web searches based on identified gaps"""
    
    async def process(self, state: TTDResearchState) -> TTDResearchState:
        """Execute web searches for research gaps"""
        
        if not state["research_gaps"]:
            self.logger.info("No gaps to search for")
            return state
        
        self.logger.info(f"Starting web search for {len(state['research_gaps'])} gaps...")
        
        # Execute searches for each gap
        all_search_results = []
        
        for gap in state["research_gaps"]:
            if gap.get("search_query"):
                self.logger.info(f"Searching for: {gap['search_query']}")
                
                try:
                    # Execute search
                    search_results = await state["search_tool"].search(
                        gap["search_query"],
                        max_results=5
                    )
                    
                    # Format results with gap context
                    formatted_results = SearchResultFormatter.format_results_for_llm(
                        search_results,
                        gap["search_query"]
                    )
                    
                    # Add metadata
                    for result in search_results:
                        result["gap_id"] = gap.get("id")
                        result["gap_section"] = gap.get("section")
                    
                    all_search_results.extend(search_results)
                    
                except Exception as e:
                    self.logger.error(f"Search failed for gap {gap.get('id')}: {e}")
        
        # Update state with search results
        state["search_results"] = all_search_results
        state["search_timestamp"] = datetime.now().isoformat()
        
        self.logger.info(f"Web search completed. Found {len(all_search_results)} results")
        
        return state

class EnhancementNode(BaseResearchNode):
    """Node for enhancing research content based on search results"""
    
    async def process(self, state: TTDResearchState) -> TTDResearchState:
        """Enhance draft with new information from search results"""
        
        if not state["search_results"]:
            self.logger.info("No search results to enhance with")
            return state
        
        self.logger.info("Enhancing research content...")
        
        # Prepare enhancement context
        search_context = "\n\n".join([
            f"Source: {result['title']}\nContent: {result['content'][:500]}..."
            for result in state["search_results"][:10]  # Limit to prevent token overflow
        ])
        
        # Create enhancement prompt
        enhancement_prompt = f"""
        Enhance the following research draft using the provided search results:
        
        ORIGINAL QUERY: {state['query']}
        
        CURRENT DRAFT:
        {state['current_draft']}
        
        NEW RESEARCH FINDINGS:
        {search_context}
        
        TASK:
        1. Integrate relevant new information into the draft
        2. Address the specific research gaps identified
        3. Maintain coherent structure and flow
        4. Add appropriate citations and references
        5. Ensure accuracy and avoid contradictions
        
        Provide the enhanced research draft.
        """
        
        # Generate enhanced draft
        response = await state["client"].generate(enhancement_prompt)
        
        # Update state
        previous_draft = state["current_draft"]
        state["current_draft"] = clean_reasoning_tags(response)
        state["previous_drafts"].append(previous_draft)
        state["sources"].extend(state["search_results"])
        state["current_iteration"] += 1
        state["enhancement_timestamp"] = datetime.now().isoformat()
        
        self.logger.info(f"Content enhanced (iteration {state['current_iteration']})")
        
        return state

class QualityEvaluatorNode(BaseResearchNode):
    """Node for evaluating research quality and determining next steps"""
    
    async def process(self, state: TTDResearchState) -> TTDResearchState:
        """Evaluate current research quality"""
        
        self.logger.info("Evaluating research quality...")
        
        # Create quality evaluation prompt
        quality_prompt = f"""
        Evaluate the quality of this research draft based on the following criteria:
        
        RESEARCH QUERY: {state['query']}
        
        CURRENT DRAFT:
        {state['current_draft']}
        
        EVALUATION CRITERIA:
        1. Comprehensiveness (0-1): How thoroughly does it address the query?
        2. Accuracy (0-1): Is the information accurate and well-sourced?
        3. Depth (0-1): Does it provide sufficient depth and analysis?
        4. Structure (0-1): Is it well-organized and coherent?
        5. Currency (0-1): Is the information current and relevant?
        
        Provide scores for each criterion (0-1 scale) and an overall quality score.
        Format as:
        COMPREHENSIVENESS: [score]
        ACCURACY: [score]
        DEPTH: [score]
        STRUCTURE: [score]
        CURRENCY: [score]
        OVERALL_QUALITY: [score]
        """
        
        # Get quality evaluation
        response = await state["client"].generate(quality_prompt)
        
        # Parse quality scores
        quality_scores = self._parse_quality_scores(response)
        overall_quality = quality_scores.get("OVERALL_QUALITY", 0.5)
        
        # Update state
        state["quality_score"] = overall_quality
        state["quality_scores"] = quality_scores
        state["quality_evaluation"] = response
        state["quality_timestamp"] = datetime.now().isoformat()
        
        self.logger.info(f"Quality evaluation complete. Score: {overall_quality:.2f}")
        
        return state
    
    def _parse_quality_scores(self, response: str) -> Dict[str, float]:
        """Parse quality scores from AI response"""
        scores = {}
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                try:
                    scores[key] = float(value.strip())
                except ValueError:
                    scores[key] = 0.5
        
        return scores

class FinalReportNode(BaseResearchNode):
    """Node for generating final polished research report"""
    
    async def process(self, state: TTDResearchState) -> TTDResearchState:
        """Generate final research report with proper formatting and references"""
        
        self.logger.info("Generating final research report...")
        
        # Create final report prompt
        final_prompt = f"""
        Create a polished final research report based on the completed research.
        
        ORIGINAL QUERY: {state['query']}
        
        RESEARCH DRAFT:
        {state['current_draft']}
        
        SOURCES ({len(state['sources'])} total):
        {self._format_sources(state['sources'])}
        
        TASK:
        1. Create a comprehensive, well-structured research report
        2. Include proper introduction and conclusion
        3. Add formatted citations and references
        4. Ensure professional presentation
        5. Remove any placeholder tags or incomplete sections
        6. Provide clear section headings and organization
        
        The report should be publication-ready.
        """
        
        # Generate final report
        response = await state["client"].generate(final_prompt)
        
        # Update state with final report
        state["final_report"] = clean_reasoning_tags(response)
        state["finalization_timestamp"] = datetime.now().isoformat()
        state["research_complete"] = True
        
        self.logger.info("Final research report generated successfully")
        
        return state
    
    def _format_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources for final report"""
        if not sources:
            return "No sources used"
        
        formatted = []
        for i, source in enumerate(sources, 1):
            title = source.get('title', 'Untitled')
            url = source.get('url', 'No URL')
            date = source.get('published_date', 'No date')
            formatted.append(f"[{i}] {title} ({date}) - {url}")
        
        return '\n'.join(formatted)