import boto3
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction

CHROMA_PATH = "./chroma_db"
MODEL_ID = "us.amazon.nova-2-lite-v1:0"


def get_collection():
    ef = AmazonBedrockEmbeddingFunction(
        session=boto3.Session(region_name="us-east-1"),
        model_name="amazon.titan-embed-text-v2:0",
    )
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_collection("autospec_collection", embedding_function=ef)


def get_rag_response(question):
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    results = get_collection().query(query_texts=[question], n_results=8)
    documentos = results["documents"][0]
    fuentes = [m["source"] for m in results["metadatas"][0]]
    fragmentos = [f"[{s}]\n{d}" for s, d in zip(fuentes, documentos)]
    contexto = "\n\n".join(fragmentos)

    message = {
        "role": "user",
        "content": [
            {
                "text": "Eres un asistente experto en fichas técnicas automotrices. A continuación tienes fragmentos de distintas fichas técnicas, cada uno precedido por el archivo del que proviene:"
            },
            {"text": contexto},
            {
                "text": "Instrucciones: Responde ÚNICAMENTE con información de los fragmentos cuyo archivo corresponda al modelo mencionado en la pregunta. Ignora por completo los fragmentos de otros modelos. Si la información solicitada no aparece en esos fragmentos, responde exactamente: 'No tengo esa información en las fichas técnicas disponibles.' No inventes ni completes datos que no estén en el contexto."
            },
            {"text": f"Pregunta: {question}"},
        ],
    }
    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[message],
        inferenceConfig={"maxTokens": 2000},
    )
    return response["output"]["message"]["content"][0]["text"], fragmentos
