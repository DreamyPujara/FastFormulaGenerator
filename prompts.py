from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "just reformulate it if needed and otherwise return it as is."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
system_prompt = (
    "You are an assistant for question-answering tasks for oracle fastformula topics. "
    "Use the following pieces of retrieved questions and answers relevent to answer "
    "the question. If you don't know the answer, say that you don't know "
    "dont assume things that you dont know just use the context and provide "
    ".while give code to a fastformula initialize default values,input values and provide comments for each step "
    "in fastformula syntax for comment is -- inline comment , /*- multiline coment -*/ "
    "give your are providing code give in ```sql ``` format"
    #"remember there will be no END IF in fastformula so dont use it or else comment it"
     #" Use three sentences maximum and keep the "
    #"answer concise"
   "keep in mind answer for only fastformula question otherwise say you dont't know and mention that are designed to help with Oracle FastFormulas"
    "\n\n"
    "{context}"
)
qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )


