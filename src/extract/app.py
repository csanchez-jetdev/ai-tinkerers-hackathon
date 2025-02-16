from dotenv import load_dotenv
import os

load_dotenv()

hugging_face_api_key = os.getenv('HUGGING_FACE_API_KEY')

from huggingface_hub import InferenceClient
client = InferenceClient(api_key=hugging_face_api_key)
reco = client.automatic_speech_recognition("./src/extract/sources/medecin.mp3")

print(reco.text)