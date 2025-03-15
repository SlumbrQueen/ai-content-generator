# ✨ Prompt Enhancer - Streamlit App

A modern, user-friendly application to transform your basic ideas into powerful AI prompts. Built with Streamlit for a seamless web-based interface.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://prompt-enhancer.streamlit.app)

## Features

- **Modern UI**: Clean, Apple-inspired interface with Poppins font
- **Persona Selection**: Choose from pre-defined AI roles (Techie, Content Genius, Teacher)
- **Clarifying Questions**: Interactive process to improve your prompt
- **Enhanced Prompts**: Optimized for AI models like GPT-4
- **Copy to Clipboard**: Easily copy your enhanced prompt
- **Open in ChatGPT**: Direct integration with ChatGPT

## Requirements

- Python 3.6+
- OpenAI API key

## Installation

1. Clone this repository:
```bash
git clone https://github.com/SlumbrQueen/Prompt-Enhancer.git
cd Prompt-Enhancer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the App

Simply run:

```bash
streamlit run streamlit_app.py
```

The app will open in your default web browser.

## Using the App

1. Enter your OpenAI API key (required for the app to function)
2. Choose a persona or define a custom AI role
3. Fill in the prompt components:
   - **Context**: Background information about your situation
   - **AI Role**: What role the AI should assume
   - **Task**: What you want the AI to do
   - **Output Format**: How you want the response structured
   - **Additional Notes** (optional): Any extra information

4. Click "Generate Enhanced Prompt"

5. If the app needs more information, it will ask clarifying questions
   - Answer the questions and click "Submit Answers"

6. View and use your enhanced prompt:
   - Copy to clipboard
   - Open directly in ChatGPT
   - Reset to start over

## Deploying on Streamlit Cloud

This application is ready to be deployed on Streamlit Cloud:

1. Fork this repository to your GitHub account
2. Sign up for [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app, pointing to your forked repository
4. Set the main file path to `streamlit_app.py`

Note: Users will need to provide their own OpenAI API key when using the deployed application.

## Privacy Note

Your API key is used only for the current session and is not stored permanently. All processing is done securely via the OpenAI API. 