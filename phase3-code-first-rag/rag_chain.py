import os
from dotenv import load_dotenv

# Carga la clave del archivo .env de forma automática
load_dotenv()

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

PROMPT_TEMPLATE = """Eres un asistente experto en fichas técnicas automotrices.
A continuación tienes fragmentos, cada uno precedido por el archivo del que proviene:

{context}

Instrucciones: Responde ÚNICAMENTE con información de los fragmentos cuyo archivo
corresponda al modelo mencionado en la pregunta. Ignora por completo los fragmentos
de otros modelos. Si la información no aparece, responde exactamente:
'No tengo esa información en las fichas técnicas disponibles.' No inventes datos.

Pregunta: {question}"""


def get_rag_response(question):
    api_key = os.environ["GEMINI_API_KEY"]

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001", google_api_key=api_key
    )
    vectorstore = Chroma(
        persist_directory="./chroma_langchain",
        collection_name="autospec_collection_v3",
        embedding_function=embeddings,
    )
    resultados = vectorstore.similarity_search_with_score(question, k=8)
    contexto = "\n\n".join(doc.page_content for doc, _ in resultados)

    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", google_api_key=api_key)

    chain = ChatPromptTemplate.from_template(PROMPT_TEMPLATE) | llm | StrOutputParser()
    answer = chain.invoke({"context": contexto, "question": question})

    return answer, resultados
