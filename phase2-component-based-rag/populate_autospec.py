import boto3
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction

CHROMA_PATH = "./chroma_db"
TAMANO = 500
SOLAPE = 100


def dividir(texto, tamano=TAMANO, solape=SOLAPE):
    chunks, inicio = [], 0
    while inicio < len(texto):
        chunks.append(texto[inicio : inicio + tamano])
        if inicio + tamano >= len(texto):
            break
        inicio += tamano - solape
    return chunks


embedding_function = AmazonBedrockEmbeddingFunction(
    session=boto3.Session(region_name="us-east-1"),
    model_name="amazon.titan-embed-text-v2:0",
)
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(
    "autospec_collection", embedding_function=embedding_function
)

archivos = [
    "modelo_alpha_ficha_tecnica.txt",
    "modelo_beta_ficha_tecnica.txt",
    "modelo_gamma_ficha_tecnica.txt",
]

for i, nombre in enumerate(archivos):
    with open(nombre, encoding="utf-8") as f:
        texto = f.read()
    chunks = dividir(texto)
    collection.upsert(
        ids=[f"{i}-{j}" for j in range(len(chunks))],
        documents=[f"Modelo: {nombre}\n{c}" for c in chunks],
        metadatas=[{"source": nombre} for _ in chunks],
    )
    print(f"{nombre}: {len(chunks)} fragmentos")

print(f"Colección lista con {collection.count()} fragmentos")
