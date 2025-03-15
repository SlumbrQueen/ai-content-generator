"""
REDIRECT to main application
This file is a simple redirect to the main application (content_generator.py)
"""

import streamlit as st
import os
import importlib.util

# Import and run the main application
try:
    # Get the path to content_generator.py
    main_app_path = os.path.join(os.path.dirname(__file__), "content_generator.py")
    
    # Import the module
    spec = importlib.util.spec_from_file_location("content_generator", main_app_path)
    content_generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(content_generator)
    
    # Add a notice that we're using the redirected app
    st.sidebar.info("This app is running from content_generator.py")
    
except Exception as e:
    st.error(f"Error loading the main application: {str(e)}")
    st.error("Please use content_generator.py directly") 