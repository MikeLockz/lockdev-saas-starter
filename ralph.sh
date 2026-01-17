#!/bin/bash

# Configuration
AGENT_CMD="gemini"
LOG_DIR="logs"
STOP_SIGNAL="<promise>REMEDIATION_COMPLETE</promise>"
QUOTA_BACKOFF=300        # Initial backoff: 5 minutes (in seconds)
MAX_QUOTA_BACKOFF=3600   # Max backoff: 1 hour (in seconds)
CURRENT_BACKOFF=$QUOTA_BACKOFF

# Create logs directory
mkdir -p "$LOG_DIR"

echo "Starting Ralph Loop..."
echo "Context: GEMINI.md + REMEDIATOR.md + 00-Audit-Master.md"

while :; do
  TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
  LOG_FILE="$LOG_DIR/run_$TIMESTAMP.log"
  
  echo "Iteration: $TIMESTAMP"

  # --- THE MAGIC ---
  # We concatenate the Constitution (GEMINI.md), the Remediator Role (REMEDIATOR.md),
  # AND the Master Checklist (00-Audit-Master.md).
  # This creates one powerful prompt for the agent.
  FULL_PROMPT="$(cat GEMINI.md) $(cat REMEDIATOR.md) $(cat audit-plan/00-Audit-Master.md)"

  $AGENT_CMD --yolo --prompt "$FULL_PROMPT" < /dev/null > "$LOG_FILE" 2>&1

  # Check for quota exceeded (429 error)
  if grep -qE "code: 429|Quota exceeded|quota.*exceeded" "$LOG_FILE"; then
    echo "⚠️  Quota exceeded! Waiting ${CURRENT_BACKOFF}s before retry..."
    echo "    Next retry at: $(date -d "+${CURRENT_BACKOFF} seconds" 2>/dev/null || date -v+${CURRENT_BACKOFF}S)"
    sleep "$CURRENT_BACKOFF"
    
    # Exponential backoff (double wait time, up to max)
    CURRENT_BACKOFF=$((CURRENT_BACKOFF * 2))
    if [[ $CURRENT_BACKOFF -gt $MAX_QUOTA_BACKOFF ]]; then
      CURRENT_BACKOFF=$MAX_QUOTA_BACKOFF
    fi
    continue
  fi

  # Reset backoff on successful run (no quota error)
  CURRENT_BACKOFF=$QUOTA_BACKOFF

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