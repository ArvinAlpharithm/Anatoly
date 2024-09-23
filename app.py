import streamlit as st
import requests
from io import BytesIO
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up page configuration
st.set_page_config(page_title='Groq Vision', page_icon='👁️')

# Initialize session state
if 'history' not in st.session_state:
    st.session_state['history'] = []
    st.session_state['cost'] = 0.0
    st.session_state['counters'] = [0, 1]

# Fetch Groq API key from environment variables
api_key = os.getenv("GROQ_API_KEY")

# Get user inputs
img_input = st.file_uploader('**Image**', accept_multiple_files=True, key=st.session_state['counters'][1])
text_input = st.text_input('**Explain the Anomaly:**', '', key=st.session_state['counters'][0])

# Function to encode the image
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Send API request
if st.button('Send'):
    if not api_key:
        st.warning('API Key required')
        st.stop()
    if not (text_input or img_input):
        st.warning('You can\'t just send nothing!')
        st.stop()
    
    msg_content = []
    if text_input:
        msg_content.append({'type': 'text', 'text': text_input})
    
    for img in img_input:
        if img.name.split('.')[-1].lower() not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
            st.warning('Only .jpg, .png, .gif, or .webp are supported')
            st.stop()
        encoded_img = encode_image(img)
        msg_content.append(
            {
                'type': 'image_url',
                'image_url': {
                    'url': f'data:image/jpeg;base64,{encoded_img}'
                }
            }
        )
    
    st.session_state['history'].append({'role': 'user', 'content': msg_content})
    history = st.session_state['history'] if st.session_state['history'] else st.session_state['history'][1:]

    # Set headers for Groq API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Construct payload for Groq
    payload = {
        "model": "llama3-70b-8192",  # Use the appropriate model for Groq
        "messages": history,
        "max_tokens": 300
    }
    
    # Send request to Groq API
    response = requests.post("https://api.groq.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        response_data = response.json()
        st.session_state['history'].append(
            {'role': 'assistant', 'content': response_data['choices'][0]['message']['content']}
        )
        # Assume cost calculation is not needed for Groq, adjust if required
    else:
        st.error(f"Error: {response.status_code} - {response.text}")

# Display the assistant's response
if st.session_state['history']:
    last_response = st.session_state['history'][-1]
    if last_response['role'] == 'assistant':
        msg_content = ''.join(['  ' + char if char == '\n' else char for char in last_response['content']])  # fixes display issue
        st.markdown('Assistant: ' + msg_content)
