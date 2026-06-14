# ZNX AI — AI Voice Receptionist for Dental Practices

An AI-powered phone receptionist designed to automate front-desk operations at dental offices, including appointment booking, insurance verification, and general patient inquiry handling. Built to address a real operational pain point: dental offices spend 15 to 25 hours per week on phone-based front-desk tasks that require no clinical skill and are a primary source of staff burnout and scheduling errors.

---

## The Problem

The average dental practice receives 40 to 80 inbound calls per day. Most are:

- Appointment requests and reschedules
- Insurance verification and coverage questions
- Post-appointment follow-ups and payment questions
- General FAQs (hours, location, accepted plans)

None of this requires a licensed dental professional, yet front-desk staff spend the majority of their time on it, at a fully loaded cost of roughly $45,000 per year per FTE. Missed calls during peak hours or after-hours mean lost patients. Human error in scheduling causes costly no-shows and double-bookings.

---

## The Solution

ZNX AI is an AI voice agent that picks up every call, 24/7, handles the full conversation in natural language, and pushes structured data to the practice management system. It does not replace staff. It eliminates the routine call volume so staff can focus on in-office patient experience.

### Core Capabilities

- **Appointment scheduling** — collects patient name, DOB, reason for visit, preferred time, and writes the appointment directly to Open Dental
- **Insurance verification** — captures insurance provider and member ID, routes to verification workflow or flags for staff callback
- **Patient FAQ handling** — hours, location, accepted insurance plans, parking, post-procedure instructions
- **After-hours coverage** — answers calls and books appointments when the office is closed
- **Call routing** — escalates to a live human when the request falls outside the agent's defined scope (pain emergencies, billing disputes, complex treatment questions)

---

## Architecture

```
[ Inbound Patient Call ]
         |
         v
[ Twilio Phone Number ]
  - Provisions a local phone number for the practice
  - Handles PSTN routing and call forwarding
         |
         v
[ Retell AI Voice Agent ]
  - Converts speech to text in real time
  - Runs LLM-based conversation engine
  - Handles intent detection, slot filling, and response generation
  - Manages conversation state across multi-turn dialogue
         |
    _____|_____
   |           |
   v           v
[ Scheduling   [ FAQ + Insurance ]
  Intent ]       - Answers from
  - Slot           practice knowledge
    filling:        base configured
    name, DOB,      in agent prompt
    date, time,
    reason ]
         |
         v
[ Open Dental API ]
  - Writes appointments to practice schedule
  - Reads existing patient records for returning callers
  - Triggers confirmation workflow
         |
         v
[ Staff Dashboard Notification ]
  - New appointment summary
  - Flagged calls requiring human follow-up
  - After-hours log review
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Telephony | Twilio (PSTN routing, number provisioning) |
| Voice AI | Retell AI (STT, LLM conversation engine, TTS) |
| Practice Management | Open Dental (scheduling, patient records) |
| Language Model | GPT-4o via Retell AI |
| Configuration | JSON-based agent config, prompt engineering |

---

## HIPAA Considerations

Dental offices handle Protected Health Information (PHI). This system was architected with the following in mind:

- **No PHI logging in Retell** — call transcripts configured to not persist sensitive patient data beyond the session
- **Twilio HIPAA eligibility** — Twilio offers a BAA (Business Associate Agreement) for covered entities; required before production deployment
- **Retell BAA** — Retell AI supports BAA execution for healthcare customers
- **Open Dental data boundary** — PHI only touches Open Dental's database, which is the practice's existing HIPAA-covered system
- **Minimum necessary principle** — agent only collects the fields required to complete the specific task (scheduling, verification); no additional data collected or stored

> Note: A full HIPAA compliance review by a qualified healthcare compliance officer is required before production deployment. This architecture represents design intent, not a certified compliance claim.

---

## Agent Configuration

The Retell AI agent is configured via a structured prompt and a set of defined intents. See [`config/agent_config.json`](config/agent_config.json) for the full configuration schema.

Key prompt design decisions:

- **Persona**: Professional, warm, brief. Does not identify as AI unless directly asked. Identifies as the practice's front desk.
- **Scope control**: Hard boundaries on what the agent handles vs. escalates. Any mention of pain, emergency, or clinical advice immediately transfers to a live human.
- **Confirmation loop**: Agent reads back all collected information before writing to Open Dental to reduce booking errors.
- **Error handling**: If the agent cannot understand the caller after two attempts, it offers a callback and routes the call.

---

## Call Flow Example

```
Agent:   "Thank you for calling Houston Family Dental, this is Maya.
          How can I help you today?"

