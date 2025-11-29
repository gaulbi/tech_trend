"""
Prompt Service Module

Handles loading and crafting prompts with context.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class PromptService:
    """Service for managing prompts."""
    
    def __init__(self, system_prompt_path: str, user_prompt_path: str):
        """
        Initialize prompt service.
        
        Args:
            system_prompt_path: Path to system prompt file
            user_prompt_path: Path to user prompt file
        """
        self.system_prompt_path = Path(system_prompt_path)
        self.user_prompt_path = Path(user_prompt_path)
        
        # Load prompts
        self.system_prompt = self._load_prompt(self.system_prompt_path)
        self.user_prompt = self._load_prompt(self.user_prompt_path)
        
        logger.info("Prompts loaded successfully")
    
    def _load_prompt(self, path: Path) -> str:
        """
        Load prompt from file.
        
        Args:
            path: Path to prompt file
            
        Returns:
            Prompt content
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.debug(f"Loaded prompt from: {path}")
        return content
    
    def craft_prompt(
        self,
        keywords: str,
        context_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Craft final prompt by replacing placeholders and merging system + user prompts.
        
        Per spec: "Merge system prompt and user prompt"
        
        Args:
            keywords: Keywords from analysis 'reason' field
            context_chunks: List of retrieved document chunks
            
        Returns:
            Complete merged prompt ready for LLM
        """
        # Format context from chunks
        context_text = self._format_context(context_chunks)
        
        # Replace placeholders in user prompt
        # Using double braces {{context}} and {{keywords}} as per spec
        user_prompt_filled = self.user_prompt.replace('{{context}}', context_text)
        user_prompt_filled = user_prompt_filled.replace('{{keywords}}', keywords)
        
        # Merge system and user prompts
        # System prompt first, then user prompt
        full_prompt = f"{self.system_prompt}\n\n{user_prompt_filled}"
        
        logger.info(f"Crafted merged prompt with {len(context_chunks)} context chunks")
        logger.debug(f"Prompt length: {len(full_prompt)} characters")
        
        return full_prompt
    
    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format context chunks into readable text.
        
        Args:
            chunks: List of document chunks from ChromaDB
            
        Returns:
            Formatted context string
        """
        if not chunks:
            logger.warning("No context chunks provided")
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            doc_text = chunk.get('document', '')
            metadata = chunk.get('metadata', {})
            url = metadata.get('url', 'Unknown source')
            distance = chunk.get('distance')
            
            # Format each context chunk with clear separation
            chunk_text = f"[Context {i}]"
            if url != 'Unknown source':
                chunk_text += f"\nSource: {url}"
            if distance is not None:
                chunk_text += f"\nRelevance Score: {1 - distance:.3f}"
            chunk_text += f"\nContent: {doc_text}\n"
            
            context_parts.append(chunk_text)
        
        formatted_context = "\n".join(context_parts)
        logger.debug(f"Formatted {len(chunks)} context chunks into {len(formatted_context)} characters")
        
        return formatted_context