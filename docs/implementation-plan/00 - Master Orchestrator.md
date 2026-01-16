# Master Orchestrator

> [!IMPORTANT]
> **CRITICAL PREREQUISITE**: Before taking ANY action based on this plan, you MUST read and apply the rules in `docs/implementation-plan/AA - Global Instructions.md`.
> This file dictates how to safely execute commands, manage context, and maintain code standards. Igoring it will result in failures.

**Objective:** Coordinate the execution of the Lockdev SaaS implementation.


## Progress Log
| Epic | Status | Owner | Directory |
| :--- | :--- | :--- | :--- |
| **Epic 1: Walking Skeleton** | [ ] Pending | Builder | `epic-01-walking-skeleton/` |
| **Epic 2: Backend Core** | [ ] Pending | Builder | `epic-02-backend-core/` |
| **Epic 3: Frontend Foundations** | [ ] Pending | Builder | `epic-03-frontend-foundations/` |
| **Epic 4: Shared Polish** | [ ] Pending | Builder | `epic-04-shared-polish/` |
| **Epic 5: Service Integrations** | [ ] Pending | Builder | `epic-05-service-integrations/` |
| **Epic 6: Architecture Docs** | [ ] Pending | Builder | `epic-06-architecture-docs/` |
| **Epic 7: User Identity** | [ ] Pending | Builder | `epic-07-user-identity/` |
| **Epic 8: Organizations** | [ ] Pending | Builder | `epic-08-organizations/` |
| **Epic 9: Dashboard Wiring** | [ ] Pending | Builder | `epic-09-dashboard-wiring/` |
| **Epic 10: Patient Management** | [ ] Pending | Builder | `epic-10-patient-management/` |
| **Epic 11: Providers & Care Teams** | [ ] Pending | Builder | `epic-11-providers-care-teams/` |
| **Epic 12: Appointments** | [ ] Pending | Builder | `epic-12-appointments/` |
| **Epic 13: Document Management** | [ ] Pending | Builder | `epic-13-document-management/` |
| **Epic 14: Proxies** | [ ] Pending | Builder | `epic-14-proxies/` |
| **Epic 15: Billing** | [ ] Pending | Builder | `epic-15-billing/` |
| **Epic 16: Notifications & Messaging** | [ ] Pending | Builder | `epic-16-notifications-messaging/` |
| **Epic 17: Call Center & Tasks** | [ ] Pending | Builder | `epic-17-call-center-tasks/` |
| **Epic 18: Support & Compliance** | [ ] Pending | Builder | `epic-18-support-compliance/` |
| **Epic 19: Super Admin** | [ ] Pending | Builder | `epic-19-super-admin/` |
| **Epic 20: Timezone Support** | [ ] Pending | Builder | `epic-20-timezone-support/` |
| **Epic 21: User Org Association** | [ ] Pending | Builder | `epic-21-user-org-association/` |
| **Epic 22: Complete Billing** | [ ] Pending | Builder | `epic-22-complete-billing/` |

## Execution Strategy
1.  Execute Epics sequentially (1 -> 19).
2.  Within each Epic, execute Stories sequentially (unless marked parallel).
3.  **Continuous Execution:** Upon successful verification of a Story or Epic, **IMMEDIATELY** proceed to the next available Story or Epic. Do not stop for user confirmation unless explicitly "BLOCKED" or if a critical failure occurs.
4.  **Blocking:** Do not proceed to the next Epic until the current Epic's verification criteria are met.
5.  **Safe Execution:** All commands must follow the **Command Execution & Safety** protocols defined in `AA - Global Instructions.md` (Timeouts, Monitoring, Cleanup).


## Resumption Logic
**"Recursive Status Check" Algorithm:**
To determine the next action without re-doing work, use the following "Documentation Driven" state check. **If a check passes (item is done), automatically recurse to the next item.**

1.  **Check Master Status:**
    - Open `docs/implementation-plan/00 - Master Orchestrator.md`.
    - Find the first **Unchecked** Epic in the "Progress Log" table.
    - *Example:* If Epic 1 is `[x]`, **automatically** check Epic 2.

2.  **Check Epic Status:**
    - Open the `index.md` file for the identified Epic (e.g., `docs/implementation-plan/epic-02-backend-core/index.md`).
    - Find the first **Unchecked** Story in the "Execution Order" list.
    - *Example:* If Story 2.1 is `[ ]`, that is the target Story.

3.  **Check Story Status:**
    - Open the specific Story file (e.g., `docs/implementation-plan/epic-02-backend-core/story-02-01-database.md`).
    - Review the "Status" section at the top.
    - If "Status" is `[ ]`, proceed to execute the "Technical Specification".
    - If "Status" is `[x]`, but the parent Epic marked it as pending, verify the "Acceptance Criteria" at the bottom.
        - If all "Acceptance Criteria" are checked `[x]`, mark the Story as `[x]` in the **Epic Index** and **IMMEDIATELY** move to the next Story.
        - If criteria are missing, resume execution of that Story.

**Completion Protocol:**
- When a task is done -> Mark the checkbox `[x]` in the file.
- When all criteria in a Story are done -> Mark the Story `[x]` in the Epic Index and **START THE NEXT STORY**.
- When all Stories in an Epic are done -> Mark the Epic `[x]` in the Master Orchestrator and **START THE NEXT EPIC**.
