import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama,ChatOpenAI




load_dotenv()
OPEN_ROUTER_KEY = os.getenv("OPEN_ROUTER_KEY")
OLLAMA_HOST = os.getenv("")
OLLAMA_MODEL = os.getenv("")
OPEN_ROUTER_MODEL = os.getenv("OPEN_ROUTER_MODEL")
LOAD_MODEL = os.getenv("LOAD_MODEL")
print(OPEN_ROUTER_KEY)
# O_llm = ChatOllama(
#     model=OLLAMA_MODEL,
#     #base_url=OLLAMA_SERVER_URL,
#     base_url = OLLAMA_HOST,
#     temperature=0.7,
#     repeat_penalty=1.2,
#     num_ctx=4096,
#     num_predict=1200,
#     keep_alive=-1,
#     stream = True,
# )

OR_llm = llm = ChatOpenAI(
  openai_api_key=OPEN_ROUTER_KEY,
  openai_api_base="https://openrouter.ai/api/v1",
  model_name=OPEN_ROUTER_MODEL,
  max_retries=4
)

# model_map = {
#      "Ollama" :  None,
#      "OpenRouter":OR_llm 
# }

llm = OR_llm

def generate(prompt):
    messages = [("human", prompt),]
    ai_msg = llm.invoke(messages)
    print("AI msg: ", ai_msg)

    return ai_msg.content
