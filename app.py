import streamlit as st
import base64
import os
from PIL import Image as PILImage
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Groq API key from the environment
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq API client with API key
client = Groq(api_key=groq_api_key)
llava_model = 'llava-v1.5-7b-4096-preview'
llama31_model = 'llama-3.1-70b-versatile'

st.set_page_config(page_title='Groq Vision', page_icon='👁️')

if 'history' not in st.session_state:
    st.session_state['history'] = []

# Get user inputs
img_input = st.file_uploader('**Image**', accept_multiple_files=True, key='image_upload')
text_input = st.text_input('**Explain the Anomaly:**', '', key='text_input')

# Function to encode the image
def encode_image(image):
    return base64.b64encode(image.read()).decode('utf-8')

# Function to generate image description using LLaVA
def image_to_text(base64_image, prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model=llava_model
    )

    return chat_completion.choices[0].message.content

# Function to generate short story using Llama 3.1
def short_story_generation(image_description):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a children's book author. Write a short story about the scene depicted in this image.",
            },
            {
                "role": "user",
                "content": image_description,
            }
        ],
        model=llama31_model
    )
    
    return chat_completion.choices[0].message.content

# Send API request
if st.button('Send'):
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
    
    # Generate image description
    description_prompt = "Describe this image in detail."
    image_description = image_to_text(encoded_img, description_prompt)
    
    st.session_state['history'].append({'role': 'user', 'content': msg_content})
    st.session_state['history'].append({'role': 'assistant', 'content': image_description})

    # Generate short story based on image description
    short_story = short_story_generation(image_description)
    st.session_state['history'].append({'role': 'assistant', 'content': short_story})

# Display the assistant's response
if st.session_state['history']:
    for response in st.session_state['history']:
        if response['role'] == 'assistant':
            st.markdown(f"**Assistant:** {response['content']}")
