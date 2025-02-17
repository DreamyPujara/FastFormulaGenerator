from langchain.schema import BaseRetriever
from pydantic import PrivateAttr
from reranker import re_rank

class MultiCollectionRetriever(BaseRetriever):
    _retriever1: BaseRetriever = PrivateAttr()
    _retriever2: BaseRetriever = PrivateAttr()

    def __init__(self, retriever1: BaseRetriever, retriever2: BaseRetriever, retriever3: BaseRetriever):
        super().__init__()
        self._retriever1 = retriever1
        self._retriever2 = retriever2
        self._retriever3 = retriever3

    def get_relevant_documents(self, query: str):
        print(f"get_relevant_documents --> query ---> {query}")
        docs1 = self._retriever1.get_relevant_documents(query)
        docs2 = self._retriever2.get_relevant_documents(query)
        docs3 = self._retriever3.get_relevant_documents(query)
        rr_doc1 = re_rank(3,docs1,query)
        rr_doc2 = []
        if (docs2 and len(docs2) > 0) or (docs3 and len(docs3) > 0) :
            rr_doc2 = re_rank(5,docs2 + docs3,query)
        rr_doc = rr_doc1
        if rr_doc2 and len(rr_doc2) > 0:
            rr_doc = re_rank(5,rr_doc1+rr_doc2,query)
        print(rr_doc)
        return rr_doc

    async def aget_relevant_documents(self, query: str):
        print(f"aget_relevant_documents --> query ---> {query}")
        docs1 = await self._retriever1.aget_relevant_documents(query)
        docs2 = await self._retriever2.aget_relevant_documents(query)
        docs3 = await self._retriever3.aget_relevant_documents(query)
        return docs1 + docs2 + docs3
