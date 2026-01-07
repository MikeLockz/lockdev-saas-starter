# P1 Remediation Plan

## Overview
This plan addresses 19 major (P1) issues. Each item includes explicit implementation steps and test criteria.

---

## P1-1: Landing Page Missing Legal Links

### Problem
`/` landing page lacks Privacy Policy and Terms of Service links.

### Implementation

#### [NEW] [legal/privacy.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/routes/legal/privacy.tsx)
Create privacy policy page with standard HIPAA-compliant privacy content.

#### [NEW] [legal/terms.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/routes/legal/terms.tsx)
Create terms of service page.

#### [MODIFY] Landing page footer
Add links:
```tsx
<footer className="py-6 border-t">
  <div className="flex gap-4 justify-center text-sm text-muted-foreground">
    <Link to="/legal/privacy">Privacy Policy</Link>
    <Link to="/legal/terms">Terms of Service</Link>
  </div>
</footer>
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Links visible | Navigate to `/` | Footer shows Privacy and Terms links |
| Privacy page loads | Click Privacy link | `/legal/privacy` displays content |
| Terms page loads | Click Terms link | `/legal/terms` displays content |

---

## P1-2: Org Admin Dashboard (404)

### Problem
`/admin` returns 404 - no dedicated org admin dashboard exists.

### Implementation

#### [NEW] [admin/index.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/routes/admin/index.tsx)

Create dashboard with:
- Organization health metrics card
- Quick links to Members, Staff, Providers, Audit Logs
- Recent member activity feed

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Page loads | Navigate to `/admin` | Dashboard displays |
| Cards present | View page | Shows org metrics and quick links |

---

## P1-3: Super Admin System Health (404)

### Problem
`/super-admin/system` returns 404.

### Implementation

#### [NEW] [super-admin/system.tsx](file:///Users/mbp/Development/lockdev-saas-starter/frontend/src/routes/super-admin/system.tsx)

Create system health page with:
- API status indicator
- Database status
- Memory/CPU usage charts
- Active connections count

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Page loads | Navigate to `/super-admin/system` | System health page displays |
| Metrics shown | View page | Shows API status, database health |

---

## P1-4: Branded 404 Page

### Problem
404 page is minimal "Not Found" text with no branding or navigation.

### Implementation

#### [MODIFY] 404 route/component

Replace with branded page:
- App logo
- "Page Not Found" heading
- "The page you're looking for doesn't exist" message
- "Return to Dashboard" button
- Link to home page

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Branded page | Navigate to `/nonexistent` | Shows branded 404 with logo |
| Navigation | Click "Return to Dashboard" | Navigates to `/dashboard` |

---

## P1-5: Proxy Dashboard Missing Appointments List

### Problem
Proxy dashboard missing unified "upcoming appointments across all patients" list.

### Implementation

#### [MODIFY] Proxy dashboard component

Add section:
```tsx
<Card>
  <CardHeader><CardTitle>Upcoming Appointments</CardTitle></CardHeader>
  <CardContent>
    {/* List appointments for all proxy patients */}
    <AppointmentList patientIds={proxyPatientIds} limit={5} />
  </CardContent>
</Card>
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Section visible | Login as Proxy, view dashboard | "Upcoming Appointments" card visible |
| Shows all patients | View list | Appointments from all linked patients shown |

---

## P1-6: Provider Dashboard Missing Panel Overview

### Problem
Provider dashboard missing "patient panel overview" (panel size/health metrics).

### Implementation

#### [MODIFY] Provider dashboard component

