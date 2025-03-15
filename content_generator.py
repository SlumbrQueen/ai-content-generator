import streamlit as st
import openai
import requests
import io
import base64
import os
import re
import json
from PIL import Image
from datetime import datetime
import html

# Prevent OpenAI from trying to use system proxies
os.environ['NO_PROXY'] = '*'

# Disable requests SSL verification if needed
# requests.packages.urllib3.disable_warnings()
# os.environ['PYTHONHTTPSVERIFY'] = '0'

# Global variable for LinkedIn style guide consistency
linkedin_style_guide = ""

# Page configuration
st.set_page_config(
    page_title="AI Content Generator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App styling
st.markdown("""
<style>
    .app-header {
        text-align: center;
        padding: 1.5rem 0;
        border-bottom: 1px solid #f0f2f5;
        margin-bottom: 2rem;
    }
    .app-header h1 {
        color: #1E3A8A;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .app-header p {
        color: #4B5563;
        font-size: 1.1rem;
    }
    .content-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
    }
    .platform-header {
        font-size: 1.3rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E5E7EB;
    }
    .platform-icon {
        margin-right: 0.5rem;
        vertical-align: middle;
    }
    .content-display {
        background: #F9FAFB;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1E3A8A;
    }
    .action-button {
        background-color: #1E3A8A;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    .action-button:hover {
        background-color: #1E40AF;
    }
    .copy-btn {
        background-color: #10B981;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        cursor: pointer;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    .copy-btn:hover {
        background-color: #059669;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .copy-btn:active {
        transform: translateY(0);
        box-shadow: none;
    }
    .hidden-content {
        display: none;
        visibility: hidden;
        position: absolute;
        left: -9999px;
    }
    .whatsapp-message {
        background-color: #DCF8C6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .linkedin-message {
        background-color: #E7F3FF;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .twitter-message {
        background-color: #F0F5FF;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .required-field::after {
        content: " *";
        color: red;
    }
    .stButton > button {
        width: 100%;
        background-color: #1E3A8A;
        color: white;
        padding: 0.75rem 0;
        font-size: 1.1rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #1E40AF;
    }
    .step-number {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: #1E3A8A;
        color: white;
        text-align: center;
        line-height: 30px;
        margin-right: 10px;
    }
    div[data-testid="stSidebar"] > div:first-child {
        background-color: #F8FAFC;
    }
    .api-notice {
        font-size: 0.8rem;
        font-style: italic;
        color: #6B7280;
        margin-top: 0.25rem;
    }
</style>

<!-- Clipboard JS functionality -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded, initializing copy buttons');
    
    // Function to handle the actual copy operation
    function copyTextToClipboard(text, button) {
        console.log('Attempting to copy text: ', text.substring(0, 30) + '...');
        
        // Try using the modern Clipboard API first
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text)
                .then(() => {
                    console.log('Copy successful with Clipboard API');
                    updateButtonFeedback(button, true);
                })
                .catch(err => {
                    console.error('Clipboard API error: ', err);
                    // Fall back to execCommand method
                    fallbackCopyMethod(text, button);
                });
        } else {
            console.log('Clipboard API not available, using fallback');
            fallbackCopyMethod(text, button);
        }
    }
    
    // Fallback copy method using execCommand
    function fallbackCopyMethod(text, button) {
        try {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            
            // Make the textarea invisible but keep it in the document flow
            textarea.style.position = 'fixed';
            textarea.style.opacity = 0;
            textarea.style.pointerEvents = 'none';
            textarea.style.left = '0';
            textarea.style.top = '0';
            
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();
            
            const successful = document.execCommand('copy');
            document.body.removeChild(textarea);
            
            if (successful) {
                console.log('Fallback copy method succeeded');
                updateButtonFeedback(button, true);
            } else {
                console.log('Fallback copy method failed');
                updateButtonFeedback(button, false);
            }
        } catch (err) {
            console.error('Fallback copy error: ', err);
            updateButtonFeedback(button, false);
        }
    }
    
    // Update button to provide user feedback
    function updateButtonFeedback(button, success) {
        const originalText = button.textContent || button.innerText;
        
        if (success) {
            button.innerText = 'Copied!';
            button.style.backgroundColor = '#059669';
        } else {
            button.innerText = 'Copy failed';
            button.style.backgroundColor = '#DC2626';
        }
        
        setTimeout(() => {
            button.innerText = originalText;
            button.style.backgroundColor = '';
        }, 2000);
    }
    
    // Add global click event listener for copy buttons
    document.body.addEventListener('click', function(event) {
        // Find if the clicked element or any of its parents is a copy button
        let target = event.target;
        while (target && !target.classList.contains('copy-btn')) {
            target = target.parentElement;
        }
        
        // If we found a copy button
        if (target && target.classList.contains('copy-btn')) {
            event.preventDefault();
            
            console.log('Copy button clicked');
            const contentId = target.getAttribute('data-content-id');
            console.log('Looking for content with ID:', contentId);
            
            if (!contentId) {
                console.error('No content ID found on button');
                updateButtonFeedback(target, false);
                return;
            }
            
            const contentElement = document.getElementById(contentId);
            
            if (!contentElement) {
                console.error('Content element not found with ID:', contentId);
                updateButtonFeedback(target, false);
                return;
            }
            
            const textToCopy = contentElement.innerText || contentElement.textContent;
            
            if (!textToCopy || textToCopy.trim() === '') {
                console.error('No text content found to copy');
                updateButtonFeedback(target, false);
                return;
            }
            
            copyTextToClipboard(textToCopy, target);
        }
    });
    
    console.log('Copy button initialization complete');
});

// Add this to ensure the script runs even if Streamlit reruns the app
if (window.frameElement) {
    // We're in an iframe
    setTimeout(() => {
        console.log('Delayed clipboard initialization for iframe');
        const event = new Event('DOMContentLoaded');
        document.dispatchEvent(event);
    }, 1000);
}
</script>

<script>
// This second script handles the case where Streamlit's iframe might be reloaded
window.addEventListener('load', function() {
    setTimeout(() => {
        const copyButtons = document.querySelectorAll('.copy-btn');
        if (copyButtons.length > 0) {
            console.log('Found', copyButtons.length, 'copy buttons after page load');
            const event = new Event('DOMContentLoaded');
            document.dispatchEvent(event);
        }
    }, 1500);
});
</script>
""", unsafe_allow_html=True)

# Function to sanitize text for safe display and processing
def sanitize_text(text):
    if text is None:
        return ""
    # Replace problematic Unicode characters with ASCII equivalents
    text = text.replace('\u2019', "'")  # Right single quotation mark
    text = text.replace('\u2018', "'")  # Left single quotation mark
    text = text.replace('\u201C', '"')  # Left double quotation mark
    text = text.replace('\u201D', '"')  # Right double quotation mark
    text = text.replace('\u2013', '-')  # En dash
    text = text.replace('\u2014', '--')  # Em dash
    text = text.replace('\u2026', '...')  # Ellipsis
    
    # Remove any remaining non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    return text

def main():
    # App header
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.markdown('<h1>✨ AI Content Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p>Generate platform-optimized content for LinkedIn, Twitter, and WhatsApp</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Settings")
        
        # API Key input
        api_key = st.text_input("OpenAI API Key", type="password", help="Required for generating content and images")
        st.markdown('<p class="api-notice">Your API key is not stored and is only used for this session</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Instructions
        st.subheader("📝 How to use")
        st.markdown("""
        <div>
            <p><span class="step-number">1</span> Enter your OpenAI API key</p>
            <p><span class="step-number">2</span> Input your topic or insight</p>
            <p><span class="step-number">3</span> Select persona and tone</p>
            <p><span class="step-number">4</span> Click "Generate Content"</p>
            <p><span class="step-number">5</span> Copy and download your content</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Additional settings
        st.subheader("🎨 Image Style")
        image_style = st.selectbox(
            "Select style for generated images",
            options=["Photorealistic", "Artistic", "Minimalist", "Infographic"],
            index=0
        )
        
        image_quality = st.radio(
            "Image quality",
            options=["Standard", "HD"],
            index=0,
            horizontal=True
        )

    # Main content area - Input section
    st.header("Step 1: Define your content")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<label class="required-field">Topic or Insight</label>', unsafe_allow_html=True)
        topic = st.text_area(
            "",
            placeholder="e.g., 'AI in Healthcare', 'Future of FinTech', or 'Rise of Creator Economy'",
            help="This is the main subject of your content",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("##### Examples")
        st.markdown("""
        - The impact of artificial intelligence on healthcare diagnostics
        - How blockchain is revolutionizing financial services
        - Why the creator economy is changing digital marketing
        """)
    
    # Persona selection
    st.header("Step 2: Choose your voice")
    
    persona_col1, persona_col2 = st.columns(2)
    
    with persona_col1:
        persona_options = {
            "Ogilvy-style storyteller": "Creative mastermind, engaging, cult-like following",
            "Data-Driven Strategist": "Insightful, fact-based, analytical",
            "Tech Visionary": "Futuristic, innovative, cutting-edge",
            "Savage Satirist": "Witty, sharp, no-BS takes"
        }
        
        persona = st.radio(
            "Select a persona",
            options=list(persona_options.keys())
        )
    
    with persona_col2:
        st.markdown(f"##### {persona}")
        st.markdown(f"*{persona_options[persona]}*")
        
        # Custom persona option
        custom_persona = st.text_input(
            "Or create your own persona",
            placeholder="Describe your custom persona",
            help="Leave empty to use the selected persona above"
        )
        
        if custom_persona:
            persona = custom_persona
    
    # Tone selection
    st.header("Step 3: Set the tone")
    
    tone_col1, tone_col2 = st.columns(2)
    
    with tone_col1:
        tone_options = {
            "Sarcastic": "Sharp, witty, cutting humor",
            "Professional": "Insightful, polished, credible",
            "Casual": "Conversational, engaging, easygoing"
        }
        
        tone = st.radio(
            "Select a tone",
            options=list(tone_options.keys())
        )
    
    with tone_col2:
        st.markdown(f"##### {tone}")
        st.markdown(f"*{tone_options[tone]}*")
    
    # Generate button
    generate_placeholder = st.empty()
    
    # Warning for missing fields
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar", icon="⚠️")
    
    # Content generation functions
    def generate_text_content(topic, persona, tone, platform):
        if not api_key:
            st.error("OpenAI API key is required to generate content")
            return None
        
        # Sanitize inputs before sending to API
        sanitized_topic = sanitize_text(topic)
        sanitized_persona = sanitize_text(persona)
        sanitized_tone = sanitize_text(tone)
        
        try:
            # Direct API call without using the client object
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # Define distinctive persona characteristics
            persona_styles = {
                "Ogilvy-style storyteller": {
                    "voice": "captivating storyteller who uses vivid metaphors and emotional appeals",
                    "structure": "narrative arc with a hook, challenge, resolution, and call to action",
                    "signature": "draws powerful analogies and uses sensory language",
                    "examples": ["Once upon a time...", "Picture this:", "Here's the truth nobody's talking about:", "The secret most people miss:"],
                    "data_use": "weaves statistics into compelling narratives, using them as plot points, not the main focus"
                },
                "Data-Driven Strategist": {
                    "voice": "analytical expert who breaks down complex trends with razor-sharp precision",
                    "structure": "thesis, evidence, implications, tactical recommendations",
                    "signature": "uses data to challenge assumptions, references research and case studies",
                    "examples": ["The data reveals something surprising:", "According to new research:", "Three critical insights from the numbers:", "Here's what most analysis gets wrong:"],
                    "data_use": "leads with statistics, contextualizes numbers, compares trends, focuses on implications"
                },
                "Tech Visionary": {
                    "voice": "forward-thinking innovator who sees around corners and challenges conventional thinking",
                    "structure": "bold prediction, supporting signals, implications, call for preparation",
                    "signature": "uses provocative questions, contrasts past/future, speaks in definitive declarations",
                    "examples": ["The next revolution isn't what you think.", "Forget everything you know about [topic].", "By 2025, we won't even recognize today's [topic].", "The future belongs to those who..."],
                    "data_use": "references cutting-edge research, early signals, adoption curves, and emerging trends"
                },
                "Savage Satirist": {
                    "voice": "brutally honest commentator who uses humor and irreverence to cut through BS",
                    "structure": "setup, unexpected punchline, sharp observation, counterintuitive take",
                    "signature": "uses rhetorical questions, cultural references, exaggeration for effect",
                    "examples": ["Let's be honest -", "Hot take:", "Unpopular opinion:", "Am I the only one who thinks...", "The uncomfortable truth about [topic]:"],
                    "data_use": "uses statistics selectively to punctuate arguments or debunk myths, often followed by satirical commentary"
                }
            }
            
            # Define distinctive tone characteristics
            tone_styles = {
                "Sarcastic": {
                    "language": "biting, irreverent, using hyperbole and unexpected twists",
                    "structure": "setup-subversion pattern, where expectations are established then deliberately broken",
                    "examples": ["Oh great, another [topic] expert with all the answers...", "Shocking news: [counterintuitive statement]", "In today's episode of 'Things Nobody Asked For'..."],
                    "punctuation": "..., ?!, *, (eye roll)"
                },
                "Professional": {
                    "language": "clear, articulate, measured, with industry terminology used naturally",
                    "structure": "logical flow with clear transitions and balanced perspective",
                    "examples": ["A critical consideration for professionals:", "Three key implications for the industry:", "What leading organizations are discovering:"],
                    "punctuation": ". , : ; —"
                },
                "Casual": {
                    "language": "conversational, using contractions, colloquialisms, and friendly asides",
                    "structure": "informal, with tangents, personal reflections, and direct reader address",
                    "examples": ["So I've been thinking about [topic] lately...", "OK, hear me out on this one:", "You know that feeling when..."],
                    "punctuation": "..., !, &, +"
                }
            }
            
            # Get the selected persona style, or use a default if custom persona
            selected_persona = persona_styles.get(sanitized_persona, {
                "voice": f"{sanitized_persona}",
                "structure": "tailored to the subject with distinctive viewpoint",
                "signature": "uses specialized language and perspectives specific to their expertise",
                "examples": ["From my perspective:", "Here's what I've observed:", "My take on this:"],
                "data_use": "uses data selectively to support key points when relevant"
            })
            
            # Get the selected tone style
            selected_tone = tone_styles.get(sanitized_tone, tone_styles["Professional"])
            
            # Common content guidelines with more flexibility
            content_guidelines = f"""
            CRITICAL CONTENT REQUIREMENTS:
            
            1. FOCUS ON REAL-WORLD TRENDS FOR THE EXACT TOPIC:
               - Focus EXCLUSIVELY on "{sanitized_topic}" - never default to AI-related content unless the topic is about AI
               - Research and reference real current trends, developments, and insights specific to this exact topic
               - Avoid generic content - find specific, unique insights about this particular subject
               - If the topic is an industry/field, focus on the latest developments, challenges, and innovations in that industry
            
            2. VOICE & PERSONALITY:
               - Write exclusively as a {selected_persona["voice"]} with a {selected_tone["language"]} tone
               - Use {selected_persona["signature"]}
               - Structure content using {selected_persona["structure"]}
               - NEVER use AI-sounding phrases like "Here's the scoop," "Let's dive in," "Here's the kicker," etc.
               - Avoid formulaic transitions and obvious rhetorical devices
            
            3. ADAPT TO TOPIC TYPE INTELLIGENTLY:
               - For leadership/personal topics: Use stories, experiences, and insights over data
               - For trends/insights: Use {selected_persona["data_use"]} 
               - For big ideas/future concepts: Be bold, provocative, and challenge assumptions
               - For practical tips: Make content actionable with clear steps
            
            4. MAKE IT DISTINCTIVELY HUMAN:
               - Write as if speaking to ONE person, never an audience
               - Avoid generic corporate language, platitudes, and robot-like phrasing
               - Include a personal angle - what YOU think, not what "people" think
               - Be willing to take a clear position rather than being neutral on everything
               - Add subtle human imperfections - occasional run-on sentences, short fragments, natural digressions
               - Use varied sentence structure - not repetitive patterns that sound formulaic
               - Keep sentences crisp and direct, with natural flow and rhythm
               
            5. FORMATTING & STYLE:
               - Use {selected_tone["punctuation"]} in a way that feels natural to this voice
               - Break ideas into digestible chunks with line breaks and emphasis
               - Vary sentence length dramatically - mix very short sentences with occasional longer ones
               - Add occasional personal asides or tangents
               - Avoid unnecessary fillers and vague generalizations
               - Speak directly to the reader, not at them
               
            6. END WITH IMPACT:
               - Conclude with something memorable that reflects the specific persona and tone
               - For {sanitized_persona}: end with something that showcases their unique perspective
               - For {sanitized_tone} tone: use the appropriate closing style for this tone
               - Add a personal touch that shows you're a real person with real opinions
               - Avoid clichéd closing lines like "What do you think?" or "Let me know in the comments"
            """
            
            if platform == "linkedin":
                prompt = f"""
                Create a distinctive LinkedIn post about "{sanitized_topic}" that absolutely could ONLY have been written by a {sanitized_persona} with a {sanitized_tone} tone.

                {content_guidelines}
                
                PLATFORM-SPECIFIC GUIDANCE:
                1. Length: 100-200 words 
                2. Include data ONLY IF it fits the selected persona style ({selected_persona["data_use"]})
                3. Structure the post with sufficient white space - never dense paragraphs
                4. Include 1-2 relevant hashtags IF they fit the persona and tone (not forced)
                5. Create a natural ending that invites engagement without sounding formulaic
                
                CRITICAL HUMANIZATION REQUIREMENTS:
                1. Include at least one personal experience, opinion, or viewpoint that makes it feel like a real person wrote it
                2. Start naturally - avoid overused AI phrases like "I'm excited to share," "Here's why," or "Let's talk about"
                3. Include at least one conversational element (rhetorical question, casual aside, etc.) that feels natural
                4. Make sure it doesn't sound overly polished or like marketing copy
                5. Write with confidence and directness - no hedging or unnecessary qualifiers
                
                IMPORTANT: The personality distinction is CRITICAL. A reader should instantly recognize this as coming from a {sanitized_persona}, not a generic writer. Make the {sanitized_tone} tone unmistakable.
                
                AVOID LIKE THE PLAGUE:
                - Clichéd phrases like "Here's the thing," "Let me tell you," "The key takeaway," etc.
                - Obvious AI-generated patterns like "As a [profession], I believe..."
                - Repetitive sentence structures that create a robotic rhythm
                - Unnecessary transitions between ideas that feel mechanical
                
                Use only ASCII characters.
                
                FINAL REMINDER: Ensure your content focuses entirely on {sanitized_topic} and real trends in this field - do NOT default to AI-related content unless the topic is specifically about AI.
                """
                max_tokens = 350
            
            elif platform == "twitter":
                prompt = f"""
                Create a Twitter post about "{sanitized_topic}" that has the UNMISTAKABLE voice of a {sanitized_persona} with a {sanitized_tone} tone.
                
                {content_guidelines}
                
                PLATFORM-SPECIFIC GUIDANCE:
                1. Length: Maximum 280 characters
                2. Start with a punchy, attention-grabbing line that establishes the distinctive voice
                3. Include a surprising insight that fits this specific persona's perspective
                4. Include hashtags ONLY if they feel organic and authentic (max 1-2)
                
                CRITICAL HUMANIZATION REQUIREMENTS:
                1. Make it sound like something typed quickly on a phone, never AI-generated or overly crafted
                2. Include natural text elements without forcing in "IMO", "Tbh" - only if it fits the voice naturally
                3. Avoid perfect sentence structures or overly sophisticated vocabulary
                4. Create a post that sounds like it came from a real person with real opinions
                
                IMPORTANT: This MUST read like it came from a real person with a distinct personality - not a generic social media post. The {sanitized_persona} voice should be instantly recognizable.
                
                AVOID LIKE THE PLAGUE:
                - Clichéd Twitter phrases like "Hot take:" or "Thread:"
                - Obvious AI patterns like "As someone who..."
                - Any hint of formulaic or template-based writing
                
                FINAL REMINDER: Ensure your content focuses entirely on {sanitized_topic} and real trends in this field - do NOT default to AI-related content unless the topic is specifically about AI.
                """
                max_tokens = 200
            
            elif platform == "whatsapp":
                # Keep all the persona and tone customization but update the formatting instructions
                prompt = f"""
                Create a WhatsApp message about "{sanitized_topic}" that follows these specific formatting instructions for high engagement while embodying the personality of a {sanitized_persona} with a {sanitized_tone} tone.
                
                CRITICAL FORMATTING REQUIREMENTS:
                1. Keep it short & punchy (50-100 words maximum)
                2. Make the first two lines attention-grabbing (they show in message preview)
                3. Use frequent line breaks - every 1-2 sentences
                4. Avoid walls of text or big paragraphs
                
                USE THESE WHATSAPP FORMATTING ELEMENTS:
                - Use *asterisks* for bold key points (include the actual * characters)
                - Use _underscores_ for italic emphasis (include the actual _ characters)
                - Use simple emojis strategically for structure (professional but engaging)
                - Create scannable lists with dashes or checkmarks
                - Use hook emojis at the start and end of important sections
                
                STRUCTURE THE MESSAGE LIKE THIS:
                1. Start with an immediate hook - create curiosity or urgency
                2. Include 1-2 bold key points (*like this*)
                3. Add 2-3 short, actionable tips (with line breaks between them)
                4. End with a simple call-to-action question
                
                EXAMPLES OF GOOD CTA ENDINGS:
                - "Reply 'YES' if you agree!"
                - "What's your take? Hit reply and let me know!"
                - "Want more tips? Drop a 👍 and I'll send the next one!"
                
                AVOID LIKE THE PLAGUE:
                - Generic openings like "Hello, hope you're well..."
                - Lengthy paragraphs or walls of text
                - Anything that sounds like a broadcast message
                - AI-generated patterns and clichés
                
                IMPORTANT PERSONALITY ELEMENTS:
                - Keep the distinctive {sanitized_persona} voice with a {sanitized_tone} tone
                - Make it conversational and directed to ONE person
                - Sound like a real person sending a quick message
                - Focus exclusively on "{sanitized_topic}" - no generic content
                
                FINAL REMINDER: Ensure your content focuses entirely on {sanitized_topic} and real trends in this field - do NOT default to AI-related content unless the topic is specifically about AI.
                """
                max_tokens = 300
            
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are an expert writer who creates authentic, human content with highly distinctive voices. Your specialty is capturing unique personalities and tones that feel like real people, never like AI. Include human imperfections, conversational elements, and natural language patterns in your writing. Focus specifically on the user's exact topic and never default to AI-related content unless the topic is specifically about AI."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 1.0  # Increased for more human-like variation and unpredictability
            }
            
            # Ensure the payload is properly encoded as JSON with ASCII only
            json_payload = json.dumps(payload, ensure_ascii=True)
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                data=json_payload,
                verify=True
            )
            
            if response.status_code != 200:
                st.error(f"Error from OpenAI API: {response.text}")
                return None
                
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            
            # Sanitize the response before returning it
            return sanitize_text(content)
            
        except Exception as e:
            st.error(f"Error generating content: {str(e)}")
            return None
    
    def generate_image(prompt, platform):
        if not api_key:
            st.error("OpenAI API key is required to generate images")
            return None
        
        # Sanitize input before sending to API
        sanitized_prompt = sanitize_text(prompt)
        sanitized_persona = sanitize_text(persona)
        sanitized_tone = sanitize_text(tone)
        
        try:
            # Direct API call without using the client object
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            quality = "hd" if image_quality == "HD" else "standard"
            style = image_style.lower()
            
            # Global variable to store the visual style guide for LinkedIn images
            global linkedin_style_guide
            
            if platform == "linkedin":
                # For LinkedIn Reel/Carousel slides
                # Extract slide number from the prompt (e.g., "AI in Healthcare - slide 1/3")
                slide_info = sanitized_prompt.split(" - ")
                main_topic = slide_info[0]
                slide_position = "1"
                if len(slide_info) > 1 and "slide" in slide_info[1]:
                    slide_position = slide_info[1].replace("slide ", "").split("/")[0]
                
                # First slide establishes the visual style for all slides
                if slide_position == "1":
                    # Define the visual style for the entire series
                    style_template_prompt = f"""
                    Create a detailed visual style guide for a series of three LinkedIn images about '{main_topic}'.
                    
                    Define exactly:
                    1. A specific visual style (e.g., cinematic realism, digital painting, cyberpunk, surreal, etc.)
                    2. A specific color palette (3-4 key colors with descriptions)
                    3. The lighting approach (e.g., dramatic side-lighting, soft natural light, etc.)
                    4. Any recurring visual elements or motifs
                    5. The overall mood and atmosphere
                    
                    Make it cohesive and distinctive so all three images will clearly belong together.
                    Keep it brief but specific - no more than 5-6 sentences total.
                    """
                    
                    try:
                        style_guide_payload = {
                            "model": "gpt-4o",
                            "messages": [
                                {"role": "system", "content": "You are a professional art director for visual storytelling campaigns. Create clear, concise style guides that ensure visual consistency across a series of images."},
                                {"role": "user", "content": style_template_prompt}
                            ],
                            "max_tokens": 300,
                            "temperature": 0.7
                        }
                        
                        json_style_payload = json.dumps(style_guide_payload, ensure_ascii=True)
                        
                        style_response = requests.post(
                            "https://api.openai.com/v1/chat/completions",
                            headers=headers,
                            data=json_style_payload,
                            verify=True
                        )
                        
                        if style_response.status_code == 200:
                            style_data = style_response.json()
                            linkedin_style_guide = style_data["choices"][0]["message"]["content"]
                        else:
                            # Fallback if API call fails
                            linkedin_style_guide = f"High-impact {style} style with consistent color palette and mood throughout all images. Maintain identical artistic approach across all visuals."
                    except Exception as e:
                        # Fallback if any exception occurs
                        linkedin_style_guide = f"High-impact {style} style with consistent color palette and mood throughout all images. Maintain identical artistic approach across all visuals."
                
                # Common guidelines for all LinkedIn images to ensure narrative flow and visual consistency
                common_styling = f"""
                CRITICAL STYLING REQUIREMENTS:
                - Follow this exact visual style guide for ALL THREE images:
                {linkedin_style_guide}
                
                IMPORTANT IMAGE GUIDELINES:
                - Create concept-driven, story-focused imagery with NO text, infographics, charts, or data elements
                - The three images MUST look like they were created by the same artist with identical style and technique
                - Use consistent lighting, color palette, and visual treatment across all images
                - Each image should build upon the narrative while maintaining visual consistency
                - Focus on powerful metaphors and symbolism that support the topic
                - Avoid generic stock photo looks - create unique, memorable visuals
                """
                
                # Different prompts based on slide position to create a progressive narrative
                if slide_position == "1":
                    # First slide: Introduction/Problem
                    image_prompt = f"""
                    Create the FIRST in a series of three visually consistent images about '{main_topic}' for a LinkedIn carousel.
                    
                    This first image should introduce the topic by:
                    - Visualizing the main concept, challenge, or current state related to {main_topic}
                    - Using powerful visual storytelling to capture attention and draw viewers in
                    - Creating an emotionally resonant scene that establishes the narrative
                    
                    {common_styling}
                    
                    SPECIFIC IMAGE DIRECTION:
                    Create a compelling, high-impact visual with strong focal points and clear storytelling.
                    Example approach: "A hyper-realistic image showing [specific scene related to the main topic that introduces the concept]"
                    
                    Remember this first image establishes the visual style for the entire series - make it striking and memorable.
                    """
                elif slide_position == "2":
                    # Second slide: Development/Contrast/Transformation
                    image_prompt = f"""
                    Create the SECOND in a series of three visually consistent images about '{main_topic}' for a LinkedIn carousel.
                    
                    This second image should develop the narrative by:
                    - Showing a transformation, contrast, or deeper exploration of {main_topic}
                    - Building on the concept introduced in the first image
                    - Creating a bridge between the problem and solution
                    
                    {common_styling}
                    
                    SPECIFIC IMAGE DIRECTION:
                    Create a visual that advances the story through contrast or transformation.
                    Example approach: "A split-screen or comparative visual showing [specific contrast or transformation related to the topic]"
                    
                    This image MUST maintain perfect visual consistency with the first image in style, colors, and technique.
                    """
                else:
                    # Third slide: Resolution/Outcome/Future
                    image_prompt = f"""
                    Create the THIRD in a series of three visually consistent images about '{main_topic}' for a LinkedIn carousel.
                    
                    This final image should complete the narrative by:
                    - Showing the resolution, outcome, or future state related to {main_topic}
                    - Providing a clear conclusion to the visual story
                    - Leaving viewers with a powerful final impression
                    
                    {common_styling}
                    
                    SPECIFIC IMAGE DIRECTION:
                    Create a visual that brings closure to the narrative through a powerful resolution.
                    Example approach: "A forward-looking scene showing [specific outcome or future state related to the topic]"
                    
                    This final image MUST maintain perfect visual consistency with the previous two images in style, colors, and technique.
                    """
            
            elif platform == "whatsapp":
                # For WhatsApp - a single high-impact, shareable image
                image_prompt = f"""
                Create a single, high-impact visual about '{sanitized_prompt}' optimized for WhatsApp sharing.
                
                CRITICAL REQUIREMENTS:
                - Create a POWERFUL, ATTENTION-GRABBING image that captures the core message of the topic
                - Focus on one strong concept or metaphor that instantly communicates the essence of '{sanitized_prompt}'
                - Use striking composition, bold colors, and strong focal points to make it immediately impactful
                - Create something highly shareable that will stop people from scrolling
                - Avoid ANY text, infographics, or data elements - focus purely on visual storytelling
                
                SPECIFIC IMAGE DIRECTION:
                - Style: Use a {style} visual style with emotional impact
                - Approach: Create a symbolic or metaphorical representation that evokes the right emotion
                - Composition: Use dramatic lighting, perspective, or contrast to create visual interest
                - Example: "A striking [specific visual related directly to the topic] that symbolizes [core concept]"
                
                Make it impossible to ignore - this single image needs to tell the entire story at a glance.
                """
            
            payload = {
                "model": "dall-e-3",
                "prompt": sanitize_text(image_prompt),
                "size": "1024x1024",
                "quality": quality,
                "n": 1
            }
            
            # Ensure the payload is properly encoded as JSON with ASCII only
            json_payload = json.dumps(payload, ensure_ascii=True)
            
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                data=json_payload,
                verify=True
            )
            
            if response.status_code != 200:
                st.error(f"Error from OpenAI API: {response.text}")
                return None
                
            response_data = response.json()
            image_url = response_data["data"][0]["url"]
            image_response = requests.get(image_url)
            image = Image.open(io.BytesIO(image_response.content))
            
            return image
            
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
            return None
    
    def get_download_link(img, filename, text):
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        href = f'<a href="data:image/png;base64,{img_str}" download="{filename}"><button class="copy-btn">{text}</button></a>'
        return href
    
    # Function to create a copy button that references content by ID
    def get_copy_button_for_id(content_id, button_text="Copy Text"):
        return f'''
        <div style="margin-top: 10px;">
            <button class="copy-btn" data-content-id="{content_id}" style="cursor: pointer;">{button_text}</button>
        </div>
        '''
    
    # Function to create a hidden div with content to be copied
    def get_hidden_content_div(content_id, content):
        # Properly escape the content for HTML
        escaped_content = html.escape(content)
        return f'''
        <div id="{content_id}" class="hidden-content" style="display:none;">
            {escaped_content}
        </div>
        '''
    
    # Function to safely escape content for JavaScript
    def js_escape(content):
        if content is None:
            return ""
        # More thorough escaping for JavaScript string safety
        return json.dumps(content)[1:-1]  # Remove the quotes added by json.dumps
        
    # Generate content when button is clicked
    with generate_placeholder.container():
        if st.button("🔮 Generate Content", disabled=not api_key or not topic, use_container_width=True):
            if not topic:
                st.error("Please enter a topic or insight")
            else:
                with st.spinner("Generating content..."):
                    # Create tabs for each platform
                    linkedin_tab, twitter_tab, whatsapp_tab = st.tabs(["LinkedIn", "Twitter", "WhatsApp"])
                    
                    # LinkedIn Content
                    with linkedin_tab:
                        st.markdown('<div class="content-card">', unsafe_allow_html=True)
                        st.markdown('<h3 class="platform-header"><span class="platform-icon">🔗</span> LinkedIn Post</h3>', unsafe_allow_html=True)
                        
                        # Generate LinkedIn post
                        linkedin_content = generate_text_content(topic, persona, tone, "linkedin")
                        if linkedin_content:
                            st.markdown('<div class="linkedin-message">', unsafe_allow_html=True)
                            st.markdown(linkedin_content)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Generate unique ID for this content
                            content_id = f"linkedin_content_{hash(linkedin_content)}"
                            
                            # Create a hidden div with the content
                            st.markdown(get_hidden_content_div(content_id, linkedin_content), unsafe_allow_html=True)
                            
                            # Create a copy button that references the hidden content
                            st.markdown(get_copy_button_for_id(content_id), unsafe_allow_html=True)
                        
                        # LinkedIn Reel (3 slides)
                        st.markdown('<h3 class="platform-header" style="margin-top: 2rem;"><span class="platform-icon">🎬</span> LinkedIn Reel Slides</h3>', unsafe_allow_html=True)
                        
                        slide_cols = st.columns(3)
                        linkedin_slides = []
                        
                        for i, col in enumerate(slide_cols):
                            with col:
                                with st.spinner(f"Creating slide {i+1}..."):
                                    slide_image = generate_image(f"{topic} - slide {i+1}/3", "linkedin")
                                    if slide_image:
                                        st.image(slide_image, use_container_width=True)
                                        st.markdown(get_download_link(slide_image, f"linkedin_slide_{i+1}.png", f"Download Slide {i+1}"), unsafe_allow_html=True)
                                        linkedin_slides.append(slide_image)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Twitter Content
                    with twitter_tab:
                        st.markdown('<div class="content-card">', unsafe_allow_html=True)
                        st.markdown('<h3 class="platform-header"><span class="platform-icon">🐦</span> Twitter Post</h3>', unsafe_allow_html=True)
                        
                        twitter_content = generate_text_content(topic, persona, tone, "twitter")
                        if twitter_content:
                            st.markdown('<div class="twitter-message">', unsafe_allow_html=True)
                            st.markdown(twitter_content)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Generate unique ID for this content
                            content_id = f"twitter_content_{hash(twitter_content)}"
                            
                            # Create a hidden div with the content
                            st.markdown(get_hidden_content_div(content_id, twitter_content), unsafe_allow_html=True)
                            
                            # Create a copy button that references the hidden content
                            st.markdown(get_copy_button_for_id(content_id), unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # WhatsApp Content
                    with whatsapp_tab:
                        st.markdown('<div class="content-card">', unsafe_allow_html=True)
                        
                        whatsapp_cols = st.columns([1, 1])
                        
                        with whatsapp_cols[0]:
                            st.markdown('<h3 class="platform-header"><span class="platform-icon">📱</span> WhatsApp Image</h3>', unsafe_allow_html=True)
                            
                            with st.spinner("Creating WhatsApp image..."):
                                whatsapp_image = generate_image(topic, "whatsapp")
                                if whatsapp_image:
                                    st.image(whatsapp_image, use_container_width=True)
                                    st.markdown(get_download_link(whatsapp_image, "whatsapp_image.png", "Download Image"), unsafe_allow_html=True)
                        
                        with whatsapp_cols[1]:
                            st.markdown('<h3 class="platform-header"><span class="platform-icon">💬</span> WhatsApp Message</h3>', unsafe_allow_html=True)
                            
                            whatsapp_content = generate_text_content(topic, persona, tone, "whatsapp")
                            if whatsapp_content:
                                st.markdown('<div class="whatsapp-message">', unsafe_allow_html=True)
                                st.markdown(whatsapp_content)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Generate unique ID for this content
                                content_id = f"whatsapp_content_{hash(whatsapp_content)}"
                                
                                # Create a hidden div with the content
                                st.markdown(get_hidden_content_div(content_id, whatsapp_content), unsafe_allow_html=True)
                                
                                # Create a copy button that references the hidden content
                                st.markdown(get_copy_button_for_id(content_id), unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"© {datetime.now().year} AI Content Generator | Built with Streamlit, OpenAI GPT, and DALL-E")

if __name__ == "__main__":
    main() 