import re
import requests
from bs4 import BeautifulSoup
import nltk
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma
#url = 'https://apps2fusion.com/old/oracle-fusion-online-training/fusion-applications/fusion-payroll/1198-global-absence-accrual-fast-formula-a-sample-example'

nltk.download('punkt')
custom_keywords = ["default", "get_context","to_date","days_between"]

def scrape_article(url,keywords):
    response = requests.get(url,verify=False)
    sentences = []
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        sections = soup.find_all(['section', 'div'])
        for idx, section in enumerate(sections, start=1):
            section_text = section.get_text(separator='\n', strip=True)
            if any(keyword.lower() in section_text.lower() for keyword in keywords):
                if(len(section_text)<2000):
                    cleaned_text = clean_text(section_text)
                    sentences.append(cleaned_text)
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
    return sentences

def clean_text(text):
    text = text.replace("\_","_")
    cleaned_text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    cleaned_text = re.sub(r'/\*=={.*?}==\*/', '', cleaned_text)
    # pattern = r'/\*+([\s\S]*?)\*+/'
    # cleaned_text = re.sub(pattern, r'/*\n\1\n*/', cleaned_text)
    return cleaned_text

def extract_link(url, keywords = custom_keywords):
    sentences = scrape_article(url,keywords)
    # for sentence in sentences:
    #     print("=====>",sentence,"\n\n")
    add_to_chroma(sentences,url)
    with open("web_links/links.py", 'r') as file:
        lines = file.readlines()
    
    lines.insert(0, f"#{url}\n")
    
    with open("web_links/links.py", 'w') as file:
        file.writelines(lines)
    return True

def add_to_chroma(sentences, source_url):
    vectorstore = Chroma(collection_name="web_collection",persist_directory="chroma", embedding_function=get_embedding_function())
    documents = [
        Document(
            page_content=sentence,
            metadata={"source": source_url}
        ) for sentence in sentences
    ]
    
    vectorstore.add_documents(documents)
    print("Documents added to ChromaDB successfully.")

def clear_web_database():
    db = Chroma(
        collection_name="web_collection",persist_directory="chroma", embedding_function=get_embedding_function()
    )
    db.delete_collection()



url="https://docs.oracle.com/en/cloud/saas/human-resources/24d/oapff/global-absence-accrual-matrix.html#Sample-Formula"
#url = 'https://apps2fusion.com/old/oracle-fusion-online-training/fusion-applications/fusion-payroll/1198-global-absence-accrual-fast-formula-a-sample-example'


# def clean_text(text):
#     text = text.replace("\_","_")
#     cleaned_text = re.sub(r'\[.*?\]\(.*?\)', '', text)
#     cleaned_text = re.sub(r'/\*=={.*?}==\*/', '', cleaned_text)
#     # pattern = r'/\*+([\s\S]*?)\*+/'
#     # cleaned_text = re.sub(pattern, r'/*\n\1\n*/', cleaned_text)
#     return cleaned_text


# def extract_sentences_with_keywords(text, keywords):
#     sentences = sent_tokenize(text)
#     keywords = [keyword.lower() for keyword in keywords]
#     relevant_sentences = [
#         sentence for sentence in sentences
#         if any(keyword in sentence.lower() for keyword in keywords)
#     ]
#     return relevant_sentences
