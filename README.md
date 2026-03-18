# BrainBoost - Smart Study Analyser

A Streamlit app to track student study efficiency and productivity with visualizations and AI-powered revision/practice tools.

## Features

- User login with name, branch, course
- Log study sessions with date, hours, and topic
- Dashboard with visualizations:
  - Monthly study hours trend
  - Topic distribution
  - Metrics: total hours, current streak, consistency percentage
- AI-powered revision and practice question generation using Ollama (local LLM)

## Setup

1. Install dependencies: `pip install -r requirements.txt`

2. **Install Ollama (Free and Open-Source AI):**
   - Download and install Ollama from [https://ollama.com/](https://ollama.com/)
   - Open a terminal and run: `ollama pull llama3.2` (this downloads the Llama 3.2 model locally)
   - Alternatively, you can use other models like `ollama pull mistral` or `ollama pull llama2`

3. **Configure the App:**
   - Run the app: `streamlit run app.py`
   - Go to Settings in the app and set API Key to `ollama` (or any dummy value, as it's not used for local setup)

4. Ensure Ollama is running in the background when using AI features.

## Usage

- Login with your details
- Log your study sessions
- View your progress on the dashboard
- Use Revision/Practice sections for AI-generated questions

## Troubleshooting

- Ensure Python 3.7+ is installed
- For AI features, Ollama must be installed and running with a pulled model
- Data is stored locally in SQLite database
- If AI doesn't work, check that Ollama is running: `ollama serve`