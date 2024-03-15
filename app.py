import streamlit as st
from openai import OpenAI
from io import BytesIO
from PIL import Image
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

st.set_page_config(page_title='GPT-4 Vision', page_icon='👁️')

if 'history' not in st.session_state:
    st.session_state['history'] = []
    st.session_state['cost'] = 0.0
    st.session_state['counters'] = [0, 1]


# Fetch OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')

# get user inputs
img_input = st.file_uploader('**Image**', accept_multiple_files=True, key=st.session_state['counters'][1])
text_input = st.text_input('**Explain the Anomaly:**', '', key=st.session_state['counters'][0])

# send api request
if st.button('Send'):
    if not api_key:
        st.warning('API Key required')
        st.stop()
    if not (text_input or img_input):
        st.warning('You can\'t just send nothing!')
        st.stop()
    msg = {'role': 'user', 'content': []}
    if text_input:
        msg['content'].append({'type': 'text', 'text': text_input})
    for img in img_input:
        if img.name.split('.')[-1].lower() not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
            st.warning('Only .jpg, .png, .gif, or .webp are supported')
            st.stop()
        encoded_img = base64.b64encode(img.read()).decode('utf-8')
        msg['content'].append(
            {
                'type': 'image_url',
                'image_url': {
                    'url': f'data:image/jpeg;base64,{encoded_img}',
                    'detail': 'low'
                }
            }
        )
    st.session_state['history'].append(msg)
    history = (
        st.session_state['history']
        if st.session_state['history']
        else st.session_state['history'][1:]
    )
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model='gpt-4-vision-preview',
        temperature=0.7,
        max_tokens=300,
        messages=history
    )
    st.session_state['history'].append(
        {'role': 'assistant', 'content': response.choices[0].message.content}
    )
    st.session_state['cost'] += response.usage.prompt_tokens * 0.01 / 1000
    st.session_state['cost'] += response.usage.completion_tokens * 0.03 / 1000
    st.session_state['counters'] = [i+2 for i in st.session_state['counters']]

# display the assistant's response
if st.session_state['history']:
    last_response = st.session_state['history'][-1]
    if last_response['role'] == 'assistant':
        msg_content = ''.join(['  ' + char if char == '\n' else char for char in last_response['content']])  # fixes display issue
        st.markdown('Assistant: ' + msg_content)
