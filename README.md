# InterviewrAI 🎯

An intelligent AI-powered technical interview system built with LangGraph and Python. The system conducts adaptive technical interviews, evaluates candidates in real-time, and generates comprehensive reports.

## How It Works 🔄

The interview follows this workflow:

1. **Introduction**: AI greets candidate and asks about experience
2. **Question Generation**: AI generates relevant technical questions based on:
   - Role and technologies
   - Candidate's experience level
   - Previous performance
3. **Answer Collection**: Candidate provides answers
4. **Evaluation**: AI evaluates answer accuracy and quality
5. **Feedback**: AI provides constructive feedback
6. **Continue/End Decision**: Interview continues or ends based on:
   - Maximum questions reached (default: 10)
   - Too many consecutive wrong answers (default: 3)
   - Minimum questions asked (default: 3)
7. **Report Generation**: Comprehensive report saved to `outputs/reports/`

## Interview Rules 📋

- **Max Questions**: 10 questions (configurable)
- **Early Termination**: Interview ends if candidate gets 3 consecutive answers wrong
- **Minimum Questions**: At least 3 questions are asked before early termination
- **Adaptive Difficulty**: Questions adjust based on performance

## Configuration ⚙️

Edit `src/config/settings.py` to customize:

```python
MAX_QUESTIONS = 10              # Maximum questions per interview
MAX_CONSECUTIVE_WRONG = 3       # End after this many wrong in a row
MIN_QUESTIONS = 3               # Minimum questions before early end
```

## Report Format 📊

Generated reports include:

1. **Candidate Summary**: Role, experience, technologies
2. **Interview Overview**: Total questions, performance metrics
3. **Performance Analysis**: Detailed breakdown
4. **Strengths**: What the candidate did well
5. **Areas for Improvement**: Constructive feedback
6. **Technical Competency Assessment**: Overall evaluation
7. **Recommendation**: Hiring recommendation

Reports are saved as `.txt` files in `outputs/reports/` with timestamps.

## Advanced Usage 🔧

### Programmatic Usage

```python
from src.agent.graph import run_interview

# Run interview programmatically
final_state, report = run_interview(
    role="Python Developer",
    languages=["Python", "Django", "PostgreSQL"],
    level="intermediate"
)

print(f"Score: {final_state['correct_answers']}/{final_state['current_question_count']}")
```

### Custom LLM Configuration

You can switch between OpenAI and Anthropic models by modifying your `.env`:

```env
# For OpenAI
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4-turbo-preview

# For Anthropic
MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
MODEL_NAME=claude-3-5-sonnet-20241022
```

## File Structure Details 📄

### Core Components

- **state.py**: Defines `InterviewState` TypedDict with all interview data
- **nodes.py**: Individual graph nodes (ask experience, generate questions, evaluate, etc.)
- **graph.py**: LangGraph workflow orchestration
- **prompts.py**: All AI prompts for different stages
- **report_generator.py**: Report generation and file saving logic
- **settings.py**: Configuration and LLM initialization

### Creating Empty **init**.py Files

Don't forget to create empty `__init__.py` files:

```bash
touch src/__init__.py
touch src/agent/__init__.py
touch src/utils/__init__.py
touch src/config/__init__.py
```

## Dependencies 📦

- **langgraph**: Workflow orchestration
- **langchain**: LLM framework
- **langchain-openai**: OpenAI integration
- **langchain-anthropic**: Anthropic integration
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation

## Troubleshooting 🔧

### Common Issues

**1. API Key Error**

```
❌ Error: No API key found!
```

Solution: Create `.env` file with your API key

**2. Import Errors**

```
ModuleNotFoundError: No module named 'src'
```

Solution: Ensure you're running from the project root and `__init__.py` files exist

**3. Model Not Found**

```
Error: Model not available
```

Solution: Check your MODEL_NAME in `.env` matches available models

## Example Output 📝

```
🎯 INTERVIEWR AI - Technical Interview System
================================================================================

Role: Python Developer
Languages/Technologies: Python, FastAPI
Level: intermediate

================================================================================

🤖 Interviewer: Hello! I'm excited to interview you today for the Python
Developer position. To get started, could you tell me about your experience
with Python and FastAPI?

👤 You: I have 3 years of experience with Python...

🤖 Interviewer: Great! Let me ask you a technical question...

[Interview continues...]

================================================================================
📊 Generating Interview Report...
================================================================================

✅ Report saved to: outputs/reports/interview_report_python_developer_20241004_143022.txt

📈 Final Score: 7/10 correct

✅ Interview Complete!
```

## Contributing 🤝

Feel free to fork this project and customize it for your needs!

## License 📄

MIT License - feel free to use this for personal or commercial projects.

## Future Enhancements 🚀

Potential improvements:

- Web interface with Flask/FastAPI
- Multiple interview sessions
- Resume parsing and analysis
- Video interview integration
- Multi-language support
- Database storage for results
- Analytics dashboard
- Team collaboration features

## Support 💬

For issues or questions, please open an issue on GitHub.

---

**Happy Interviewing! 🎉** Features ✨

- **Adaptive Interviewing**: AI adjusts questions based on candidate's experience and performance
- **Real-time Evaluation**: Immediate feedback on each answer
- **Smart Termination**: Ends interview early if candidate struggles (3 consecutive wrong answers)
- **Comprehensive Reports**: Detailed analysis saved as text files
- **Flexible Configuration**: Support for OpenAI or Anthropic models
- **Multi-technology Support**: Interview for any programming language or technology stack

## Project Structure 📁

```
interviewr-ai/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── state.py          # Interview state management
│   │   ├── nodes.py          # Graph node implementations
│   │   └── graph.py          # LangGraph workflow
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── prompts.py        # AI prompts
│   │   └── report_generator.py  # Report generation
│   └── config/
│       ├── __init__.py
│       └── settings.py       # Configuration
├── outputs/
│   └── reports/              # Generated interview reports
├── main.py                   # Entry point
├── requirements.txt
└── README.md
```

## Installation 🚀

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd interviewr-ai
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:

```env
# Choose your provider (openai or anthropic)
MODEL_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4-turbo-preview

# OR Anthropic Configuration
# MODEL_PROVIDER=anthropic
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# MODEL_NAME=claude-3-5-sonnet-20241022
```

## Usage 💻

### Basic Usage

Run the interview agent:

```bash
python main.py
```

You'll be prompted to enter:

- **Role**: e.g., "Python Developer", "Full Stack Engineer"
- **Languages/Technologies**: e.g., "Python, Django, REST API"
- **Level**: beginner, intermediate, or advanced

### Example Session

```
📋 Role: Python Developer
💻 Languages/Technologies: Python, FastAPI, PostgreSQL
📊 Level: intermediate

🤖 Interviewer: Hello! Welcome to this technical interview...
👤 You: I have 3 years of experience...

🤖 Interviewer: Can you explain how async/await works in Python?
👤 You: [Your answer here]
```

##
