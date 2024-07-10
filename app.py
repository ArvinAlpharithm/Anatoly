import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import base64
import os

st.set_page_config(page_title='GPT-4 Vision', page_icon='👁️')

if 'history' not in st.session_state:
    st.session_state['history'] = []
    st.session_state['cost'] = 0.0
    st.session_state['counters'] = [0, 1]

# Hardcoded OpenAI API key
api_key = "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"

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
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": history,
        "max_tokens": 300
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        response_data = response.json()
        st.session_state['history'].append(
            {'role': 'assistant', 'content': response_data['choices'][0]['message']['content']}
        )
        st.session_state['cost'] += response_data['usage']['prompt_tokens'] * 0.01 / 1000
        st.session_state['cost'] += response_data['usage']['completion_tokens'] * 0.03 / 1000
        st.session_state['counters'] = [i+2 for i in st.session_state['counters']]
    else:
        st.error(f"Error: {response.status_code} - {response.text}")

# Display the assistant's response
if st.session_state['history']:
    last_response = st.session_state['history'][-1]
    if last_response['role'] == 'assistant':
        msg_content = ''.join(['  ' + char if char == '\n' else char for char in last_response['content']])  # fixes display issue
        st.markdown('Assistant: ' + msg_content)
