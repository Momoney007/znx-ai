# Business Validation — Discovery Research Summary

## Methodology

Before building, I conducted structured discovery conversations with 23 dental practice owners and office managers across the Houston, TX metro area between late 2024 and early 2025. The goal was to validate the core problem hypothesis before committing to the technical build.

**Hypothesis:** Dental front desks are overwhelmed by routine, repetitive inbound phone calls that require no clinical skill and could be handled by AI, at a cost savings significant enough to justify a monthly SaaS fee.

---

## Who I Talked To

| Type | Count |
|---|---|
| Solo practice owners (dentist-operator) | 11 |
| Office managers at small group practices (2–5 dentists) | 8 |
| DSO regional managers (5–20 locations) | 4 |
| **Total** | **23** |

Geographic coverage: Houston Heights, Katy, Sugar Land, Pearland, Spring, The Woodlands, Memorial area.

---

## Key Findings

### Problem Validation

**100% of respondents confirmed that phone volume was a top-3 operational pain point.**

The most common words used across interviews: *overwhelming*, *chaotic*, *we miss calls*, *my front desk is burned out*, *I'm losing patients to voicemail*.

Specific pain points reported:

- Missed calls during peak morning hours (8–10am) when every chair is full and staff are checking in patients
- After-hours calls going to voicemail; significant percentage of callers do not leave messages and call a competitor instead
- Front desk staff spending 60–70% of their time on calls that did not require their training or expertise
- Scheduling errors from rushed phone conversations (wrong dates, wrong procedure booked, wrong doctor)
- Staffing gaps from turnover; average front desk tenure reported at 14 months

**78% reported at least one staffing gap in the past 6 months that directly affected phone coverage.**

---

### Cost Data (Self-Reported)

Respondents were asked to estimate their front desk phone-handling cost. Figures are self-reported and not audited.

| Metric | Range | Average |
|---|---|---|
| Hourly wage (front desk) | $15–$24/hr | $18/hr |
| Hours/week on phone tasks | 12–28 hrs | 19 hrs |
| Annual cost (phone-only hours) | $11,700–$35,100 | $22,700 |
| Fully loaded cost (wage + benefits + turnover) | $36,000–$54,000/yr | $44,000 |

The fully loaded cost range of $36,000–$54,000/year is the relevant figure, as it represents the true economic cost of maintaining a single FTE whose primary function is phone call handling.

---

### Willingness to Pay

Respondents were asked: *"If a system reliably handled appointment scheduling, basic insurance questions, and general FAQs by phone, 24/7, with no missed calls — what would that be worth to you per month?"*

| Price Point | Expressed Interest |
|---|---|
| $299/month | 21 of 23 (91%) |
| $599/month | 16 of 23 (70%) |
| $899/month | 14 of 23 (61%) |
| $1,200/month | 6 of 23 (26%) |

**Conclusion:** The $599–$899/month price range has strong expressed interest from 61–70% of the sample. At $899/month ($10,788/year), the product pays for itself if it eliminates just 3–4 months of one front desk staffer's phone hours annually.

---

### Objections Raised

| Objection | Frequency | Notes |
|---|---|---|
| "Patients won't want to talk to a robot" | 17/23 | Most common. Mitigated in testing by not identifying as AI unless asked. |
| "What if it books the wrong thing?" | 14/23 | Requires confirmation readback loop before any write. |
| "We tried something like this before and it didn't work" | 7/23 | Prior experiences were mostly phone trees/IVR, not conversational AI. |
| "HIPAA compliance concerns" | 9/23 | Significant. Required detailed explanation of BAA structure. |
| "I'd need to try it before paying" | 19/23 | Strong signal for free trial or pilot structure. |

---

### Segment Analysis

**Solo practice owners** were the most interested but the slowest to commit. They make every decision themselves and are highly risk-averse about anything that touches patient interaction. Sales cycle estimated at 3–6 months.

**Office managers at small group practices** showed the strongest urgency. They are personally experiencing the phone volume problem daily and have budget authority up to a threshold (~$1,000/month without owner approval). Best first-sale target.

**DSO regional managers** showed the highest potential deal size but had procurement processes that made quick sales impossible. Best long-term enterprise target; wrong first customer.

---

## Key Insight for Go-To-Market

The right first customer is an office manager at a 2–5 dentist practice who has personally missed calls this week and is actively frustrated. Not the dentist-owner who is insulated from the day-to-day phone chaos. Not the DSO with a 6-month procurement cycle.

The objection about "patients won't like talking to a robot" is best handled by not calling it a robot in the pitch. The product is a "24/7 receptionist" or "overflow answering service." Demo it live. Let them hear Maya handle a sample call. The objection dissolves in about 90 seconds.

---

## What I Would Do Differently

If I ran this discovery phase again, I would:

1. **Talk to 5 before talking to 23.** The first 5 interviews revealed 90% of what 23 interviews confirmed. The additional 18 validated but did not surprise.

2. **Demo earlier.** Even a scripted demo call (playing a recording of the agent) would have moved conversations further than a verbal pitch. I had the technical prototype working but did not use it in sales conversations effectively.

3. **Target office managers first, not owners.** I reached owners first because they were easier to find (Google Maps, LinkedIn). Office managers were harder to reach but more motivated buyers.

4. **Ask about budget explicitly.** I asked about willingness-to-pay in abstract terms. I should have asked: "Do you currently pay for an answering service?" (Many did, at $200–$600/month.) That's the competitive frame, not replacing a staff member.
