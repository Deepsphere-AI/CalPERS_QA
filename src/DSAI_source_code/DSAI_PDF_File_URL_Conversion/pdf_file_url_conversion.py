import streamlit as st
import requests
from src.DSAI_Utility.download_file import download_pdf_file
from src.DSAI_Utility.Assistant_API import conversation_for_FAQ
from streamlit_chat import message


def url_pdf_file_conversation():
    
    col1,col2,col3,col4 = st.columns((2,2.5,3.5,2))
    col11,col22,col33 = st.columns((2,8,2))
    
    with col2:
        st.write('# ')
        st.write('### ')
        st.markdown("<p style='text-align: left; color: black; font-size:20px;'><span style='font-weight: bold'>Model Input Type</span></p>", unsafe_allow_html=True)
    with col3:
        st.write('## ')
        vAR_URL = st.text_input(" ", placeholder="Enter URL")     
        
    if vAR_URL:
        vAR_directory,vAR_num_pages = download_pdf_file(vAR_URL)
        
        with col22:
            st.write('# ')
            st.write('# ')
            ########################################### chatbot UI###############################################
            if 'history' not in st.session_state:
                    st.session_state['history'] = []

            if 'generated' not in st.session_state:
                st.session_state['generated'] = ["Greetings! I am DeepSphere Live Agent. How can I help you?"]

            if 'past' not in st.session_state:
                st.session_state['past'] = ["We are delighted to have you here in the DeepSphere Live Agent Chat room!"]
            
            #container for the chat history
            response_container = st.container()
            
            #container for the user's text input
            container = st.container()
            with container:
                with st.form(key='my_form', clear_on_submit=True):
                    
                    user_input = st.text_input("(Prompt) Ask Your Question:", placeholder="How can I help you?", key='input')
                    submit_button = st.form_submit_button(label='Interact with LLM')
                    
                if submit_button and user_input:
                    # messages_history.append(HumanMessage(content=user_input))
                    vAR_response = conversation_for_FAQ(user_input,vAR_directory,vAR_num_pages)               
                    st.session_state['past'].append(user_input)
                    st.session_state['generated'].append(vAR_response)

            if st.session_state['generated']:
                    with response_container:
                        for i in range(len(st.session_state['generated'])):
                            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                            message(st.session_state["generated"][i], key=str(i+55), avatar_style="thumbs")