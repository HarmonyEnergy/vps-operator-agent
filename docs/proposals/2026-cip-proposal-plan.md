# 2026 Distributed Wind CIP — Proposal Plan

**Solicitation:** 2026 Distributed Wind Turbine Competitiveness Improvement Project (CIP) RFP
**Issuer:** National Laboratory of the Rockies (NLR), on behalf of DOE Wind Energy Technologies Office
**Posted on:** SAM.gov (full and open)
**Proposals due:** Thursday, 13 November 2026, 2:00 p.m. MST
**Technical questions due:** Friday, 16 October 2026 (to Kyndall.Jackson@nlr.gov; Q&A amendment posted to SAM.gov)
**Award type:** Firm fixed-price subcontract with price participation (cost share) plus NLR technical assistance
**Expected period of performance:** begins spring 2027 (per NLR pre-solicitation)
**Plan author:** Dan Clunies  |  **Plan date:** 1 October 2026

---

## 1. Decision summary

| Item | Recommendation |
|---|---|
| Lead proposal | **Topic: Inverter / power-electronics listing** for 50–150 kW distributed wind. Emerson as offeror, turbine OEM(s) as validation partners. |
| Second proposal (conditional) | **Type Certification and Listing** of the ESPE FX series (50–100 kW) for the U.S. market, only if ESPE commits to U.S. assembly and funds the cost share. |
| Do not pursue this round | Prototype design / manufacture topics (50% cost share, needs an in-house turbine design). |
| Go / no-go date | **Friday 9 October 2026** |
| Submit date (internal) | **Thursday 12 November 2026** (one-day buffer before the 2 p.m. MST deadline) |

**Why this shape.** The 2026 RFP's four stated priorities are (a) tested and certified turbine options, (b) validation and commercialization, (c) power electronics built for distributed wind and listed to national safety standards, and (d) advanced manufacturing to cut hardware cost. Priority (c) is the one where a large U.S. electronics and controls company has an unfair advantage and where the industry gap is documented: the 2025 round funded XFlow specifically because there is a "lack of UL 1741-SB listed power conversion system options for distributed wind" in the 5–150 kW class, and funded Matric/Windurance to cut converter cost for 15–95 kW turbines. A listed, grid-support-capable converter that any mid-size OEM can buy is exactly what NLR says it wants.

---

## 2. What we know and what we still need to confirm

### Confirmed (from the NLR notice and the DWEA Summer 2026 bulletin)
- 13 topic areas, each with its own cost-share percentage and funding cap.
- Offerors must prove U.S. incorporation, demonstrate team skills/capabilities, and provide financial information.
- Work must be performed in the U.S. or territories unless justified.
- NLR provides technical assistance alongside the subcontract (lab engineers, test support, certification guidance).
- A webinar is planned; registration will be on the NLR CIP webpage.

### Unverified — the RFP PDF could not be retrieved from this environment (SAM.gov and nlr.gov are blocked)
- The exact list of the 13 topics and their caps. The 2025 round had 10 topics (table below); three are new. Given the stated priorities, the likely additions are a power-electronics design/innovation topic distinct from listing, a field-validation topic, and an advanced-manufacturing topic.
- Evaluation criteria and weights (2024 RFP used weighted criteria including Team/Personnel at 15%).
- Page limits, volume structure, required forms, and the financial-disclosure template.
- Whether in-kind cost share is accepted and in what form.

**Action (Dan, by 2 Oct):** download the full RFP package and all attachments from SAM.gov, save to this folder, and update sections 2–4 of this plan.

### 2025 round topic structure (baseline for planning)

| 2025 topic | Max award | Cost share | 2026 relevance |
|---|---|---|---|
| Prototype Design Development | ~$150k–$400k | 20–50% | Low — needs own turbine design |
| Prototype Manufacture | $800k | 50% | Low |
| Prototype Installation and Testing | $400k | 20% | Medium — could pair with a converter field test |
| Component Innovation | ~$400k | 20% | **High** — converter/controls as the component |
| System Optimization | ~$400k | 20% | Medium |
| Small Turbine Certification and/or Listing | ~$400k | 20% | Low (≤ small class) |
| **Inverter Listing** | $800k | 20% | **Lead topic** |
| **Type Certification and Listing** (turbines up to 1 MW) | $800k | 20% | **Second proposal** (ESPE FX) |
| Manufacturing Process Innovation | ~$400k | 20% | Medium — U.S. converter or nacelle assembly |
| Technology Commercialization | ~$150k–$400k | 20–50% | Medium — fleet validation data |

Figures are from the 2025 RFP press coverage; confirm against the 2026 RFP before budgeting.

---

