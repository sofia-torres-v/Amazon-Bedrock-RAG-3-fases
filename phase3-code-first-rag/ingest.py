import os
from dotenv import load_dotenv

# Carga la clave de la API desde el archivo .env guardado en tu carpeta
load_dotenv()

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

archivos = [
    "data/modelo_alpha_ficha_tecnica.txt",
    "data/modelo_beta_ficha_tecnica.txt",
    "data/modelo_gamma_ficha_tecnica.txt",
]

documentos = []
for nombre in archivos:
    with open(nombre, encoding="utf-8") as f:
        texto = f.read()
    documentos.append(Document(page_content=texto, metadata={"source": nombre}))

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_documents(documentos)

for c in chunks:
    c.page_content = f"[{c.metadata['source']}]\n{c.page_content}"

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=os.environ["GEMINI_API_KEY"],
)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_langchain",
    collection_name="autospec_collection_v3",
)

print(f"Colección lista con {vectorstore._collection.count()} fragmentos")
