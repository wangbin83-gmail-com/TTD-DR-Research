#!/usr/bin/env python3
"""
TTD-DR: Test-Time Diffusion Deep Research
Main execution script for running AI-powered research using Kimi API
"""

import asyncio
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from langgraph_ttd_dr.interface import TTDResearcher
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_research(
    query: str,
    max_iterations: int = 3,
    client_type: str = "kimi",
    save_to_file: bool = True,
    output_dir: str = "research_outputs",
    research_context: str = "",
    quality_threshold: float = 0.85
) -> Dict[str, Any]:
    """
    Run comprehensive research using TTD-DR methodology
    
    Args:
        query: Research question or topic
        max_iterations: Maximum refinement iterations
        client_type: AI client type ('kimi', 'openai', 'azure')
        save_to_file: Whether to save results to file
        output_dir: Directory for saving outputs
        research_context: Additional context for multi-faceted research
        quality_threshold: Target quality score for stopping
        
    Returns:
        Dictionary containing research results and metadata
    """
    
    logger.info(f"Starting research: {query}")
    
    # Initialize researcher
    researcher = TTDResearcher(
        query=query,
        client_type=client_type,
        max_iterations=max_iterations,
        quality_threshold=quality_threshold,
        research_context=research_context
    )
    
    # Run research
    try:
        result = await researcher.run()
        
        if save_to_file:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = "".join(c for c in query[:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_query = safe_query.replace(' ', '_')
            filename = f"research_{safe_query}_{timestamp}"
            
            # Save final report
            report_file = output_path / f"{filename}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(result["final_report"])
            
            # Save metadata
            metadata_file = output_path / f"{filename}_metadata.json"
            metadata = {
                "query": query,
                "research_context": research_context,
                "timestamp": datetime.now().isoformat(),
                "quality_score": result.get("quality_score", 0),
                "iterations": result.get("iterations", 0),
                "sources_count": len(result.get("sources", [])),
                "gaps_identified": result.get("gaps_identified", 0),
                "files": {
                    "report": str(report_file),
                    "metadata": str(metadata_file)
                }
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Research saved to: {report_file}")
            result["output_file"] = str(report_file)
            result["metadata_file"] = str(metadata_file)
        
        return result
        
    except Exception as e:
        logger.error(f"Research failed: {str(e)}")
        raise

async def run_batch_research(
    queries: list,
    **kwargs
) -> list:
    """
    Run multiple research queries in parallel
    
    Args:
        queries: List of research questions
        **kwargs: Additional arguments for run_research
        
    Returns:
        List of research results
    """
    
    logger.info(f"Starting batch research with {len(queries)} queries")
    
    tasks = [run_research(query, **kwargs) for query in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions
    successful_results = [r for r in results if not isinstance(r, Exception)]
    failed_count = len([r for r in results if isinstance(r, Exception)])
    
    if failed_count > 0:
        logger.warning(f"{failed_count} queries failed during batch processing")
    
    logger.info(f"Batch research completed: {len(successful_results)} successful, {failed_count} failed")
    
    return successful_results

async def main():
    """Main execution function with example usage"""
    
    # Example research queries
    test_queries = [
        "What are the latest developments in AI-powered drug discovery in 2024?",
        "Analyze the impact of quantum computing on cryptography and cybersecurity",
        "Compare different approaches to sustainable energy storage technologies"
    ]
    
    print("🚀 TTD-DR: Test-Time Diffusion Deep Research")
    print("=" * 50)
    
    # Check for Kimi API key
    kimi_key = os.getenv("KIMI_API_KEY")
    if not kimi_key:
        print("❌ KIMI_API_KEY not found in environment variables")
        print("Please set your Kimi API key in .env file")
        return
    
    # Run single research example
    print("\n📊 Running single research example...")
    
    try:
        result = await run_research(
            query=test_queries[0],
            max_iterations=2,  # Reduced for demo
            save_to_file=True,
            output_dir="demo_outputs"
        )
        
        print(f"✅ Research completed!")
        print(f"📄 Report saved to: {result['output_file']}")
        print(f"📈 Quality score: {result['quality_score']:.2f}")
        print(f"🔄 Iterations: {result['iterations']}")
        print(f"📚 Sources used: {len(result['sources'])}")
        
    except Exception as e:
        print(f"❌ Research failed: {str(e)}")
        logger.error(f"Demo research failed: {str(e)}")

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())