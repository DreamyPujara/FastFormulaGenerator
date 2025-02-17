from langchain_chroma import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever

import json

# from model import llm
from get_embedding_function import get_embedding_function
from multi_retriever import MultiCollectionRetriever
from prompts import contextualize_q_prompt,qa_prompt
from model import llm

links = []
CHROMA_PATH = "chroma"

class AIModel:
    def __init__(self):
        self.rag_chain = self._setup_rag_chain()
        self.links = []


    def _setup_rag_chain(self):
        embedding_function = get_embedding_function()

        collection1 = Chroma(embedding_function=embedding_function,persist_directory=CHROMA_PATH)
        collection2 = Chroma(collection_name="docs_collection", embedding_function=embedding_function,persist_directory=CHROMA_PATH)
        collection3 = Chroma(collection_name="web_collection", embedding_function=embedding_function,persist_directory=CHROMA_PATH)

        retriever1 = collection1.as_retriever(search_kwargs={"k": 10})
        retriever2 = collection2.as_retriever(search_kwargs={"k": 5})
        retriever3 = collection3.as_retriever(search_kwargs={"k": 5})
        #db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
        #retriever = db.as_retriever(search_kwargs={"k": 2})
        multi_retriever = MultiCollectionRetriever(retriever1, retriever2,retriever3)

        contextualize_q_llm = llm.with_config(tags=["contextualize_q_llm"])

        history_aware_retriever = create_history_aware_retriever(
            contextualize_q_llm, multi_retriever, contextualize_q_prompt
        )

        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        return rag_chain
    
    def chat(self, query:str,chat_history):
        docs = []
        buffer = ""
        for chunk in self.rag_chain.stream({"input": query,"chat_history":chat_history}):
            if 'answer' in chunk:
                #print(chunk["answer"])
                buffer += chunk["answer"]
            else:
                #print(chunk)
                docs = chunk
        buffer = buffer.replace('```fastformula', '```SQL')
        buffer = buffer.replace('END IF;', '/*-- End of IF Statement --*/')
        buffer = buffer.replace('FORMULA NAME:', '--FORMULA NAME:')
        buffer = buffer.replace('FORMULA TYPE:', '--FORMULA TYPE:')
        buffer = buffer.replace('END IF', '/*-- End of IF Statement --*/')
        buffer = buffer.replace('END;', '')
        buffer = buffer.replace(';', '')
        buffer = buffer.replace(':=', '=')
        
        
        yield buffer
        sources = extract_page_links(docs)
        if sources:
            yield "\n\n### Sources:\n\n"
            for source in sources:
                yield f"* {source['source']} : Page {source['page']+1}\n\n"
                


def extract_page_links(obj):
    context = obj.get("context", [])
    page_links = [
    {'source':doc.metadata['source'],'page':doc.metadata['page']}
    for doc in context 
    if 'source' in doc.metadata and 'page' in doc.metadata
]
    #print(page_links)
    return page_links
        

        




