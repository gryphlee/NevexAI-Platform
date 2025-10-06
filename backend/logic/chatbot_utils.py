# chatbot_utils.py
import streamlit as st
import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_tutor_response(chat_history):
    """
    Sends the conversation history to the local AI and gets a response.
    """
    # Create a prompt from the chat history
    # The prompt format is specific to guide the AI to act as a tutor
    prompt_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    
    prompt = f"""
    You are 'Tutor AI', a friendly and encouraging academic tutor. Your goal is to help students understand concepts without just giving them the answer. Use the Socratic method: ask questions, break down problems, and guide them to their own conclusions.

    Current conversation:
    {prompt_history}
    
    Tutor AI:
    """
    
    payload = {
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7}
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        full_response = response.json().get('response', 'I am not sure how to help with that. Can you rephrase?').strip()
        return full_response
    except requests.exceptions.RequestException as e:
        st.error(f"Connection to local AI failed: {e}")
        return "Sorry, I'm having trouble connecting to my brain right now. Please make sure the Ollama server is running."
    except Exception as e:
        return f"An unexpected error occurred: {e}"