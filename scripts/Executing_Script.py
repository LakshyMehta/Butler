#!/usr/bin/env python3
"""
Dynamic Butler System with FREE RAG (ChromaDB version for M1/M2 Macs)
- Builds a knowledge base of scripts (from docstrings)
- Retrieves most relevant script for a user query
- Uses Ollama (local LLM) to parse arguments
"""

import os
import json
import subprocess
from pathlib import Path
import ollama
import chromadb
from sentence_transformers import SentenceTransformer

# -------------------------------
# Load embedding model
# -------------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------
# Discover scripts
# -------------------------------
SCRIPTS_DIR = Path("scripts")
scripts = []
descriptions = []

for script in SCRIPTS_DIR.glob("*.py"):
    with open(script, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
        desc = next((line.strip().strip('"""') for line in lines if "Description:" in line), script.stem)
    scripts.append(str(script))
    descriptions.append(desc)

print("📂 Indexed scripts:")
for s, d in zip(scripts, descriptions):
    print(f" - {Path(s).name}: {d}")

# -------------------------------
# Create ChromaDB client
# -------------------------------
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="scripts")

# Embed & add scripts to Chroma
embeddings = embedder.encode(descriptions).tolist()
collection.add(
    documents=descriptions,
    embeddings=embeddings,
    ids=[str(i) for i in range(len(scripts))]
)

# -------------------------------
# Retrieve relevant script
# -------------------------------
def retrieve_script(user_input: str) -> str:
    query_emb = embedder.encode([user_input]).tolist()
    results = collection.query(query_embeddings=query_emb, n_results=1)
    idx = int(results["ids"][0][0])
    return scripts[idx]

# -------------------------------
# Ask LLM for arguments
# -------------------------------
def ask_llm(user_input: str, script_path: str) -> dict:
    prompt = f"""
    Script selected: {Path(script_path).name}
    User query: "{user_input}"

    Extract arguments for this script.
    Return JSON ONLY:
    - command: script file name without .py
    - arguments: list of arguments
    """

    response = ollama.chat(model="mistral", messages=[
        {"role": "user", "content": prompt}
    ])

    try:
        return json.loads(response["message"]["content"])
    except Exception:
        return {"command": Path(script_path).stem, "arguments": []}

# -------------------------------
# Run script
# -------------------------------
def run_command(script: str, args: list[str]):
    cmd = ["python3", script] + args
    print(f"🚀 Running: {' '.join(cmd)}")
    subprocess.run(cmd)

# -------------------------------
# Main loop
# -------------------------------
if __name__ == "__main__":
    while True:
        user_in = input(">> ")
        if user_in.lower() in ["quit", "exit"]:
            break

        script = retrieve_script(user_in)
        print(f"📌 RAG picked script: {Path(script).name}")

        result = ask_llm(user_in, script)
        print("🤖 LLM decided:", result)

        run_command(script, result.get("arguments", []))
