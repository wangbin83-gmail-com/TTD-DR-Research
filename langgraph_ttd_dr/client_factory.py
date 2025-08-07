"""
TTD-DR Client Factory Module
Factory for creating AI clients with different providers
"""

import os
import logging
from typing import Optional, Dict, Any

from langchain_openai import ChatOpenAI, AzureChatOpenAI

logger = logging.getLogger(__name__)

class KimiClient:
    """Custom Kimi/Moonshot AI client wrapper"""
    
    def __init__(self, api_key: str, model: str = "moonshot-v1-8k", **kwargs):
        self.client = ChatOpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
            model=model,
            **kwargs
        )
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from Kimi AI"""
        try:
            response = await self.client.ainvoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Kimi API error: {e}")
            raise

def create_client(
    client_type: str = "kimi",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Create AI client based on specified type
    
    Args:
        client_type: Type of client ('kimi', 'openai', 'azure')
        api_key: API key for authentication
        model: Specific model to use
        **kwargs: Additional configuration options
        
    Returns:
        Configured AI client
    """
    
    if client_type == "kimi":
        return create_kimi_client(api_key, model, **kwargs)
    elif client_type == "openai":
        return create_openai_client(api_key, model, **kwargs)
    elif client_type == "azure":
        return create_azure_client(api_key, **kwargs)
    else:
        raise ValueError(f"Unsupported client type: {client_type}")

def create_kimi_client(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> KimiClient:
    """Create Kimi/Moonshot AI client"""
    
    api_key = api_key or os.getenv("KIMI_API_KEY")
    if not api_key:
        raise ValueError("KIMI_API_KEY not provided and not found in environment")
    
    # Default model selection
    model = model or get_kimi_model(**kwargs)
    
    logger.info(f"Creating Kimi client with model: {model}")
    
    return KimiClient(
        api_key=api_key,
        model=model,
        temperature=kwargs.get("temperature", 0.7),
        max_tokens=kwargs.get("max_tokens", 4000),
        **kwargs
    )

def create_openai_client(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> ChatOpenAI:
    """Create OpenAI client"""
    
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not provided and not found in environment")
    
    # Default model selection
    model = model or "gpt-4-turbo-preview"
    
    logger.info(f"Creating OpenAI client with model: {model}")
    
    return ChatOpenAI(
        api_key=api_key,
        model=model,
        temperature=kwargs.get("temperature", 0.7),
        max_tokens=kwargs.get("max_tokens", 4000),
        **kwargs
    )

def create_azure_client(
    api_key: Optional[str] = None,
    **kwargs
) -> AzureChatOpenAI:
    """Create Azure OpenAI client"""
    
    api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = kwargs.get("azure_endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = kwargs.get("api_version") or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    deployment_name = kwargs.get("deployment_name") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY not provided and not found in environment")
    if not azure_endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT not provided and not found in environment")
    if not deployment_name:
        raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME not provided and not found in environment")
    
    logger.info(f"Creating Azure OpenAI client with deployment: {deployment_name}")
    
    return AzureChatOpenAI(
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        azure_deployment=deployment_name,
        temperature=kwargs.get("temperature", 0.7),
        max_tokens=kwargs.get("max_tokens", 4000),
        **kwargs
    )

def get_kimi_model(**kwargs) -> str:
    """
    Determine appropriate Kimi model based on requirements
    
    Args:
        **kwargs: Configuration parameters
        
    Returns:
        Model name string
    """
    
    # Available Kimi models
    models = {
        "moonshot-v1-8k": "8k context",
        "moonshot-v1-32k": "32k context", 
        "moonshot-v1-128k": "128k context"
    }
    
    # Default to 8k context for most use cases
    default_model = "moonshot-v1-8k"
    
    # Check for specific model override
    requested_model = kwargs.get("model")
    if requested_model and requested_model in models:
        return requested_model
    
    # Auto-select based on expected length
    expected_length = kwargs.get("expected_length", 0)
    if expected_length > 24000:  # 75% of 32k
        return "moonshot-v1-128k"
    elif expected_length > 6000:   # 75% of 8k
        return "moonshot-v1-32k"
    
    return default_model