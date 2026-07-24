#!/usr/bin/env bash
# run.sh - Run DocuMind on Linux/Mac

echo "=============================================="
echo "       DocuMind - AI Document Platform"
echo "=============================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found."
    exit 1
fi

# Install Dependencies
echo "[INFO] Checking dependencies..."
python3 -m pip install -r requirements.txt > /dev/null 2>&1

# Run Streamlit
echo "[INFO] Starting Streamlit UI..."
python3 -m streamlit run app/main.py
