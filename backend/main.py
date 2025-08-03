import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn
import os


app = FastAPI(
    title="Arabic Law LLM Inference API",
    description="API for the fine-tuned Qwen3-8B-Base model on Arabic legal questions.",
    version="1.0.0",
)

origins = [
    "http://localhost",
    "http://localhost:3000", 
    "http://127.0.0.1:5500", 
    "null", 
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_ID = "Mohamed453/Arabic-Law-Meta-Qwen3-8B-Base" 

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
    """
    Load the model and tokenizer when the FastAPI application starts up.
    This prevents reloading the model for every request.
    The original code had an issue with 'device_map' and 'offload_folder'.
    This fix simplifies the loading process by explicitly moving the model
    to the correct device after initialization.
    """
    global model, tokenizer
    print(f"Loading model: {MODEL_ID}...")
    try:
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)


        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16, 
        ).to(device) 

        model.eval() 

        print("Model and tokenizer loaded successfully!")
    except Exception as e:
        print(f"Error loading model or tokenizer: {e}")
        
@app.get("/")
async def root():
    """
    Root endpoint for a simple health check.
    """
    return {"message": "Arabic Law LLM Inference API is running!"}

@app.post("/predict")
async def predict_answer(request: QueryRequest):
    """
    Predicts an answer to an Arabic legal question using the fine-tuned LLM.

    Args:
        request (QueryRequest): A Pydantic model containing the 'question' string.

    Returns:
        dict: A dictionary containing the original question and the model's response.
    """
    if model is None or tokenizer is None:
        return {"error": "Model not loaded. Please wait for startup or check logs."}

    question = request.question
    print(f"Received question: {question}")

    # Format the input using the system prompt
    formatted_input = SYSTEM_PROMPT.format(question, "")

    try:
   
        inputs = tokenizer([formatted_input], return_tensors="pt").to(model.device)

        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=600, # Max tokens for the generated response
            pad_token_id=tokenizer.eos_token_id, # Important for generation
        )

       
        response = tokenizer.batch_decode(outputs, skip_special_tokens=True)

        
        generated_text = response[0]
        
        if "### Response:" in generated_text:
            final_answer = generated_text.split("### Response:")[1].strip()
        else:
            final_answer = generated_text.strip() # Fallback if split doesn't work as expected

        print(f"Generated response: {final_answer}")
        return {"question": question, "answer": final_answer}

    except Exception as e:
        print(f"Error during inference: {e}")
        return {"error": f"An error occurred during inference: {str(e)}"}

