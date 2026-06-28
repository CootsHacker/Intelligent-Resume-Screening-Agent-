# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Intelligent Resume Screening Agent - A FastAPI-based service that parses PDF resumes using LLM (Qwen), extracts structured information, and stores vectorized resume data in Milvus for semantic search. The system is designed for AI-powered resume screening and interview assistance.

## Commands

### Run the Application
```bash
uvicorn main:app --reload
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Core Pipeline Flow

1. **Resume Parsing Pipeline** (`/agent/api/v1/resume/parse`)
   - PDF extraction → LLM structured extraction → JSON response
   - Uses PyMuPDF to extract raw text from PDF
   - Sends text to Qwen LLM API (DashScope) with structured prompt
   - Returns parsed resume data with schema validation

2. **Vectorization Pipeline** (`/agent/api/v1/resume/vectorize`)
   - Takes structured resume JSON → splits long text → generates embeddings → batch writes to Milvus
   - Uses `RecursiveCharacterTextSplitter` for Chinese text (chunk_size=150, overlap=15)
   - Generates embeddings via local Ollama server (all-minilm-l6-v2 model at localhost:11434)
   - Uses `QueueBatchWriter` for async batch insertion (max_size=10, timeout=3s)

### Key Components

**LLM Service** (`app/api/service/llm_service.py`)
- Calls Qwen API via DashScope SDK with structured prompt from `app/prompt/pdf_parse.py`
- Extracts JSON from LLM response using regex pattern matching
- Requires `DASHSCOPE_API_KEY` environment variable

**Embedding Service** (`app/core/embedding/embedding_service.py`)
- **Critical**: Expects local Ollama server running at `http://localhost:11434`
- Model: `all-minilm-l6-v2`
- Blocking HTTP calls wrapped in `asyncio.to_thread()` for concurrency

**Milvus Integration** (`app/core/vector/`)
- `QueueBatchWriter`: Async queue-based batch writer that accumulates items until max_size or timeout
- Collection name: `ai_interviewer_resumes`
- Stores: resumeId, name, city, skills, education, awards, and vectorized fields (projects, workExperience, overallSummary)

**Text Splitting** (`app/utils/text_spliter_service.py`)
- Two-stage splitting optimized for Chinese text
- Primary: 150 chars with 15 overlap, splits on `\n\n`, `\n`, Chinese punctuation
- Secondary: 100 chars for oversized chunks

### Exception Handling Strategy

Global exception handlers defined in `main.py`:
- `PDFParseError` (1001): PDF file parsing failures
- `LLMCalledFailed` (1002): DashScope API call failures
- `InvalidJSON` (1004): LLM returned invalid JSON
- `LLMParseError` (1005): Resume information extraction logic errors
- `FileNotFoundError` (404): Missing PDF files
- `InsertException`: Milvus batch write failures

All API responses use HTTP 200 with business error codes in JSON body.

## External Dependencies

- **DashScope API**: Requires `DASHSCOPE_API_KEY` environment variable for Qwen LLM
- **Ollama Server**: Must be running at `http://localhost:11434` with `all-minilm-l6-v2` model loaded
- **Milvus**: Connection and collection setup must exist before vectorization endpoint is called

## Important Notes

- The LLM prompt (`system_prompt` in `app/prompt/pdf_parse.py`) is critical for parsing quality - it defines the exact JSON schema expected
- Text splitter is tuned for Chinese text with specific chunk sizes and Chinese punctuation separators
- The vectorization endpoint uses lifespan context manager to manage `QueueBatchWriter` lifecycle, but the implementation in `resume.py:32-38` creates a separate FastAPI app instance that may not be properly integrated
- Resume parsing is synchronous (blocking LLM call), wrapped in `asyncio.to_thread()` for async API
- Embeddings are generated in parallel using `asyncio.gather()` for projects, work experience, and overall summary
