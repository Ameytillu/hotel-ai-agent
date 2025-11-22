import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# ---------- Config ----------
API_KEY = os.getenv("API_KEY", "changeme")  # set in env for real usage
MODEL_PATH = os.getenv("PHI_MODEL_PATH", r"D:\phi_finetuned_full_model")  # change if needed

# ---------- Load model once ----------
print(f"[INFO] Loading model from: {MODEL_PATH}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    device_map="auto",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    trust_remote_code=True,
)
model.eval()
print("[INFO] Model loaded.")

# ---------- FastAPI ----------
app = FastAPI(title="Phi Hotel Agent API", version="1.0.0")

class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 220
    temperature: float = 0.7
    top_p: float = 0.95
    stop_at_assistant: bool = True     # trims to first assistant reply style

class GenerateResponse(BaseModel):
    response: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest, x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Simple “guest → assistant” formatting (matches your fine-tune style)
    prompt = req.prompt
    if not ("Assistant:" in prompt):
        prompt = f"Guest: {prompt}\nAssistant:"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=req.max_new_tokens,
            do_sample=True,
            temperature=req.temperature,
            top_p=req.top_p,
            pad_token_id=tokenizer.eos_token_id,
        )

    decoded = tokenizer.decode(output[0], skip_special_tokens=True)

    if req.stop_at_assistant:
        # extract only the assistant's first reply
        reply = decoded.split("Assistant:", 1)[-1].split("Guest:", 1)[0].strip()
    else:
        reply = decoded

    return GenerateResponse(response=reply)