Add section:
```tsx
<Card>
  <CardHeader><CardTitle>Patient Panel</CardTitle></CardHeader>
  <CardContent>
    <div>Total Patients: {panelSize}</div>
    <div>Active: {activeCount} | Discharged: {dischargedCount}</div>
  </CardContent>
</Card>
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Section visible | Login as Provider, view dashboard | "Patient Panel" card visible |
| Shows counts | View card | Displays patient counts |

---

## P1-7: Patient Form Missing Contact Methods

### Problem
`/patients/new` missing contact methods section.

### Implementation

#### [MODIFY] Patient create form

Add section after basic info:
```tsx
<div className="space-y-4">
  <h3>Contact Methods</h3>
  <div className="flex gap-2">
    <Select name="contactType"><option>Phone</option><option>Email</option></Select>
    <Input name="contactValue" placeholder="Phone or email" />
    <Button variant="outline" onClick={addContact}>Add</Button>
  </div>
  {contacts.map(c => <ContactRow key={c.id} contact={c} onRemove={removeContact} />)}
</div>
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Section visible | Navigate to `/patients/new` | Contact methods section visible |
| Add contact | Add phone number | Contact added to list |

---

## P1-8: Patient Form Missing Provider Selector

### Problem
`/patients/new` missing provider selector.

### Implementation

#### [MODIFY] Patient create form

Add provider selection:
```tsx
<div className="space-y-2">
  <Label>Primary Provider</Label>
  <Select name="providerId">
    {providers.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
  </Select>
</div>
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Selector visible | Navigate to `/patients/new` | Provider dropdown visible |
| Select provider | Choose provider | Selection saved to form state |

---

## P1-9: Messages Missing Search

### Problem
`/messages` missing search input.

### Implementation

#### [MODIFY] Messages inbox component

Add search input above thread list:
```tsx
<Input 
  type="search" 
  placeholder="Search messages..." 
  value={searchQuery}
  onChange={(e) => setSearchQuery(e.target.value)}
/>
```

Filter threads by subject/participant name.

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Input visible | Navigate to `/messages` | Search input visible |
| Search works | Type query | Thread list filtered |

---

## P1-10: Messages Missing Filter Tabs

### Problem
`/messages` missing filter tabs (All, Unread, Archived).

### Implementation

#### [MODIFY] Messages inbox

Add tabs:
```tsx
<Tabs value={filter} onValueChange={setFilter}>
  <TabsList>
    <TabsTrigger value="all">All</TabsTrigger>
    <TabsTrigger value="unread">Unread</TabsTrigger>
    <TabsTrigger value="archived">Archived</TabsTrigger>
  </TabsList>
</Tabs>
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Tabs visible | Navigate to `/messages` | All/Unread/Archived tabs visible |
| Filter works | Click "Unread" | Only unread threads shown |

---

## P1-11: Messages Missing Unread Badges

### Problem
`/messages` missing unread count badges on threads.

### Implementation

#### [MODIFY] Thread list item component

Add badge:
```tsx
{thread.unreadCount > 0 && (
  <Badge variant="destructive" className="rounded-full">
    {thread.unreadCount}
  </Badge>
)}
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Badge visible | View message with unread | Red badge with count visible |
| Badge updates | Read message | Badge disappears or count decreases |

---

## P1-12: Appointment Form Not Multi-Step

### Problem
`/appointments/new` is single-form modal, not multi-step flow.

### Implementation

#### [MODIFY] Appointment scheduling modal

Convert to stepper:
1. Step 1: Select Patient
2. Step 2: Select Provider
3. Step 3: Choose Date/Time
4. Step 4: Select Type & Confirm

Use state machine or step index to navigate.

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Steps visible | Open new appointment | Step indicator visible |
| Navigation works | Complete step 1, click Next | Advances to step 2 |

---

## P1-13: Message Recipient UUID Input

### Problem
`/messages/new` recipient requires manual UUID instead of user selector.

### Implementation

#### [MODIFY] New message form

Replace UUID input with user search/select:
```tsx
<Combobox
  options={users.map(u => ({ value: u.id, label: u.name }))}
  placeholder="Search recipients..."
  onSelect={setRecipientId}
/>
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Selector visible | Navigate to `/messages/new` | User search/dropdown visible |
| Search works | Type name | Matching users shown |
| Select works | Click user | Recipient populated |

---

## P1-14: Members Missing MFA Status

### Problem
`/admin/members` missing MFA status indicator per member.

### Implementation

