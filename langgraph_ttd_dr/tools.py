"""
TTD-DR Tools Module
Web search tools with multiple engine support
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from duckduckgo_search import DDGS
from tavily import TavilyClient
import aiohttp
import requests

logger = logging.getLogger(__name__)

class WebSearchTool:
    """
    Multi-engine web search tool with caching and error handling
    
    Supports Tavily, DuckDuckGo, and Naver search engines
    """
    
    def __init__(self, engines: List[str] = None):
        """
        Initialize web search tool
        
        Args:
            engines: List of search engines to use ['tavily', 'duckduckgo', 'naver']
        """
        self.engines = engines or ["tavily", "duckduckgo"]
        self.cache = {}
        
        # Initialize clients
        self.tavily_client = None
        self.naver_client_id = None
        self.naver_client_secret = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize search engine clients"""
        
        # Initialize Tavily
        if "tavily" in self.engines:
            tavily_key = self._get_tavily_key()
            if tavily_key:
                self.tavily_client = TavilyClient(api_key=tavily_key)
            else:
                logger.warning("Tavily API key not found, skipping Tavily")
                self.engines.remove("tavily")
        
        # Initialize Naver
        if "naver" in self.engines:
            self.naver_client_id = self._get_naver_client_id()
            self.naver_client_secret = self._get_naver_client_secret()
            
            if not (self.naver_client_id and self.naver_client_secret):
                logger.warning("Naver credentials not found, skipping Naver")
                self.engines.remove("naver")
    
    def _get_tavily_key(self) -> Optional[str]:
        """Get Tavily API key from environment"""
        return os.getenv("TAVILY_API_KEY")
    
    def _get_naver_client_id(self) -> Optional[str]:
        """Get Naver client ID from environment"""
        return os.getenv("NAVER_CLIENT_ID")
    
    def _get_naver_client_secret(self) -> Optional[str]:
        """Get Naver client secret from environment"""
        return os.getenv("NAVER_CLIENT_SECRET")
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
        engine: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute web search using specified engine(s)
        
        Args:
            query: Search query
            max_results: Maximum results per engine
            engine: Specific engine to use (None for all available)
            
        Returns:
            List of search results
        """
        
        # Check cache
        cache_key = f"{query}_{max_results}_{engine or '_'.join(self.engines)}"
        if cache_key in self.cache:
            logger.info(f"Using cached results for: {query}")
            return self.cache[cache_key]
        
        all_results = []
        
        # Use specific engine if provided
        engines_to_use = [engine] if engine else self.engines
        
        for engine_name in engines_to_use:
            try:
                if engine_name == "tavily" and self.tavily_client:
                    results = await self._search_tavily(query, max_results)
                elif engine_name == "duckduckgo":
                    results = await self._search_duckduckgo(query, max_results)
                elif engine_name == "naver":
                    results = await self._search_naver(query, max_results)
                else:
                    continue
                
                all_results.extend(results)
                
            except Exception as e:
                logger.error(f"Search failed for {engine_name}: {e}")
        
        # Cache results
        self.cache[cache_key] = all_results
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Limit total results
        return all_results[:max_results * len(engines_to_use)]
    
    async def _search_tavily(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using Tavily API"""
        
        try:
            response = self.tavily_client.search(
                query=query,
                max_results=max_results,
                include_raw_content=True
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "id": str(uuid.uuid4()),
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "raw_content": result.get("raw_content", ""),
                    "published_date": result.get("published_date", ""),
                    "source": "tavily",
                    "score": result.get("score", 0.0)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            raise
    
    async def _search_duckduckgo(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo"""
        
        try:
            ddgs = DDGS()
            results = []
            
            # Use text search
            search_results = ddgs.text(
                query,
                max_results=max_results,
                region="wt-wt",
                safesearch="moderate"
            )
            
            for result in search_results:
                results.append({
                    "id": str(uuid.uuid4()),
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "content": result.get("body", ""),
                    "raw_content": result.get("body", ""),
                    "published_date": "",
                    "source": "duckduckgo",
                    "score": 0.5  # DuckDuckGo doesn't provide scores
                })
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    async def _search_naver(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using Naver API"""
        
        if not (self.naver_client_id and self.naver_client_secret):
            return []
        
        try:
            url = "https://openapi.naver.com/v1/search/webkr.json"
            headers = {
                "X-Naver-Client-Id": self.naver_client_id,
                "X-Naver-Client-Secret": self.naver_client_secret
            }
            
            params = {
                "query": query,
                "display": min(max_results, 100),  # Naver max is 100
                "start": 1,
                "sort": "sim"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()
                    
                    results = []
                    for item in data.get("items", []):
                        results.append({
                            "id": str(uuid.uuid4()),
                            "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                            "url": item.get("link", ""),
                            "content": item.get("description", "").replace("<b>", "").replace("</b>", ""),
                            "raw_content": item.get("description", ""),
                            "published_date": item.get("postdate", ""),
                            "source": "naver",
                            "score": 0.7  # Naver doesn't provide scores
                        })
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Naver search error: {e}")
            return []
    
    def clear_cache(self):
        """Clear search cache"""
        self.cache.clear()
        logger.info("Search cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "engines": self.engines,
            "tavily_available": self.tavily_client is not None,
            "naver_available": bool(self.naver_client_id and self.naver_client_secret)
        }