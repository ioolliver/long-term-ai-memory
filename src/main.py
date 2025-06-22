from google import genai, generativeai
import os
import weaviate
from weaviate.collections.classes.grpc import MetadataQuery
from memorySchema import createMemoryCollection, COLLECTION_NAME
import json

try:
    geminiClient = genai.Client(api_key=os.environ["API_KEY"])
except Exception as e:
    print(f"Error initializing Gemini client: {e}")

weaviateClient = weaviate.connect_to_local()
generativeai.configure(api_key=os.environ["API_KEY"])
model = generativeai.GenerativeModel("gemini-2.0-flash")


if not weaviateClient.collections.exists(COLLECTION_NAME):
    print("Creating Memory collection...")
    createMemoryCollection(weaviateClient)

def embedPrompt(prompt: str) -> list[float]:
    result = geminiClient.models.embed_content(model='gemini-embedding-exp-03-07', contents=prompt)
    return result.embeddings[0].values

def sendPrompt(prompt: str, extra_info):
    finalPrompt = f"""
    The user sent a prompt: "{prompt}"

    Here are some informations that you may need to answer the prompt: []

    If you think you have enough information to answer the prompt, you can answer it directly. Otherwise, you can ask for more information or clarify the prompt.

    Return a JSON object with the following keys:
    - needed_info: a list with info that you may need. If no info is needed, return an empty list. Example, if the users asks "what is my name", you would need info "userName"
    - store_info: extract info that you may need in the future. It should be an matriz:
        - The first column is a shortDescription
        - The second column is a mediumDescription
        - The third column is a longDescription
    Example of store_info: if the user says it name is "John", you would store info [["John", "User name is John", "The user provided that his name is John."]]
    - answer: If you need no extra info, return you answer here. If you need extra info, returns null.
    """
    response = model.generate_content(finalPrompt,
        generation_config={"response_mime_type": "application/json"}
    )
    response = json.loads(response.text)

    print(response)

    if response['answer']:
        return response['answer']
    else:
        return "nothing"

def getNearVectors(vector: list[float]):
    memory_collection = weaviateClient.collections.get(COLLECTION_NAME)
    response = memory_collection.query.near_vector(
        near_vector=vector,
        limit=30,
        return_properties=["shortDescription"],
        return_metadata=MetadataQuery(distance=True)
    )
    print(f"Found {len(response.objects)} memories.")

    return response

while True:
    prompt = input("Enter your prompt: ")
    prompt_vector = embedPrompt(prompt)
    near_vectors = getNearVectors(prompt_vector)
    response = sendPrompt(prompt, near_vectors)
    print(response)
