import os
import requests
from functools import lru_cache

HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    raise ValueError("HF_API_KEY not set in environment")

MODEL_SUMMARY = "facebook/bart-large-cnn"
HF_URL = f"https://api-inference.huggingface.co/models/{MODEL_SUMMARY}"

def summarize_text(text:str) -> str:
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs" : text}
    response = requests.post(HF_URL,headers=headers, json = payload, timeout = 60)
    response.raise_for_status()
    data = response.json()
    return data[0]["summary_text"]

def generate_pitch(prompt:str) -> str:
    model_id = "mistralai/Mistral-7B-Instruct-v0.2"
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 300}}
    print("hellooo1")
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    print("response")
    response.raise_for_status()
    print("hellooo3")
    data = response.json()
    print("hellooo4")
    return data[0]["generated_text"]
    
    

