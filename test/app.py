import streamlit as st
from streamlit_extras.stylable_container import stylable_container

from htmlTemplates import css, bot_template, user_template
import pysqlite3
import sys
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
from populate_database import populate,clear_database
from web_scrap import extract_link,clear_web_database


import os
from rag_chain import AIModel
import asyncio


aiModel = AIModel()

UPLOAD_FOLDER = "docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ai_model = AIModel()

async def handle_ai_response(query):
    async for chunk in ai_model.chat(query):
        if chunk:
            st.session_state.messages.append(("ai", chunk))
            with st.chat_message("ai"):
                st.write(chunk)


async def main():
    st.set_page_config(
    page_title="Velocity AI",
    page_icon="📘", # Set sidebar to collapsed by default
    layout="wide"
)
    
    st.title("Velocity Formula AI")
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Render existing messages
    for role, content in st.session_state.messages:
        with st.chat_message(role):
            st.markdown(content)
    with stylable_container(
        key="bottom_content",
        css_styles="""
            {
                position: fixed;
                bottom: 120px;
            }
            """,
    ):
        if st.checkbox("Include chat history"):
            st.session_state.is_chat_history = True
            
        else:
            st.session_state.is_chat_history = False
    # Handle user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to session state
        st.session_state.messages.append(("human", prompt))
        with st.chat_message("human"):
            st.markdown(prompt)

        # Generate and display assistant response
        if len(st.session_state.messages) > 0:
            with st.chat_message("ai"):
                #chat_history = st.session_state.messages[:-1]
                if st.session_state.is_chat_history:
                    lst = st.session_state.messages
                    chat_history = ([lst[-3],lst[-2]] if len(lst) > 2 else [])
                else:
                    chat_history = []
                print(chat_history)
                stream = ai_model.chat(st.session_state.messages[-1][1],chat_history)
                response = st.write_stream(stream)
                st.session_state.messages.append(("ai", response))
            

    option = st.sidebar.radio(
        "Choose an option:",
        ("Web Links", "PDFs")
    )

    if option == "Web Links":
        st.sidebar.subheader("Web Links")
        
        num_links = st.sidebar.number_input("Number of Links", min_value=1, max_value=10, value=1, step=1)
        links = []

        for i in range(num_links):
            link = st.sidebar.text_input(f"Web Link {i + 1}:")
            if link:
                links.append(link)

        if st.sidebar.button("Extract Links"):
            if links:
                with st.spinner("Extracting..."):
                    for link in links:
                        extract_link(link)
                st.sidebar.success("Data Extracted from web links")
                links.clear() 
                num_links=1
                st.rerun()
            else:
                st.sidebar.warning("Please enter at least one link.")

        if os.path.exists("web_links/links.py") and os.path.isfile("web_links/links.py"):
            with open("web_links/links.py", 'r') as file:
                lines = file.readlines()
                link_lines = [line for line in lines if line.strip().startswith("#")]
                if link_lines:
                    st.sidebar.write("Using WebLinks")
                    
                    if st.sidebar.button("Clear Links"):
                        clear_web_database()
                        with open("web_links/links.py", 'w') as file:
                            pass  
                        st.sidebar.success("All links have been cleared!")
                else:
                    st.sidebar.info("No links found in the file.")
        else:
            st.sidebar.warning("File does not exist.")

    elif option == "PDFs":
        st.sidebar.subheader("Your PDFs")
        
        if os.path.exists(UPLOAD_FOLDER) and os.path.isdir(UPLOAD_FOLDER):
            pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.pdf')]
            if len(os.listdir(UPLOAD_FOLDER)) > 0:
                for pdf in pdf_files:
                    st.sidebar.write(pdf)
                if st.sidebar.button("Clear PDFs"):
                    clear_database()
                    st.sidebar.success("PDFs cleared!")
                    st.rerun()
            else:
                st.sidebar.warning("No PDFs found in the directory.")
        
        pdf_docs = st.sidebar.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.sidebar.button("Process"):
            with st.spinner("Uploading"):
                if pdf_docs:
                    for pdf in pdf_docs:
                        file_path = os.path.join(UPLOAD_FOLDER, pdf.name)
                        with open(file_path, "wb") as f:
                            f.write(pdf.read())
                else:
                    st.sidebar.warning("No files uploaded!")

            with st.spinner("Extracting Data"):
                populate()  
                st.sidebar.success(f"Extracted data from PDFs successfully!")
                st.rerun()



if __name__ == '__main__':
    asyncio.run(main())

