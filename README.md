<img src="https://github.com/user-attachments/assets/a9f996f7-6cbb-468d-8796-409aff63a82e" alt="alt text" width="500" height="300">



# TDS Course Project 1 (Jan 2025)  

## Submitted by :-

- **VIKASH PRASAD**  
- **Roll Number** - 21f3002277

## Project Title : 🤖 LLM-based Automation Agent

This repository contains an automation agent designed for **DataWorks Solutions** to streamline operational and business tasks using a Large Language Model (LLM) as an intermediate transformer. The agent parses plain-English task descriptions, executes the required steps, and produces deterministic, verifiable outputs.

---

## 🚀 Features

- Accepts plain-English task descriptions via API and automates multi-step processes.
- Integrates GPT-4o-Mini for language understanding and content generation.
- Supports file reading for task output verification.
- Handles both structured operations and dynamic business tasks.
- Secure by design: prevents file deletions and restricts access to `/data` only.

---

## 🛠️ Endpoints

### `POST /run?task=<task description>`

Executes a plain-English task.

- ✅ `200 OK`: Task completed successfully.
- ❌ `400 Bad Request`: Error in the task description.
- ⚠️ `500 Internal Server Error`: Agent failed to process the task.

### `GET /read?path=<file path>`

Returns the content of the specified file.

- ✅ `200 OK`: Returns plain text file content.
- ❌ `404 Not Found`: File not found.

---

## 📦 Supported Tasks

### ✅ Phase A – Operations

- Install and execute data generators
- Format Markdown with `prettier@3.4.2`
- Count weekdays in date files
- Sort JSON contact lists
- Extract log headlines from recent files
- Create index of Markdown titles
- Extract sender's email via LLM
- Extract credit card number from image via LLM
- Find most similar comments via embeddings
- Compute total ticket sales from SQLite

### 💼 Phase B – Business

- Prevents external file access and file deletions
- Fetch API data and save
- Clone Git repos and commit
- Run SQL queries on SQLite/DuckDB
- Scrape websites
- Compress/resize images
- Transcribe MP3 audio
- Convert Markdown to HTML
- Create API endpoint to filter CSV and return JSON

---

## 🧪 Usage

```bash
# Clone this repo
git clone https://github.com/21f3002277/TDS-LLM-Project-1.git
cd TDS-LLM-Project-1

# Run the app using Docker
podman run --rm -e AIPROXY_TOKEN=$AIPROXY_TOKEN -p 8000:8000 vikash2277/tds_project_1_llm
