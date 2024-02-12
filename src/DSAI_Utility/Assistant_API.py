import streamlit as st
import os
from openai import OpenAI
from src.DSAI_Utility.prompt import prompt
from dotenv import load_dotenv
import os


# Openai Assistant API
def conversation_for_FAQ(user_input,vAR_directory,vAR_num_pages):
    if 'client' not in st.session_state:
        st.session_state.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        st.session_state.file = st.session_state.client.files.create(
            file=open(vAR_directory, "rb"),
            purpose='assistants'
        )
        st.session_state.assistant = st.session_state.client.beta.assistants.update(
        os.environ["calPERS_FAQ"],
        instructions=prompt(vAR_num_pages),
        name="calPERS_FAQ",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
        file_ids=[st.session_state.file.id],
        )
        
        # Create a Thread
        st.session_state.thread = st.session_state.client.beta.threads.create()

    message = st.session_state.client.beta.threads.messages.create(thread_id=st.session_state.thread.id,role="user",content=user_input,file_ids=[st.session_state.file.id])
    run = st.session_state.client.beta.threads.runs.create(thread_id=st.session_state.thread.id,assistant_id=st.session_state.assistant.id)
    # run = client.beta.threads.runs.create(thread_id=thread.id,assistant_id=assistant.id,run_id=run.id)
    
    while run.status!="completed":
        run = st.session_state.client.beta.threads.runs.retrieve(thread_id=st.session_state.thread.id, run_id=run.id)


    messages = st.session_state.client.beta.threads.messages.list(thread_id=st.session_state.thread.id)
    latest_message = messages.data[0]
    text = latest_message.content[0].text.value   

    # # Retrieve the message object
    # message_content = latest_message.content[0].text
    # print(message_content)
    # annotations = message_content.annotations
    # print(annotations)
    # citations = []
    
    # full_response = process_message_with_citations(message_content,annotations,citations,vAR_directory)
    
    print('response - ',text)
    
    # print("Full Response - ",full_response)
    return text


  
# Define the function to process messages with citations
def process_message_with_citations(message_content,annotations,citations,vAR_directory):

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        print(annotations)
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index}]')

        # Gather citations based on annotation attributes
        if (file_citation := getattr(annotation, 'file_citation', None)):
            # Retrieve the cited file details (dummy response here since we can't call OpenAI)
            # cited_file = {'filename': 'vAR_directory'}  # This should be replaced with actual file retrieval
            # citations.append(f'[{index + 1}] {file_citation.quote} from {cited_file["filename"]}')
            print(file_citation.file_id)
            print(file_citation.quote)           
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            # Placeholder for file download citation
            cited_file = client.files.retrieve(file_path.file_id)
            citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
            # cited_file = {'filename': 'vAR_directory'}  # This should be replaced with actual file retrieval
            # citations.append(f'[{index + 1}] Click [here](#) to download {cited_file["filename"]}')  # The download link should be replaced with the actual download path

    # Add footnotes to the end of the message content
  
    full_response = str(message_content) + "\n\n" + "\n".join(citations)
    return full_response