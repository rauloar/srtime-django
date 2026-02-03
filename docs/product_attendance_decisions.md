# Product Decisions - Attendance Control System

**Document Version:** 1.0  
**Date:** 2026-02-03  
**Status:** APPROVED & FROZEN  
**Audience:** Product, HR, Legal, Engineering  

---

## Purpose

This document establishes non-negotiable product decisions for the attendance control system. It serves as:
- A binding contract between product, HR, and engineering
- A reference for current and future development decisions
- A defensible position for system behavior and limitations

**This document closes decisions. It does not open debates.**

---

## 1. Timeline as Informational, Not Legal

### Decision
The Timeline view is **informational only**. It does not constitute legal proof of attendance.

### Implications
- Timeline reflects system reconstruction, not ground truth
- HR and Legal departments independently define how attendance information is used
- The system's role is to provide **accurate reconstruction**, not to determine labor law compliance
- Discrepancies between Timeline and device data are documented but not auto-corrected

### Non-Negotiable
- No automated inference of missing time blocks
- No implicit assumptions about employee intent or availability
- System remains transparent about data gaps and limitations

---

## 2. Role of Human Resources

### Decision
HR observes, verifies, and corrects. Every recorded punch is a fact.

### Principles
1. **A punch is a recorded event**, regardless of correctness
   - A punch **cannot be deleted** (it happened on the device)
   - A punch **can be marked as erroneous** and corrected through manual adjustment
   - The original event remains visible and auditable

2. **Special Case: Repeated Punches in Same Minute**
   - Multiple punches within the same minute (caused by facial recognition, device repetition, etc.) are recognized as a known pattern
   - HR may establish a minimum time interval between consecutive punches of the same type
   - When a minimum interval is applied, duplicate punches are flagged as "duplicate" (not deleted)
   - The original events remain in the log

3. **HR Authority**
   - HR validates patterns against company policy
   - HR corrects obvious errors (wrong day, wrong time, etc.)
   - HR documents all corrections with reason codes
   - HR can override system interpretation, but only through explicit manual action

### Non-Negotiable
- No silent data deletion
- No automatic deduplication without HR review
- Every action leaves an audit trail

---

## 3. Incomplete Days and Reporting

### Decision
An incomplete day **does not block reports**. It is reported as absence with explicit indicators.

### Definitions
- **Complete day:** Both IN and OUT events recorded and paired
- **Incomplete day:** Missing IN, missing OUT, or unpaired events
- **Device failure indicator:** Pattern suggests terminal malfunction (to be flagged)

### Behavior
When a day is incomplete:
1. Report is still generated (not blocked)
2. Day is marked as `status: INCOMPLETE` or `status: ABSENT`
3. Specific reason is provided:
   - "Missing IN event"
   - "Missing OUT event"
   - "Terminal may have failed"
4. HR is alerted for review
5. No time is auto-credited or inferred

### Non-Negotiable
- Reports function even with incomplete data
- Incompleteness is transparent (not hidden)
- HR decides consequences of incomplete days per labor agreement

---

## 4. Manual Edits and Audit Trail

### Decision
Manual edits are allowed. All edits must be marked and traceable.

### Requirements
1. Every manual edit creates a record:
   - Original values (preserved, visible)
   - New values
   - Reason code (set by HR or system)
   - Editor identity
   - Timestamp of edit

2. Edit markers are permanent:
   - The Timeline view indicates "Manual Adjustment Applied"
   - The original data remains queryable
   - Reports can filter by manual vs. auto-detected data

3. Corrections do not erase:
   - Original punch remains in audit log
   - Reason for correction is documented
   - No data is deleted, only status-changed

### Non-Negotiable
- Transparency is mandatory
- Audit trail is immutable
- Original facts are always recoverable

---

## 5. Accuracy vs. Truth

### Decision
The system prioritizes **accuracy over inference**. When uncertain, the system reports rather than decides.

### Principles
1. **Accuracy:** The system faithfully reproduces what the device recorded
2. **Truth:** Only HR and Legal determine what time data means
3. **Uncertainty:** When the system cannot accurately pair events or infer state, it says so explicitly

### Examples of Correct Behavior
- **Not this:** "Employee worked 9 hours, assuming a 1-hour lunch break" ❌
- **This:** "IN 09:00, OUT 18:00 (8 events recorded, pattern suggests break but not confirmed)" ✅

- **Not this:** "Missing OUT event on 2026-02-01; assuming employee left at 18:00" ❌
- **This:** "Missing OUT event on 2026-02-01; day marked INCOMPLETE; HR review required" ✅

### Non-Negotiable
- No guessing
- No inference without explicit flag
- Uncertainty is communicated, not hidden

---

## Technical Implications

### What the System May Do

#### Defensive Rules (Acceptable)
- Validate event timing (e.g., punch cannot occur before device was enabled)
- Flag anomalies (e.g., "3 IN events without matching OUT")
- Detect patterns (e.g., "10 punches in 1 minute suggests device malfunction")
- Deduplicate within HR-defined time windows (with full visibility)
- Generate alerts for ambiguous cases (awaiting HR decision)

#### Audit and Traceability (Required)
- Log every decision point (why was this event included/excluded/flagged?)
- Preserve original device data in raw format
- Mark transformations at every step
- Maintain edit history with attribution

### What the System Must NOT Do

#### Inference Without Consent (Prohibited)
- Assume employees worked when no events exist
- Infer breaks from gaps (gaps could be legitimate work outside sensor range)
- Apply business rules that contradict product decisions (e.g., "round down to nearest 15 min")
- Auto-correct without HR involvement
- Delete or alter original device data

#### Automation That Bypasses HR (Prohibited)
- Automatically mark incomplete days as "absent" without review
- Auto-approve or auto-reject suspicious patterns
- Apply company policy without explicit HR trigger
- Infer shift intent from punch history

### Correctability is by Design
The system acknowledges that:
1. Device data can be wrong (false positives, malfunctions, user error)
2. Initial reconstruction can be wrong (algorithm limitations)
3. Correction must be human-driven, documented, and visible
4. Transparency enables defensibility in disputes

### Future Data Integration
If additional sources of truth are added (GPS, badge readers, workstations):
- They remain separate until explicitly reconciled
- Discrepancies are flagged, not auto-resolved
- HR reviews multi-source conflicts before trusting any single source

---

## Constraints and Boundaries

### In Scope (System Responsibility)
- Faithful retrieval of device data
- Accurate time-series reconstruction
- Event pairing when unambiguous
- Pattern detection and alerting
- Audit logging of all transformations
- HR tools for manual correction and review

### Out of Scope (External Responsibility)
- Determining labor law compliance
- Defining company attendance policy
- Deciding consequences of absences
- Interpreting business intent
- Enforcing compensation rules
- Resolving disputes

These remain the responsibility of HR, Legal, and Management.

---

## Decision Closure

### What This Document Establishes
✅ Timeline is informational  
✅ HR has final authority over data interpretation  
✅ Incomplete data does not block reporting  
✅ Manual edits are visible and auditable  
✅ System accuracy is prioritized over inference  

### What This Document Does NOT Do
❌ Define technical implementation details  
❌ Specify algorithm thresholds or rules  
❌ Impose labor policy  
❌ Override HR or Legal authority  
❌ Eliminate human judgment from the system  

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | | |
| HR Manager | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | | |
| Legal Counsel | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | | |
| Tech Lead | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | | |

---

**Document Status:** FROZEN  
**Version History:** v1.0 (2026-02-03) - Initial approval

