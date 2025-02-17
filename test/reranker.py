import cohere
import os
from dotenv import load_dotenv


load_dotenv()
COHERE_KEY = os.getenv("COHERE_KEY")

co = cohere.ClientV2(COHERE_KEY)
import json

def re_rank(n,documents,query):
    if(len(documents) == 0): return []
    print("n=====>",n)
    text_array = [doc.page_content for doc in documents]
    response = co.rerank(
        model="rerank-v3.5",
        query= query,
        documents=text_array,
        top_n=n,
    )
    response_json = response.json()
    parsed_response = json.loads(response_json)

# Extract indexes
    indexes = [result["index"] for result in parsed_response["results"]]
    filtered_documents = [documents[i] for i in indexes]
    return filtered_documents
