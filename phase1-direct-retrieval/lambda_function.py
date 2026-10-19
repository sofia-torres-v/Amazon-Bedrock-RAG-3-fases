import os
import boto3

client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")


def lambda_handler(event, context):
    resp = client.retrieve(
        knowledgeBaseId=os.environ["KB_ID"],
        retrievalQuery={"text": event["prompt"]},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}},
    )

    resultados = []
    for i, r in enumerate(resp["retrievalResults"], start=1):
        resultados.append(
            {
                "n": i,
                "score": round(r["score"], 2),
                "texto": r["content"]["text"][:300],
            }
        )
    return resultados