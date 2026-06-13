"""
Semantic Kernel configuration for multi-agent orchestration.
"""
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from backend.config.settings import settings


def create_kernel() -> Kernel:
    """
    Create and configure a Semantic Kernel instance.
    
    Returns:
        Kernel: Configured Semantic Kernel with Azure OpenAI connection
    """
    kernel = Kernel()

    # Add Azure OpenAI chat completion service
    kernel.add_service(
        AzureChatCompletion(
            deployment_name=settings.azure_openai_model_deployment,
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
    )

    return kernel


def get_kernel() -> Kernel:
    """
    Get or create the global kernel instance.
    
    Returns:
        Kernel: Semantic Kernel instance
    """
    if not hasattr(get_kernel, "_instance"):
        get_kernel._instance = create_kernel()
    return get_kernel._instance

