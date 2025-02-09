import streamlit as st
import os
import PyPDF2
import openai

# Set up OpenAI API
openai.api_key = os.getenv("OPEN_API_KEY")

# Function to read files from the current directory
def read_files():
    contents = []
    for filename in os.listdir():
        if filename.endswith('.pdf'):
            with open(filename, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                pdf_text = '\n'.join([page.extract_text() for page in reader.pages])
                contents.append({"filename": filename, "content": pdf_text})
        elif filename.endswith('.txt'):
            with open(filename, 'r') as file:
                text = file.read()
                contents.append({"filename": filename, "content": text})
    return contents

# Function to generate a response using ChatGPT
def generate_response(user_input, file_contents):
    # Prepare the prompt for ChatGPT
    prompt = f"Based on the following documents:\n\n"
    for file in file_contents:
        prompt += f"--- {file['filename']} ---\n{file['content'][:500]}\n\n"
    prompt += f"\nAnswer the question: {user_input}"
    
    # Use ChatGPT to generate a response
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "assistant", "content": prompt}]
    )
    
    return response.choices[0].message.content

# Streamlit app layout
st.title("Claim-Related Chatbot")
st.write("This chatbot answers claim-related questions")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Read files from the current directory
file_contents = read_files()

# Display chat messages from history
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

# User input for chatbot interaction
user_input = st.text_input("What would you like to ask?")

if st.button("Submit"):
    # Generate a response using ChatGPT
    response = generate_response(user_input, file_contents)
    
    # Add user input and bot response to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Display the new messages dynamically
    st.chat_message("user").markdown(user_input)
    st.chat_message("assistant").markdown(response)
