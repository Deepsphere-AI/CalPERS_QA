import streamlit as vAR_st
vAR_st.set_page_config(page_title="Calpers Assistant", layout="wide")

from src.DSAI_Utility.Sidemenu_initialization import All_Initialization,CSS_Property
from src.DSAI_source_code.DSAI_QA_Langchain.DSAI_QALangchain import QAwithLangchain
from src.DSAI_source_code.DSAI_SQL_Agent.DSAI_SQL_agent import SQL_DB_Agent
from src.DSAI_source_code.DSAI_PDF_File_URL_Conversion.pdf_file_url_conversion import url_pdf_file_conversation
from src.DSAI_source_code.DSAI_Assistant.dsai_assistant import CalpersAssistant

if __name__=='__main__':
    vAR_hide_footer = """<style>
            footer {visibility: hidden;}
            </style>
            """
    vAR_st.markdown(vAR_hide_footer, unsafe_allow_html=True)
    # Applying CSS properties for web page
    CSS_Property("src/DSAI_Utility/DSAI_style.css")
    # Initializing Basic Componentes of Web Page
    choice = All_Initialization()
 
    if choice=="Policy Q&A (PDF File)":

        # function to call QA langchain
        QAwithLangchain() 
        
        
    if choice=="Transactional Q&A (Database)":

        #function to call SQL DB Agent
        SQL_DB_Agent()

    if choice == "Job Aid Q&A (URL)":
        url_pdf_file_conversation()

    if choice =="Calpers Law Enquiry":

        print("Calling calpers assistant")
        CalpersAssistant()