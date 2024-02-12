import streamlit as st
from streamlit_chat import message
import time
from openai import OpenAI
import os



ASSISTANT_ID = os.environ["ASSISTANT_ID"]


def CalpersAssistant():
    if 'history_as' not in st.session_state:
        st.session_state['history_as'] = []

    if 'generated_as' not in st.session_state:
        st.session_state['generated_as'] = ["Greetings! I am Calpers Live Agent. How can I help you?"]

    if 'past_as' not in st.session_state:
        st.session_state['past_as'] = ["We are delighted to have you here in the Calpers Live Agent Chat room!"]
        

    #container for the chat history
    response_container = st.container()
    
    #container for the user's text input
    container = st.container()
    with container:
        with st.form(key='my_form', clear_on_submit=True):
            
            user_input = st.text_input("Prompt:", placeholder="How can I help you?", key='input')
            submit_button = st.form_submit_button(label='Interact with LLM')
            
        if submit_button and user_input:
            # messages_history.append(HumanMessage(content=user_input))
            vAR_response = conversation_for_FAQ(user_input)                    
            st.session_state['past_as'].append(user_input)
            st.session_state['generated_as'].append(vAR_response)

    if st.session_state['generated_as']:
            with response_container:
                for i in range(len(st.session_state['generated_as'])):
                    message(st.session_state["past_as"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                    message(st.session_state["generated_as"][i], key=str(i+55), avatar_style="thumbs")








def conversation_for_FAQ(user_input):
    if 'client' not in st.session_state:
        st.session_state.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        
        # Create a Thread
        st.session_state.thread = st.session_state.client.beta.threads.create()

    message = st.session_state.client.beta.threads.messages.create(thread_id=st.session_state.thread.id,role="user",content=user_input)
    run = st.session_state.client.beta.threads.runs.create(thread_id=st.session_state.thread.id,assistant_id=ASSISTANT_ID)
    # run = client.beta.threads.runs.create(thread_id=thread.id,assistant_id=assistant.id,run_id=run.id)
    a = 0
    while True:
        run = st.session_state.client.beta.threads.runs.retrieve(thread_id=st.session_state.thread.id, run_id=run.id)
        time.sleep(2)
        print(run.status)
        a = a+1
        print(a)
        if run.status=="completed":
            messages = st.session_state.client.beta.threads.messages.list(thread_id=st.session_state.thread.id)
            print("response$$ - ",messages)
            latest_message = messages.data[0]
            text = latest_message.content[0].text.value
            return text
        




def ReadCitation(client):

    # Retrieve the message object
    message = client.beta.threads.messages.retrieve(
    thread_id="...",
    message_id="..."
    )

    # Extract the message content
    message_content = message.content[0].text
    annotations = message_content.annotations
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index}]')

        # Gather citations based on annotation attributes
        if (file_citation := getattr(annotation, 'file_citation', None)):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            cited_file = client.files.retrieve(file_path.file_id)
            citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
            # Note: File download functionality not implemented above for brevity

    # Add footnotes to the end of the message before displaying to user
    message_content.value += '\n' + '\n'.join(citations)