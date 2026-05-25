# 🛡️ VeriFAI LLM: Model Alignment & Training Specification

**Lead Engineer:** NOUYEUTCHUI YOUMBI JUNIOR BRONDON  
**Alignment Strategy:** Cognitive Security Specialization (CSS)  
**Base Architecture:** Local Ollama (Phi-3)  
**Alignment Date:** May 2026

## 1. Persona Alignment (The "Training" Kernel)
The AI was trained via a specialized **System Message Architecture** to operate as a Senior Security Engineer. This alignment forces the model to prioritize:
- **OWASP Top 10 Mapping:** Direct correlation between code patterns and industry standards.
- **Exploit Logic:** The model is "taught" to think like an attacker to identify reachable vulnerabilities.
- **Remediation Precision:** Generating standard Unified Diff patches for automatic patching.

## 2. Dataset Integration (Heuristic Knowledge)
The model was aligned using a curated set of security patterns:
- **Semgrep Pattern Library:** Integrated static analysis rules as a secondary validation layer.
- **Vulnerability Datasets:** The system instructions include heuristics for SQLi, XSS, and RLS bypasses specific to InsForge/PostgreSQL architectures.

## 3. Cognitive Tuning Parameters
- **Temperature Control:** Fixed at `0.1 - 0.2` to ensure "Deterministic Security Analysis" (avoiding hallucination in exploit paths).
- **Chunking Strategy:** Recursive newline-aware chunking to handle large codebases without losing logical context (implemented in `src/utils/text_chunk.py`).

## 4. Verification Logic
Every analysis goes through a dual-gate verification:
1. **Static Gate:** Semgrep identifies the pattern.
2. **AI Gate:** The "trained" AI confirms the context and exploitability.

---
*This document serves as technical evidence of the specific alignment and tuning performed to specialize the AI for this application.*
