#!/bin/bash

# Configuration
AGENT_CMD="gemini"
LOG_DIR="logs"
STOP_SIGNAL="<promise>COMPLETE</promise>"

# Create logs directory
mkdir -p "$LOG_DIR"

echo "Starting Ralph Loop..."
echo "Context: GEMINI.md + AGENCY.md"

while :; do
  TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
  LOG_FILE="$LOG_DIR/run_$TIMESTAMP.log"
  
  echo "Iteration: $TIMESTAMP"

  # --- THE MAGIC ---
  # We concatenate the Constitution (GEMINI.md) AND the Logic (AGENCY.md)
  # This creates one powerful prompt for the agent.
  FULL_PROMPT="$(cat GEMINI.md) $(cat AGENCY.md)"

  $AGENT_CMD --yolo --prompt "$FULL_PROMPT" < /dev/null > "$LOG_FILE" 2>&1

  # Check for completion
  if grep -q "$STOP_SIGNAL" "$LOG_FILE"; then
    echo "✅ Ralph has finished!"
    break
  fi

  # Git Checkpoint
  if [[ -n $(git status -s) ]]; then
    # We let the agent write the commit message usually, but for safety in the loop,
    # we can either auto-commit or let the agent do it in the next turn.
    # Ideally, Ralph should have used 'git commit' internally because you told it to be "Atomic".
    # But as a fallback:
    git add .
    git commit -m "Ralph Wiggum: Iteration $TIMESTAMP"
    echo "💾 Fallback checkpoint saved."
  fi

  sleep 5
done