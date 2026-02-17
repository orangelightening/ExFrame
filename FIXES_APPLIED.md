# BrainUse Dashboard Fixes

**Date:** February 16, 2026
**Issues Fixed:** Consent flow + Edit/Delete functionality

---

## Issues Reported

1. **Cannot edit candidate name** (typo in "Alice jOHNSTON")
2. **Cannot delete candidate**
3. **"Failed to record consent" error** when starting assessment

---

## Fixes Applied

### 1. Added Consent Checkbox ✅

**Location:** Detail modal, visible for pending candidates

**What it does:**
- Shows checkbox: "Candidate has given consent for assessment"
- Explains GDPR requirement
- Records consent via API when checked
- Start Assessment button **disabled until consent given**

**How to use:**
1. Open candidate detail modal
2. Check the consent box
3. Consent recorded automatically
4. "Start Assessment" button becomes enabled

### 2. Added Edit Button ✅

**Location:** Detail modal, next to Delete button

**What it does:**
- Pre-fills create/edit form with candidate data
- Changes modal title to "Edit Candidate"
- Button text changes to "Update Candidate"
- Calls PUT endpoint to update candidate

**How to use:**
1. Click candidate card to open detail modal
2. Click "Edit" button
3. Modify name, email, role, company, domains, or notes
4. Click "Update Candidate"
5. Changes saved to database

### 3. Added Delete Button ✅

**Location:** Detail modal, next to Edit button

**What it does:**
- Shows confirmation dialog
- Deletes candidate from database (with cascading deletes)
- Removes from candidate list
- Shows success toast

**How to use:**
1. Click candidate card to open detail modal
2. Click "Delete" button (red)
3. Confirm deletion
4. Candidate removed permanently

---

## API Endpoints Added

### PUT /api/brainuse/candidates/{candidate_id}
**Update candidate information**

Request:
```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "role": "Senior Backend Engineer",
  "company": "TestCorp",
  "assessment_domains": ["cloud_assessment", "leadership_assessment", "api_assessment"],
  "recruiter_notes": "Updated notes"
}
```

Response: Updated candidate object

### DELETE /api/brainuse/candidates/{candidate_id}
**Delete candidate**

Response:
```json
{
  "status": "deleted",
  "candidate_id": "abc-123"
}
```

---

## Testing

### Fix Alice's Name
```bash
# Open dashboard
open http://localhost:3000/brainuse

# Click "Alice jOHNSTON" card
# Click "Edit" button
# Change name to "Alice Johnson"
# Click "Update Candidate"
# ✅ Name fixed!
```

### Test Consent Flow
```bash
# Open candidate detail (any pending candidate)
# ✅ See consent checkbox
# ✅ "Start Assessment" button is grayed out
# Check consent checkbox
# ✅ Consent recorded (toast notification)
# ✅ "Start Assessment" button becomes blue
# Click "Start Assessment"
# ✅ Assessment starts successfully
```

### Test Delete
```bash
# Open candidate detail
# Click "Delete" button (red)
# Confirm deletion
# ✅ Candidate removed from list
# ✅ Success toast shows
```

---

## Consent Flow (Fixed)

**Before:**
1. Click "Start Assessment"
2. ❌ Error: "Failed to record consent"
3. Assessment doesn't start

**After:**
1. Open candidate detail
2. Check "Candidate has given consent" checkbox
3. Consent recorded automatically
4. "Start Assessment" button becomes enabled
5. Click "Start Assessment"
6. ✅ Assessment starts successfully

---

## UI Changes

### Detail Modal Header
```
[Name]          
[Email]
                [Edit] [Delete] [Start Assessment]
```

### Consent Section (Pending Candidates Only)
```
☐ Candidate has given consent for assessment
  Required: Candidate must consent to having their learning 
  patterns analyzed for hiring purposes (GDPR compliance).
```

### Modal Title Changes
- Create mode: "Create New Candidate"
- Edit mode: "Edit Candidate"

### Button Text Changes
- Create mode: "Create Candidate"
- Edit mode: "Update Candidate"
- Saving: "Saving..."

---

## Database Changes

**Cascade delete added:**
When deleting a candidate, also deletes:
- Related assessments
- Related reports
- All associated data

This is already configured in the database models (`cascade="all, delete-orphan"`).

---

## Files Modified

1. **tao/vetting/frontend/index.html**
   - Added consent checkbox
   - Added Edit/Delete buttons
   - Updated modal title (create vs edit)
   - Updated button text

2. **tao/vetting/frontend/assets/brainuse.js**
   - Added `recordConsent()` function
   - Added `editCandidate()` function
   - Added `deleteCandidate()` function
   - Updated `createCandidate()` to handle both create and update
   - Updated `startAssessment()` to not auto-record consent

3. **tao/vetting/api_router.py**
   - Added PUT endpoint for updating candidates
   - Added DELETE endpoint for deleting candidates

---

## Summary

✅ **All issues fixed:**
- Can edit candidate name (and all other fields)
- Can delete candidates
- Consent flow works correctly
- "Start Assessment" button properly disabled until consent given

**Test it:**
```bash
open http://localhost:3000/brainuse
```

1. Fix Alice's name: Edit → Change name → Update
2. Record consent: Open detail → Check box → Consent recorded
3. Start assessment: Click "Start Assessment" → Works!
4. Delete if needed: Click Delete → Confirm → Gone

**All functionality working as expected!** 🎉
