"""
Prompt Enhancer - Streamlit Version

This is a Streamlit version of the Prompt Enhancer app that provides a modern UI
with better scrolling and compatibility.

Requirements:
- Python 3.6+
- An OpenAI API key
- Streamlit (pip install streamlit)
"""

import os
import json
import sys
import webbrowser
import urllib.request
import urllib.parse
import urllib.error
import base64
import http.client
import threading
import streamlit as st
from typing import List, Dict, Any, Optional

# --- Page Configuration ---
st.set_page_config(
    page_title="✨ Prompt Enhancer",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Apple-like aesthetics ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    h1 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 24px;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }
    
    h2, h3 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 18px;
        margin-top: 8px !important;
        margin-bottom: 4px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    
    .stTextInput, .stTextArea {
        background-color: #f9f9f9;
        border-radius: 8px;
        border: 1px solid #eaeaea;
        padding: 8px;
    }
    
    .stButton > button {
        background-color: #007AFF;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-size: 14px;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
    }
    
    /* Persona button styles */
    .persona-button button {
        background-color: #f0f0f0 !important;
        color: #333 !important;
        font-weight: 500 !important;
        border: 1px solid #ddd !important;
        transition: all 0.2s ease !important;
    }
    
    .persona-button button:hover {
        background-color: #e0e0e0 !important;
        border-color: #bbb !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }
    
    /* Active persona button style */
    .persona-button-active button {
        background-color: #f0f7ff !important;
        color: #007AFF !important;
        border-color: #007AFF !important;
    }
    
    /* Super compact layout styles */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* Results container - keeping just this one container for the results */
    .result-container {
        background-color: #f9f9f9;
        padding: 0.8rem;
        border-radius: 8px;
        border: 1px solid #eaeaea;
        margin-top: 1rem;
    }
    
    .footer {
        text-align: right;
        color: #888888;
        font-size: 12px;
        margin-top: 0.5rem;
    }
    
    /* Streamlit default element spacing adjustments */
    div.stTextInput > div > div > input {
        padding: 0.4rem 0.5rem;
    }
    
    div.stTextArea > div > div > textarea {
        padding: 0.4rem 0.5rem;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 0.3rem !important;
    }
    
    div[data-testid="stForm"] > div {
        padding-top: 0.3rem !important;
        padding-bottom: 0.3rem !important;
    }
    
    div.stMarkdown p {
        margin-bottom: 0.3rem;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Remove excess padding from header */
    header[data-testid="stHeader"] {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Remove extra padding from all elements */
    div[data-testid="stToolbar"] {
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
    }
    
    [data-testid="stAppViewContainer"] > section:first-child {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* Tighter form spacing */
    .stForm > div:first-child {
        padding-top: 0 !important;
    }
    
    /* Small margin between form elements */
    .stForm [data-testid="stVerticalBlock"] > div {
        margin-bottom: 0.5rem !important;
    }
    
    /* Custom spacing for our sections */
    .tight-section {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- OpenAI API Client (Minimal Implementation) ---

class MinimalOpenAIClient:
    """A minimal OpenAI API client that doesn't require the openai package"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "api.openai.com"
    
    def create_chat_completion(self, model, messages, temperature=0.7, response_format=None):
        """Create a chat completion using the OpenAI API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        payload_bytes = json.dumps(payload).encode('utf-8')
        
        conn = http.client.HTTPSConnection(self.base_url)
        conn.request("POST", "/v1/chat/completions", payload_bytes, headers)
        response = conn.getresponse()
        
        if response.status != 200:
            raise Exception(f"API request failed with status {response.status}: {response.read().decode('utf-8')}")
        
        data = json.loads(response.read().decode('utf-8'))
        conn.close()
        
        return {
            "choices": [
                {
                    "message": {
                        "content": data["choices"][0]["message"]["content"]
                    }
                }
            ]
        }

# --- Models ---

class PromptComponents:
    """Represents the components of a prompt"""
    
    def __init__(self, context, ai_role, task, output_format, additional_notes=None):
        self.context = context
        self.ai_role = ai_role
        self.task = task
        self.output_format = output_format
        self.additional_notes = additional_notes

# --- API Functions ---

def enhance_prompt(components, api_key):
    """Use OpenAI to enhance the user's prompt components into a powerful prompt"""
    try:
        client = MinimalOpenAIClient(api_key)
        
        system_message = """
        You are a world-class prompt engineering expert specializing in creating highly effective prompts.
        Your task is to transform the provided components into a powerful, well-structured prompt that will
        produce exceptional results with AI models.
        
        Create a prompt that:
        1. Is clear, concise, and comprehensive
        2. Includes all necessary context and constraints
        3. Defines the AI's role precisely
        4. Specifies the exact task and desired outcome
        5. Provides clear formatting requirements
        6. Incorporates best practices in prompt engineering
        
        Return ONLY the enhanced prompt text without additional explanations.
        """
        
        user_message = f"""
        Please transform these prompt components into a powerful prompt:
        
        CONTEXT: {components.context}
        
        AI ROLE: {components.ai_role}
        
        TASK: {components.task}
        
        OUTPUT FORMAT: {components.output_format}
        
        ADDITIONAL NOTES: {components.additional_notes if components.additional_notes else "None provided"}
        """
        
        with st.spinner("Enhancing your prompt..."):
            response = client.create_chat_completion(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def ask_clarifying_questions(components, api_key):
    """Use OpenAI to generate clarifying questions about the prompt components"""
    try:
        client = MinimalOpenAIClient(api_key)
        
        system_message = """
        You are a prompt engineering expert who helps users create better prompts.
        Your task is to identify what information might be missing from the prompt components provided
        and ask 1-3 clarifying questions that would help improve the final prompt.
        
        Only ask questions if you genuinely need more information. If the prompt components are
        comprehensive enough, state that no clarifying questions are needed.
        
        Return your response as a JSON object with a "questions" key containing an array of strings, each string being a question.
        If no questions are needed, return an empty array.
        """
        
        user_message = f"""
        Please review these prompt components and suggest clarifying questions if needed:
        
        CONTEXT: {components.context}
        
        AI ROLE: {components.ai_role}
        
        TASK: {components.task}
        
        OUTPUT FORMAT: {components.output_format}
        
        ADDITIONAL NOTES: {components.additional_notes if components.additional_notes else "None provided"}
        """
        
        with st.spinner("Analyzing your prompt components..."):
            response = client.create_chat_completion(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
        
        result = json.loads(response["choices"][0]["message"]["content"])
        return result.get("questions", [])
    except Exception as e:
        st.error(f"Error connecting to OpenAI API: {str(e)}")
        return []

# --- Session State Initialization ---
if 'enhanced_prompt' not in st.session_state:
    st.session_state.enhanced_prompt = None
if 'clarifying_questions' not in st.session_state:
    st.session_state.clarifying_questions = None
if 'clarifying_answers' not in st.session_state:
    st.session_state.clarifying_answers = {}
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        "context": "",
        "ai_role": "",
        "task": "",
        "output_format": "",
        "additional_notes": ""
    }
if 'custom_ai_role' not in st.session_state:
    st.session_state.custom_ai_role = ""

# --- Main App UI ---

# Use two-column layout for the entire app
main_col1, main_col2 = st.columns([3, 2])

with main_col1:
    # Page header - removed section container
    st.title("Prompt Enhancer")
    st.markdown("Transform your basic prompts into expertly crafted instructions for AI.")
    
    # API Key input - removed section container
    api_key = st.text_input("OpenAI API Key", 
                          type="password", 
                          help="Your API key is only used for this session and is not stored.",
                          value=st.session_state.get('api_key', ''),
                          placeholder="Enter your OpenAI API key")

    if api_key:
        st.session_state.api_key = api_key
    
    # Persona selection - removed section container
    st.subheader("Persona Selection")
    st.write("Choose a persona or enter your own custom role:")
    personas_col1, personas_col2, personas_col3 = st.columns(3)

    # Define persona descriptions
    techie_desc = "Highly experienced tech engineer expertise in AI, Deep tech, python, front end design. Think CTO in a company like Apple."
    content_desc = "A super creative mastermind that knows how to tell a story and craft great content."
    teacher_desc = "Explaining concepts to a 5 year old, adult explanation and real world example."

    # Helper function to create persona buttons with active state styling
    def persona_button(label, description, column, persona_type):
        # Check if this persona is currently active
        is_active = st.session_state.custom_ai_role == description
        
        # Apply the appropriate CSS class based on active state
        button_class = "persona-button-active" if is_active else "persona-button"
        
        # Create the button with the appropriate styling
        with column:
            st.markdown(f'<div class="{button_class}">', unsafe_allow_html=True)
            if st.button(label, use_container_width=True, help=description):
                st.session_state.custom_ai_role = description
            st.markdown('</div>', unsafe_allow_html=True)

    # Create the persona buttons with proper styling
    persona_button("💻 Techie", techie_desc, personas_col1, "techie")
    persona_button("✏️ Content Genius", content_desc, personas_col2, "content")
    persona_button("🧑‍🏫 Teacher", teacher_desc, personas_col3, "teacher")
    
    # Prompt Components Form - removed section container
    st.subheader("Prompt Components")
    
    # Create the form with a submit button
    with st.form("prompt_components_form", clear_on_submit=False):
        # Two-column layout for input controls
        col1, col2 = st.columns(2)
        
        with col1:
            # AI Role - Use the selected persona from session state if available
            ai_role = st.text_area("AI Role", height=80,
                                value=st.session_state.get('custom_ai_role', ''),
                                placeholder="What role should the AI play? (e.g., coding expert, marketing specialist)")
            
            # Context
            context = st.text_area("Context", height=80,
                                placeholder="What background context does the AI need to know to help with this task?")
        
        with col2:
            # Task
            task = st.text_area("Task", height=80,
                            placeholder="What specific task should the AI perform?")
            
            # Output Format
            output_format = st.text_input("Output Format", 
                                        placeholder="How should the AI format its response?")
        
        # Additional Notes in a full-width row - increasing minimum height to 68
        additional_notes = st.text_area("Additional Notes (Optional)", height=68,
                                    placeholder="Any additional information or requirements (optional)")
        
        # Add a submit button to the form
        submitted = st.form_submit_button("Generate Enhanced Prompt", use_container_width=True)
        
        # Store the form data whenever the form is rendered
        if context or ai_role or task or output_format or additional_notes:
            st.session_state.form_data = {
                "context": context,
                "ai_role": ai_role,
                "task": task,
                "output_format": output_format,
                "additional_notes": additional_notes
            }

with main_col2:
    # Show Clarifying Questions UI if needed
    if st.session_state.clarifying_questions and not st.session_state.enhanced_prompt:
        st.subheader("Clarifying Questions")
        st.write("Please answer these questions to improve your prompt:")
        
        # Create a form for the clarifying questions
        with st.form("clarifying_questions_form"):
            for i, question in enumerate(st.session_state.clarifying_questions):
                st.markdown(f"**Q{i+1}:** {question}")
                # Changed height from 60 to 68 to meet Streamlit's minimum requirement
                answer = st.text_area(f"Answer {i+1}", key=f"answer_{i}", height=68, label_visibility="collapsed")
                # Store answers in session state
                st.session_state.clarifying_answers[i] = answer
            
            submit_answers = st.form_submit_button("Submit Answers", use_container_width=True)
        
        # Process answers if submitted
        if submit_answers:
            try:
                # Get the saved form data from session state
                form_data = st.session_state.form_data
                
                # Create the PromptComponents object using saved data
                components = PromptComponents(
                    context=form_data["context"],
                    ai_role=form_data["ai_role"],
                    task=form_data["task"],
                    output_format=form_data["output_format"],
                    additional_notes=form_data["additional_notes"] if form_data["additional_notes"] else ""
                )
                
                # Add answers to additional notes
                additional_info = "\n\nClarifying Information:\n"
                for i, q in enumerate(st.session_state.clarifying_questions):
                    a = st.session_state.clarifying_answers[i]
                    additional_info += f"Q: {q}\nA: {a}\n\n"
                
                components.additional_notes = (components.additional_notes or "") + additional_info
                
                # Generate the enhanced prompt
                enhanced_prompt = enhance_prompt(components, api_key)
                if enhanced_prompt:
                    st.session_state.enhanced_prompt = enhanced_prompt
                    # Force a rerun to show the results
                    st.rerun()
            except Exception as e:
                st.error(f"Error processing answers: {str(e)}")
    
    # Show Enhanced Prompt Result
    if st.session_state.enhanced_prompt:
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.subheader("Enhanced Prompt")
        
        # Display the enhanced prompt
        st.text_area("", value=st.session_state.enhanced_prompt, height=200, disabled=True, label_visibility="collapsed")
        
        # Add buttons for actions
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("Copy", use_container_width=True):
                st.success("Copied!")
                # Fix: Use a different approach to escape backticks in JavaScript
                prompt_js_safe = st.session_state.enhanced_prompt.replace("\n", "\\n").replace("\r", "").replace("`", "\\\`").replace("'", "\\'").replace("\"", "\\\"")
                st.markdown("""
                <script>
                    navigator.clipboard.writeText("{0}");
                </script>
                """.format(prompt_js_safe), unsafe_allow_html=True)
        
        with col2:
            if st.button("Reset", use_container_width=True):
                # Reset the session state
                st.session_state.enhanced_prompt = None
                st.session_state.clarifying_questions = None
                st.session_state.clarifying_answers = {}
                st.rerun()
        
        # Optional: Add a button to open in ChatGPT
        with col3:
            if st.button("ChatGPT", use_container_width=True):
                chatgpt_url = f"https://chat.openai.com/?prompt={urllib.parse.quote(st.session_state.enhanced_prompt)}"
                webbrowser.open(chatgpt_url)
                st.success("Opening...")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Compact footer
st.markdown('<div class="footer">Created with ❤️ | Powered by OpenAI GPT-4 Turbo</div>', unsafe_allow_html=True)

# Form Processing
if submitted:
    if not api_key:
        st.error("Please provide your OpenAI API key.")
    elif not context or not ai_role or not task or not output_format:
        st.error("Please fill in all required fields.")
    else:
        try:
            # Set processing state
            st.session_state.processing = True
            
            # Create the PromptComponents object from the current form values
            components = PromptComponents(
                context=context,
                ai_role=ai_role,
                task=task,
                output_format=output_format,
                additional_notes=additional_notes if additional_notes else None
            )
            
            # First, check if we need clarifying questions
            questions = ask_clarifying_questions(components, api_key)
            
            if questions and len(questions) > 0:
                st.session_state.clarifying_questions = questions
                # Initialize answer placeholders in session state
                st.session_state.clarifying_answers = {i: "" for i in range(len(questions))}
            else:
                # No questions needed, generate prompt directly
                enhanced_prompt = enhance_prompt(components, api_key)
                if enhanced_prompt:
                    st.session_state.enhanced_prompt = enhanced_prompt
                    st.session_state.clarifying_questions = None
            
            # Reset processing state
            st.session_state.processing = False
            
            # Force a rerun to show the new UI based on state
            st.rerun()
        except Exception as e:
            st.error(f"Error generating prompt: {str(e)}")
            st.session_state.processing = False 