## 3. Proposal A (lead): Listed power-conversion system for mid-size distributed wind

**Working title:** *A UL 1741-SB / IEEE 1547-2018 listed, OEM-agnostic power conversion and control platform for 50–150 kW distributed wind turbines.*

**Offeror:** Emerson (U.S.-incorporated business unit to be named — confirm which legal entity holds SAM.gov registration, UEI, and will sign the subcontract).

**Problem statement (as NLR frames it).** Mid-size turbines (50–150 kW) are the sweet spot for farms and rural businesses, but almost none ship with a converter listed to UL 1741-SB with IEEE 1547-2018 grid-support functions. OEMs either adapt solar/ESS inverters (poor fit for variable-speed PMG generators, dynamic braking, and overspeed protection) or run unlisted equipment that triggers field evaluations, permitting delays, and utility interconnection rejections. This is a direct barrier to REAP-funded farm projects, which is the market Harmony served.

**Technical approach (three phases, matching CIP's phase convention).**
1. **Phase 1 — Requirements and design (months 1–6).** Interface spec covering PMG rectification, DC-link, dynamic brake/dump load control, grid-support functions (volt-VAR, freq-watt, ride-through), anti-islanding, and turbine supervisory I/O. Work with two or three OEM partners to define a common interface so one listing covers multiple turbines.
2. **Phase 2 — Build and field validation (months 6–14).** Two field units on partner turbines at U.S. sites; data logging to IEC 61400-12 and IEEE 1547.1 test plans; NLR technical assistance for test design and data review.
3. **Phase 3 — Listing (months 12–18).** NRTL certification to UL 1741 (3rd ed., Supplement SB) and IEEE 1547.1-2020; CSIP/DER interoperability where required; listing report to DOE and public summary.

**Partner shortlist (all DWEA members, all prior CIP recipients, which matters to evaluators):**
- Bergey Windpower (Excel 15 listed to UL 6142; Excel 75 in development under 2025 CIP) — a listed converter for the Excel 75 is a natural fit.
- NPS Solutions (NPS 100C) — 100 kW class, prior inverter-listing award.
- ESPE (via Harmony) — FX series 50–100 kW direct-drive PMG, currently relying on third-party converters.
- Carter Wind, Pecos Wind Power — larger class, optional.
- Windurance/Matric — potential competitor; decide early whether to compete or team.

**Budget framing.** Target the topic cap (historically $800k for inverter listing at 20% cost share, so roughly $1.0M total project value with $200k cost share). Emerson in-kind engineering time is the simplest cost-share source if the RFP allows it; otherwise cash.

**Scoring strengths to write to:** U.S. manufacturing footprint, documented quality system, NRTL relationships, prior IEEE 1547 listing experience, and a commercialization path that does not depend on any single turbine OEM surviving.

**Scoring risks to pre-empt:**
- Evaluators have historically funded small manufacturers. Address head-on: the award buys down the OEM-agnostic listing that no single small OEM can afford, and the product will be sold to all of them. Letters of intent from at least three OEMs are essential.
- "Why does Emerson need DOE money?" Answer with market size (hundreds of units per year, not tens of thousands), the NRTL cost that no OEM will fund alone, and the explicit RFP priority.

---

## 4. Proposal B (conditional): Type Certification and Listing — ESPE FX series for the U.S. market

**Offeror options:** (i) Harmony Energy Solutions (U.S.-incorporated; thin balance sheet after the 2025 REAP pause, which will show in the required financial disclosure), or (ii) a newly formed U.S. ESPE subsidiary or JV with Harmony as commercialization lead. Option (ii) is stronger on financials and on the "U.S. manufacturer" optics.

**Scope:** ANSI/ACP 101-1 (or IEC 61400-1 class) type certification plus UL 6141 listing of the FX EVO 21-50 / 30B-100, with U.S. nacelle or tower assembly to satisfy work-location rules and improve domestic-content positioning for 45X / ITC.

**Gating questions (submit to NLR by 16 Oct):**
1. Is a turbine designed outside the U.S. eligible for Type Certification and Listing if the offeror is U.S.-incorporated and final assembly, testing, and certification are performed in the U.S.?
2. Can a U.S. distributor/commercialization partner be the offeror with the foreign OEM as a subcontractor?
3. Is in-kind cost share (engineering labour, test hardware, site access) acceptable and at what valuation rules?
4. May one offeror submit to more than one topic, and may the same organisation appear as a partner on another offeror's proposal?
5. For inverter listing, must the listed unit be tied to a specific turbine model, or is an OEM-agnostic listing acceptable?

**Go only if** ESPE confirms in writing by 9 October: U.S. assembly commitment, cost-share funding, and release of design documentation to the certification body.

---

## 5. Compliance checklist (both proposals)

- [ ] SAM.gov registration active and UEI confirmed for the offeror entity (new registrations take 2–6 weeks — **start immediately** if Harmony or a new entity is the offeror)
- [ ] Proof of U.S. incorporation (certificate of good standing)
- [ ] Financial information per RFP template (likely last two years' statements; Emerson will need a business-unit-level approach agreed with corporate finance)
- [ ] Key-personnel resumes and a team matrix mapping expertise to tasks
- [ ] Letters of commitment from partners, including cost-share commitment language
- [ ] Work-location statement (all tasks in U.S.; justify any exception)
- [ ] Budget by phase and by task, firm fixed price, with milestone payment schedule
- [ ] Cost-share schedule matched to milestones
- [ ] IP and data-rights review (DOE flowdowns; NLR technical assistance implies data sharing)
- [ ] Export-control screen if ESPE design data is involved
- [ ] Emerson legal/contracts sign-off on subcontract terms before submission
- [ ] Webinar attended and Q&A amendment incorporated

---

## 6. Schedule (working back from 13 Nov 2026, 2 p.m. MST)

| Date | Milestone | Owner |
|---|---|---|
| Thu 1 Oct | Plan drafted (this document) | Dan |
| Fri 2 Oct | RFP package downloaded from SAM.gov; webinar registered; email Kyndall Jackson to be added to the update list | Dan |
| Mon 5 Oct | Identify Emerson offeror entity, SAM.gov/UEI owner, and executive sponsor; confirm internal bid process | Dan + Emerson BU lead |
| Tue 6 – Thu 8 Oct | Partner outreach calls: Bergey, NPS, ESPE, (Carter/Pecos optional). Ask for LOI and cost-share appetite | Dan |
| Fri 9 Oct | **Go / no-go** on Proposal A and B; freeze topic selection | Sponsor |
| Wed 14 Oct | Submit technical questions (two-day buffer before 16 Oct) | Dan |
| Mon 19 – Fri 30 Oct | Draft technical volume, work plan, budget, team section; collect LOIs and resumes | Dan + engineering lead |
| Mon 2 Nov | Q&A amendment review; adjust scope | Dan |
| Tue 3 – Fri 6 Nov | Red-team review; legal, finance, export-control sign-off | Reviewers |
| Mon 9 – Wed 11 Nov | Final edits, forms, cost-share letters, compliance check | Dan |
| **Thu 12 Nov** | **Submit** | Dan |
| Fri 13 Nov, 2 p.m. MST | Deadline | — |

---

## 7. Competitive landscape (2025 awards, for context)

Five companies, six projects, $4.4M DOE funding with $2.3M private cost share:
- Bergey Windpower — Excel 75 development and certification (three phases)
- Matric Limited — 20% cost reduction on Windurance UL-listed inverters/converters for 15–95 kW turbines (manufacturing process)
- NPS Solutions — ACP 101-1 certification of NPS 100C-27
- Wetzel Wind Energy Services — new Skystream blade
- XFlow Energy — (1) VAWT prototype manufacture, install, test, certify; (2) power conversion and control system toward UL 1741-SB listing, targeting 5–150 kW turbines

Implication: the power-electronics lane has two incumbents (Matric/Windurance, XFlow). Differentiate on OEM-agnostic design, grid-support certification depth (IEEE 1547-2018 full compliance), and production scale, not on "first to list".

---

## 8. Open items for Dan

1. Which Emerson business unit and legal entity would be the offeror, and who is the executive sponsor? This decides whether Proposal A is viable at all.
2. Does Emerson have an existing UL 1741 / IEEE 1547 listed inverter platform that can be adapted, or is this a new product? The answer sets Phase 1 scope and budget.
3. Does ESPE want the U.S. market badly enough to fund Proposal B's cost share and commit to U.S. assembly?
4. Is Harmony Energy Solutions' SAM.gov registration current?
5. Confirm there is no conflict between Dan's Emerson role and a Harmony-led submission; if both proposals go in, keep the teams and cost-share sources separate.

---

## Sources
- NLR RFP notice email, Kyndall Jackson, Senior Subcontract Administrator (received by Dan, forwarded 1 Oct 2026)
- DWEA Summer 2026 Bulletin, "NLR Previews Next Round of Distributed Wind CIP Funding"
- DWEA Jan–Feb 2026 Bulletin, "2025 Competitiveness Improvement Project selections announced"
- NLR/NREL CIP program page and 2025 RFP press coverage (topic list and award caps)
- SAM.gov pre-solicitation 4c7006e313044ff08d03719b67007d7b (summary only; full text not retrievable from this environment)
