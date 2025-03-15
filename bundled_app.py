"""
DEPRECATED - NOT THE MAIN APPLICATION
This file is kept for reference only. 
The main application is content_generator.py.
"""

"""
Prompt Enhancer - Minimal Version

This is a simplified version of the Prompt Enhancer app that uses minimal dependencies.
It provides basic functionality without requiring pip installation.

Requirements:
- Python 3.6+
- An OpenAI API key
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
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import threading

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
        return f"Error: {str(e)}"

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
        messagebox.showerror("Error", f"Error connecting to OpenAI API: {str(e)}")
        return []

# --- GUI Application ---

class PromptEnhancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Prompt Enhancer")
        self.root.geometry("1000x900")  # Increased size for better visibility
        self.root.minsize(800, 700)     # Increased minimum size
        self.root.configure(bg="white") # Set white background for Apple-like aesthetic
        
        # Configure style
        self.style = ttk.Style()
        
        # Try to use Poppins font if available, otherwise fallback to a system font
        try:
            # Check if Poppins is available
            font_families = tk.font.families()
            if "Poppins" in font_families:
                base_font = "Poppins"
            else:
                base_font = "Helvetica"  # Apple-like fallback
        except:
            base_font = "Helvetica"  # Fallback if font checking fails
        
        # Configure styles with thicker fonts and more spacing
        self.style.configure("TFrame", background="white")
        self.style.configure("TLabelframe", background="white")
        self.style.configure("TLabelframe.Label", font=(base_font, 14, "bold"), background="white")
        self.style.configure("TButton", font=(base_font, 14, "bold"), padding=15, background="white")
        self.style.configure("TLabel", font=(base_font, 14), background="white", padding=5)
        self.style.configure("Header.TLabel", font=(base_font, 20, "bold"), background="white", padding=10)
        self.style.configure("Subheader.TLabel", font=(base_font, 16), background="white", padding=8)
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=30)  # Increased padding
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 30))  # Increased spacing
        
        ttk.Label(header_frame, text="✨ Prompt Enhancer", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(header_frame, text="Transform your ideas into powerful AI prompts", style="Subheader.TLabel").pack(anchor=tk.W, pady=(10, 0))
        
        # API Key
        api_frame = ttk.LabelFrame(main_frame, text="API Configuration", padding=10)
        api_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(api_frame, text="OpenAI API Key:").pack(anchor=tk.W)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*", width=50)
        self.api_key_entry.pack(fill=tk.X, pady=5)
        ttk.Label(api_frame, text="Your API key is only used for this session and is not stored.").pack(anchor=tk.W)
        
        # Form Frame
        form_frame = ttk.LabelFrame(main_frame, text="Prompt Components", padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Context
        ttk.Label(form_frame, text="Context:").pack(anchor=tk.W, pady=(5, 0))
        self.context_text = scrolledtext.ScrolledText(form_frame, height=4, width=50, wrap=tk.WORD)
        self.context_text.pack(fill=tk.X, pady=5)
        
        # Two-column layout for role and format
        role_format_frame = ttk.Frame(form_frame)
        role_format_frame.pack(fill=tk.X, pady=5)
        
        # AI Role
        role_frame = ttk.Frame(role_format_frame)
        role_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Label(role_frame, text="AI Role:").pack(anchor=tk.W)
        self.role_var = tk.StringVar()
        self.role_entry = ttk.Entry(role_frame, textvariable=self.role_var)
        self.role_entry.pack(fill=tk.X, pady=5)
        
        # Output Format
        format_frame = ttk.Frame(role_format_frame)
        format_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        ttk.Label(format_frame, text="Output Format:").pack(anchor=tk.W)
        self.format_var = tk.StringVar()
        self.format_entry = ttk.Entry(format_frame, textvariable=self.format_var)
        self.format_entry.pack(fill=tk.X, pady=5)
        
        # Task
        ttk.Label(form_frame, text="Task:").pack(anchor=tk.W, pady=(5, 0))
        self.task_text = scrolledtext.ScrolledText(form_frame, height=4, width=50, wrap=tk.WORD)
        self.task_text.pack(fill=tk.X, pady=5)
        
        # Additional Notes
        ttk.Label(form_frame, text="Additional Notes (Optional):").pack(anchor=tk.W, pady=(5, 0))
        self.notes_text = scrolledtext.ScrolledText(form_frame, height=3, width=50, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.X, pady=5)
        
        # Enhance Button
        self.enhance_button = ttk.Button(
            main_frame, 
            text="Enhance Prompt", 
            command=self.enhance_prompt,
            style="TButton"
        )
        self.enhance_button.pack(pady=10)
        
        # Output frame (initially hidden)
        self.output_frame = ttk.LabelFrame(main_frame, text="Enhanced Prompt", padding=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Label(footer_frame, text="Created with ❤️ | Powered by OpenAI GPT-4 Turbo").pack(side=tk.RIGHT)
    
    def enhance_prompt(self):
        # Validate inputs
        if not self.api_key_var.get():
            messagebox.showerror("Error", "Please provide your OpenAI API key.")
            return
        
        context = self.context_text.get("1.0", tk.END).strip()
        ai_role = self.role_var.get().strip()
        task = self.task_text.get("1.0", tk.END).strip()
        output_format = self.format_var.get().strip()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        if not context or not ai_role or not task or not output_format:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return
        
        # Create the PromptComponents object
        components = PromptComponents(
            context=context,
            ai_role=ai_role,
            task=task,
            output_format=output_format,
            additional_notes=notes if notes else None
        )
        
        # Disable the enhance button and update status
        self.enhance_button.config(state=tk.DISABLED)
        self.status_var.set("Processing... Please wait.")
        self.root.update_idletasks()
        
        # Process in a separate thread to keep the UI responsive
        threading.Thread(target=self.process_prompt, args=(components,), daemon=True).start()
    
    def process_prompt(self, components):
        try:
            # Ask clarifying questions
            questions = ask_clarifying_questions(components, self.api_key_var.get())
            
            if questions and len(questions) > 0:
                # Show questions in a dialog
                self.show_clarifying_questions(components, questions)
            else:
                # Generate enhanced prompt directly
                enhanced_prompt = enhance_prompt(components, self.api_key_var.get())
                self.display_result(enhanced_prompt)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred during processing.")
        finally:
            # Re-enable the enhance button
            self.enhance_button.config(state=tk.NORMAL)
    
    def show_clarifying_questions(self, components, questions):
        # Create a new dialog window for questions
        dialog = tk.Toplevel(self.root)
        dialog.title("Clarifying Questions")
        dialog.geometry("800x600")  # Larger dialog size
        dialog.minsize(700, 500)    # Set minimum size
        dialog.transient(self.root)
        dialog.configure(bg="white")  # White background
        
        # Make dialog modal
        dialog.grab_set()
        
        # Create a canvas with scrollbar for scrolling
        canvas = tk.Canvas(dialog, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas for the content
        main_frame = ttk.Frame(canvas, padding=30)
        
        # Add the frame to the canvas
        canvas_frame = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # Instructions
        ttk.Label(
            main_frame, 
            text="To create a better prompt, please answer these questions:",
            style="Header.TLabel"
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Create a frame for questions and answers
        questions_frame = ttk.Frame(main_frame)
        questions_frame.pack(fill=tk.X, expand=True)
        
        # Create entry fields for each question
        answer_widgets = []
        for i, question in enumerate(questions):
            q_frame = ttk.LabelFrame(questions_frame, text=f"Question {i+1}", padding=15)
            q_frame.pack(fill=tk.X, pady=15)
            
            ttk.Label(q_frame, text=question, wraplength=700, style="Subheader.TLabel").pack(anchor=tk.W, pady=(5, 10))
            
            answer = scrolledtext.ScrolledText(q_frame, height=4, width=60, wrap=tk.WORD, font=(base_font, 12))
            answer.pack(fill=tk.X, pady=5)
            answer_widgets.append(answer)
        
        # Submit button - placed in a separate frame to ensure visibility
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        submit_button = ttk.Button(
            button_frame,
            text="Submit Answers",
            command=lambda: self.process_answers(dialog, components, questions, answer_widgets)
        )
        submit_button.pack(pady=10)
        
        # Update the canvas scroll region when the frame size changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        main_frame.bind("<Configure>", configure_scroll_region)
        
        # Bind mousewheel to scroll
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Make sure the canvas expands to fill the dialog
        canvas.update_idletasks()
        canvas.config(width=dialog.winfo_width(), height=dialog.winfo_height())
    
    def process_answers(self, dialog, components, questions, answer_widgets):
        # Get answers from widgets
        answers = [widget.get("1.0", tk.END).strip() for widget in answer_widgets]
        
        # Add answers to additional notes
        additional_info = "\n\nClarifying Information:\n"
        for q, a in zip(questions, answers):
            additional_info += f"Q: {q}\nA: {a}\n\n"
        
        components.additional_notes = (components.additional_notes or "") + additional_info
        
        # Close the dialog
        dialog.destroy()
        
        # Update status
        self.status_var.set("Generating enhanced prompt...")
        self.root.update_idletasks()
        
        # Generate the enhanced prompt
        threading.Thread(
            target=lambda: self.generate_with_answers(components),
            daemon=True
        ).start()
    
    def generate_with_answers(self, components):
        try:
            enhanced_prompt = enhance_prompt(components, self.api_key_var.get())
            self.display_result(enhanced_prompt)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred during processing.")
        finally:
            self.enhance_button.config(state=tk.NORMAL)
    
    def display_result(self, enhanced_prompt):
        # If the output frame is already displayed, remove it
        if self.output_frame.winfo_ismapped():
            self.output_frame.pack_forget()
        
        # Configure and display the output frame
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))  # Increased spacing
        
        # Clear any previous content
        for widget in self.output_frame.winfo_children():
            widget.destroy()
        
        # Add the enhanced prompt text widget with improved styling
        result_text = scrolledtext.ScrolledText(
            self.output_frame, 
            height=10,  # Increased height
            width=60,   # Increased width
            wrap=tk.WORD,
            font=(base_font, 14)  # Larger font
        )
        result_text.pack(fill=tk.BOTH, expand=True, pady=10)
        result_text.insert(tk.END, enhanced_prompt)
        result_text.config(state=tk.DISABLED)  # Make it read-only
        
        # Add a copy button with improved styling
        copy_button = ttk.Button(
            self.output_frame,
            text="Copy to Clipboard",
            command=lambda: self.copy_to_clipboard(enhanced_prompt)
        )
        copy_button.pack(pady=15)  # Increased padding
        
        # Update status
        self.status_var.set("Enhanced prompt generated successfully!")
    
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("Copied to clipboard!")

# --- Main Entry Point ---

def main():
    root = tk.Tk()
    app = PromptEnhancerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 