Patient: "Hi, I need to schedule a cleaning."

Agent:   "Of course. Can I get your first and last name?"

Patient: "Sarah Johnson."

Agent:   "Hi Sarah. Are you a new patient or have you been here before?"

Patient: "I've been there before."

Agent:   "Great. Can I get your date of birth to pull up your file?"

Patient: "March 12th, 1989."

Agent:   "Thank you. For a routine cleaning, I have availability
          this Thursday at 10am or Friday at 2pm. Which works better?"

Patient: "Thursday works."

Agent:   "Perfect. I've got you scheduled for Thursday at 10am
          with Dr. Patel for a routine cleaning. You'll get a
          confirmation text shortly. Is there anything else
          I can help you with?"
```

---

## Business Validation

Before building, I did discovery calls with 23 dental practice owners and office managers across Houston, TX. Key findings:

- **100%** reported that phone volume was a top-3 operational complaint
- **78%** had experienced at least one staffing gap in the past 6 months that affected phone coverage
- **Average quoted cost** of front-desk staff handling only phone duties: $38,000 to $52,000/year
- **Willingness to pay**: 14 of 23 expressed interest at a $599 to $899/month price point if the system handled scheduling reliably

Modeled revenue impact per practice: **$35,000 to $45,000/year in staffing offset** against a $7,200 to $10,800/year software cost.

---

## Project Status

This project reached the prototype and business validation stage. Full production deployment requires:

- BAA execution with Twilio and Retell AI
- Open Dental API access approval per practice
- Practice-specific agent prompt customization and testing
- Staff training on dashboard and escalation protocols

---

## What I Learned

**On the technical side:**
Conversational AI for phone calls is harder than chatbots because you lose all the affordances of a screen. Callers mumble, switch topics mid-sentence, and hang up faster than they would close a chat window. Retell's STT handles this better than raw Whisper for real-time calls, but prompt engineering for voice requires a different mental model than text-based prompting. Shorter agent turns, more confirmation checkpoints, and explicit escalation triggers matter far more in voice than in text.

**On the business side:**
The product-market fit signal was strong, but the sales motion for healthcare AI is slow. Dental practice owners are risk-averse about anything that touches patient interaction. The right first customer is not a solo practice — it's a DSO (Dental Support Organization) with 5 to 20 locations that has already invested in practice management software and is actively looking for staff cost reduction. Solo practices move too slowly and want too much customization per location.

---

## Repository Structure

```
znx-ai/
├── README.md                    # This file
├── config/
│   ├── agent_config.json        # Retell AI agent configuration schema
│   └── open_dental_mapping.json # Field mapping: agent slots to Open Dental fields
├── scripts/
│   ├── provision_number.py      # Twilio number provisioning script
│   └── test_webhook.py          # Local webhook testing for Retell callbacks
├── docs/
│   ├── call_flow.md             # Detailed call flow documentation
│   ├── hipaa_notes.md           # HIPAA architecture decisions
│   └── discovery_findings.md   # Business validation research summary
└── assets/
    └── architecture_diagram.png # System architecture visual
```

---

## Contact

**Momin Abbas**
CS Student, University of Houston | Cybersecurity Track
[LinkedIn](https://linkedin.com/in/mominabbas) · [GitHub](https://github.com/mominabbas)
