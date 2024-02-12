from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import os
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
import streamlit as st
from streamlit_chat import message
from src.DSAI_Utility.prompt import prompt_sql_agent

def SQL_DB_Agent():
    col11,col22,col33 = st.columns((2,8,2))

    llm = ChatOpenAI(model_name="gpt-4", api_key=os.environ["OPENAI_API_KEY"])
    db = SQLDatabase.from_uri()
    table_names = "\n".join(db.get_usable_table_names())
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=SQLDatabaseToolkit(db=db, llm=llm ),
        prompt=prompt_sql_agent(table_names),
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )
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
                
                user_input = st.text_input("Prompt:", placeholder="How can I help you?", key='input')
                submit_button = st.form_submit_button(label='Interact with LLM')
                
            if submit_button and user_input:
                # messages_history.append(HumanMessage(content=user_input))
                vAR_response = agent_executor.run(user_input)                   
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(vAR_response)

        if st.session_state['generated']:
                with response_container:
                    for i in range(len(st.session_state['generated'])):
                        message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                        message(st.session_state["generated"][i], key=str(i+55), avatar_style="thumbs")