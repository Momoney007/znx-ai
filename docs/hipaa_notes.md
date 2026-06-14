# HIPAA Architecture Notes

This document outlines the HIPAA-relevant design decisions made during the development of ZNX AI. It is intended for technical and compliance review, not as a certified compliance statement.

> **Disclaimer:** This is an architecture reference document produced during the design and prototyping phase. It does not constitute legal advice or a formal HIPAA compliance assessment. Any dental practice deploying this system must engage a qualified healthcare compliance officer and execute appropriate Business Associate Agreements (BAAs) before handling any real patient data.

---

## What Counts as PHI in This System

Under HIPAA, Protected Health Information (PHI) includes any individually identifiable health information. In the context of ZNX AI, the following data collected during calls qualifies as PHI:

- Patient name combined with date of birth
- Appointment reason (implies health condition or treatment)
- Insurance member ID combined with patient name
- Call recordings or transcripts that include any of the above

---

## Data Flow and PHI Boundaries

```
[Patient Phone Call]
       |
       | PHI enters system here
       v
[Twilio PSTN / SIP Layer]
  - Audio stream only at this layer
  - No PHI stored in Twilio call logs if properly configured
  - Twilio is HIPAA-eligible; BAA required
       |
       v
[Retell AI Voice Agent]
  - Receives audio stream, runs STT, LLM, TTS
  - PHI is present in transcript during active call session
  - Retell supports BAA for healthcare customers
  - Configure: disable transcript persistence beyond session
  - Do NOT enable Retell call recording storage for PHI-containing calls
       |
       v
[Webhook to Your Backend]
  - Structured appointment data (name, DOB, datetime, reason)
  - This is where PHI leaves Retell and enters your control
  - Your backend must be HIPAA-compliant infrastructure
  - Recommended: AWS with HIPAA BAA, or equivalent
  - Encrypt data in transit (TLS 1.2+) and at rest (AES-256)
       |
       v
[Open Dental API]
  - Existing HIPAA-covered system operated by the dental practice
  - PHI written here is under the practice's existing HIPAA program
  - Open Dental is deployed on-premises; data does not leave practice network
  - API calls from your backend to Open Dental should be made over the practice's internal network or VPN, not the public internet
```

---

## BAA Requirements

Three Business Associate Agreements are required before handling real patient data:

| Vendor | BAA Available | Notes |
|---|---|---|
| Twilio | Yes | Available in Twilio console under HIPAA compliance settings |
| Retell AI | Yes (healthcare tier) | Contact Retell sales; required before enabling healthcare use cases |
| Your backend infrastructure | Depends on provider | AWS, Azure, and GCP all offer HIPAA BAAs |

Open Dental does not require a BAA from ZNX AI because it is deployed and operated entirely by the dental practice. The practice's existing HIPAA program covers Open Dental.

---

## Minimum Necessary Principle

The agent is designed to collect only the specific data required to complete each task:

| Task | Data Collected | Data Not Collected |
|---|---|---|
| Schedule appointment | Name, DOB, reason, preferred time | SSN, medical history, medications, treatment details |
| Insurance inquiry | Name, DOB, provider, member ID | Plan details beyond what caller volunteers |
| FAQ | Nothing | — |
| Emergency escalation | Nothing | Call transfers before any data collection |

The agent prompt explicitly prohibits collecting information outside the defined slots. LLM temperature is set low (0.3) to reduce the risk of the agent going off-script and asking unauthorized questions.

---

## Transcript Handling

Retell AI generates transcripts of every call. For HIPAA compliance:

- **Do not** store full call transcripts in any non-BAA-covered system (e.g., a standard database, Airtable, Google Sheets)
- **Do not** send full transcripts via email or Slack without encryption
- **Do** configure Retell to send only structured slot data (not raw transcript) to your webhook endpoint
- **Do** log only the minimum fields needed for appointment confirmation and audit purposes
- If audit logging of transcripts is required, store in a HIPAA-covered encrypted store with access controls

---

## Access Controls

Production deployment should include:

- Role-based access to the staff dashboard (only staff who need it)
- Audit logging of all accesses to PHI (who accessed what and when)
- Automatic session timeout for dashboard logins
- MFA for all staff dashboard accounts
- No PHI in URL parameters, email subject lines, or notification titles

---

## Incident Response

If PHI is exposed, disclosed, or breached:

1. Isolate the affected system immediately
2. Notify the dental practice's HIPAA Privacy Officer within 24 hours
3. Practice's Privacy Officer assesses breach under HIPAA Breach Notification Rule
4. If breach meets reporting threshold: HHS notification required within 60 days
5. If 500+ individuals affected in one state: media notification required
6. Document everything from the moment of discovery

---

## What This Architecture Does Not Cover

- **Voicemail handling:** If calls go to voicemail and the voicemail system is not HIPAA-covered, PHI left in voicemails is a compliance gap. The ZNX AI agent does not leave voicemails and does not record them.
- **SMS/text confirmations:** If appointment confirmations are sent via SMS, the SMS system must be HIPAA-compliant. Standard carrier SMS is not HIPAA-covered. Use a HIPAA-eligible SMS provider (e.g., Twilio with BAA, or a healthcare-specific platform).
- **Multi-practice deployments:** Each practice location requires its own BAA review and may have separate HIPAA obligations.
- **State privacy laws:** Several states (California, Texas, etc.) have additional healthcare privacy requirements beyond HIPAA. This document covers federal HIPAA only.
