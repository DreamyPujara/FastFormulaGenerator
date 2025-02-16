from langchain_cohere import CohereEmbeddings
import os
from dotenv import load_dotenv


load_dotenv()
COHERE_KEY = os.getenv("COHERE_KEY")

if not os.getenv("COHERE_API_KEY"):
    os.environ["COHERE_API_KEY"] = COHERE_KEY
def get_embedding_function():
    embeddings = CohereEmbeddings(
    model = "embed-english-v3.0",
)
    # embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings
