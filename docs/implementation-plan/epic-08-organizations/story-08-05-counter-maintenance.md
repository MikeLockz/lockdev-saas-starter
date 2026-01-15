# Story 8.5: Organization Counter Maintenance

**Status:** Complete  
**Priority:** Medium  
**Addresses:** Database Review Warning - Denormalized Counter Inconsistency

## User Story
As a system administrator, I want organization member and patient counts to stay accurate, so that dashboard metrics and reports are reliable.

## Background
The `Organization` model has `member_count` and `patient_count` fields that are denormalized for performance. Currently, these are only set during organization creation and are not updated when members/patients are added or removed.

## Acceptance Criteria
- [ ] `member_count` increments when a member is added to the organization
- [ ] `member_count` decrements when a member is removed (hard or soft delete)
- [ ] `patient_count` increments when a patient is enrolled
- [ ] `patient_count` decrements when a patient is discharged/removed
- [ ] Existing data is reconciled via migration
- [ ] Unit tests verify counter behavior

## Technical Approach
Use SQLAlchemy event listeners (`after_insert`, `after_delete`, `after_update`) on:
- `OrganizationMember` → updates `member_count`
- `OrganizationPatient` → updates `patient_count`

## Implementation Files
- `apps/backend/src/models/organizations.py` - Add event listeners
- `apps/backend/migrations/versions/xxxx_counter_reconciliation.py` - Data fix
- `apps/backend/tests/test_organizations.py` - Add counter tests

## Test Cases
1. Create org → member_count = 1
2. Invite + accept member → member_count = 2
3. Remove member → member_count = 1
4. Enroll patient → patient_count = 1
5. Discharge patient → patient_count = 0
