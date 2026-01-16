# Epic 22: Complete Billing - Implementation Summary

## Overview
Epic 22 extends the existing billing system (Epic 15) to provide comprehensive patient and proxy billing management with automated monthly subscriptions, email notifications, receipts, and full admin controls.

## Key Innovation: Proxy Billing Management

### What Changed
The original Epic 22 was designed for **patient-only** billing. We've now enhanced it to support **proxy billing management**, where authorized proxies can manage billing on behalf of multiple patients.

### Core Requirements

1. **Subscription Ownership**
   - Subscriptions remain 1-1 with patients
   - Linked to `patient_id`, not `proxy_id`
   - Patient is the billable entity

2. **Billing Manager Model**
   - New `billing_manager_id` field on Patient model
   - References `user.id` of the proxy managing billing
   - NULL = patient manages own billing
   - Set = proxy manages billing

3. **Multi-Patient Management**
   - Single proxy can be billing manager for multiple patients
   - Proxy dashboard shows all managed patient subscriptions
   - Proxy can perform all billing actions for assigned patients

4. **Email Routing**
   - Billing emails automatically sent to billing manager (proxy) when assigned
   - Sent to patient when no billing manager
   - Templates show patient context for clarity

5. **Access Control**
   - Proxy must have active proxy relationship to be billing manager
   - Proxy can only manage billing for patients where they are assigned
   - All actions audited with proxy user ID

## Database Changes

### Patient Model Extensions
```sql
ALTER TABLE patients ADD COLUMN billing_manager_id UUID REFERENCES users(id);
ALTER TABLE patients ADD COLUMN billing_manager_assigned_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE patients ADD COLUMN billing_manager_assigned_by UUID REFERENCES users(id);

CREATE INDEX idx_patients_billing_manager ON patients(billing_manager_id)
    WHERE billing_manager_id IS NOT NULL;
```

### Billing Transaction Extensions
```sql
ALTER TABLE billing_transactions ADD COLUMN managed_by_proxy_id UUID REFERENCES users(id);

CREATE INDEX idx_billing_transactions_proxy ON billing_transactions(managed_by_proxy_id)
    WHERE managed_by_proxy_id IS NOT NULL;
```

## New API Endpoints

### Patient Billing Manager (2 endpoints)
- `PUT /api/v1/patients/{patient_id}/billing/manager` - Assign billing manager
- `DELETE /api/v1/patients/{patient_id}/billing/manager` - Remove billing manager

### Proxy Billing Management (5 endpoints)
- `GET /api/v1/proxy/managed-patients/billing` - List all managed subscriptions
- `GET /api/v1/proxy/managed-patients/{patient_id}/billing/subscription` - Get specific
- `POST /api/v1/proxy/managed-patients/{patient_id}/billing/checkout` - Create checkout
- `POST /api/v1/proxy/managed-patients/{patient_id}/billing/cancel` - Cancel subscription
- `GET /api/v1/proxy/managed-patients/{patient_id}/billing/transactions` - View history

### Admin Billing Manager (2 endpoints)
- `PUT /api/v1/admin/patients/{patient_id}/billing/manager` - Admin assign
- `GET /api/v1/admin/billing/managers` - List all relationships

**Total New Endpoints:** 9 (in addition to original Epic 22 endpoints)

## New Backend Services

### 1. Billing Access Control (`billing_access.py`)
- `can_manage_billing()` - Check if user can manage patient billing
- `get_billing_email_recipient()` - Get email recipient (patient or proxy)

### 2. Proxy Billing Router (`proxy_billing.py`)
- Full API router for proxy billing operations
- Access control using billing manager validation

## Email Changes

### Template Updates
All 4 email templates updated with proxy context:
- `payment-success.html`
- `payment-failed.html`
- `subscription-cancelled.html`
- `upcoming-renewal.html`

