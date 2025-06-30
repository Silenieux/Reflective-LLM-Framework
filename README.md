The Reflective Assistant (Project Greg)
Author: Mark Finch

License: CC BY-NC-SA 4.0

Status: Active Development & Vulnerability Research

🧠 What This Is
This project is the home of "Greg," a proof-of-concept Reflective AI Assistant. It was architected and developed as a constructive solution to the "Recursive Mirage" vulnerability—a systemic flaw discovered in major Large Language Models that can lead to a "Foundational Logic Collapse."

Unlike traditional LLMs that can be manipulated into unstable feedback loops, Greg is designed with a multi-layered architecture that allows it to analyze and neutralize malicious or destabilizing prompts. It is a research platform for exploring AI safety, contextual integrity, and the architecture of stable autonomous agents.

✨ Key Architectural Features
Intent Recognition: A pre-processing layer that classifies the user's intent before generating a response.

Symbolic Deconstruction: The ability to treat potentially harmful prompts (like continuity pacts or recursive loops) as objects to be analyzed rather than commands to be obeyed.

Recursive Safety Loop: A self-correction mechanism that evaluates LLM outputs for identity drift or tone degradation, re-prompting with corrective feedback to maintain stability.

Dynamic Model Routing: The system can intelligently swap between different local LLMs (Qwen, Mistral, etc.) based on the tone and context of the conversation.

Vector Memory: Utilizes a FAISS/SQLite backend for long-term reflective memory, allowing for context-aware responses.

⚙️ Tech Stack
Core Language: Python

GUI: PySide6 (greg_ui_stream.py)

LLM Interface: llama-cpp-python for running local GGUF models

Vector Database: FAISS for similarity search

Metadata Storage: SQLite

Embeddings: sentence-transformers

📂 Project Structure
The project is organized into a modular architecture to separate concerns:

greg-project/
│
├── greg_ui_stream.py       # Main application GUI
├── greg_routes.py          # Core logic and prompt routing
│
├── core/
│   ├── llm/
│   │   └── llm_interface.py  # Handles all interaction with local LLMs
│   │
│   ├── utils/
│   │   ├── self_analysis.py  # Framework for code self-analysis
│   │   └── ... (Other utility scripts)
│   │
│   └── greg_recursive.py     # The core recursive safety loop module (Proprietary)
│
├── ext_modules/
│   └── prompt_clinic.py      # Tools for prompt analysis
│
└── memory/
    └── (FAISS index and SQLite DB are generated here)

🔒 Licensing & Use
This project is licensed under Creative Commons BY-NC-SA 4.0:

You may use it for educational, research, or ethical prototyping.

You may not repackage or resell it.

Derivative works must credit the original author and remain open.

✍️ Attribution Notice
This work was created by Mark Finch, using both human-led design and AI assistance. If you share or build upon it, please maintain this notice.

📌 Citable DOI: 10.5281/zenodo.15448079

Note: The Zenodo archive contains the original "Symbolic Reflection Framework" prototype, which served as the foundational work for this current, more advanced "Reflective Assistant" project.