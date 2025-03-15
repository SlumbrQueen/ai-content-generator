import streamlit as st
import io
from PIL import Image
import base64
import os
from dotenv import load_dotenv
import requests
import json
from requests.exceptions import RequestException

# Load environment variables from .env file (if available)
load_dotenv()

def main():
    # Set page title and configuration
    st.set_page_config(
        page_title="Mandala Art Generator",
        page_icon="🔄",
        layout="centered"
    )

    # Add custom CSS for styling
    st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
        max-width: 900px;
        margin: 0 auto;
    }
    .title-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    .subheader {
        color: #888;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #7E57C2;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .download-btn {
        text-align: center;
        margin-top: 1rem;
    }
    footer {
        text-align: center;
        margin-top: 3rem;
        color: #888;
    }
    .mandala-type {
        margin-top: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="title-container">', unsafe_allow_html=True)
    st.title("✨ Mandala Art Generator")
    st.markdown('<p class="subheader">Create beautiful mandala art inspired by Buddhism and Hinduism</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Sidebar for API key
    with st.sidebar:
        st.title("Settings")
        api_key = st.text_input("Enter your OpenAI API Key", 
                             value=os.getenv("OPENAI_API_KEY", ""),
                             type="password",
                             help="Your API key is stored only for the current session")
        
        st.divider()
        st.markdown("### About")
        st.info("""
        This app generates mandala art using OpenAI's DALL-E API. 
        It requires an API key to function.
        
        Mandalas are sacred geometric figures that represent the universe in 
        Hindu and Buddhist symbolism.
        """)

    # Check if API key is provided
    if not api_key:
        st.warning("Please enter your OpenAI API key in the sidebar to use this app.")
        st.stop()

    # Input section
    st.markdown("### Enter a word for inspiration")
    input_word = st.text_input("Enter a single word:", max_chars=20)
    
    # Validate input
    if input_word and len(input_word.split()) > 1:
        st.error("Please enter only a single word.")
        input_word = ""

    # Mandala type selection
    st.markdown('<div class="mandala-type">', unsafe_allow_html=True)
    st.markdown("### Select Mandala Type")
    mandala_type = st.radio(
        "Choose a style:",
        options=[
            "Black and White Mandala",
            "Color Mandala",
            "New Age Mandala"
        ],
        horizontal=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Generate button
    generate_button = st.button("Generate Mandala", use_container_width=True)

    # Store the generated image in session state
    if "generated_image" not in st.session_state:
        st.session_state.generated_image = None
    
    # Generate image when button is clicked
    if generate_button and input_word:
        with st.spinner(f"Creating your '{input_word}'-inspired mandala..."):
            try:
                prompt = create_prompt(input_word, mandala_type)
                image_url = generate_image_direct(api_key, prompt)
                st.session_state.generated_image = image_url
            except Exception as e:
                st.error(f"Error generating image: {str(e)}")
    
    # Display generated image
    if st.session_state.generated_image:
        st.subheader(f"Your '{input_word}'-inspired Mandala:")
        st.image(st.session_state.generated_image, use_container_width=True)
        
        # Download button
        image_data = download_image(st.session_state.generated_image)
        if image_data:
            st.markdown('<div class="download-btn">', unsafe_allow_html=True)
            st.download_button(
                label="Download Mandala",
                data=image_data,
                file_name=f"mandala_{input_word}.png",
                mime="image/png"
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown('<footer>Created with ❤️ | Powered by OpenAI DALL-E</footer>', unsafe_allow_html=True)

def create_prompt(word, mandala_type):
    """Create a prompt for the image generation based on input and type."""
    base_prompt = f"A sacred mandala with a central '{word}' figure or image as the main focal point. The '{word}' should be clearly depicted and recognizable in the center of the design"
    
    if mandala_type == "Black and White Mandala":
        return f"{base_prompt}. Create a detailed black and white mandala with a '{word}' as the central figure/element that is clearly visible and detailed (like a dragon in the center of a mandala). Pure black and white, high contrast, intricate symmetric geometric design surrounding the central '{word}' in the style of traditional Buddhist mandalas. Detailed pen and ink drawing style with concentric circles and patterns radiating outward from the '{word}' in the center. The '{word}' must be the main focus and clearly identifiable."
    
    elif mandala_type == "Color Mandala":
        return f"{base_prompt}. Create a colorful vibrant mandala with a '{word}' as the prominently displayed central element (like having a detailed '{word}' in the center of the design). Use colors that relate to the nature of '{word}'. The mandala should have concentric rings, geometric patterns, and perfect radial symmetry surrounding and emanating from the central '{word}'. The '{word}' should be unmistakably recognizable as the main subject and focal point."
    
    elif mandala_type == "New Age Mandala":
        return f"{base_prompt}. Create a modern digital interpretation of a mandala with a '{word}' as the clearly depicted central element. The '{word}' should be detailed and recognizable at the center, with glowing elements and sacred geometry patterns radiating outward from it. Include fractal patterns that follow radial symmetry from the central '{word}'. The '{word}' must be unmistakably the main subject and focal point, not abstract."
    
    return base_prompt

def generate_image_direct(api_key, prompt):
    """Generate an image by directly calling the OpenAI API without using the Python client."""
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "prompt": prompt,
        "model": "dall-e-3",
        "n": 1,
        "size": "1024x1024",
        "quality": "standard"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        result = response.json()
        return result["data"][0]["url"]
    except RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except (KeyError, IndexError) as e:
        raise Exception(f"Unexpected API response format: {str(e)}")

def download_image(image_url):
    """Download image from URL and return as bytes for the download button."""
    try:
        response = requests.get(image_url)
        return response.content
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

if __name__ == "__main__":
    main() 