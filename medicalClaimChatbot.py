import streamlit as st
import os
import PyPDF2
import openai
import time

# Set up OpenAI API using environment variable
with st.spinner("🔄 Mool AI agent Authentication In progress..."):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if not openai.api_key:
        st.error("❌ API_KEY not found in environment variables.")
        st.stop()
    time.sleep(5)
st.success("✅ Mool AI agent Authentication Successful")

if openai.api_key is None:
    st.error("OPENAI_API_KEY environment variable is not set. Please set it before running the app.")
    st.stop()

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

# Function to generate a response using OpenAI
def generate_response(user_input, file_contents):
    # Prepare the prompt for OpenAI
    prompt = f"Based on the following documents:\n\n"
    for file in file_contents:
        prompt += f"--- {file['filename']} ---\n{file['content'][:2500]}\n\n"
    prompt += f"\nAnswer the question: {user_input}"

    # Use OpenAI to generate a response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a medical claim assistant. Use the provided documents to answer questions accurately."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {e}"

# Streamlit app layout
st.title("Claim-Related Chatbot")
st.write("This chatbot answers claim-related questions")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add welcome message only once at the start
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your medical claim assistant. How can I help you today?"})

# Initialize the user input in session state to an empty string
if "user_input_value" not in st.session_state:
    st.session_state["user_input_value"] = ""

# User input for chatbot interaction
user_input = st.text_input("What would you like to ask?", key="user_input", value=st.session_state["user_input_value"])

if st.button("Submit"):
    # Check if user input is not empty
    if user_input:
        # Generate a response using OpenAI
        file_contents = read_files()
        response = generate_response(user_input, file_contents)

        # Add user input and bot response to the end of chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Clear the input field by setting the session state value to an empty string
        st.session_state["user_input_value"] = ""
        
        # Re-run the script to update the display
        st.rerun()

# Display chat messages from history (newest at the top)
st.write("Chat History:")
welcome_message = None
for message in reversed(st.session_state.messages):
    if message["role"] == "assistant" and message["content"].startswith("Hello!"):
        welcome_message = message
    else:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**Assistant:** {message['content']}")

if welcome_message:
    st.write(f"**Assistant:** {welcome_message['content']}")
