# ZNX AI — Call Flow Documentation

## Overview

Every inbound call to a ZNX AI-enabled dental practice follows a deterministic decision tree. The agent collects only what it needs, confirms before writing, and escalates anything outside its defined scope immediately. This document maps all branches.

---

## Primary Call Entry

```
INBOUND CALL
     |
     v
Twilio receives call on provisioned number
     |
     v
Twilio POSTs to Retell AI inbound webhook
     |
     v
Retell connects call to agent
     |
     v
Agent greeting:
"Thank you for calling [Practice Name], this is Maya.
 How can I help you today?"
     |
     v
INTENT DETECTION
```

---

## Intent Branches

### Branch 1: Schedule / Reschedule / Cancel Appointment

```
Caller says: "I need to book a cleaning" / "I want to reschedule" / "Cancel my appointment"
     |
     v
SLOT COLLECTION (in order):
  1. patient_first_name
  2. patient_last_name
  3. date_of_birth
  4. patient_type (new / returning)
  5. appointment_reason
  6. preferred_date
  7. preferred_time
     |
     v
AVAILABILITY CHECK
     |
     |-- Slots available --> Offer top 2 options
     |
     |-- No slots available --> Offer next 3 available days
     |
     v
CALLER CONFIRMS SLOT
     |
     v
CONFIRMATION READBACK:
"Just to confirm — I have you scheduled for [DATE] at [TIME]
 for a [REASON] with Dr. [NAME]. Does that all look correct?"
     |
     |-- Caller confirms --> POST to Open Dental /appointments
     |                       Send webhook: appointment-confirmed
     |                       "Perfect. You'll receive a confirmation
     |                        text shortly. Is there anything else
     |                        I can help you with?"
     |
     |-- Caller corrects --> Re-prompt corrected slot only. Loop back to readback.
     |
     v
CALL WRAP:
"Have a great day. Goodbye."
Retell sends call-ended webhook with transcript + collected data.
```

---

### Branch 2: Insurance Inquiry

```
Caller says: "Do you take Delta Dental?" / "I want to give you my insurance info"
     |
     v
IF yes/no insurance plan question:
  Agent checks knowledge_base.accepted_insurance
  Answers directly from configured list
     |
     v
IF verification needed:
  SLOT COLLECTION:
    1. patient_first_name
    2. patient_last_name
    3. date_of_birth
    4. insurance_provider
    5. member_id
     |
     v
"Got it. I've noted your insurance information and a member
 of our team will verify your coverage and follow up with you
 before your appointment."
     |
     v
POST to Open Dental /tasks (staff task created)
Send webhook: slot-filled (all insurance fields)
```

---

### Branch 3: General FAQ

```
Caller asks about: hours, location, parking, new patient process, cancellation policy
     |
     v
Agent answers from knowledge_base (no slots required)
     |
     v
"Is there anything else I can help you with?"
     |
     |-- Yes --> Return to intent detection
     |-- No  --> Wrap call
```

---

### Branch 4: Emergency Escalation (IMMEDIATE)

```
Trigger keywords detected:
pain / hurts / swollen / emergency / bleeding / broken / knocked out /
abscess / infection / can't eat / dental emergency
     |
     v
IMMEDIATE RESPONSE (no additional data collected):
"I want to make sure you get the right help — let me connect
 you with someone on our team right now."
     |
     v
Twilio call transfer to [PRACTICE_TRANSFER_NUMBER]
Agent disconnects.
Webhook fires: call-ended with end_reason: "emergency_transfer"
```

No exceptions. Emergency escalation fires on any keyword match regardless of conversation state.

---

### Branch 5: Billing / Account Inquiry

```
Caller mentions: bill / invoice / payment / balance / charge / statement
     |
     v
"For billing questions I'm going to connect you with
 our billing team. One moment."
     |
     v
Twilio call transfer
```

---

### Branch 6: Clinical / Treatment Questions

```
Caller asks: "Should I get a crown or a filling?" / "Is this normal after my extraction?"
     |
     v
"That is a great question for Dr. [NAME] — I would not want
 to give you the wrong information. Would you like me to
 schedule a consultation, or leave a message for the doctor
 to call you back?"
     |
     v
Either: schedule_appointment branch
     or: take_message flow (name, callback number, question summary)
```

---

## After-Hours Behavior

When calls arrive outside configured office hours:

```
"Thank you for calling [Practice Name]. Our office is currently closed.
 If this is a dental emergency, please call [EMERGENCY_NUMBER].
 Otherwise, I can schedule an appointment for you right now, or you
 can call us back during business hours. What would you prefer?"
     |
     |-- Schedule now --> Full scheduling branch (same as daytime)
     |-- Call back   --> "Of course. We'll be open [HOURS]. Talk to you then."
     |-- Emergency   --> "Please call [EMERGENCY_NUMBER] or 911 if this is urgent."
```

---

## Error and Fallback Handling

### Caller Unclear After Two Attempts

```
Agent cannot understand input → Reprompt once with simpler language
Still unclear → "I want to make sure someone can help you properly.
                 Let me have a team member give you a call back.
                 Can I get a good number to reach you?"
     |
     v
Collect callback number → Create callback task in Open Dental
```

### API Failure (Open Dental unreachable)

```
Appointment confirmed but Open Dental write fails → 
  Agent tells caller: "You are all set. You'll receive a confirmation shortly."
  System queues appointment data locally
  Fires alert webhook to staff
  Retries write up to 3 times with exponential backoff
  If all retries fail → flags for manual staff entry
```

### Caller Silence / Hang-Up

```
No response for 8 seconds → "Are you still there?"
No response for additional 5 seconds → "Feel free to call us back anytime. Goodbye."
Call ends cleanly.
```

---

## Data Collected Per Call Type

| Intent | Fields Collected | Written To |
|---|---|---|
| Schedule appointment | name, DOB, reason, datetime | Open Dental /appointments |
| Insurance inquiry | name, DOB, provider, member ID | Open Dental /tasks (staff) |
| General FAQ | none | — |
| Emergency | none | webhook log only |
| Billing | none | transfer log |
| Callback request | name, callback number, note | Open Dental /tasks (staff) |

---

## Confirmation Requirement

Any flow that writes to Open Dental requires explicit verbal confirmation from the caller before the write executes. The agent reads back all collected data and waits for a clear "yes," "correct," "that's right," or equivalent before firing the webhook that triggers the Open Dental write. A hesitant or unclear response routes back to re-prompt.
