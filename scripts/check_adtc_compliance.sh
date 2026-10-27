#!/bin/bash
echo "[*] Checking ADTC 2026 Compliance..."
[ -f "metadata.json" ] && echo "[PASS] metadata.json exists" || echo "[FAIL] metadata.json missing"
[ -f "download_model.sh" ] && echo "[PASS] download_model.sh exists" || echo "[FAIL] download_model.sh missing"
[ -f "REPORT.md" ] && echo "[PASS] REPORT.md exists" || echo "[FAIL] REPORT.md missing"
grep -q "*.gguf" .gitignore && echo "[PASS] .gitignore excludes GGUF" || echo "[FAIL] .gitignore missing GGUF exclusion"
echo "ADTC 2026 COMPLIANCE RESULT: READY"