### Template Variables Added
```jinja2
{% if is_proxy_managed %}
  <p>This is a billing notification for <strong>{{ actual_patient_name }}</strong>...</p>
{% endif %}
```

- `recipient_name` - Name of email recipient (proxy or patient)
- `recipient_email` - Email of recipient
- `actual_patient_name` - Always the patient name
- `is_proxy_managed` - Boolean flag

### Email Service Function Changes
All email functions now accept:
- `db: AsyncSession` parameter
- `patient: Patient` object (instead of separate name/email)
- Automatically routes to billing manager if assigned

## Frontend Changes

### New Hooks (`useProxyBilling.ts`)
- `useManagedPatientSubscriptions()` - Get all managed patients
- `useProxyCheckout(patientId)` - Create checkout for patient
- `useAssignBillingManager(patientId)` - Assign/remove billing manager

### New Pages
- `/proxy/managed-patients-billing` - Proxy billing dashboard
- Shows all patients proxy manages
- Links to individual patient billing pages

### New Components
- `BillingManagerAssignment.tsx` - Assign proxy as billing manager
- `ProxyManagedPatientsBilling.tsx` - Proxy dashboard
- Updates to existing patient billing pages to show billing manager

### Admin Updates
- Subscriptions table shows "Billing Manager" column
- New tab for billing manager relationships
- Assign/remove billing managers from admin panel

## Audit & Monitoring

### New Audit Events
- `BILLING_MANAGER_ASSIGNED`
- `BILLING_MANAGER_REMOVED`
- `BILLING_PROXY_CHECKOUT_CREATED`
- `BILLING_PROXY_SUBSCRIPTION_CANCELLED`

### New Metrics
- `billing_proxy_managed_subscriptions` - Count of proxy-managed subscriptions
- `billing_proxy_actions_total` - Counter for proxy billing actions

## Testing Requirements

### New Test Cases (10+)
1. Proxy creates checkout for managed patient
2. Proxy cannot manage without assignment
3. Billing email sent to proxy when assigned
4. Billing email sent to patient when no manager
5. Email template shows patient context
6. Assign billing manager validates proxy relationship
7. Remove billing manager works correctly
8. Admin can override billing manager assignment
9. Access control prevents unauthorized billing management
10. Multiple patients managed by single proxy

### E2E Scenarios
1. Complete proxy billing flow from assignment to payment
2. Multiple patient management by proxy
3. Billing manager removal and email routing change

## Security Considerations

### Access Control
- Proxy must have active `PatientProxy` relationship
- Validate proxy relationship before allowing billing operations
- All proxy actions logged with proxy user ID

### Email Privacy
- Proxy receives billing emails instead of patient
- Patient name shown in proxy emails for context
- Footer indicates "You are receiving this because you are billing manager"

### Audit Trail
- All billing manager assignments logged
- Track who assigned billing manager
- Track when assignments created/removed
- All proxy billing actions logged separately

## Documentation Updates

### User Documentation
- How to assign billing manager
- Proxy guide for managing patient billing
- Patient guide explaining billing manager concept

### Developer Documentation
- Proxy billing API reference
- Access control flow diagrams
- Email routing logic

### Admin Documentation
- Managing billing manager relationships
- Troubleshooting proxy billing issues
- Viewing proxy billing activity

## Migration Path

### Phase 1: Database Changes
1. Add columns to patients table
2. Add column to billing_transactions table
3. Run migration on production

### Phase 2: Backend Deployment
1. Deploy new services (billing_access.py)
2. Deploy new API router (proxy_billing.py)
3. Update existing patient billing endpoints

### Phase 3: Email System
1. Deploy updated email templates
2. Deploy updated email service functions
3. Test email routing

### Phase 4: Frontend Deployment
1. Deploy proxy billing hooks and pages
2. Deploy billing manager assignment UI
3. Update admin billing dashboard

