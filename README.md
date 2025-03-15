# AI Content Generator

A Streamlit application that creates platform-optimized content for LinkedIn, Twitter (X), and WhatsApp based on your insights, using AI-powered text and image generation.

![AI Content Generator](https://img.shields.io/badge/AI-Content%20Generator-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)
![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-412991)

## ✨ Features

- **Multi-Platform Content Generation**: Create optimized content for LinkedIn, Twitter, and WhatsApp in one go
- **Persona-Based Content**: Choose from pre-defined personas or create your own custom persona
- **Tone Selection**: Select from different tones to match your content style
- **AI-Powered Visuals**: Generate custom images for LinkedIn Reels and WhatsApp posts using DALL-E
- **Easy Copy & Download**: One-click copy for text content and download for images

## 🚀 Live Demo

Access the live app: [AI Content Generator on Streamlit Cloud](https://ai-content-generator.streamlit.app/) (Link will be active once deployed)

## 📱 Platform-Specific Content

- **LinkedIn**:
  - Thoughtful, professional posts optimized for engagement
  - 3-slide visual story for LinkedIn Reels with consistent visual style

- **Twitter (X)**:
  - Punchy, high-engagement tweets under character limit
  - Optimized for virality and engagement

- **WhatsApp**:
  - Eye-catching image for instant sharing
  - Conversational message with proper formatting for maximum readability

## 🛠️ Requirements

- Python 3.7+
- OpenAI API key
- Required packages (see requirements.txt)

## 🔧 Installation & Local Development

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ai-content-generator.git
cd ai-content-generator
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:
```bash
streamlit run content_generator.py
```

## 🧙‍♂️ How to Use

1. Enter your OpenAI API key in the sidebar (it's only used for the current session and not stored)
2. Input your topic or insight (e.g., "AI in Healthcare," "Future of FinTech")
3. Select a persona:
   - Ogilvy-style storyteller
   - Data-Driven Strategist
   - Tech Visionary
   - Savage Satirist
   - Or create your own custom persona
4. Choose your tone:
   - Sarcastic
   - Professional
   - Casual
5. Click "Generate Content"
6. Copy the generated text content and download images for each platform

## 🚀 Deployment on Streamlit Cloud

This app is ready to be deployed on Streamlit Cloud. Simply:

1. Fork this repository to your GitHub account
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and select this repository
4. Set the main file path to `content_generator.py`
5. Deploy!

Note: You'll still need to provide your OpenAI API key when using the deployed app.

## 🔒 Security Note

Your OpenAI API key is only used for the current session and is not stored anywhere. All content generation happens through the OpenAI API directly.

## 📄 License

This project is licensed under the MIT License.

## 👏 Acknowledgements

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI's GPT and DALL-E](https://openai.com/)
- Made with ❤️ for content creators and marketers 