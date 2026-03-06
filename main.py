"""
🤖 Autonomous Research Agent - CLI Entry Point
Run the research agent from the command line.

Usage:
    python main.py --topic "AI in healthcare" --format report
    python main.py --topic "Quantum computing" --format blog
    python main.py --topic "Climate change solutions" --format slides --sources 10
"""

import argparse
import sys
import os
from agent import ResearchAgent


def parse_args():
    parser = argparse.ArgumentParser(
        description="🤖 Autonomous Research Agent - AI-powered research automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --topic "Impact of AI on healthcare"
  python main.py --topic "Quantum computing advances" --format blog
  python main.py --topic "Climate change" --format slides --sources 10
  python main.py --topic "Space exploration" --format report --output ./my_outputs

Output formats:
  report  - Formal academic research paper (Markdown)
  blog    - Engaging blog post (Markdown)
  slides  - HTML presentation with Reveal.js
        """
    )

    parser.add_argument(
        "--topic", "-t",
        required=True,
        help="Research topic or question"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["report", "blog", "slides"],
        default="report",
        help="Output format: report | blog | slides (default: report)"
    )
    parser.add_argument(
        "--sources", "-s",
        type=int,
        default=8,
        help="Number of internet sources to use (default: 8)"
    )
    parser.add_argument(
        "--output", "-o",
        default="outputs",
        help="Output directory (default: ./outputs)"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--ollama",
        action="store_true",
        help="Use local Ollama instead of OpenAI"
    )
    parser.add_argument(
        "--ollama-model",
        default="llama3.2",
        help="Ollama model name (default: llama3.2)"
    )
    parser.add_argument(
        "--ask", "-a",
        help="Ask a follow-up question after research (optional)"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # ── Configure LLM Backend ──────────────────────────────
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key

    if args.ollama:
        os.environ["USE_OLLAMA"] = "true"
        os.environ["OLLAMA_MODEL"] = args.ollama_model
        print(f"🦙 Using Ollama with model: {args.ollama_model}")
    elif not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OpenAI API key required.")
        print("   Set OPENAI_API_KEY environment variable or use --api-key flag.")
        print("   Or use --ollama flag for local Ollama inference.")
        sys.exit(1)

    # ── Run Research ──────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  🤖 AUTONOMOUS RESEARCH AGENT")
    print(f"{'='*60}")
    print(f"  Topic: {args.topic}")
    print(f"  Format: {args.format}")
    print(f"  Sources: {args.sources}")
    print(f"{'='*60}\n")

    config = {"max_sources": args.sources}
    agent = ResearchAgent(config=config)

    result = agent.research(args.topic, output_format=args.format)

    # ── Save Output ───────────────────────────────────────
    output_file = agent.save_output(result, output_dir=args.output)

    # ── Display Summary ───────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  📊 RESEARCH SUMMARY")
    print(f"{'='*60}")
    print(f"  Topic: {args.topic}")
    print(f"  Sources Analyzed: {result['metadata']['source_count']}")
    print(f"  Output Format: {args.format}")
    print(f"  Saved to: {output_file}")
    print(f"{'='*60}")

    # ── Handle Follow-up Question ─────────────────────────
    if args.ask:
        print(f"\n💬 Follow-up Question: {args.ask}")
        print("-" * 40)
        answer = agent.ask(args.ask)
        print(answer)

    # ── Interactive Mode ──────────────────────────────────
    print("\n💬 Enter follow-up questions (or 'quit' to exit):")
    while True:
        try:
            question = input("\n❓ Question: ").strip()
            if question.lower() in ("quit", "exit", "q", ""):
                break
            answer = agent.ask(question)
            print(f"\n📖 Answer:\n{answer}")
        except (KeyboardInterrupt, EOFError):
            break

    print("\n👋 Research session complete!")


if __name__ == "__main__":
    main()