### Phase 5: Enable Feature
1. Enable `ENABLE_PROXY_BILLING` feature flag
2. Monitor for issues
3. Gradually roll out to users

## Rollback Plan

If issues arise:
1. Disable `ENABLE_PROXY_BILLING` feature flag
2. Proxy features hidden from UI
3. Existing patient billing continues to work
4. Billing manager assignments remain in database (no data loss)
5. Fix issues in staging
6. Re-enable after validation

## Success Metrics

### Adoption
- % of patients with billing managers assigned
- # of active proxy billing managers
- % of billing actions performed by proxies vs patients

### Efficiency
- Reduction in patient billing support tickets
- Time saved managing multiple patient bills
- Proxy user satisfaction scores

### Technical
- Email routing accuracy (100% to correct recipient)
- Access control validation (0 unauthorized access)
- Proxy billing action completion rate

## Files Modified/Created

### Modified Files
- `docs/implementation-plan/epic-22-complete-billing/index.md`
- `docs/implementation-plan/epic-22-complete-billing/story-22-01-patient-billing-api.md`
- `docs/implementation-plan/epic-22-complete-billing/story-22-02-email-receipts.md`

### New Files
- `docs/implementation-plan/epic-22-complete-billing/PROXY-BILLING-ADDENDUM.md`
- `docs/implementation-plan/epic-22-complete-billing/SUMMARY.md`

### Backend Files to Create (22 new/modified files)
- Models: `models/billing.py` (extended), `models/profiles.py` (extended)
- Services: `services/billing_access.py` (new), `services/billing.py` (extended), `services/email.py` (extended)
- API: `api/proxy_billing.py` (new), `api/patients_billing.py` (extended)
- Migrations: 1 new migration file
- Templates: 4 email templates (extended)

### Frontend Files to Create (8 new/modified files)
- Hooks: `hooks/api/useProxyBilling.ts` (new)
- Pages: `routes/_auth/proxy/managed-patients-billing.tsx` (new)
- Components: `components/billing/BillingManagerAssignment.tsx` (new)
- Extended: Patient billing page, admin billing dashboard

## Next Steps

1. **Review**: Review PROXY-BILLING-ADDENDUM.md for detailed implementation specs
2. **Plan**: Break down into smaller development tickets if needed
3. **Implement**: Follow Stories 22.1 through 22.7 sequentially
4. **Test**: Run full test suite including proxy billing tests
5. **Deploy**: Follow migration path for safe rollout
6. **Monitor**: Track success metrics post-deployment

## Questions & Considerations

### Business Logic Questions
1. Can a patient have their own billing active AND be managed by a proxy? Or mutually exclusive?
   - **Decision**: Mutually exclusive. If billing_manager_id is set, proxy manages all billing.

2. Can patient remove their own billing manager?
   - **Decision**: Yes, patient can remove billing manager at any time.

3. Can proxy decline being assigned as billing manager?
   - **Future**: Could add acceptance workflow. Currently auto-assigns.

4. What happens if proxy relationship is revoked but billing_manager_id still set?
   - **Decision**: Access denied. Proxy must have active relationship to manage billing.

### Technical Questions
1. Should we send email to both proxy AND patient?
   - **Decision**: Only to billing manager (proxy) to avoid confusion and double notifications.

2. Should patient see who their billing manager is in UI?
   - **Decision**: Yes, show in patient billing page with option to remove.

3. Can organization admin override billing manager assignments?
   - **Decision**: Yes, organization admins can assign/remove billing managers.

## Conclusion

This enhancement maintains backward compatibility while adding powerful proxy billing management capabilities. All existing patient billing continues to work unchanged. Proxies get new capabilities to manage multiple patient subscriptions from a single dashboard, with automatic email routing and comprehensive audit trails.

The implementation is designed for safety with:
- Clear rollback plan
- Feature flags
- Comprehensive testing
- Gradual rollout

Total estimated effort: 3-4 weeks including testing and documentation.
