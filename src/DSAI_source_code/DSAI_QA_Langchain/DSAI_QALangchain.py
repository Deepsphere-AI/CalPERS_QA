from langchain.document_loaders import PyPDFLoader
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from streamlit_chat import message
import os
import streamlit as st
import time

# os.environ["OPENAI_API_KEY"] = "" # Update with your API key
os.environ["OPENAI_API_KEY"]

messages = []

def input_fields():

    '''
    This function is to get the input file from the user. The file type here is pdf.

    return:
        This would return success message on uploading the correct formate of the file.
    '''
        
    st.session_state.source_docs = st.file_uploader(label="LLM Knowledgebase Upload", type="pdf", accept_multiple_files=True)
    
    if st.session_state.source_docs:
        st.success("Knowledge base file(s) successfully uploaded!")

def process_documents():
    '''
    This function is to process the uploaded document. It would use the pdf loader to read the uploaded file and convert it to a list.
    If there are multiple files, all the content in each files are append to the same list.

    return: 
        This function would store the list of words in documents to session_state.retriever
    '''
    if st.session_state.source_docs:
        file_list = []
        documents=[]
        loader_pdf_list=[]
        
        for source_doc in st.session_state.source_docs:
            # iterate each file to add to the list
            file_list.append("input_"+source_doc.name)
            with open("input_"+source_doc.name, mode='wb') as w:
                w.write(source_doc.getvalue())
    
        for source_doc in file_list:
            #iterate each file to load to pdfloader and extract the content
            loader_pdf = PyPDFLoader(source_doc)
            loader_pdf_list.append(loader_pdf)
            #add the content to the list datatype documents
            documents.extend(loader_pdf.load())
            st.session_state.retriever_doc = documents
    else:
        # st.warning(f"Please upload the documents")
        pass
        
def conversational_retrieval_chain(retriever):
    '''
    This function split the text into chunks, store the text in chroma db, and retrive it. Also, works with conversational
    retrival chain.

    args:
        retriever: list of text from document
    
    return:
        Store the conversational retrieval chain object in st.session_state.qachain
    '''
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    # texts=text_splitter.split_documents(documents)
    texts=text_splitter.split_documents(retriever)
    
    #create an open source embedding function
    embeddings=OpenAIEmbeddings()
    
    #load embeddings and texts to chroma
    vAR_db=Chroma.from_documents(texts, embeddings)
    #retrive from chroma using search_type similarity 
    retriever=vAR_db.as_retriever(search_type="similarity", search_kwargs={"k":3})
    #chain for having a conversation based on retrived documents. 
    vAR_qa = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(model_name="gpt-3.5-turbo",temperature=0),
         retriever=retriever,
         return_source_documents=True)
    # qa = ConversationalRetrievalChain.from_llm(OpenAI(), retriever, return_source_documents=True)
    st.session_state.qachain = vAR_qa
    
def query_llm(user_input):
    '''
    This function queries to retrive the relevant answer to the query.

    args:
        user_input: Questions and follow up questions asked by the user

    return:
        Returns answer for the query along with cititation where it can be found in the uploaded documents
    '''
    vAR_qa_chain = st.session_state.qachain
    vAR_query = user_input
    #query also pass the chat history
    vAR_result_queries=vAR_qa_chain({"question":vAR_query, "chat_history":st.session_state.messages})
    #add the queries to the chat history
    st.session_state.messages.append((vAR_query, vAR_result_queries["answer"]))
    #return the answer for the query with citation
    return vAR_result_queries["answer"]+"\t CITATION : "+str(vAR_result_queries["source_documents"][0].metadata)
    
def QAwithLangchain():
    '''
    This is the main function to display the queries and their repective answers. This function calls processing document function, 
    and other llm function to storing and retrive the answers.
    '''
    start = time.time()
    start_time1 = time.time()
    input_fields()
    print('input file read - ',time.time()-start_time1)
    submit_button = False
    

    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'qachain' not in st.session_state:
        st.session_state.qachain = None
    if 'retriever' not in st.session_state:
        st.session_state.retriever = None        
    if 'source_docs' not in st.session_state:
        st.session_state.source_docs = None
    
    start_time2 = time.time()
    if not st.session_state.retriever:
        with st.spinner("Processing files!"):
            process_documents()
    
    print('input file process - ',time.time()-start_time2)
    
    if 'generated' not in st.session_state:
        if st.session_state.source_docs:
            st.session_state['generated'] = ["Ask your question here"]

    if 'past' not in st.session_state:
        if st.session_state.source_docs:
            st.session_state['past'] = ["We're delighted to have you in our calPERS Retirement System Live Agent Chat room!"]
    
    container1 = st.container()
    container2 = st.container()
    
    
    start_time3 = time.time()
    with container2:
        if st.session_state.source_docs:
            with st.form(key='my_form ', clear_on_submit=True):
                if st.session_state.retriever_doc:
                    #get the input from the user
                    user_input = st.text_input("Prompt:", placeholder="What information are you looking for?", key='user_input')
                    if st.session_state.qachain is None:
                        #call the conversational retrival chain
                        conversational_retrieval_chain(st.session_state.retriever_doc)
                    #pass the user input for querying the llm
                    response = query_llm(user_input)

                    # Add custom CSS for the button
                    st.write(
                        """
                        <style>
                        .stButton button {
                            background-color: #007bff; /* Replace with your desired background color */
                            color: #fff; /* Text color */
                            border: none; /* Remove the default button border */
                            padding: 10px 20px; /* Adjust padding as needed */
                            border-radius: 5px; /* Add rounded corners */
                            cursor: pointer;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    submit_button = st.form_submit_button(label='Interact with LLM')
                    
                    if submit_button and user_input:
                        #append the question
                        st.session_state['past'].append(user_input)
                        #append the answer
                        st.session_state['generated'].append(str(response))
    print('query llm response - ',time.time()-start_time3)
    if 'generated' in st.session_state:         
        if st.session_state['generated']:
            with container1:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i],is_user=True, key=str(i) + '_user ', avatar_style="big-smile")
                    message(st.session_state["generated"][i], key=str(i), avatar_style="thumbs")
    print('overall time - ',time.time()-start)      
    
    
