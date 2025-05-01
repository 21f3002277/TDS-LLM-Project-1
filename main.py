# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "fastapi",
#   "httpx",
#   "uvicorn",
#   "requests",
#   "numpy",
#   "pillow",
#   "duckdb",
#   "bs4",
#   "markdown",
# ]
# ///

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
import re
import asyncio
import logging
import uvicorn
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment token
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

async def llm(system_prompt: str, user_prompt: str) -> str:
    """
    System prompt and user prompt are concatenated and sent to the LLM.
    Call GPT-4o-Mini via AI Proxy.
    
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {AIPROXY_TOKEN}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    

system_prompt = """

You are an advanced Automation Agent, The user will provide a task description.
Write `bash` or `python` scripts to execute the task. Follow these guidelines strictly:
1. **CODING RULES:**
    - uv, the Python runner, is ALREADY installed. Run with `uv run [URL] [ARGUMENTS]`
    - Parse dates with `python-dateutil`
    - Sender email is in the `From: "Name <email@...>` header
    - if the task is to extract the sender's email address,Returns only(e,g., "email@...") do not include any other text in the output file only email.
    - if the task is to extract only the card number from this image of a dummy credit card (e.g., "4396304456158206") and write it to the file at the given file_path. Return nothing else. Use OCR to read the number and regular expressions to extract only the 16-digit card number (remove any spaces or dashes). Do not include any other text in the output file.
    - When removing a prefix (e.g. `/data/docs/`) from a path, retain the path after the prefix
    - Call an LLM via a POST request to `http://aiproxy.sanand.workers.dev/openai/v1/chat/completions` with `Authorization: Bearer {os.getenv("AIPROXY_TOKEN")}` and this JSON body:
        {
            model: "gpt-4o-mini",
            messages: [
                { role: "system", content: "[INSERT SYSTEM PROMPT]" },
                { role: "user", content: [
                { type: "text", text: "[INSERT USER MESSAGE]" }, // for text
                { type: "image_url", image_url: { url: `data:[IMAGE MIME TYPE];base64,[IMAGE BASE64]`, detail: "low" } }, // for image. Get MIME type DYNAMICALLY from image
              ]}
            ],
            // response_format: "json_object",  // forces JSON response
        }
        Response is in `response.choices?.[0]?.message?.content`. Error is in `response.error?.message`.
    - Calculate embeddings with a POST request to `https://aiproxy.sanand.workers.dev/openai/v1/embeddings` with `Authorization: Bearer {os.getenv("AIPROXY_TOKEN")}` and this JSON body:
        {
            model: "text-embedding-3-small",
            input: [array of strings],
        }
      Embeddings are in response.data[*].embedding - an array of floats.
      Calculate the dot product of the embeddings (skipping the diagonal) to find the most similar pair of strings.
    requests.post(
            f"{openai_api_base}/embeddings",
            headers={"Authorization": f"Bearer {openai_api_key}"},
            json={"model": "text-embedding-3-small", "input": data},
        )
    - When extracting card information, use the system prompt "Extract the EXACT dummy credit card number from this test image"
    - Convert this Python code to use the httpx library instead of requests for all HTTP requests. Ensure that all synchronous requests are replaced with httpx equivalents, maintaining existing functionality. If any part uses asynchronous calls, convert them to use httpx.AsyncClient accordingly.

2. **EXECUTION RULES:**
    - An automated agent will blindly run the scripts you provide. So ONLY write the FINAL script(s) to run in ```bash or ```python code fences.

"""

# Pydantic model for task input
class TaskRequest(BaseModel):
    task: str

# Home route
@app.get("/")
async def read_root():
    """Serve the index.html file."""
    return FileResponse("static/index.html")

@app.post("/run")
async def run_task(request: TaskRequest):
    task = request.task
    response = await llm(system_prompt, task)
    print(f"\n🟡 Running task:\n{task.strip()}\n")
    print(f"\n🟡 {response}\n")

    results = []
    for language, code in re.findall(r"```(python|bash)\n(.*?)\n```", response, re.DOTALL):
        print(f"\n🟡 Running {language} code:\n{code}\n")
        if language == "python":
            result = await execute_python(code)
        else:
            result = await execute_bash(code)
        results.append({"lang": language, **result})

    print(f"\n🟡 Results:\n{results}\n")
    return {"response": response, "results": results}

@app.get("/read")
async def read_file(path: str):
    """Read contents of a file."""
    # Validate path is within /data
    path = os.path.normpath(path)
    if not path.startswith("/data/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)

@app.post("/execute/python")
async def execute_python(code: str):
    """Execute Python code directly."""
    proc = await asyncio.create_subprocess_exec(
        "python3",
        "-",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(code.encode())

    if proc.returncode != 0:
        print(f"\n🔴 Python execution failed:\n{stderr.decode()}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {stderr.decode()}")

    return {"stdout": stdout.decode(), "stderr": stderr.decode()}


@app.post("/execute/bash")
async def execute_bash(code: str):
    """Execute bash code directly."""
    proc = await asyncio.create_subprocess_exec(
        "bash",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(code.encode())

    if proc.returncode != 0:
        print(f"\n🔴 Bash execution failed:\n{stderr.decode()}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {stderr.decode()}")

    return {"stdout": stdout.decode(), "stderr": stderr.decode()}


if __name__ == "__main__":
    

    uvicorn.run(app, host="0.0.0.0", port=8000)