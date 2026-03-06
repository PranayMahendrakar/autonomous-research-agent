"""
🧠 Summarizer Module
Uses LLM (OpenAI / Ollama) to summarize articles and synthesize research.
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class Summarizer:
    """
    LLM-powered summarizer that:
    - Summarizes individual articles
    - Synthesizes multiple summaries into insights
    - Answers follow-up questions via RAG
    """

    def __init__(self):
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        
        if self.use_ollama:
            # Use local Ollama instance
            self.client = OpenAI(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                api_key="ollama"
            )
            self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        else:
            # Use OpenAI
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self.max_tokens = int(os.getenv("MAX_TOKENS", "1500"))

    def summarize_article(self, article: Dict, topic: str) -> Optional[str]:
        """
        Summarize a single article in the context of the research topic.

        Args:
            article: Article dict with title, url, content
            topic: Research topic for context

        Returns:
            Summary string or None on failure
        """
        content = article.get("content", "")
        title = article.get("title", "Unknown")
        url = article.get("url", "")

        if not content:
            return None

        # Truncate if too long
        content = content[:4000]

        prompt = f"""You are a research assistant. Summarize the following article in the context of researching: "{topic}"

Article Title: {title}
Article URL: {url}

Article Content:
{content}

Please provide:
1. A 2-3 sentence overview of what this article covers
2. The 3-5 most relevant key points related to "{topic}"
3. Any important data, statistics, or findings mentioned

Keep the summary focused and factual. Format as plain text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert research assistant that creates concise, accurate summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"   Summarization error: {e}")
            return None

    def synthesize(self, topic: str, summaries: List[str]) -> str:
        """
        Synthesize multiple article summaries into a coherent research overview.

        Args:
            topic: Research topic
            summaries: List of article summaries

        Returns:
            Synthesized research findings
        """
        if not summaries:
            return "Insufficient data to synthesize."

        combined = "\n\n---\n\n".join(
            [f"Source {i+1}:\n{s}" for i, s in enumerate(summaries)]
        )

        prompt = f"""You are a senior research analyst. Based on the following article summaries about "{topic}", 
create a comprehensive synthesis of the key findings.

SUMMARIES:
{combined[:6000]}

Please synthesize:
1. **Main Themes**: What are the 3-5 major themes across all sources?
2. **Key Findings**: What are the most important facts, trends, or insights?
3. **Consensus & Disagreements**: Where do sources agree or differ?
4. **Current State**: What is the current state of "{topic}"?
5. **Future Outlook**: What trends or developments are anticipated?
6. **Research Gaps**: What questions remain unanswered?

Write in a professional, analytical tone suitable for a research report."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior research analyst that synthesizes information from multiple sources into clear insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"   Synthesis error: {e}")
            return "Synthesis could not be completed due to an error."

    def answer_question(self, question: str, context: str, topic: str) -> str:
        """
        Answer a follow-up question using retrieved context (RAG).

        Args:
            question: User's question
            context: Relevant chunks from vector DB
            topic: Original research topic

        Returns:
            Answer string
        """
        prompt = f"""You are a research assistant. Using ONLY the provided context from the research on "{topic}", 
answer the following question.

CONTEXT:
{context[:5000]}

QUESTION: {question}

Provide a detailed, accurate answer based solely on the context. 
If the answer is not in the context, say so clearly.
Cite which parts of the context support your answer."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant. Answer questions based only on provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Could not answer question: {e}"
