from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import pickle
from datetime import datetime
import time


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        total_time = time.time() - start_time
        return result

    return wrapper


class rag:
    def __init__(self, text_chunks, vector_db):
        self.text = text_chunks
        self.api = 'AIzaSyBcro2ScpI592K-IV5jhQEzO2Qv8X0wjf0'
        self.vector_db = vector_db

    def get_texts(self):
        return self.text

    def load_vector_db(self):
        genai.configure(api_key=self.api)
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=self.api)
        vector_store = FAISS.from_texts(self.text, embedding=embeddings)
        vector_store.save_local(self.vector_db)
        # new_db.save_local(self.vector_db)
        # new_db = FAISS.load_local(self.vector_db, embeddings, allow_dangerous_deserialization=True)
        # new_db.merge_from(vector_store)
        # new_db.save_local(self.vector_db)

    def get_conversational_chain(self):
        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
        provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
        Context:\n {context}?\n
        Question: \n{question}\n

        Answer:
        """
        model = ChatGoogleGenerativeAI(model="gemini-pro",
                                       temperature=0.3, google_api_key=self.api)

        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

        return chain

    @measure_time
    def user_input(self, query):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=self.api)
        vector_db = FAISS.load_local(self.vector_db, embeddings, allow_dangerous_deserialization=True)
        similar_docs = vector_db.similarity_search(query)
        chain = self.get_conversational_chain()

        response = chain.invoke(
            {"input_documents": similar_docs, "question": query}
            , return_only_outputs=True)

        print(response)

    def start(self):
        self.load_vector_db()
        while True:
            user_question = input("ask question")

            self.user_input(user_question)


if __name__ == '__main__':
    text = '''
    Panisha's AAdhar number is 334591488370
    Veerababu's PAN number is DWMPB5377N
    Avinash's PAN number is EWGPB8035L
    Avinash's Academics number is 1608124924
    '''
    texts = [text]
    rag(texts, "qfaiss_index").start()
