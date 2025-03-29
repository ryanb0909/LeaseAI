import streamlit as st
import PyPDF2
import base64
from openai import OpenAI
from speechAi import AI_Assistant

#Set OpenAI API Key
OpenAI.api_key = "APIKEY"

# Set page configuration
st.set_page_config(page_title="AI-Powered Deal Making")
st.header("AI-Powered Deal Making")
st.caption(
    "Upload a PDF to have an AI review the lease, summarize key deal points, and generate a dashboard that highlights key terms in the lease for easy review.")

# Custom CSS to expand sidebar width
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            min-width: 800px;
            max-width: 900px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar title
st.sidebar.header("PDF Upload")

# File uploader in the sidebar
uploaded_file = st.sidebar.file_uploader("Upload a lease in PDF format to be scanned by an AI reviewer.", type=["pdf"])

# Function to display PDF in the sidebar
def display_pdf(file):
    # Read the file and encode it in Base64
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px"></iframe>'

    # Render in sidebar using markdown
    st.sidebar.markdown(pdf_display, unsafe_allow_html=True)

# Show PDF in sidebar if uploaded
if uploaded_file is not None:
    display_pdf(uploaded_file)

# Extract data from PDF
def extract_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

lease_text = ""
if uploaded_file:
    lease_text = extract_pdf(uploaded_file)
    st.session_state["lease_text"] = lease_text

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat messages on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input for chat
user_input = st.chat_input("Ask a question about the lease PDFs.")

transcribed_input = None

if st.button("🎤 Start Voice Prompt"):
    assistant = AI_Assistant()
    greeting = "Hi Ryan, please ask me any question you like"
    assistant.generate_audio(greeting)

   
    # transcribed_input = assistant.start_transcription() uncomment this line once assembly is purchased

    if transcribed_input:
        st.success(f"Transcribed: {transcribed_input}")
        user_input = transcribed_input 

# Set up the language model
client = OpenAI(api_key=OpenAI.api_key)

if user_input:
    if not lease_text:
        st.warning("Please upload PDFs first before asking questions.")
    else:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate AI response:
        response = client.chat.completions.create(
            model="gpt-4o",
            store=True,
            messages=[
                {"role": "system", "content": "You are an AI assistant that accurately answers questions about the lease PDFs. Do NOT answer any questions about lease commissions."},
                {"role": "user", "content": f"Here are the lease PDFs: {lease_text}\n\nUser question: {user_input}"}
            ]
        )
        ai_response = response.choices[0].message.content

        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})