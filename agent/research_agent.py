"""
🤖 Autonomous Research Agent - Core Agent
Orchestrates the full research pipeline: search → scrape → summarize → report
"""

import os
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from .web_scraper import WebScraper
from .summarizer import Summarizer
from .vector_store import VectorStore
from .report_generator import ReportGenerator

load_dotenv()


class ResearchAgent:
    """
    Autonomous AI Research Agent that:
    1. Searches the internet for a given topic
    2. Scrapes and reads articles
    3. Summarizes content using LLM
    4. Stores in vector DB for retrieval
    5. Generates structured output (report/blog/slides)
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.scraper = WebScraper()
        self.summarizer = Summarizer()
        self.vector_store = VectorStore()
        self.report_generator = ReportGenerator()
        self.research_data = []
        self.topic = ""
        self.max_sources = self.config.get("max_sources", 8)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def research(self, topic: str, output_format: str = "report") -> Dict:
        """
        Main entry point: research a topic and produce output.

        Args:
            topic: The research topic or question
            output_format: 'report' | 'blog' | 'slides'

        Returns:
            Dict with generated content and metadata
        """
        self.topic = topic
        print(f"\n🤖 Starting autonomous research on: '{topic}'")
        print("=" * 60)

        # Step 1: Search for relevant URLs
        print("\n🔍 Step 1: Searching the internet...")
        urls = self.scraper.search(topic, num_results=self.max_sources)
        print(f"   Found {len(urls)} sources")

        # Step 2: Scrape and read articles
        print("\n📰 Step 2: Reading articles...")
        articles = []
        for i, url in enumerate(urls, 1):
            print(f"   [{i}/{len(urls)}] Scraping: {url[:60]}...")
            article = self.scraper.scrape(url)
            if article and article.get("content"):
                articles.append(article)
                print(f"   ✅ Extracted {len(article['content'])} chars")
            else:
                print(f"   ⚠️  Skipped (no content)")
            time.sleep(1)

        print(f"\n   Successfully read {len(articles)} articles")

        # Step 3: Summarize each article
        print("\n✍️  Step 3: Summarizing content with LLM...")
        summaries = []
        for i, article in enumerate(articles, 1):
            print(f"   [{i}/{len(articles)}] Summarizing: {article['title'][:50]}...")
            summary = self.summarizer.summarize_article(article, topic)
            if summary:
                summaries.append(summary)
                article["summary"] = summary

        # Step 4: Store in vector DB
        print("\n🗄️  Step 4: Storing in vector database...")
        self.vector_store.add_documents(articles)
        print(f"   Stored {len(articles)} documents")

        # Step 5: Generate synthesis
        print("\n🧠 Step 5: Synthesizing research findings...")
        synthesis = self.summarizer.synthesize(topic, summaries)

        # Step 6: Generate output
        print(f"\n📄 Step 6: Generating {output_format}...")
        context = {
            "topic": topic,
            "articles": articles,
            "summaries": summaries,
            "synthesis": synthesis,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "source_count": len(articles),
        }

        output = self.report_generator.generate(context, output_format)
        print("\n✅ Research complete!")

        return {
            "topic": topic,
            "output_format": output_format,
            "content": output,
            "metadata": {
                "sources": [a["url"] for a in articles],
                "source_count": len(articles),
                "session_id": self.session_id,
                "timestamp": context["timestamp"],
            },
        }

    def ask(self, question: str) -> str:
        """Ask a follow-up question using vector DB (RAG)."""
        if not self.vector_store.has_documents():
            return "No research data available. Run research() first."
        relevant_chunks = self.vector_store.search(question, top_k=5)
        context_text = "\n\n".join([c["content"] for c in relevant_chunks])
        return self.summarizer.answer_question(question, context_text, self.topic)

    def save_output(self, result: Dict, output_dir: str = "outputs") -> str:
        """Save research output to file."""
        os.makedirs(output_dir, exist_ok=True)
        fmt = result["output_format"]
        ext = {"report": "md", "blog": "md", "slides": "html"}.get(fmt, "md")
        filename = f"{output_dir}/{self.session_id}_{fmt}.{ext}"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result["content"])
        meta_file = f"{output_dir}/{self.session_id}_metadata.json"
        with open(meta_file, "w") as f:
            json.dump(result["metadata"], f, indent=2)
        print(f"\n💾 Output saved to: {filename}")
        return filename
