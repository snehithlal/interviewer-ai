#!/usr/bin/env python3
"""
InterviewerAI - AI-Powered Technical Interview Agent
Main entry point for running interviews
"""

from src.agent.graph import run_interview
from src.config.settings import settings

def main():
    """Main function to start the interview"""

    # Check for API keys
    if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
        print("❌ Error: No API key found!")
        print("\nPlease set up your .env file with either:")
        print("  OPENAI_API_KEY=your_key_here")
        print("  or")
        print("  ANTHROPIC_API_KEY=your_key_here")
        print("\nYou can also specify MODEL_PROVIDER (openai or anthropic)")
        return

    print("\n" + "="*80)
    print("🚀 Welcome to InterviewerAI!")
    print("="*80)

    # Get interview parameters
    print("\nPlease provide the interview details:\n")

    role = input("📋 Role (e.g., Python Developer, Full Stack Engineer): ").strip()
    if not role:
        role = "Software Developer"

    languages_input = input("💻 Languages/Technologies (comma-separated, e.g., Python, Django, REST API): ").strip()
    if not languages_input:
        languages = ["Python"]
    else:
        languages = [lang.strip() for lang in languages_input.split(",")]

    level = input("📊 Level (beginner/intermediate/advanced): ").strip().lower()
    if level not in ["beginner", "intermediate", "advanced"]:
        level = "intermediate"

    # Run the interview
    try:
        final_state, report = run_interview(role, languages, level)

        print(f"\n🎉 Thank you for using InterviewerAI!")
        print(f"📈 Final Score: {final_state['correct_answers']}/{final_state['current_question_count']} correct")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interview interrupted by user.")
        print("Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()