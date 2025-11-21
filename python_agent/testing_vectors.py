from langchain_core.vectorstores import InMemoryVectorStore
import os
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore(embeddings)

# add sample_tweets/file1.txt and sample_tweets/file2.txt to the vector store
for filename in os.listdir("sample_tweets"):
    if filename.endswith(".txt"):
        with open(os.path.join("sample_tweets", filename), "r") as f:
            content = f.read()
            doc = Document(page_content=content, metadata={"source": filename})
            vector_store.add_documents([doc])

similar_docs = vector_store.similarity_search("blue", k=2)
print(similar_docs)