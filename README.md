# Mandala Art Generator

A Streamlit application that generates beautiful mandala art using OpenAI's DALL-E API.

## Live Demo

You can access the deployed app at [Mandala Art Generator](https://mandala-art-generator.streamlit.app) (link will be active after deployment)

## Description

This application allows users to generate different styles of mandala art by providing a single word as inspiration. The app integrates with OpenAI's DALL-E to create beautiful mandalas inspired by the spiritual traditions of Buddhism and Hinduism.

## Features

- Generate three types of mandala art:
  - Black and White Mandala: Simple, elegant design
  - Color Mandala: Vibrant, colorful version
  - New Age Mandala: Modern interpretation with digital art elements
- Single word input for inspiration
- Secure API key input
- Download generated images

## Setup Instructions for Local Development

1. Clone this repository
   ```bash
   git clone https://github.com/YourUsername/mandala-art-generator.git
   cd mandala-art-generator
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # On Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Deployment on Streamlit Cloud

This app is ready to be deployed on Streamlit Cloud:

1. Fork or push this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select this repository, branch (main) and file (app.py)
6. Deploy!

Note: Users will need to provide their own OpenAI API key when using the deployed application.

## Requirements

- Python 3.10+
- Streamlit
- OpenAI API key
- Git

## Usage

1. Enter your OpenAI API key in the sidebar
2. Type a single word as inspiration
3. Select the type of mandala you want to generate
4. Click the "Generate Mandala" button
5. Download the generated image if desired

## Privacy Note

Your OpenAI API key is used only for the current session and is not stored permanently. 