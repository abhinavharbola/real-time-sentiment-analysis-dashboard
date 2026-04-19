# Downloads a pre-trained DistilBERT sentiment model and tokenizer
# saving them locally to ensure the backend API can start up instantly without internet access

import os
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def download_and_save_model(model_name="distilbert-base-uncased-finetuned-sst-2-english", save_path="./local_model"):
    print(f"Downloading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    os.makedirs(save_path, exist_ok=True)
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    print(f"Base model saved locally to {save_path}")

if __name__ == "__main__":
    download_and_save_model()