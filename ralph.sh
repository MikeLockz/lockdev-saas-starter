#!/bin/bash

# Configuration
AGENT_CMD="gemini"
# If you haven't installed it globally, use: AGENT_CMD="npx @google/gemini-cli"

LOG_DIR="logs"
STOP_SIGNAL="<promise>COMPLETE</promise>"

# Create logs directory
mkdir -p "$LOG_DIR"

echo "Starting Ralph Loop for Gemini (YOLO Mode)..."
echo "Press Ctrl+C to stop manually."

while :; do
  TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
  LOG_FILE="$LOG_DIR/run_$TIMESTAMP.log"
  
  echo "------------------------------------------------"
  echo "Iteration starting: $TIMESTAMP"
  echo "Logging to: $LOG_FILE"

  # INSTRUCTION:
  # 1. --yolo : Auto-approves all tool calls (file writes, shell commands).
  # 2. --prompt "..." : Passes the prompt as an argument.
  # 3. < /dev/null : Ensures stdin is closed so it doesn't wait for user input.
  $AGENT_CMD --yolo --prompt "Read PROMPT.md and execute the next step in agent/TODO.md. If finished, output $STOP_SIGNAL" < /dev/null > "$LOG_FILE" 2>&1

  # Check for the completion signal
  if grep -q "$STOP_SIGNAL" "$LOG_FILE"; then
    echo "✅ Ralph has finished the job!"
    break
  fi

  # Git Checkpoint
  if [[ -n $(git status -s) ]]; then
    git add .
    git commit -m "Ralph iteration: $TIMESTAMP"
    echo "💾 Checkpoint saved to git."
  else
    echo "no changes this iteration."
  fi

  echo "Cooling down for 5 seconds..."
  sleep 5
done