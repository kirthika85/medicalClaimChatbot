import streamlit as st
import os
import PyPDF2
import openai
import time

# Set up OpenAI API using environment variable
#openai.api_key = st.secrets["OPENAI_API_KEY"]

with st.spinner("🔄 Mool AI agent Authentication In progress..."):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if not openai.api_key:
        st.error("❌ API_KEY not found in environment variables.")
        st.stop()
    time.sleep(5)
st.success("✅ Mool AI agent Authentication Successful")

if openai.api_key is None:
    st.error("OPENAI_API_KEY environment variable is not set. Please set it before running the app.")
else:
    # Function to read files from the current directory
    def read_files():
        contents = []
        #st.write("Reading files from the current directory...")
        for filename in os.listdir():
            if filename.endswith('.pdf'):
                #st.write(f"Found file: {filename}")
                with open(filename, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    pdf_text = '\n'.join([page.extract_text() for page in reader.pages])
                    contents.append({"filename": filename, "content": pdf_text})
                    #st.write(f"Successfully read PDF file: {filename}")
                    #st.write(f"Content snippet: {pdf_text[:200]}...")
            elif filename.endswith('.txt'):
                with open(filename, 'r') as file:
                    text = file.read()
                    contents.append({"filename": filename, "content": text})
                    #st.write(f"Successfully read TXT file: {filename}")
                    #st.write(f"Content snippet: {text[:200]}...")
        #st.write(f"Total files read: {len(contents)}")
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
                    {"role": "assistant", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {e}"

    # Streamlit app layout
    st.title("Claim-Related Chatbot")
    st.write("This chatbot answers claim-related questions based on the documents in the current directory.")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Read files from the current directory
    file_contents = read_files()

    # Display chat messages from history
    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])

    # Add welcome message
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your medical claim assistant. How can I help you today?"})

    # User input for chatbot interaction
    user_input = st.text_input("What would you like to ask?")

    if st.button("Submit"):
        # Generate a response using OpenAI
        response = generate_response(user_input, file_contents)

        # Add user input and bot response to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display the new messages dynamically
        st.chat_message("user").markdown(user_input)
        st.chat_message("assistant").markdown(response)

    # Read files from the current directory
    file_contents = read_files()

    # Display chat messages from history (newest at the top)
    for message in reversed(st.session_state.messages):
        st.chat_message(message["role"]).markdown(message["content"])
