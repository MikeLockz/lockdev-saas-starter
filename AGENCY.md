# Execution Algorithm: The Recursive Status Check
You are currently in "Execution Mode". Your goal is to find the next pending task and complete it.

## Step 1: Find the Work
1.  **Read `docs/implementation-plan/00 - Master Orchestrator.md`**.
    - Find the first Epic marked `[ ]`.
2.  **Read that Epic's `index.md`**.
    - Find the first Story marked `[ ]`.
3.  **Read that Story file**.
    - This is your task.

## Step 2: Execute
- Implement the "Technical Specification" in the Story file.
- Follow the **Engineering Standards** defined in your system context (GEMINI.md).

## Step 3: Completion Signal
- If ALL Epics in the Master Orchestrator are `[x]`, output:
  <promise>COMPLETE</promise>