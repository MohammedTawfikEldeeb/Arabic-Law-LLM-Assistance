import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Arabic Law LLM Inference API (Efficient)",
    description="Efficient API for Arabic Law Q&A using PEFT adapter.",
    version="2.0.0",
)

# Allow all origins (or customize as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use base model + adapter
BASE_MODEL = "unsloth/Qwen3-8B-Base"
ADAPTER_PATH = "Mohamed453/Arabic-Law-LoRA"

model = None
tokenizer = None

SYSTEM_PROMPT = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
Answer the following question in Arabic:

### Input:
{}

### Response:
{}"""

class QueryRequest(BaseModel):
    question: str

@app.on_event("startup")
async def load_model():
    global model, tokenizer

    try:
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

        print("Loading base model in 4-bit...")
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16,
            load_in_4bit=True,
            device_map="auto",
        )

        print("Loading PEFT adapter...")
        model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)

        model.eval()
        print("Model and adapter loaded successfully!")

    except Exception as e:
        print(f"Error loading model/adapter: {e}")

@app.get("/")
async def root():
    return {"message": "Arabic Law LLM Inference API is running!"}

@app.post("/predict")
async def predict_answer(request: QueryRequest):
    if model is None or tokenizer is None:
        return {"error": "Model not loaded. Please wait for startup."}

    question = request.question
    print(f"Received question: {question}")

    formatted_input = SYSTEM_PROMPT.format(question, "")
    try:
        inputs = tokenizer([formatted_input], return_tensors="pt").to(model.device)

        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=300,  # Reduced for speed and memory
            pad_token_id=tokenizer.eos_token_id,
        )

        response = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        generated_text = response[0]

        if "### Response:" in generated_text:
            final_answer = generated_text.split("### Response:")[1].strip()
        else:
            final_answer = generated_text.strip()

        print(f"Generated response: {final_answer}")
        return {"question": question, "answer": final_answer}

    except Exception as e:
        print(f"Inference error: {e}")
        return {"error": str(e)}
