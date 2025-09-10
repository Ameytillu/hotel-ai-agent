# model_loader.py

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def load_phi_model(model_path="D:/your_model_directory"):
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )
    return tokenizer, model
