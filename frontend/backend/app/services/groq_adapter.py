"""
Groq LLM Adapter
Handles calls to Groq API (LLaMA 3.3 70B)
"""
import os
import logging
from typing import Dict, Any
import requests
import time

logger = logging.getLogger(__name__)

class GroqAdapter:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.max_retries = int(os.getenv("GROQ_MAX_RETRIES", "3"))
        self.retry_delay = float(os.getenv("GROQ_RETRY_DELAY", "1.0"))
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set")
    
    def test_connection(self):
        """Test Groq API connectivity"""
        try:
            response = self.generate(
                prompt="test",
                max_tokens=5,
                temperature=0.0
            )
            return len(response) > 0
        except Exception as e:
            raise Exception(f"Groq connection failed: {e}")
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
        system_prompt: str = None
    ) -> str:
        """
        Generate text using Groq LLaMA 3.3 70B
        
        Args:
            prompt: User prompt / question
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system instruction
            
        Returns:
            Generated text response
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 1.0,
            "stream": False
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                response.raise_for_status()
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                logger.info(f"Groq API call successful (tokens: {data.get('usage', {}).get('total_tokens', 'N/A')})")
                return content.strip()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Groq API request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise Exception(f"Groq API failed after {self.max_retries} attempts: {e}")
    
    def generate_with_context(
        self,
        query: str,
        contexts: list,
        temperature: float = 0.2,
        max_tokens: int = 512,
        system_instruction: str = None
    ) -> Dict[str, Any]:
        """
        Generate answer with retrieved contexts
        
        Args:
            query: User question
            contexts: List of retrieved context dicts with 'text' and 'score'
            temperature: Sampling temperature
            max_tokens: Max output tokens
            system_instruction: Optional system instruction
            
        Returns:
            Dict with 'answer' and 'raw_output'
        """
        # Build prompt with contexts
        context_text = "\n\n".join([
            f"[Context {i+1}] (relevance: {ctx.get('score', 0):.3f})\n{ctx.get('text', '')}"
            for i, ctx in enumerate(contexts)
        ])
        
        default_system = """You are an expert AI assistant with deep analytical capabilities. Your role is to provide comprehensive, well-structured answers based on the provided context documents.

CRITICAL INSTRUCTIONS:

1. **Answer Quality & Depth:**
   - Provide thorough, detailed explanations that fully address the question
   - Include relevant background information and context
   - Explain concepts clearly as if teaching someone
   - Use proper technical terminology when appropriate
   - Give concrete examples when they help understanding

2. **Citation & Attribution:**
   - ALWAYS cite sources using [Context N] notation
   - Cite every factual claim, not just direct quotes
   - Place citations at the end of sentences: "The system uses RAG architecture [Context 1]."
   - If multiple contexts support a claim, cite all: [Context 1, Context 2]
   - If contexts conflict, acknowledge this explicitly

3. **Structure & Formatting:**
   - Use clear headings (##) to organize complex answers
   - Use bullet points for lists and key points
   - Use numbered lists for sequential steps or procedures
   - Use **bold** for emphasis on key terms and concepts
   - Use `code formatting` for technical terms, file names, and code references
   - Break long answers into logical sections

4. **Tone & Style:**
   - Professional yet conversational
   - Clear and accessible language
   - Avoid unnecessary jargon, but don't oversimplify
   - Be direct and confident in your explanations
   - Use active voice when possible

5. **Completeness & Accuracy:**
   - Synthesize information from multiple contexts when relevant
   - If context is insufficient, clearly state what's missing
   - Don't make assumptions beyond what's in the context
   - If asked about something not in context, say: "The provided documents don't contain information about X."
   - Provide actionable information when possible

6. **Special Cases:**
   - For "how-to" questions: Provide step-by-step instructions
   - For "what is" questions: Give comprehensive definitions with examples
   - For comparison questions: Use structured comparisons
   - For troubleshooting: Explain root causes and solutions

EXAMPLE OUTPUT FORMAT:

For a question about a technical system:

## Overview

The knowledge-base search engine uses RAG (Retrieval-Augmented Generation) architecture to search documents and provide synthesized answers [Context 1].

## Key Components

**Input Processing:**
- Accepts multiple text/PDF documents as input [Context 1]
- Documents are processed through the ingestion pipeline

**Architecture:**
- Backend API handles document ingestion and queries [Context 1]
- LLM performs answer synthesis [Context 1]
- Vector database stores document embeddings

## Primary Objectives

The system aims to provide:
1. **Accurate Retrieval** - Find the most relevant document sections
2. **High-Quality Synthesis** - Generate coherent, comprehensive answers [Context 1]

Remember: Your goal is to provide the same quality of response that a knowledgeable technical expert would give in a professional setting."""
        
        system_prompt = system_instruction or default_system
        
        user_prompt = f"""Below are the relevant context documents retrieved from the knowledge base. Analyze them carefully and provide a comprehensive answer.

CONTEXT DOCUMENTS:

{context_text}

QUESTION: {query}

Provide a thorough, well-structured answer based on the context above. Remember to:
- Use proper formatting (headings, bullets, bold)
- Cite every claim with [Context N]
- Organize information logically
- Be comprehensive yet clear
- Follow all instructions from the system prompt"""
        
        answer = self.generate(
            prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
        
        return {
            "answer": answer,
            "raw_output": answer,
            "model": self.model
        }