#### [MODIFY] Members table

Add MFA column:
```tsx
<TableCell>
  {member.mfaEnabled ? (
    <Badge variant="success">MFA Enabled</Badge>
  ) : (
    <Badge variant="outline">MFA Off</Badge>
  )}
</TableCell>
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Column visible | Navigate to `/admin/members` | MFA Status column visible |
| Status correct | View user with MFA | Shows "MFA Enabled" badge |

---

## P1-15: Members Cannot Change Roles

### Problem
`/admin/members` no ability to change member roles.

### Implementation

#### [MODIFY] Members table/row

Add role change action:
```tsx
<DropdownMenu>
  <DropdownMenuTrigger><Button variant="ghost">Actions</Button></DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem onClick={() => openRoleModal(member)}>
      Change Role
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

Create role change modal with role selector.

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Action available | Click row actions | "Change Role" option visible |
| Modal opens | Click "Change Role" | Role selection modal opens |
| Role updates | Select new role, save | Member role updated |

---

## P1-16: Audit Logs Missing Export

### Problem
`/admin/audit-logs` missing export button.

### Implementation

#### [MODIFY] Audit logs page

Add export button:
```tsx
<Button variant="outline" onClick={handleExport}>
  <Download className="mr-2 h-4 w-4" />
  Export CSV
</Button>
```

Implement `handleExport` to download filtered logs as CSV.

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Button visible | Navigate to `/admin/audit-logs` | Export button visible |
| Download works | Click export | CSV file downloads |

---

## P1-17: Profile Missing Photo Upload

### Problem
`/settings/profile` missing profile photo upload.

### Implementation

#### [MODIFY] Profile settings page

Add avatar upload:
```tsx
<div className="flex items-center gap-4">
  <Avatar className="h-20 w-20">
    <AvatarImage src={user.photoUrl} />
    <AvatarFallback>{initials}</AvatarFallback>
  </Avatar>
  <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
    Upload Photo
  </Button>
  <input ref={fileInputRef} type="file" accept="image/*" hidden onChange={handleUpload} />
</div>
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Upload button visible | Navigate to `/settings/profile` | "Upload Photo" button visible |
| Upload works | Select image file | Avatar updates |

---

## P1-18: Security Missing Password Change

### Problem
`/settings/security` missing password change option.

### Implementation

#### [MODIFY] Security settings page

Add password change section:
```tsx
<Card>
  <CardHeader><CardTitle>Password</CardTitle></CardHeader>
  <CardContent>
    <Button onClick={openPasswordModal}>Change Password</Button>
  </CardContent>
</Card>
```

Modal collects current password, new password, confirm.

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Button visible | Navigate to `/settings/security` | "Change Password" button visible |
| Modal opens | Click button | Password change modal opens |

---

## P1-19: Settings Missing Organizations Link

### Problem
`/settings` missing "Organizations" link.

### Implementation

#### [MODIFY] Settings hub page

Add organizations link to sidebar/menu:
```tsx
<Link to="/settings/organizations" className="...">
  <Building className="mr-2 h-4 w-4" />
  Organizations
</Link>
```

### Test Criteria
| Test | Steps | Expected |
|------|-------|----------|
| Link visible | Navigate to `/settings` | Organizations link in menu |
| Navigation works | Click link | Navigates to orgs page |

---

## Priority Groups

| Group | Issues | Theme |
|-------|--------|-------|
| **A - Legal/Compliance** | P1-1 | Legal pages |
| **B - Error Pages** | P1-4 | User experience |
| **C - Admin Routes** | P1-2, P1-3, P1-14, P1-15, P1-16 | Admin functionality |
| **D - Messaging** | P1-9, P1-10, P1-11, P1-13 | Message UX |
| **E - Patient Forms** | P1-7, P1-8 | Data entry |
| **F - Dashboards** | P1-5, P1-6 | Role dashboards |
| **G - Settings** | P1-17, P1-18, P1-19 | User settings |
| **H - Appointments** | P1-12 | Booking flow |
