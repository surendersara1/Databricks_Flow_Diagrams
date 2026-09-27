# Deep-Dive Business Case — Sterling Meridian Bank
## A Regulated Lakehouse for Retail, Commercial and Capital Markets

> **Fictional composite.** Sterling Meridian Bank ("SMB") does not exist. It is assembled from patterns
> seen repeatedly across global systemically important banks and large universal banks.
> **Every number in this document is illustrative** and exists so that the shape of the argument can be
> examined, challenged and re-based against a real client's figures. Nothing here is a benchmark.
>
> **Regulatory language.** Where this document refers to a regulatory obligation it does so generically —
> "the jurisdiction's capital reporting regime", "the home regulator's risk data aggregation expectations".
> Specific rule text is deliberately not quoted. **No platform makes a bank compliant.** A platform can
> make evidence cheap to produce, controls consistent to apply, and lineage continuous rather than
> reconstructed. The attestation remains the bank's.
>
> **Product naming.** Current Databricks names only: Lakeflow Connect, Lakeflow Jobs, Lakeflow Spark
> Declarative Pipelines, Declarative Automation Bundles, Unity Catalog, OpenSharing (formerly Delta
> Sharing), Lakehouse Federation, Databricks SQL. Capability claims are sourced from the poster series at
> `D:\NBS_DataBricks_Data_Associate\MASTER_Databricks_Study_Series\` and its `*_SOURCES.md` files.
> Anything not verified there is written **[TBC]** rather than asserted.

**Document status:** Deep-dive business case, v1.0
**Audience:** Group CDO, Group CRO, CFO, Head of Regulatory Reporting, CISO, COO Capital Markets
**Prepared for:** Investment committee and the Group Data Council

---

## Table of contents

| § | Section |
|---|---|
| 1 | Executive summary |
| 2 | Current state |
| 3 | The data inventory |
| 4 | Use cases and value |
| 5 | Target architecture |
| 6 | Data products and domain ownership |
| 7 | Governance, risk and compliance |
| 8 | Delivery plan |
| 9 | Team, ways of working and enablement |
| 10 | Cost model and commercials |
| 11 | Risks and mitigations |
| 12 | Success metrics |
| 13 | What we would draw next |
| 14 | Appendix — glossary and assumptions register |

---

# 1. Executive summary

## 1.1 The bank

| Dimension | Figure (illustrative) |
|---|---|
| Retail banking | 6 countries — UK, Ireland, Germany, Poland, Singapore, Hong Kong |
| Retail customers | ~18.4 m; ~26 m accounts; ~31 m active cards |
| Commercial / corporate | ~240,000 clients across 14 booking locations |
| Capital markets | Equities (cash and derivatives), FX, rates; London, New York, Singapore |
| Employees | ~62,000, of whom ~9,400 in technology |
| Total assets | ~USD 780 bn |
| Legal entities in scope | 8 material entities; 3 separately capitalised and separately reported |
| Regulators | 1 home prudential, 5 host prudential, 3 conduct/securities, 2 market-infrastructure |

## 1.2 The problem in one paragraph

SMB cannot answer, within the window its regulators expect, the question *"what was our exposure to this
counterparty, as the books stood at this moment, and prove where every number came from."* The bank
answers it today by assembling extracts from a mainframe core, a Teradata risk warehouse, a Hadoop
landing zone and roughly 1,900 controlled spreadsheets, then reconciling them by hand. Assembly takes
between four and eleven days depending on the report. Two open supervisory findings cite the absence of
demonstrable end-to-end lineage. A prudential add-on is currently held against data-quality uncertainty.
Delivering a new regulatory report takes nine months, of which six are spent locating and reconciling
source data rather than writing logic.

## 1.3 The outcome we propose

A Unity Catalog-governed lakehouse that becomes the **single point of assembly** for regulatory, risk,
finance and customer data — with three properties the current estate does not have:

1. **Point-in-time correctness is a first-class property, not a convention.** Every fact carries both when
   it happened and when the bank learned it. As-of reporting, restatement and late correction are
   supported by the data model, not by a rerun and a memo.
2. **Lineage is continuous and machine-readable**, captured by the platform as work executes and
   exportable as an evidence pack, rather than reconstructed by an analyst after the request arrives.
3. **The capital-markets arm is separated by construction**, not by policy — information barriers
   expressed as Unity Catalog grants and attribute-based policies over governed MNPI tags, with every
   access attempt in the audit trail.

## 1.4 Value case (illustrative, steady-state run-rate)

| Value stream | Annual range (USD m) | Confidence |
|---|---|---|
| Regulatory reporting cost and add-on release | 18 – 26 | Medium-high |
| Intraday risk aggregation | 12 – 20 | Medium |
| Real-time fraud and AML detection | 22 – 38 | Medium |
| Customer 360 (retail + commercial) | 15 – 30 | Medium-low |
| Credit decisioning features | 9 – 16 | Medium |
| Market surveillance | 4 – 8 | Medium |
| Finance close acceleration | 6 – 11 | Medium-high |
| Client reporting | 3 – 7 | Low-medium |
| **Total steady-state run-rate** | **89 – 156** | — |
| Decommission savings (Teradata, Hadoop, 2 bespoke marts) from month 22 | 14 – 19 | Medium-high |

Against an illustrative Year-1 programme cost of **USD 26 – 34 m** (platform, cloud, systems integration,
internal FTE) and a steady-state run cost of **USD 11 – 16 m/yr**, payback lands at **14 – 20 months** on the
mid case. Every one of these numbers is a placeholder for a client-supplied baseline; §10 states which
number must come from where.

## 1.5 Timeline

| Phase | Weeks | Exit gate |
|---|---|---|
| 0 — Mobilise and prove access | 1 – 6 | Mainframe extract landed in a governed volume; UC metastore live; first catalog topology approved by Legal |
| 1 — Thin regulated slice | 7 – 22 | One statutory report produced end to end and dual-run against the incumbent |
| 2 — Reconcile and attest | 23 – 34 | Three consecutive cycles reconciled to the penny; first examiner-ready evidence pack |
| 3 — Domain build-out | 35 – 70 | Customer, payments, positions, risk, finance and market-data products published with contracts |
| 4 — Real-time and decisioning | 55 – 86 | Fraud scoring in production; intraday exposure live for two desks |
| 5 — Decommission | 78 – 104 | Teradata risk mart and Hadoop landing zone retired under formal gates |

## 1.6 The ask

| Item | Detail |
|---|---|
| Funding | Year 1 USD 26 – 34 m; 3-year envelope USD 58 – 76 m (illustrative) |
| Executive sponsor | Group CDO, with a named Group CRO deputy. A data programme without a risk sponsor fails at the attestation gate |
| Named client roles | Regulatory Reporting lead, Model Risk lead, Compliance (MNPI and surveillance) lead, Mainframe Services lead, Group Architecture, Data Privacy Officer |
| Decisions required at kick-off | Cloud region map per legal entity; customer-managed key policy; mainframe extraction mechanism and MIPS budget; which report is the thin slice |
| Standing commitment | Four-eyes approval capacity on production change, and a named examiner-facing evidence owner |

## 1.7 What we are explicitly not promising

| Not promising | Why it matters |
|---|---|
| That the platform makes SMB compliant | Compliance is an attestation by the bank's officers. The platform makes the evidence for that attestation continuous and cheap |
| That the mainframe is retired | Core banking replacement is a separate, larger programme. This one makes the mainframe's data usable and auditable outside it |
| That reconciliation disappears | It moves from spreadsheets to code, becomes automated and regression-tested, and it is still reconciliation |
| A fixed platform cost | Databricks pricing is contract-specific. §10 gives drivers, ratios and control mechanisms, and says where the real number must come from |

---

# 2. Current state

## 2.1 The estate

```
  MAINFRAME (z/OS)              RISK WAREHOUSE            "DATA LAKE"
  COBOL + DB2, 4 LPARs          Teradata, ~340 TB          Cloudera CDP, ~5.2 PB
  deposits, loans, cards,       credit + market risk       ~420 nodes
  GL postings                   marts, T+1 batch           mostly a landing zone
        |                               |                         |
        | nightly VSAM/DB2 unloads      | ~11,000 Informatica     | Sqoop + Flume, 2016 era
        | ~2,900 scheduler jobs         | mappings                | Hive tables with no owner
        v                               v                         v
  =========================== RECONCILIATION LAYER ===========================
   ~1,900 controlled spreadsheets + 61 Access databases + 2 Alteryx estates
  ============================================================================
        |                   |                    |                   |
   Regulatory          Finance close        Risk committee      Front office
   reporting (manual)  (11 working days)    packs (T+2)         (own extracts)
```

## 2.2 What each component actually is

| Component | Reality |
|---|---|
| **Core banking** | COBOL on z/OS, DB2 for z/OS, 4 LPARs split by region. ~38 years of accretion. Batch window 22:00–04:30 local per region; the Singapore and Hong Kong windows overlap the European online day. Core change requires a 14-week release train |
| **Risk data warehouse** | Teradata, ~340 TB, fed by ~11,000 Informatica mappings. Designed for T+1 credit risk, extended to market risk in 2019. Missed its 11:00 T+1 publication in 4 of the last 24 month-ends |
| **"Data lake"** | Cloudera CDP, ~5.2 PB, ~420 nodes. In practice a landing zone: ~72% of stored bytes are raw copies read by at most one consumer. No enforced schema, no column-level access control, no lineage. Vendor support runway ends inside the programme window |
| **Market data** | Two primary vendor feeds (real-time prices; end-of-day reference and corporate actions), one ratings feed, one FX composite. Licensed per user and per application, with redistribution clauses the current estate cannot evidence compliance against |
| **Customer view** | Retail CIF on the mainframe; commercial client data on a separate corporate banking platform; capital markets keeps its own client and legal-entity master. A group client hierarchy exists in a fourth system, maintained manually |
| **Regulatory reporting** | A reporting engine consuming flat files, wrapped in manual preparation. Every submission has a reconciliation workbook with sign-off cells |
| **Scheduling** | Three schedulers (mainframe, distributed, cloud) with no shared dependency graph. The critical path is known to four people |

## 2.3 Pain, in business terms

| Pain | Illustrative magnitude | Who feels it |
|---|---|---|
| Open supervisory findings on risk data aggregation and lineage | 2 findings, both in their second remediation extension | Group CRO, Board Risk Committee |
| Prudential add-on held against data uncertainty | ~USD 240 m CET1 held; at a 12% cost of equity ≈ **USD 29 m/yr carrying cost** | CFO, Treasurer |
| Regulatory reporting run cost | ~185 FTE across group and entities; ~USD 21 m/yr fully loaded | Head of Regulatory Reporting |
| Report change lead time | **9 months** median from request to first production submission | Every regulatory stakeholder |
| Fraud and scam losses | ~USD 128 m/yr gross (cards, payments, APP scams); alert false-positive ratio ≈ 18:1 | Head of Financial Crime |
| AML alert backlog | ~14,000 open alerts; median age 26 days against a 30-day internal standard | MLRO |
| Commercial client onboarding | Median 47 days from KYC-complete to first transaction; ~USD 60 m annualised revenue sits in the queue at any moment | Head of Commercial Banking |
| Finance close | 11 working days to a signed group close; 3 of them reconciliation | Group Financial Controller |
| Intraday counterparty exposure | Available T+1. In a stress week the bank manages exposure on a one-day-old picture | Group Treasurer, CRO |
| Client reporting | Institutional clients receive T+2 position and transaction reports; two mandates cited this in an RFP loss | Head of Client Service |
| Analyst time on data plumbing | ~62% of quantitative analyst hours spent sourcing and reconciling rather than analysing | Heads of Risk Analytics, Finance |

## 2.4 Pain, in engineering terms

| Pain | Consequence |
|---|---|
| **No lineage for attestation** | The bank cannot mechanically answer "which upstream field produced this cell". Attestation is an analyst writing a memo from tribal knowledge. Each supervisory information request costs 200–600 person-hours |
| **Overnight-only batch** | Every fact is at best last night's snapshot. Intraday questions are answered from front-office spreadsheets outside the control environment |
| **Brittle reconciliations** | ~1,900 controlled spreadsheets, each a single point of failure with a single owner. Breaks are discovered late, at sign-off |
| **No test coverage** | The Informatica estate has no automated regression suite. A change to a shared mapping is validated by running month-end and looking at the numbers |
| **No point-in-time model** | Restating a prior period means restoring a backup. Late corrections overwrite history in place; the bank cannot reproduce what it reported on the day it reported it |
| **Duplicate golden sources** | Counterparty identifiers exist in 7 systems with 3 hierarchies. The golden source is whichever one the current report author trusts |
| **No schema contract** | Upstream teams change field semantics without notice. Detection happens downstream at reconciliation, weeks later |
| **Access control by system, not by data** | A user with access to the corporate banking platform sees all of it. With no column-level control, segregation is achieved by copying subsets into separate systems, which multiplies the estate |
| **Compute and data coupled** | Teradata capacity is the constraint on analytics. Risk analysts queue behind the regulatory batch |
| **Environments are not equivalent** | The non-production estate has masked, partial and stale data. A change that passes there routinely fails in production for data reasons |

## 2.5 Why "another warehouse" does not fix this

Three reasons, each of which the target architecture must answer directly:

1. **The problem is provenance, not query performance.** A faster warehouse that still receives
   hand-assembled extracts inherits the attestation gap unchanged.
2. **The problem is semantics, not storage.** The Hadoop estate proves that landing everything cheaply
   produces a swamp unless ownership, contracts and access control land with the data.
3. **The problem is bitemporality, not batch throughput.** Any design that keeps only current state fails
   at the first restatement and at every as-of enquiry.

---

# 3. The data inventory

This is the section the architect builds from. One table per source system: what it is, what it carries,
how it moves, how big, how fast, how dirty, how sensitive, how long it must be kept, and — the column
that drives the build — **the ingestion pattern it dictates**.

Volumes are illustrative and describe a normal business day unless stated. "Peak" means the busiest hour
of the busiest day, typically month-end or a quad-witching Friday.

## 3.1 Source register — summary

| # | System | Domain | Latency need | Classification | Pattern |
|---|---|---|---|---|---|
| S1 | Core banking (DB2 z/OS) | Customer, accounts, balances | 15 min → intraday | PII, Confidential | Log-based CDC + reconciling batch extract |
| S2 | Payments hub (ISO 20022) | Payments | Seconds | PII, Confidential | Kafka → Structured Streaming |
| S3 | Card authorisation switch | Cards | Seconds for analytics | PII, **PCI** | Kafka → Structured Streaming; Auto Loader for clearing |
| S4 | General ledger (Oracle) | Finance | Hourly; continuous at close | Confidential, periodic MNPI | Lakeflow Connect managed CDC |
| S5 | Order / execution management (FIX) | Positions, trading | Seconds | **MNPI**, Confidential | Kafka drop-copy → Structured Streaming |
| S6 | Market data — real-time | Market data | Seconds | Licensed | Feed handler → Kafka → Structured Streaming |
| S7 | Market data — reference / EOD | Market data | Daily, pre-open | Licensed | Auto Loader; OpenSharing where offered |
| S8 | KYC / AML case management | Risk, Customer | 15 min | PII, **Restricted** | Lakeflow Connect managed CDC (SQL Server) |
| S9 | CRM (retail + commercial) | Customer | Hourly; 15 min for consent | PII | Lakeflow Connect SaaS + SQL Server connectors |
| S10 | Collateral and positions | Positions, Risk | 15 min intraday | Confidential, MNPI-adjacent | Lakeflow Connect CDC (PostgreSQL) + Auto Loader + Kafka |
| S11 | Credit decisioning platform | Risk, Customer | Minutes | PII | Kafka events + Auto Loader |
| S12 | Digital channel and call centre | Customer | Seconds | PII, PCI leakage risk | Kafka / Zerobus → Structured Streaming; Auto Loader |
| S13 | Third-party reference data | Reference | Minutes (sanctions) to daily | Licensed | OpenSharing preferred; Auto Loader otherwise |
| S14 | Legacy risk warehouse (Teradata) | Risk | Migration only | Confidential | Lakehouse Federation for parallel run; bulk extract for history |

## 3.2 S1 — Core banking, DB2 for z/OS

| Attribute | Detail |
|---|---|
| **Contents** | Customer information file (~18.4 m parties), deposit accounts (~26 m), loans and mortgages (~4.1 m), card accounts (~31 m), balances, standing orders, interest accruals, product master, branch and entity codes |
| **Format / protocol** | DB2 for z/OS tables; some entities only in VSAM/IMS, reached through a COBOL extract. EBCDIC, packed decimal (COMP-3), REDEFINES, OCCURS DEPENDING ON. Copybooks are the only schema definition and ~15% are stale |
| **Volume** | ~41 m changed rows/day across ~340 in-scope tables; ~62 GB/day of change; full-table footprint ~19 TB across 4 LPARs. Peak hour ~6.2 m rows |
| **Change rate** | Balances change daily for ~9% of accounts; CIF demographics ~0.4%/day; product master ~monthly |
| **Latency requirement** | **15 minutes** for balances and positions feeding intraday risk and fraud context; **T+1 06:00** for the reconciling batch that anchors regulatory reporting |
| **Quality issues** | Duplicate parties across country LPARs (~11% of retail parties have a probable duplicate); free-text addresses; date sentinels (`00000000`, `9999-12-31`); implied decimals; soft deletes as status codes with per-country conventions |
| **Classification** | PII (name, address, national identifier, date of birth), Confidential; a subset is special-category under some privacy regimes |
| **Retention / residency** | 7–10 years post account closure by jurisdiction **[TBC per entity with Legal]**. Two jurisdictions require in-country processing and storage for retail customer data — **residency map [TBC]** |
| **Ingestion pattern dictated** | **Two-track.** (a) **Log-based CDC** from the DB2 log for the ~90 high-velocity tables, landed to bronze as an append-only change stream. (b) **Daily full or high-water-mark extract** for the ~250 low-velocity tables and, critically, as the **reconciling anchor** that proves the CDC stream did not drift. Both land in a Unity Catalog external volume and are read with **Auto Loader**. Copybook decoding happens once, in bronze, and the decoder is version-controlled alongside the pipeline |
| **Why not a managed connector** | The Lakeflow Connect managed database connectors cover MySQL, PostgreSQL, SQL Server and Oracle (Oracle via LogMiner). **DB2 for z/OS is not among them.** The mainframe route is therefore a third-party or IBM log-capture product writing to object storage or Kafka, then Auto Loader or Structured Streaming. **Product selection, licence and MIPS cost [TBC with Mainframe Services]** |

## 3.3 S2 — Payments hub

| Attribute | Detail |
|---|---|
| **Contents** | ISO 20022 `pacs.008` / `pacs.002` / `camt.05x`, domestic instant payments, SEPA, cross-border, direct debits, standing orders, payment status events |
| **Format / protocol** | XML (ISO 20022) plus a normalised internal Avro envelope on Kafka; ~14 topics |
| **Volume** | ~42 m messages/day; ~96 GB/day raw XML, ~31 GB/day Avro. Peak ~4.8 m messages/hour on salary days |
| **Change rate** | Append-only event stream; each payment produces 3–6 lifecycle events |
| **Latency requirement** | **Seconds** for fraud scoring and liquidity; 5 minutes for operational dashboards; T+1 for regulatory aggregates |
| **Quality issues** | Free-text remittance fields containing PII; inconsistent debtor/creditor identification across corridors; late `camt` reversals arriving up to 5 business days after the original — the **canonical late-arriving-correction case** |
| **Classification** | PII, Confidential; remittance free-text is a PII leakage channel |
| **Retention / residency** | 5–7 years by jurisdiction; sanctions-screening evidence retained longer. Cross-border corridors touch all six retail countries — **corridor-level residency [TBC]** |
| **Ingestion pattern dictated** | **Kafka → Structured Streaming into a bronze streaming table**, one flow per topic family, with the raw payload preserved verbatim beside the parsed columns. Reversals and status updates are **not** applied in place in bronze; they become new rows and are resolved in silver by an **AUTO CDC flow sequenced by event timestamp**. Idempotency key `(msg_id, event_type, event_ts)` |

## 3.4 S3 — Card authorisation switch

| Attribute | Detail |
|---|---|
| **Contents** | ISO 8583 authorisation requests and responses, clearing and settlement files, chargebacks, tokenised card references, merchant and terminal data |
| **Format / protocol** | ISO 8583 on the switch; a JSON projection on Kafka for analytics; nightly fixed-width clearing files from the schemes |
| **Volume** | ~58 m authorisations/day; ~140 GB/day JSON. Peak ~7.1 m/hour |
| **Change rate** | Append-only; clearing records match back to authorisations over 1–5 days with a ~2.3% non-match rate |
| **Latency requirement** | The **authorisation decision is sub-second and stays on the switch** — the lakehouse is never in that path. The lakehouse supplies **features** and receives the event stream within seconds for near-real-time fraud analytics and case management |
| **Quality issues** | Merchant category codes misapplied by acquirers; unnormalised merchant name strings (~340,000 distinct strings for ~90,000 real merchants); duplicate authorisation events on switch retry |
| **Classification** | **PCI** — PAN must never land in the lakehouse. Tokens only. Also PII |
| **Retention / residency** | Scheme and regulatory retention ~7 years **[TBC]**; PCI scope must be **excluded by design**, not controlled after the fact |
| **Ingestion pattern dictated** | **Kafka → Structured Streaming**, under a hard producer contract that tokenisation happens before publication. The lakehouse declares a schema with no PAN column; any PAN-shaped value in a free-text field is **quarantined by an expectation, not masked** — masking a PCI leak still means the leak reached the platform. Clearing files land via **Auto Loader** on an external volume. Idempotency on `(switch_id, stan, transmission_ts)` |

## 3.5 S4 — General ledger

| Attribute | Detail |
|---|---|
| **Contents** | Chart of accounts, journal headers and lines, sub-ledger postings, period balances, FX revaluation, intercompany eliminations, legal-entity and consolidation hierarchies |
| **Format / protocol** | Oracle behind the ERP; CDC via redo logs (LogMiner); plus a nightly trial-balance extract |
| **Volume** | ~11 m journal lines/day normal, ~48 m at period close; ~9 GB/day, ~38 GB at close. ~14 TB with 10 years of history |
| **Change rate** | Postings are append-only. **The hierarchy and chart of accounts are the volatile part** and they are restated retrospectively — a reorganisation re-maps prior periods |
| **Latency requirement** | Hourly during the month; **continuous during the 11-day close**; intraday for flash P&L |
| **Quality issues** | Manual journals with unstructured narratives; suspense accounts used as a workflow queue; late adjustments posted into closed periods; three intercompany conventions across regions |
| **Classification** | Confidential; pre-announcement group results are **MNPI for a defined window** |
| **Retention / residency** | Statutory accounting retention 7–10 years by jurisdiction; audit trail aligned to external audit |
| **Ingestion pattern dictated** | **Lakeflow Connect managed CDC connector for Oracle** (documented, LogMiner-based) into a bronze streaming table, plus the trial balance via Auto Loader as the **reconciliation anchor**. The chart-of-accounts hierarchy is the clearest bitemporal case in the bank (§5.4). Note: the managed connector's **ingestion gateway runs on classic compute in the workspace network and is billed continuously even when the pipeline is idle** — a cost line, not a footnote |

## 3.6 S5 — Order and execution management (FIX)

| Attribute | Detail |
|---|---|
| **Contents** | Parent and child orders, amendments, cancels, executions, allocations, venue acknowledgements, algo parameters, trader and desk attribution, client order identifiers |
| **Format / protocol** | **FIX 4.4 / 5.0 SP2 drop-copy** sessions from OMS/EMS and from venues; a normalised internal event on Kafka; end-of-day trade files from clearing |
| **Volume** | ~9.4 m FIX messages/day across equities, FX and rates; ~1.1 m executions/day; ~46 GB/day. Peak at the close auction ~1.9 m messages in 15 minutes |
| **Change rate** | Append-only; order state is derived by replaying the event sequence |
| **Latency requirement** | **Seconds** for intraday exposure and surveillance; intraday-accurate for limits; T+1 for transaction reporting |
| **Quality issues** | Out-of-order arrival across venue sessions; sequence gaps on session reset; clock skew between venue and internal timestamps (hundreds of microseconds to low milliseconds); custom FIX tags per venue; cancel/replace chains that must be threaded to reconstruct a parent order |
| **Classification** | **MNPI** — client order flow is the most sensitive dataset in the bank. Also Confidential and, for named natural-person clients, PII |
| **Retention / residency** | Order and execution records retained under the jurisdiction's market-conduct regime, commonly 5–7 years **[TBC per venue and per regulator]**. Some venues impose data-locality terms |
| **Ingestion pattern dictated** | **Kafka → Structured Streaming**, with raw FIX preserved as a string beside the parsed tags so a surveillance replay is byte-faithful. **Watermarked stateful processing** threads order chains, with a documented lateness bound and a **side output** for messages beyond it — silently dropping a late execution is a surveillance failure, not a data-quality blemish. This domain lands in a **separate catalog behind an information barrier from first ingestion** (§5.6) |

## 3.7 S6 — Market data, real-time

| Attribute | Detail |
|---|---|
| **Contents** | Level 1 and Level 2 quotes, trades, index values, FX spot and forward points, yield curves, volatility surfaces |
| **Format / protocol** | Vendor binary protocol into a feed handler in the bank's low-latency estate. The lakehouse consumes a **conflated Kafka projection**, never the raw feed |
| **Volume** | Raw feed peaks in the millions of updates per second and is **out of scope**. Conflated projection: ~180 m ticks/day across the risked instrument universe; ~210 GB/day |
| **Change rate** | Continuous during market hours; near-zero overnight for cash equities, continuous for FX |
| **Latency requirement** | **Seconds** for intraday risk marks. The trading path is never routed through the lakehouse |
| **Quality issues** | Stale quotes at open and around halts; crossed and locked markets; vendor correction ticks arriving minutes later; instrument identifier changes on corporate actions |
| **Classification** | **Vendor-licensed.** Redistribution and derived-data rights are contractual and vary by feed. Not PII |
| **Retention / residency** | Governed by **licence terms, not regulation**. Some contracts prohibit indefinite retention of raw ticks; some permit derived data only. **Per-contract terms [TBC with Market Data Services before a single tick is persisted]** |
| **Ingestion pattern dictated** | **Feed handler → Kafka → Structured Streaming** into a bronze streaming table clustered by trading date and instrument, with conflation applied **upstream** so the lakehouse ingests a defensible sample rather than the firehose. Retention per feed is a table property enforced by a scheduled job, because **the licence sets the horizon, not the engineer** |

## 3.8 S7 — Market data, reference and end-of-day

| Attribute | Detail |
|---|---|
| **Contents** | Instrument master, ISIN/CUSIP/SEDOL/FIGI cross-reference, corporate actions, dividends, closing prices, index constituents, credit ratings, issuer hierarchies |
| **Format / protocol** | Vendor SFTP drops (CSV, fixed-width, some XML) and vendor APIs; a growing number of vendors offer **OpenSharing** delivery |
| **Volume** | ~40 files/day, ~26 GB/day; instrument master ~3.4 m instruments; corporate actions ~14,000 events/day |
| **Change rate** | Instrument master ~0.3%/day; corporate actions bursty around season. **Restatements of closing prices occur and must be absorbed without losing the prior value** |
| **Latency requirement** | **Pre-open.** The whole downstream day depends on reference data being loaded and validated before markets open. A hard clock, not a best-effort batch |
| **Quality issues** | Identifier collisions and reuse; corporate actions delivered late or superseded; conflicting values between two vendors for the same field, with no documented golden-source rule for ~40% of overlapping fields |
| **Classification** | Vendor-licensed; not PII |
| **Retention / residency** | Licence-driven; several contracts require deletion on termination, which the current estate cannot evidence |
| **Ingestion pattern dictated** | **Auto Loader** over a Unity Catalog external volume for SFTP drops — file-notification detection where the storage supports it, with Auto Loader's exactly-once file tracking so a redelivered file is not double-counted. **Where the vendor publishes via OpenSharing, prefer it**: zero-copy, no ambiguity about local copies, and no egress cost within a region. Corporate actions are modelled **bitemporally** because a superseded action must not erase the version the bank priced on |

## 3.9 S8 — KYC / AML case management and screening

| Attribute | Detail |
|---|---|
| **Contents** | Customer due diligence records, beneficial ownership, PEP and sanctions screening hits, transaction monitoring alerts, case notes and dispositions, suspicious activity filings, customer risk ratings |
| **Format / protocol** | SQL Server behind the case management vendor; nightly screening-list refresh files; an alert event stream |
| **Volume** | ~2.1 m screening evaluations/day; ~4,800 alerts/day; ~11 GB/day; case history ~6 TB |
| **Change rate** | Case records mutate heavily through their lifecycle — the classic CDC-with-state case |
| **Latency requirement** | **15 minutes** for alert context and the analyst workbench. Real-time screening in the payment path stays in the payment system |
| **Quality issues** | Names transliterated inconsistently across six countries; fuzzy entity resolution against sanctions lists where the match rationale is not always persisted; disposition free-text carries the actual reasoning |
| **Classification** | **PII and Restricted.** The existence of a suspicious activity filing is itself confidential in most jurisdictions and disclosure is an offence in several. This dataset needs a stricter barrier than general PII |
| **Retention / residency** | Financial-crime retention typically 5–7 years post relationship end **[TBC per jurisdiction]**. In several jurisdictions this **overrides** an erasure request — see §7.4 |
| **Ingestion pattern dictated** | **Lakeflow Connect managed CDC connector for SQL Server** into bronze streaming tables, then an **AUTO CDC flow to SCD Type 2** in silver so case history is queryable as it stood at any point. Filing-related tables land in a **dedicated schema with its own grants**, not merely a column mask — a mask protects a value, a separate schema protects the fact that a row exists |

## 3.10 S9 — CRM (retail and commercial)

| Attribute | Detail |
|---|---|
| **Contents** | Contacts, opportunities, service cases, campaign membership, consent and marketing preferences, relationship-manager coverage, commercial client hierarchies |
| **Format / protocol** | SaaS CRM with a documented Lakeflow Connect managed connector; plus a legacy on-premises commercial CRM on SQL Server |
| **Volume** | ~640,000 record changes/day; ~3 GB/day; ~2.8 TB total |
| **Change rate** | Moderate. Consent records change rarely but **every change is legally material** |
| **Latency requirement** | Hourly for analytics; **15 minutes for consent**, because consent gates outbound activity |
| **Quality issues** | Free-text account names not matched to the legal-entity master; duplicate contacts; consent captured at three different granularities across the six countries |
| **Classification** | PII. Consent and preference data is itself a control artefact |
| **Retention / residency** | Marketing data retention shorter than banking data; consent evidence retained as long as the processing it authorises |
| **Ingestion pattern dictated** | **Lakeflow Connect managed SaaS connector** for the cloud CRM — it produces Unity Catalog-governed streaming tables on serverless compute, tracks changes between runs, and handles schema evolution by adding new columns on the next run (deleted columns become inactive rather than disappearing). Legacy commercial CRM via the **SQL Server CDC connector**. Consent is promoted to a **separate high-frequency flow** so it is never queued behind a bulk CRM sync. Note: with a managed connector you choose objects, destination, schedule and permissions — you cannot customise the ingestion itself; if we need transformation at ingest, drop to a Lakeflow pipeline |

## 3.11 S10 — Collateral, positions and sub-ledgers

| Attribute | Detail |
|---|---|
| **Contents** | Securities positions, repo and securities-lending positions, collateral agreements, margin calls, haircuts, eligibility schedules, netting sets, custody positions |
| **Format / protocol** | PostgreSQL for the collateral platform; position sub-ledgers export end-of-day fixed-width files; an intraday position delta feed on Kafka for the trading book |
| **Volume** | ~3.2 m position records end of day; ~420,000 intraday deltas/day; ~18 GB/day; history ~48 TB |
| **Change rate** | Trading-book positions change continuously; banking-book daily. **Collateral agreements change rarely but retrospectively** — an amendment signed today can be effective from a past date |
| **Latency requirement** | **15 minutes intraday** for exposure; end-of-day authoritative for regulatory capital |
| **Quality issues** | Netting-set membership disagrees between the collateral platform and the risk warehouse for ~2% of agreements; eligibility schedules held in attached PDFs for ~8% of agreements; three position conventions (trade date, settlement date, custody date) used interchangeably |
| **Classification** | Confidential. Trading-book positions are **MNPI-adjacent**; desk-level detail sits behind the barrier |
| **Retention / residency** | Contract lifetime plus ~7 years **[TBC]**; agreements are legal records |
| **Ingestion pattern dictated** | **Lakeflow Connect CDC for PostgreSQL** for collateral; **Auto Loader** for sub-ledger files; **Kafka streaming** for intraday deltas. Collateral agreements are the second clear **bitemporal** case — effective date and knowledge date differ routinely, and a capital number computed under pre-amendment terms must remain reproducible |

## 3.12 S11 — Credit decisioning platform

| Attribute | Detail |
|---|---|
| **Contents** | Applications, bureau pulls, affordability assessments, scorecards and their inputs, decisions and reason codes, limit changes, behavioural scores, model versions used |
| **Format / protocol** | Decision events on Kafka; model artefacts and scorecard definitions as files; bureau responses as XML/JSON payloads |
| **Volume** | ~62,000 retail decisions/day; ~1,400 commercial; ~7 GB/day |
| **Change rate** | Decision records are immutable once made. **Behavioural features are recomputed monthly across the book** |
| **Latency requirement** | The decision path is sub-second inside the platform. The lakehouse serves **features** and receives the outcome stream within minutes. The monthly behavioural refresh is batch |
| **Quality issues** | Bureau schema changes without notice; reason codes unharmonised across the six countries; feature definitions drift between the training environment and the production platform — **training/serving skew is an active model-risk finding** |
| **Classification** | PII. Decision rationale is subject to the jurisdiction's automated-decision and explainability expectations |
| **Retention / residency** | Credit decision evidence retained for the life of the facility plus a statutory tail **[TBC]**. Bureau data carries **contractual** retention limits distinct from regulatory ones |
| **Ingestion pattern dictated** | **Kafka streaming** for decision events; **Auto Loader** for bureau payload archives and model artefacts. The material design point is on the serving side: features computed **once** in Unity Catalog feature tables and served to both training and production. That single change is what closes the skew finding |

## 3.13 S12 — Digital channel and call-centre events

| Attribute | Detail |
|---|---|
| **Contents** | App and web clickstream, login and step-up authentication events, device and session telemetry, IVR paths, call metadata, chat transcripts, complaint records |
| **Format / protocol** | Event SDK → Kafka; call metadata from the contact-centre platform; transcripts as files |
| **Volume** | ~310 m events/day; ~240 GB/day; ~92,000 calls/day; transcripts ~14 GB/day |
| **Change rate** | Append-only |
| **Latency requirement** | **Seconds** for fraud signals (device change, impossible travel, session anomalies); minutes for service analytics; daily for journey analytics |
| **Quality issues** | Bot and synthetic traffic ~9% of web events; device identifiers reset by OS privacy features; transcripts contain PII spoken aloud, including card numbers |
| **Classification** | PII. Transcripts are both a **PCI leakage risk** and a special-category-data risk |
| **Retention / residency** | Clickstream typically 13–25 months **[TBC against each country's privacy regime]**; complaint records retained far longer as conduct evidence |
| **Ingestion pattern dictated** | **Kafka → Structured Streaming** for events. **Zerobus Ingest** — the documented push-based API that writes directly into Unity Catalog Delta tables with no message bus — is a candidate for the event SDK and should be evaluated, not assumed. Transcripts land via **Auto Loader** into a restricted schema; redaction is applied bronze→silver and the un-redacted copy is retained only where a conduct obligation requires it, with its own shorter retention clock |

## 3.14 S13 — Third-party and vendor reference data

| Attribute | Detail |
|---|---|
| **Contents** | LEI registry, sanctions and watch lists, PEP lists, credit ratings, country risk, official FX fixings, holiday calendars, industry classifications, beneficial-ownership registries |
| **Format / protocol** | Mixed — public bulk downloads, vendor APIs, SFTP drops, and increasingly **OpenSharing** |
| **Volume** | ~12 GB/day aggregate; LEI full file ~3 GB weekly; sanctions deltas intraday |
| **Change rate** | Sanctions lists change intraday and are **time-critical**; LEI weekly; ratings event-driven |
| **Latency requirement** | **Sanctions: minutes.** Everything else: daily |
| **Quality issues** | Overlapping and contradictory identifiers; classification taxonomies that do not map cleanly; vendors restating history without notification |
| **Classification** | Licensed. Sanctions data is public but its **application** is confidential |
| **Retention / residency** | Licence-driven. Several vendors require deletion on termination and prohibit onward sharing — **the redistribution clause is the binding design constraint on any outbound OpenSharing** |
| **Ingestion pattern dictated** | **Prefer OpenSharing where the vendor offers it** — nothing is copied, the provider controls the version, and within a region there is no egress cost. Otherwise **Auto Loader** on a governed volume. Every vendor dataset carries a **governed tag holding its licence class**, so an ABAC policy can prevent it being included in an outbound share (§7.6) |

## 3.15 S14 — The legacy risk warehouse itself

| Attribute | Detail |
|---|---|
| **Contents** | Eleven years of credit and market risk marts — exposures, PD/LGD/EAD, RWA calculations, stress results, limit utilisation, and the historical regulatory submissions themselves |
| **Format / protocol** | Teradata; JDBC access; bulk export utilities |
| **Volume** | ~340 TB; ~2.1 TB/day of batch churn |
| **Change rate** | Historical partitions static except for restatements; current partitions rebuild nightly |
| **Latency requirement** | None new. This is a **migration and parallel-run source**, not a permanent one |
| **Quality issues** | The known-good and the known-wrong live side by side. ~15% of tables are orphaned outputs of retired processes. The mart's own reconciliation breaks are documented in spreadsheets held outside it |
| **Classification** | Confidential; contains derived PII |
| **Retention / residency** | Submitted regulatory history must survive decommission. **A migration deliverable, not an afterthought** |
| **Ingestion pattern dictated** | **Two mechanisms, deliberately different.** (a) **Lakehouse Federation** — a read-only foreign catalog over Teradata for the parallel-run comparison, so the reconciliation query reads the legacy value live with nothing copied. Federation is documented for precisely this: ad hoc reporting, proofs of concept, incremental migration and long-term hybrid models. (b) A **one-time bulk extract** of submitted-report history and the partitions needed for back-testing, landed with Auto Loader and frozen as an immutable archive with its own retention. Do **not** federate the production path — federation is for comparison, not for the daily regulatory run |

## 3.16 What the inventory tells the architect

| Observation | Consequence for design |
|---|---|
| Four distinct latency tiers appear (sub-second, seconds, 15 minutes, daily) | Do not build one pipeline cadence. Tier the medallion by domain, not across the whole platform |
| Three sources restate history retrospectively (GL hierarchy, collateral agreements, corporate actions); two deliver late corrections (payment reversals, market-data corrections) | **Bitemporality is not optional.** See §5.4 |
| Two sources carry MNPI (FIX, trading-book positions), one carries PCI (cards), one carries filing data (AML) | Three separate barrier regimes, not one undifferentiated "sensitive" bucket |
| Every vendor feed has contractual terms distinct from regulatory terms | Licence class must be a **tag on the data**, enforced at share time and at retention time |
| The mainframe is not covered by any managed connector | The single largest delivery risk. Phase 0 exists to retire it |
| Six countries, eight legal entities, at least two residency constraints | Workspace and catalog topology is a **legal** decision before it is a technical one |
| The legacy warehouse is both the thing to replace and the thing to reconcile against | Federation is a migration tool with a decommission date attached to it |

---

# 4. Use cases and value

Eight use cases, prioritised. For each: the business question, the consumer, the **true** latency need
(as distinct from the one first asked for), dependencies, value driver, an illustrative value range with
the assumption that generates it, and the regulatory hook where one exists.

## 4.1 UC-1 — Regulatory reporting with lineage attestation

| Field | Detail |
|---|---|
| **Business question** | "Produce this return for this entity for this reporting date, and show, field by field, where every number came from and who approved each transformation." |
| **Consumer** | Regulatory Reporting, Group Finance, the attesting officer, the examiner |
| **Latency asked for** | "Real-time" |
| **True latency need** | **T+1 by 07:00 for the assembly; the report itself is periodic.** What is actually urgent is not freshness but *reproducibility* — the ability to rerun a prior period and get the same answer |
| **Dependencies** | S1 (core banking), S4 (GL), S10 (positions and collateral), S14 (history), bitemporal model (§5.4), lineage capture, four-eyes change control |
| **Value driver** | Reporting FTE reduction; avoidance of remediation cost; **release of the add-on held against data uncertainty**; reduced cost per supervisory information request |
| **Illustrative value** | **USD 18 – 26 m/yr.** Assumption: 30–40% of the ~185 reporting FTE redeploy (≈USD 6.5–8.5 m), plus partial release of the ~USD 240 m CET1 add-on. Releasing 40% at a 12% cost of equity ≈ USD 11.5 m/yr. **The add-on component is a supervisory judgement the bank does not control and must be modelled as an option, not a certainty** |
| **Regulatory hook** | The home regulator's risk data aggregation and reporting expectations, and the two open findings. Generic by design; the specific rule references belong in the client's own remediation plan |
| **Why it is first** | It is the only use case that both closes an open finding and forces every foundational capability — bitemporality, lineage, reconciliation, four-eyes — to be real |

## 4.2 UC-2 — Intraday risk aggregation

| Field | Detail |
|---|---|
| **Business question** | "What is our current exposure to this counterparty, this issuer, this country, across all books and all entities — right now?" |
| **Consumer** | Group Treasury, market and credit risk managers, the CRO, the trading desks' risk officers |
| **Latency asked for** | "Real-time" |
| **True latency need** | **15 minutes for the aggregate; 60 seconds for limit breaches on the top 200 counterparties.** No human acts on a sub-second exposure number; a limit system does, and that limit system is not the lakehouse |
| **Dependencies** | S5 (FIX), S10 (positions, collateral), S6 (marks), S1 (banking-book balances), the counterparty hierarchy from S13, entity resolution |
| **Value driver** | Reduced intraday credit line buffers; faster reaction in a stress event; avoided limit breaches; reduced manual exposure assembly |
| **Illustrative value** | **USD 12 – 20 m/yr.** Assumption: a 15% reduction in precautionary intraday buffers on ~USD 1.1 bn of committed intraday lines, valued at funding cost; plus ~14 FTE of manual exposure assembly |
| **Regulatory hook** | The home regulator's expectations on the timeliness and completeness of risk aggregation. Also the internal ICAAP narrative |
| **Note** | The honest framing at the investment committee: this is primarily a **loss-avoidance and stress-readiness** case. It is defensible but it should not carry the payback argument |

## 4.3 UC-3 — Real-time fraud and AML detection

| Field | Detail |
|---|---|
| **Business question** | "Is this payment, this card authorisation, this session, consistent with this customer's behaviour — and if not, what do we do in the next 300 milliseconds?" |
| **Consumer** | Financial Crime operations, the payment and card decision engines, the MLRO, customer service |
| **Latency asked for** | Sub-second |
| **True latency need** | **Feature freshness in seconds; decision latency owned by the decision engine, not the lakehouse.** The lakehouse serves features and receives outcomes. Putting a lakehouse query in a 300 ms authorisation path is an architectural mistake, and we will say so |
| **Dependencies** | S2, S3, S12 (streams), S1 (customer context), S8 (case history and screening), feature tables, online feature serving, model serving, model governance sign-off |
| **Value driver** | Fraud loss reduction; false-positive reduction releasing investigator capacity; faster alert triage; fewer customer-friction events |
| **Illustrative value** | **USD 22 – 38 m/yr.** Assumption: 12–18% reduction on ~USD 128 m gross fraud loss (USD 15–23 m), plus a 25–35% cut in false positives releasing ~90–120 investigator FTE (USD 7–15 m) |
| **Regulatory hook** | The jurisdiction's financial-crime and payment-fraud regimes; increasing reimbursement liability for authorised push-payment scams in some jurisdictions makes the loss line directional. **Model approval is a gate** — see UC dependency on model governance (§7.7) |
| **Risk** | The highest-value case is also the one with the longest approval tail. Model risk sign-off is the critical path, not the engineering |

## 4.4 UC-4 — Customer 360 across retail and commercial

| Field | Detail |
|---|---|
| **Business question** | "Who is this client, what is the whole relationship across retail, commercial and markets, and what are we allowed to do with that knowledge?" |
| **Consumer** | Relationship managers, retail marketing, product, pricing, Financial Crime, the client-service desk |
| **Latency asked for** | Real-time |
| **True latency need** | **Hourly for the profile; 15 minutes for consent and for financial-crime flags.** A relationship manager does not need a second-by-second profile; they need one that is right |
| **Dependencies** | S1, S9, S10, S12, S13 (LEI and hierarchies), entity resolution across retail CIF / commercial platform / markets client master; consent model; **information barrier — the markets relationship must not be visible to retail marketing** |
| **Value driver** | Cross-sell and retention uplift; faster onboarding; reduced duplicate KYC effort; better pricing decisions |
| **Illustrative value** | **USD 15 – 30 m/yr.** Assumption: 30% reduction in the 47-day commercial onboarding median releases ~USD 18 m of annualised revenue earlier (valued at ~USD 5–9 m/yr of NPV effect); plus a 0.4–0.9 pp improvement in retail primary-relationship retention |
| **Regulatory hook** | Consent and purpose limitation under each jurisdiction's privacy regime; customer due diligence refresh obligations. **The information barrier is a conduct obligation, not a preference** |
| **Caution** | Confidence is medium-low because the uplift depends on business adoption, not on the data being available. Do not fund this case on the data alone |

## 4.5 UC-5 — Credit decisioning features

| Field | Detail |
|---|---|
| **Business question** | "What is this applicant's affordability and risk profile, computed the same way in training and in production, with reasons we can explain?" |
| **Consumer** | Credit Risk, the decisioning platform, model developers, Model Risk Management |
| **Latency asked for** | Sub-second |
| **True latency need** | **Feature lookup in low milliseconds at decision time; feature computation in minutes to hours.** Online serving of pre-computed features, not online computation |
| **Dependencies** | S1, S2, S11, S13 (bureau, ratings), feature tables in Unity Catalog, online feature store, model governance, reason-code harmonisation |
| **Value driver** | Better discrimination in the scorecards; **closure of the training/serving skew finding**; faster model iteration; reduced manual underwriting referral |
| **Illustrative value** | **USD 9 – 16 m/yr.** Assumption: a 3–6% improvement in Gini on the retail book translating to a 2–4% reduction in expected credit loss on new originations; plus reduced referral handling |
| **Regulatory hook** | Model risk management expectations; the jurisdiction's rules on automated decision-making and adverse-action explanation. **The reason code must be reproducible from the feature values as at decision time** — which is a bitemporality requirement, not an ML one |

## 4.6 UC-6 — Market surveillance

| Field | Detail |
|---|---|
| **Business question** | "Did any of our traders or clients engage in conduct that requires investigation, and can we replay exactly what happened?" |
| **Consumer** | Compliance surveillance, the capital-markets COO, the conduct committee |
| **Latency asked for** | T+1 |
| **True latency need** | **T+1 for the alert sweep; intraday for a small set of high-risk patterns; and — the real requirement — byte-faithful replay of any historical day** |
| **Dependencies** | S5 (raw FIX preserved), S6 (market data at the relevant timestamps), S12 (communications metadata), S13 (instrument reference), clock-skew normalisation, **the information barrier itself** |
| **Value driver** | Reduced false-positive review effort; faster response to regulatory enquiry; evidence quality in an investigation |
| **Illustrative value** | **USD 4 – 8 m/yr.** Assumption: 35–50% reduction in surveillance analyst review hours on ~30 FTE, plus avoided external counsel cost on enquiries. The larger value is **tail-risk avoidance**, which we do not put a number on |
| **Regulatory hook** | The jurisdiction's market-abuse and conduct regime; the requirement to retain order and communication records. **Generic by design — the specific retention periods must be confirmed per venue and per regulator** |

## 4.7 UC-7 — Finance close acceleration

| Field | Detail |
|---|---|
| **Business question** | "Can we close the group books faster, with the sub-ledger-to-GL reconciliation automated and evidenced?" |
| **Consumer** | Group Financial Controller, entity controllers, external audit |
| **Latency asked for** | Faster |
| **True latency need** | **Continuous reconciliation during the month, so that close is a confirmation rather than an investigation.** The value is in moving work out of the close window, not in speeding the window up |
| **Dependencies** | S4 (GL), S1 (core sub-ledgers), S10 (position sub-ledgers), bitemporal hierarchy, reconciliation framework, audit evidence export |
| **Value driver** | Close cycle reduction; audit fee reduction; finance FTE redeployment; fewer late adjustments |
| **Illustrative value** | **USD 6 – 11 m/yr.** Assumption: close reduced from 11 to 6–7 working days; ~40 finance FTE partially released; a 5–10% external audit fee reduction on ~USD 24 m of audit and assurance spend |
| **Regulatory hook** | Statutory reporting deadlines; internal control over financial reporting attestations |
| **Why it scores well** | High confidence, measurable, and the sponsor (CFO) also controls the budget |

## 4.8 UC-8 — Institutional client reporting

| Field | Detail |
|---|---|
| **Business question** | "Can our institutional clients see their positions, transactions and fees when they want them, in their own systems?" |
| **Consumer** | Institutional clients, client service, the sales desks |
| **Latency asked for** | Real-time |
| **True latency need** | **T+0 end-of-day authoritative; intraday indicative for a subset of clients.** Clients want reliability and self-service more than they want low latency |
| **Dependencies** | S5, S10, S4 (fees), client entitlement model, **OpenSharing with per-recipient governance**, licence review of any embedded vendor data |
| **Value driver** | Mandate retention and win rate; reduced client-service query volume; reduced bespoke-extract engineering |
| **Illustrative value** | **USD 3 – 7 m/yr.** Assumption: retention of 1–2 at-risk mandates worth ~USD 2–4 m of annual revenue, plus ~8 FTE of bespoke-extract work eliminated |
| **Regulatory hook** | Client reporting obligations under the jurisdiction's conduct regime. **Vendor licence redistribution terms are the binding constraint** — see the licence-class tag in §3.14 |
| **Note** | This is the natural first external OpenSharing use case, which is why it appears despite a modest value range: it proves the outbound governance pattern |

## 4.9 Prioritisation matrix

Scored 1–5. **Value** = illustrative annual benefit midpoint. **Confidence** = how well we can defend the
number. **Feasibility** = engineering tractability given the source estate. **Regulatory pull** = does an
external party want this. **Dependency depth** = how much foundation must exist first (5 = shallow).

| Use case | Value | Confidence | Feasibility | Reg pull | Dep. depth | **Score** | Wave |
|---|---|---|---|---|---|---|---|
| UC-1 Regulatory reporting + lineage | 4 | 4 | 3 | **5** | 2 | **18** | **Wave 1** |
| UC-7 Finance close | 3 | 4 | 4 | 3 | 3 | **17** | **Wave 1** |
| UC-3 Fraud / AML | **5** | 3 | 3 | 4 | 2 | **17** | Wave 2 |
| UC-2 Intraday risk | 4 | 3 | 3 | 4 | 2 | **16** | Wave 2 |
| UC-5 Credit features | 3 | 3 | 4 | 3 | 3 | **16** | Wave 2 |
| UC-4 Customer 360 | 4 | 2 | 3 | 2 | 2 | **13** | Wave 3 |
| UC-6 Market surveillance | 2 | 3 | 2 | 4 | 2 | **13** | Wave 3 |
| UC-8 Client reporting | 2 | 2 | 4 | 2 | 4 | **14** | Wave 3 |

**Reading the matrix.** UC-1 wins not on value but on regulatory pull and on the fact that it forces every
foundation. UC-7 is the highest-confidence money. UC-3 is the largest number and the longest approval
tail, which is exactly why it goes in Wave 2 rather than Wave 1 — it must not be on the critical path of
the first credibility milestone. UC-4 has the weakest confidence and should be funded on a business
adoption plan, not on data availability.

## 4.10 Value realisation sequencing

| Quarter | Cumulative run-rate unlocked (illustrative, USD m/yr) | What makes it real |
|---|---|---|
| Q2 | 0 | Thin slice in dual-run; no benefit claimed while the incumbent still runs |
| Q3 | 4 – 7 | First report cut over; reconciliation FTE released |
| Q4 | 16 – 24 | Finance close improvement; second and third reports |
| Q6 | 42 – 68 | Fraud model in production; intraday exposure live |
| Q8 | 74 – 122 | Customer 360 and credit features adopted by the business |
| Q9 | 89 – 156 + 14 – 19 decommission | Teradata and Hadoop retired |

---

# 5. Target architecture

Every decision below is stated with the alternative we rejected and why. A design document that only
lists what was chosen is a catalogue, not an architecture.

## 5.1 Architecture at a glance

```
 SOURCES                    INGEST                    MEDALLION                 SERVE
 ───────                    ──────                    ─────────                 ─────
 DB2 z/OS ────► log capture ─► volume ─► Auto Loader ─┐
 GL (Oracle) ──► Lakeflow Connect managed CDC ────────┤
 KYC (SQL Svr) ► Lakeflow Connect managed CDC ────────┤   BRONZE          ┌─► SQL warehouses (BI, ad hoc)
 CRM (SaaS) ───► Lakeflow Connect SaaS connector ─────┤   raw, append,    │
 Collateral ───► Lakeflow Connect CDC (PostgreSQL) ───┼─► immutable ──┐   ├─► Regulatory extract jobs
                                                      │               │   │   (Lakeflow Jobs, as-of param)
 Payments ─────┐                                      │   SILVER      │   │
 Cards ────────┼─► Kafka ─► Structured Streaming ─────┤   conformed, ─┼───┼─► Feature tables → online store
 FIX drop-copy │        (Lakeflow SDP)                │   bitemporal  │   │
 Digital ──────┘                                      │               │   ├─► Model serving (fraud, credit)
                                                      │   GOLD        │   │
 Market data RT ► feed handler ─► Kafka ──────────────┤   products,  ─┘   ├─► OpenSharing (clients, vendors)
 Market ref/EOD ► SFTP volume ─► Auto Loader ─────────┤   metric views    │
 Vendor ref ────► OpenSharing (inbound) ──────────────┤                   └─► Metric views (semantic layer)
                                                      │
 Teradata ──────► Lakehouse Federation (read-only) ───┘   [parallel run only, decommission gate]

 ACROSS EVERYTHING: Unity Catalog · lineage · audit · governed tags · ABAC · Declarative Automation Bundles
```

## 5.2 Ingestion decisions, per source

The general rule we apply, which matches the documented Databricks guidance, is: **start at the most
managed layer and drop down only when it does not satisfy the requirement.** The layers, ordered, are
managed connectors → Lakeflow pipelines → Structured Streaming.

| Source | Chosen mechanism | Rejected alternative | Why the rejection |
|---|---|---|---|
| **S1 Core banking (DB2 z/OS)** | Third-party log capture → object storage or Kafka → **Auto Loader** into a bronze streaming table, plus a daily reconciling extract | (a) Lakeflow Connect managed CDC (b) Nightly full extract only (c) Direct JDBC query against DB2 | (a) DB2 for z/OS is not in the managed connector list. (b) Fails the 15-minute latency need and leaves the bank blind intraday. (c) Query load on a production core is a MIPS and availability risk the mainframe team will veto, correctly |
| **S4 General ledger (Oracle)** | **Lakeflow Connect managed CDC connector** (Oracle, LogMiner) + trial-balance anchor via Auto Loader | Hand-built Debezium into Kafka | We would be operating a CDC platform we did not need to operate. The managed connector produces UC-governed streaming tables on serverless compute with schema evolution handled. Trade-off accepted: **the ingestion gateway runs on classic compute and bills continuously even when idle** |
| **S8 KYC/AML (SQL Server)** | **Lakeflow Connect managed CDC connector** | Vendor's own export API | The export API is a nightly file and loses intra-day case state transitions, which is precisely what the alert-context use case needs |
| **S9 CRM (SaaS)** | **Lakeflow Connect managed SaaS connector** | Bespoke API extraction | The bespoke path is a rate-limit and pagination maintenance burden with no governance benefit. Accepted limitation: you cannot customise the ingestion itself — objects, destination, schedule and permissions only |
| **S10 Collateral (PostgreSQL)** | **Lakeflow Connect managed CDC connector** + Auto Loader for sub-ledger files + Kafka for intraday deltas | Single mechanism for all three | Three genuinely different shapes. Forcing one mechanism would either lose the intraday deltas or over-engineer the file path |
| **S2 Payments, S3 Cards, S5 FIX, S12 Digital** | **Kafka → Structured Streaming inside Lakeflow Spark Declarative Pipelines** | (a) Lakeflow Connect Kafka connector (b) Micro-batch file drops | (a) Viable for simple landing, but these four need custom parsing (ISO 20022, ISO 8583, FIX) and stateful chain-threading at ingest, so we drop to the pipeline layer deliberately. (b) File drops add minutes of latency and a fragile file-completeness contract |
| **S12 Digital events (option)** | Evaluate **Zerobus Ingest** — push directly into UC Delta tables, no message bus | Assume Kafka | Zerobus is documented as a push-based direct-write API with gRPC/REST/OTLP/Kafka-compatible SDKs. **Fit, throughput at 310 m events/day and regional availability [TBC]** — evaluated in Phase 0, not assumed in the design |
| **S6 Market data real-time** | Feed handler → Kafka → Structured Streaming, **conflated upstream** | Ingest the raw feed | The raw feed peaks in millions of updates per second. Ingesting it would cost more than the risk value it produces and would breach retention terms on several contracts |
| **S7 Market reference, S13 Vendor reference** | **OpenSharing where the vendor offers it**; otherwise **Auto Loader** on a UC external volume | COPY INTO | Documented guidance: thousands of files over time → COPY INTO; millions → Auto Loader. Reference data is thousands, so COPY INTO is defensible, but Auto Loader gives us one operational pattern across file ingestion, better schema-evolution primitives and file-notification detection. **We keep COPY INTO in the toolkit for targeted reloads of a re-delivered subset**, which is the case where the docs say it is easier to manage |
| **S14 Teradata** | **Lakehouse Federation** (read-only foreign catalog) for parallel run + one-time bulk extract for history | Full replication of 340 TB | Replicating a system we are decommissioning is 340 TB of cost and a second reconciliation surface. Federation is documented for incremental migration; it has a decommission date attached |
| **Cross-entity data movement** | **OpenSharing between regional metastores** | Copy pipelines per region | Zero-copy within a region with no egress cost; the provider controls the version. **Cross-region shares may incur egress charges — [TBC in the cloud cost model]** |

### 5.2.1 The rule we will be asked to defend

*Why not federate everything and avoid ingestion entirely?* Because federation is read-only, runs against
the source's capacity, cannot carry bitemporal history the source does not keep, and offers no lineage
into the source. It is a migration accelerant and an ad hoc tool. A regulatory production path that reads
live from a mainframe or from a system being decommissioned is not a production path.

## 5.3 The medallion contract, per domain

Bronze, silver and gold mean different things in different domains, and pretending otherwise is how
medallion architectures rot. The contract below is explicit per domain.

| Domain | Bronze | Silver | Gold |
|---|---|---|---|
| **Customer** | Raw CDC change stream from S1/S9, EBCDIC decoded, no dedup, source columns preserved, `_ingest_ts` and `_source_file` attached | SCD Type 2 party, account and consent entities; cross-LPAR entity resolution applied with a confidence score and a survivorship audit column | Customer 360 product; segment and behaviour marts; metric views for retail and commercial |
| **Payments** | Append-only event stream, raw XML retained alongside parsed columns | Payment lifecycle resolved by AUTO CDC sequenced on event time; reversals applied as corrections, never as overwrites | Payment flows product; liquidity views; regulatory payment aggregates |
| **Positions** | FIX and position deltas, raw message preserved verbatim | Order chains threaded (watermarked, with a late side-output); positions bitemporal on trade/settlement/knowledge dates | Exposure product; intraday aggregate; end-of-day authoritative position |
| **Risk** | Landed risk-engine inputs and outputs; federated legacy values for comparison only | Conformed exposures, netting sets, counterparty hierarchy resolved bitemporally | RWA and exposure products; limit utilisation; stress result sets |
| **Finance** | GL CDC stream; trial-balance anchor | Bitemporal chart of accounts and legal-entity hierarchy; postings conformed to a single intercompany convention | Statutory and management reporting products; reconciliation results |
| **Market data** | Conflated tick stream; reference files as delivered | Instrument master with identifier survivorship; bitemporal corporate actions; validated closing prices | Curve and surface products; pricing inputs; licence-tagged distributions |

### Non-negotiable bronze rules

| Rule | Reason |
|---|---|
| Bronze is **append-only and immutable**. No UPDATE, no DELETE except under the erasure control process (§7.4) | Bronze is the evidence layer. If bronze can be edited, nothing downstream can be attested |
| The **raw payload is retained verbatim** beside parsed columns for payments, cards and FIX | A surveillance or dispute replay must be byte-faithful. A reparse must be possible without re-extraction |
| Every bronze row carries `_ingest_ts`, `_source_system`, `_source_file` or `_offset`, `_batch_id`, `_pipeline_run_id` | These five columns are what make the lineage graph joinable to an operational event |
| Schema evolution is **additive only**; a type change forces a new column and a documented migration | A silent type change is how a reconciliation breaks three months later |
| Quality expectations run at bronze→silver, **not at ingest**. Bronze accepts what arrived | You cannot evidence what you rejected if you never landed it |

## 5.4 Point-in-time correctness and bitemporality

**This is the section that distinguishes a banking lakehouse from every other lakehouse.** A retailer that
overwrites yesterday's price loses a fact. A bank that overwrites yesterday's exposure loses an
attestation.

### 5.4.1 The four time axes

| Axis | Meaning | Example |
|---|---|---|
| **Event time** | When the thing happened in the world | The trade executed at 14:32:07.114 |
| **Effective time (valid time)** | The period over which the fact is true of the business | The collateral amendment is effective from 1 March, though signed on 14 April |
| **Knowledge time (transaction time)** | When the bank first knew it | The bank learned of the amendment at 14 April 09:12 |
| **Ingest time** | When the platform received it | The row landed at 14 April 09:19 |

Most estates model one axis. SMB needs **effective time and knowledge time together** — bitemporality —
plus event time where the source is an event stream. Ingest time is operational metadata, not a business
axis, and must never be used as a proxy for knowledge time.

### 5.4.2 The four scenarios that break a unitemporal model

| Scenario | Source | What a unitemporal model does | What bitemporality does |
|---|---|---|---|
| **As-of reporting** | Any | Cannot reproduce last quarter's number after a correction | `AS OF knowledge_ts = <submission timestamp>` reproduces exactly what was reported |
| **Restatement** | GL hierarchy reorganisation | Overwrites prior-period mapping; prior reports become irreproducible | Inserts a new knowledge version with a backdated effective range; both the original and the restated view are queryable |
| **Late-arriving correction** | Payment reversal 5 days later; market-data correction tick | Updates the row, destroying the value on which a decision was made | Closes the prior knowledge version and opens a new one; the decision remains explicable |
| **Backdated amendment** | Collateral agreement effective from a past date | Either rewrites history or ignores the effective date | Effective range starts in the past; knowledge range starts today. Both capital numbers — the one computed then and the one computed now — are reproducible |

### 5.4.3 How we implement it

| Mechanism | Where | Notes |
|---|---|---|
| **AUTO CDC flows with `STORED AS SCD TYPE 2`** | Silver dimensional entities: party, account, instrument, counterparty hierarchy, chart of accounts, collateral agreement | Documented in Lakeflow Spark Declarative Pipelines. `SEQUENCE BY` is required. Produces `__START_AT` / `__END_AT` validity columns; the current row has `__END_AT IS NULL`. Requires serverless pipelines or the Pro/Advanced edition |
| **`STORED AS BITEMPORAL`** | Candidate for the entities where effective and knowledge time genuinely diverge — GL hierarchy, collateral agreements, corporate actions | **This option is documented but marked Beta.** We design the logical model so that it works either way, and we prove the Beta in Phase 0 against the GL hierarchy. **Fallback: an explicit two-pair-of-columns model maintained by MERGE, which is the pattern the industry used before the feature existed.** Do not make the delivery plan depend on a Beta |
| **Explicit bitemporal columns** | The fallback and the model for fact tables | `effective_from`, `effective_to`, `knowledge_from`, `knowledge_to`, half-open intervals `[from, to)`, `knowledge_to` = `TIMESTAMP '9999-12-31'` for current. Every as-of query filters on both pairs |
| **As-of join predicate** | Every gold query that joins a fact to a dimension | `fact.event_ts >= dim.__START_AT AND fact.event_ts < coalesce(dim.__END_AT, TIMESTAMP '9999-12-31')` — the half-open window. A closed window double-counts on the boundary day, which is the single most common bitemporal bug and it produces a plausible-looking wrong number |
| **Delta time travel** | Operational recovery and short-window forensics **only** | Bounded by `delta.logRetentionDuration` (default 30 days) and `delta.deletedFileRetentionDuration` (default 7 days), and destroyed by `VACUUM` beyond the retention period. On DBR 18.0+ time travel is blocked beyond the deleted-file retention threshold. **Time travel is not a bitemporal model and must never be sold as one.** It is a platform feature with a retention clock; bitemporality is a data model with a legal obligation |
| **Submission snapshots** | Regulatory reporting | Every submitted return is materialised as an immutable table with the knowledge timestamp of submission, the pipeline run id, the code version and the approver. This is the artefact the examiner asks for |

### 5.4.4 The report contract

Every regulatory gold table is a **function of two parameters**: `reporting_date` (the effective date the
return covers) and `as_of_knowledge_ts` (the state of the bank's knowledge at which to compute it).
Re-running with the original `as_of_knowledge_ts` must return the original numbers, bit for bit.
Re-running with `now()` returns the restated numbers. **The difference between the two is the restatement
disclosure** — computed, not narrated.

This single design decision is the one that closes the lineage finding, because it converts "prove this
number" from an archaeology exercise into a parameterised query.

### 5.4.5 What bitemporality costs

| Cost | Magnitude | Mitigation |
|---|---|---|
| Storage | 1.6× – 2.4× versus current-state-only, domain dependent | Liquid clustering on the key plus `knowledge_from`; archive closed knowledge versions older than the statutory window to a cheaper tier |
| Query complexity | Every join gains two predicates | Encapsulate in views and metric views. Analysts never hand-write the predicate; if they do, we have failed |
| Compute | 20 – 35% more on the silver layer | Accept. This is the cost of the attestation |
| Cognitive load | High. The most common failure is an engineer who "simplifies" the predicate | Testing gate: every bitemporal entity has a mandatory boundary-condition test suite (§9.5) |

## 5.5 Streaming versus batch, per use case

We do not run everything streaming. Streaming is an operational commitment — checkpoints, state,
watermarks, restart semantics — and it should be paid for only where the latency is real.

| Use case | Mode | Trigger | Justification |
|---|---|---|---|
| Fraud feature freshness | Continuous streaming | Default pipeline trigger interval (5 s for streaming sources) | Seconds latency is genuine; features go stale in minutes |
| Intraday exposure | Streaming ingest, **micro-batch aggregate every 5 minutes** | `availableNow` on a 5-minute schedule for the aggregate | The aggregate is read by humans on a 15-minute cadence. Continuous aggregation would buy nothing and cost state |
| Payments and cards bronze | Continuous streaming | Streaming | Downstream fraud requires it, and replaying a day of Kafka to catch up is worse than staying current |
| FIX bronze and order threading | Continuous streaming, watermarked | Streaming, documented lateness bound with a side output | Surveillance replay depends on completeness, not speed; the stream is for exposure |
| Core banking CDC | Streaming ingest to bronze, **15-minute micro-batch to silver** | `availableNow`, 15-minute schedule | Matches the stated latency need exactly. Continuous silver would run SCD2 merges every few seconds for no consumer |
| GL, CRM, KYC, collateral | Managed connector schedule | Hourly, 15 min for consent and alerts | The connector's own scheduling |
| Market reference / EOD | Batch | Scheduled, pre-open, with a hard SLA alert | It is a file drop with a deadline |
| Regulatory report assembly | Batch | Lakeflow Jobs, parameterised, triggered on upstream completion | It is periodic by definition. Streaming a quarterly return is theatre |
| Finance close reconciliation | Batch, continuous during month | Nightly, then hourly in the close window | The work moves out of the window; the cadence does not need to be sub-hourly |
| Market surveillance sweep | Batch, T+1, over the raw preserved stream | Nightly | Deliberate. The alert quality depends on full-day context |

**The rejected alternative** — "stream everything for consistency" — was rejected because it multiplies
always-on compute, multiplies checkpoint and state management surface, and makes full-refresh recovery
dangerous where upstream retention is short (a full refresh of a streaming table discards all data and
restarts the stream from the beginning; if Kafka retention has expired, that history is unrecoverable).
Streaming is chosen per flow, with a named consumer who needs the latency.

## 5.6 Unity Catalog design

### 5.6.1 Catalog topology

Two axes have to be reconciled: **environment** (dev / test / prod) and **legal entity plus residency**.
We resolve them as follows.

| Level | Decision |
|---|---|
| **Metastore** | One metastore **per region**, because a metastore is regional and residency is a legal boundary. Illustrative: EU (Frankfurt), UK (London), APAC (Singapore), US (for the markets entity) |
| **Catalog** | `<env>_<entity>_<domain-group>`. Examples: `prod_smb_plc_core`, `prod_smb_de_core`, `prod_smb_sec_markets`, `dev_smb_plc_core` |
| **Why entity in the catalog, not the schema** | A legal entity is the unit of regulatory reporting, of capital, of residency and of recharge. Making it a catalog means an entity's data can be granted, audited, budgeted and — if the bank sells the entity — detached, as one object |
| **Why environment in the catalog, not the metastore** | A separate metastore per environment breaks lineage continuity across promotion and doubles the governance surface. Separate catalogs give isolation with a single governance model. **Counter-argument acknowledged: some banks require a physically separate non-production metastore. If SMB's security policy requires it, this is a one-line change to the bundle targets, at the cost of cross-environment lineage** |
| **Schema** | `<domain>_<layer>`: `customer_bronze`, `customer_silver`, `customer_gold`, `payments_bronze`, … Plus `_ops` per domain for run metadata and reconciliation results, and `_quarantine` for expectation rejects |
| **Volumes** | `<catalog>.<domain>_bronze.landing_<source>` external volumes over the governed landing paths. All file ingestion is `/Volumes/…`, never a raw cloud path |

### 5.6.2 Information barriers — the capital-markets separation

This is the hardest governance requirement in the bank and it is solved structurally, not by policy text.

| Layer of control | Mechanism |
|---|---|
| **Separate catalogs** | `prod_smb_sec_markets` is a distinct catalog. Retail and commercial principals hold no grant on it at all — not a masked grant, **no grant** |
| **Separate metastore where the entity is in another region** | The US markets entity sits in a US metastore. Cross-metastore access is only possible via an explicit OpenSharing share, which is an auditable, approvable object |
| **Governed tags for MNPI** | Governed tags are defined at the account level with their own access controls. `mnpi.class` with values `order_flow`, `pre_announcement`, `research_embargo`, `none`. Governed tags inherit from catalog and schema to table — **but column tags do not inherit and must be applied directly**, which is a build task, not an assumption |
| **ABAC policies** | Row filter and column mask policies attached at catalog or schema level, matching on `has_tag_value('mnpi.class', …)`. Because policies set at a higher level **cannot be overridden or removed by table owners**, a desk team cannot unmask its own data. That property is the reason ABAC is chosen over table-level filters |
| **Wall-crossing** | A wall-crossing is a time-boxed group membership with an approval record, not a grant change. The group is empty by default and membership expires. Expiry enforcement is an operational job, and **whether the identity provider can enforce time-boxed membership natively is [TBC with IAM]** |
| **Detection** | A scheduled query over `system.access.audit` for any access by a principal in a restricted group to an MNPI-tagged object, alerting Compliance. Note: audit logs are regional, so this query runs per region |

**Rejected alternative:** a single catalog with column masks separating markets data. Rejected because a
mask hides a value but not the existence of the row, the table or the counterparty — and in a market-abuse
context, knowing that the bank holds an order in a name is itself the information. Separation must be at
the level of *visibility of existence*, which means separate catalogs and no grant.

### 5.6.3 Groups and grants

| Group pattern | Example | Grants |
|---|---|---|
| Domain owner | `dom-owner-payments` | `MANAGE` on the domain's schemas |
| Domain engineer | `dom-eng-payments` | `CREATE`/`MODIFY` in dev and test; **no direct production write** — production writes are made by a service principal via a bundle |
| Data consumer, entity-scoped | `cons-smb-de-risk` | `SELECT` on gold schemas in that entity's catalog only |
| Regulatory reporting | `reg-reporting-eu` | `SELECT` on gold and on submission snapshots, across the entities in scope for that return |
| Markets-side principals | `mkt-desk-equities` | Grants only within `prod_smb_sec_markets` |
| Restricted (financial crime filings) | `fc-filings` | `SELECT` on the filings schema; membership approved by the MLRO |
| Platform service principals | `sp-prod-deploy-<domain>` | The only principals with production write. `run_as` on all production jobs and pipelines |

**Rule:** no individual human holds a production write grant. This is not a Databricks constraint; it is
how segregation of duties is evidenced (§7.8).

### 5.6.4 ABAC policy set (illustrative)

| Policy | Attaches at | Matches | Effect |
|---|---|---|---|
| `mask_pii_default` | Each entity catalog | `has_tag('pii.class')` on a column | Masks unless the principal is in the entity's PII-cleared group. Uses governed tags, so a new table inheriting the schema tag is protected on creation, not after a review |
| `secure_by_default_pending` | Each bronze schema | `review_status = 'pending'` control tag | Masks every column until a data steward marks the schema reviewed. This is the documented secure-by-default pattern and it is what stops a new source leaking on day one |
| `restrict_mnpi` | Markets catalog | `has_tag_value('mnpi.class','order_flow')` | Row filter restricting to the owning desk plus Compliance |
| `block_licensed_share` | All catalogs | `has_tag_value('licence.class','no_redistribution')` | GRANT policy preventing the object being added to an outbound share |
| `residency_<country>` | Entity catalogs with a residency constraint | `has_tag_value('residency','<country>')` | Row filter restricting to principals in the in-country group |

**Constraints we design around, taken from the documented behaviour:**
- Only one distinct row filter and one distinct column mask can resolve at runtime per table (or per
  column) per user. If two apply, **Databricks blocks access and errors**. Our policy set is therefore
  designed so that scopes do not overlap for any principal, and a conflict test is part of the CI suite.
- ABAC-secured tables require serverless compute (any version), or standard/dedicated compute on **DBR
  16.4+** with fine-grained access control filtering. Older runtimes cannot read them. This sets a
  **runtime floor for the whole estate**.
- ABAC policies cannot be applied directly to views, and clones of ABAC-protected tables are not
  supported. This constrains the cloning patterns available for test data (§9.5).
- **OpenSharing interacts with masking in a way that must be understood before any share is created**:
  providers cannot share tables carrying table-level row filters or column masks; an ABAC-protected table
  can be shared only if the share owner is exempt via the `EXCEPT` clause, and **the recipient then sees
  unfiltered data by default**. Outbound shares therefore publish **purpose-built, already-filtered gold
  views**, never a protected base table. This is written into the sharing runbook.

## 5.7 Serving

| Consumer | Mechanism | Decision notes |
|---|---|---|
| BI and ad hoc analysis | **Databricks SQL serverless warehouses**, one per entity and workload class | Serverless starts in seconds versus roughly four minutes for pro/classic, and carries Predictive IO and Intelligent Workload Management. **Rejected pro warehouses as the default** — but pro is retained for any workload needing custom networking or federation, which is the documented reason to choose it |
| Regulatory extracts | **Lakeflow Jobs** with `reporting_date` and `as_of_knowledge_ts` job parameters, on serverless job compute | Rejected: a scheduled notebook. A notebook is not a promotable, parameterised, evidenced artefact. Jobs deployed via Declarative Automation Bundles are |
| Semantic layer | **Metric views** over gold | Gives one definition of "exposure", "RWA", "net revenue" shared by BI, Genie and downstream. Note the documented limits: measures need `MEASURE()`, `SELECT *` is not usable, metric views cannot be joined directly at query time (wrap in a CTE), and **materialisation is blocked when row filters, column masks or ABAC apply** — so materialised metric views are available only on non-restricted gold |
| Feature serving | **Unity Catalog feature tables**; online serving via Databricks Online Feature Stores | Closes the training/serving skew finding by construction: the same table definition feeds `create_training_set` and the online store. Note the `feature` securable is **Public Preview** |
| Model serving | **Model Serving endpoints** for fraud and credit scorecards, with inference tables enabled | Inference tables are the model-governance evidence trail. Endpoint ACLs are CAN VIEW / CAN QUERY / CAN MANAGE; the decision engines get CAN QUERY via a service principal only |
| Client and vendor exchange | **OpenSharing** outbound (clients) and inbound (vendor reference data) | Zero-copy, no egress within a region, governed as a UC object. Subject to the masking interaction in §5.6.4 and to vendor redistribution terms |
| Regulatory submission handoff | File extract to the existing reporting engine, from a **submission snapshot table** | Rejected: direct connection from the reporting engine to the lakehouse. The snapshot is the evidence artefact; the engine consumes the snapshot, not a live query |

## 5.8 Platform layer

| Decision | Choice | Rejected alternative | Why |
|---|---|---|---|
| **Workspace topology** | One workspace per (region × environment), plus a dedicated workspace for the markets entity in each region it books in | One global workspace per environment | Residency, network isolation and the information barrier all fail with a single workspace. Accepted cost: more workspaces to administer, which is why everything is deployed by bundle |
| **Compute default** | **Serverless** for pipelines, jobs and SQL, with classic compute only where required | Classic everywhere | Documented recommendation is serverless for new pipelines; incremental refresh of materialized views is **serverless-only** (on classic, an MV is always fully recomputed), and ABAC works on serverless at any version. Classic remains required for the Lakeflow Connect ingestion gateway, for legacy Hive metastore access during migration, and where private networking or region availability demands it |
| **Runtime floor** | DBR 16.4+ where classic compute is used | Mixed runtimes | ABAC-secured tables are unreadable on standard/dedicated compute below 16.4. A mixed estate would produce silent "no data" failures, which in a bank is worse than an error |
| **Network isolation** | Private connectivity between control plane and compute; no public IPs on compute; egress controlled | Public endpoints with IP allowlists | An allowlist is a control that a misconfiguration silently removes. Serverless SQL warehouses are documented as having no public IP addresses and using private connectivity |
| **Customer-managed keys** | **Assume required; confirm scope.** CMK has two scopes — managed services (control-plane data: notebooks, secrets, SQL query data) and workspace storage. For serverless-only workspaces, only the managed-services key is configured. CMK is an Enterprise-tier capability | Platform-managed keys | Most banks' key policy requires CMK. **The specific requirement, the key custodian, the rotation period and whether workspace-storage CMK is needed given a serverless-first design are all [TBC with the CISO]** |
| **Hardened profile** | Evaluate the **compliance security profile** (part of the Enhanced Security and Compliance add-on): CIS Level 1 hardened host OS, FIPS 140 validated encryption modules, enforced instance types, TLS 1.2+ egress, enhanced security monitoring, automatic cluster update. It can be enabled for hardening alone | Default profile | It supports processing of data regulated under several regimes including PCI-DSS. **Whether SMB requires it, in which workspaces, and its cost and regional availability are [TBC]. The customer remains responsible for compliance verification** |
| **Identity** | SCIM from the corporate IdP; groups are the only grant target; service principals with workload identity federation for CI/CD | Personal access tokens in CI | Documented CI/CD guidance is to use service principals rather than users, and workload identity federation to eliminate stored Databricks secrets. A PAT in a pipeline is an audit finding waiting to happen |
| **Everything as code** | **Declarative Automation Bundles** for jobs, pipelines, warehouses and permissions; Terraform for account-level and workspace-level infrastructure | Click-ops with a change ticket | A bundle in Git with a signed commit is the four-eyes evidence. A screenshot is not |
| **Audit and observability** | `system.access.audit`, `system.access.table_lineage` / `column_lineage`, `system.billing.usage`, `system.lakeflow` job tables, pipeline event logs published to a UC table | Third-party log aggregation only | The system tables are the primary record. Note: `system.access.audit` is **Public Preview**; most system tables retain 365 days and lineage keeps a rolling 1-year window — **which is shorter than every regulatory retention period in this bank**, so §7.2 defines an archival copy |

## 5.9 Data layout and performance

| Decision | Applies to | Notes |
|---|---|---|
| **Liquid clustering** on `(entity_id, business_date)` or `(counterparty_id, knowledge_from)` | Silver and gold fact tables | Preferred over static partitioning because regulatory query predicates change with every new return and repartitioning a 48 TB table is not a change we want to make quarterly |
| Date partitioning retained | Bronze tick and event tables where a retention job deletes whole days | Partition-aligned deletion is far cheaper than predicate deletion at this volume |
| **Predictive optimization** on UC managed tables | All managed tables | Runs `OPTIMIZE`, `VACUUM` and `ANALYZE` automatically. Note it **does not run `ZORDER`**, and it runs `VACUUM` — which interacts with the time-travel retention discussion in §5.4.3 and with the erasure controls in §7.4. Its behaviour must be documented in the evidence pack, not left implicit |
| Deletion vectors | Enabled on tables subject to erasure | Consequence to design for: because deletion vectors mark rows as deleted in metadata, **`DELETE` alone is not physical erasure**. `REORG TABLE … APPLY (PURGE)` then `VACUUM` is required. This sequence is the erasure runbook (§7.4) |
| Informational primary and foreign keys | Gold dimensional models | Not enforced, but they drive BI tooling and Genie's understanding of relationships |

---

# 6. Data products and domain ownership

## 6.1 Domain map

| Domain | Accountable owner (client role) | Technical owner | Primary sources | Consumers |
|---|---|---|---|---|
| **Customer** | Chief Customer Officer, delegated to Head of Customer Data | Customer data engineering pod | S1, S9, S12, S13 | Marketing, RM coverage, Financial Crime, Credit, Client Service |
| **Payments** | COO Payments | Payments pod | S2, S3 | Fraud, Liquidity, Regulatory Reporting, Finance |
| **Positions** | COO Capital Markets (markets book), Head of Product Control (banking book) | Positions pod (split across the barrier) | S5, S10 | Risk, Finance, Surveillance, Client Reporting |
| **Risk** | Group CRO, delegated to Head of Risk Data | Risk pod | S10, S14, plus Customer and Positions products | Regulatory Reporting, Treasury, Risk Committee, Credit |
| **Finance** | Group Financial Controller | Finance pod | S4, plus Positions and Payments products | Statutory reporting, Management reporting, External audit |
| **Market data** | Head of Market Data Services | Market data pod | S6, S7, S13 | Risk, Positions, Finance, Surveillance |

**Note the split ownership of Positions.** The markets book and the banking book are owned by different
executives, sit in different catalogs, and the markets side sits behind the barrier. Pretending Positions
is one domain with one owner is how a bank ends up with an MNPI incident.

## 6.2 Published data products

A data product here means: a named set of gold tables or views, with an owner, a published contract, a
support commitment and a deprecation policy. If it has no contract, it is a table, not a product.

| Product | Domain | Grain | Refresh | Key contract terms |
|---|---|---|---|---|
| `customer_party_360` | Customer | One row per resolved party, bitemporal | Hourly | Resolution confidence exposed as a column; consent state is authoritative; **no markets relationship attributes** |
| `customer_consent_current` | Customer | One row per party × purpose | 15 min | Consent is the gate for outbound activity; 15-minute SLA is contractual |
| `payment_lifecycle` | Payments | One row per payment × knowledge version | Streaming | Reversals appear as new knowledge versions; never an update |
| `card_transaction_enriched` | Payments | One row per authorisation | Streaming | **Guaranteed to contain no PAN.** Any breach of this term is a P1 incident, not a data-quality ticket |
| `position_eod_authoritative` | Positions | Position × book × business date, bitemporal | Daily, by 06:00 | The number capital is computed from. Changes only via a knowledge version |
| `position_intraday` | Positions | Position × book, latest | 5 min | Explicitly **indicative**; not usable for regulatory capital. Contract states this |
| `exposure_counterparty` | Risk | Counterparty × entity × date, bitemporal | 15 min intraday, authoritative daily | Hierarchy resolution rules published; netting-set membership sourced from collateral, not risk |
| `rwa_components` | Risk | Exposure class × entity × reporting date | Daily | Reproducible for any `as_of_knowledge_ts` within the statutory window |
| `gl_balances_bitemporal` | Finance | Account × entity × period, bitemporal | Hourly; continuous at close | Hierarchy restatements are knowledge versions; prior-period reproducibility guaranteed |
| `reconciliation_results` | Finance | Reconciliation × run × date | Per run | Machine-readable break register. Replaces the spreadsheets |
| `instrument_master` | Market data | Instrument, bitemporal | Pre-open | Identifier survivorship rules published; licence class tagged per field group |
| `pricing_marks_eod` | Market data | Instrument × date × source | Pre-open | Corrections are knowledge versions; the mark used on the day is always recoverable |
| `submission_<return>_<period>` | Risk / Finance | The submitted return, frozen | Per submission | Immutable. Carries run id, code version, approver, input table versions |

## 6.3 How ownership maps to catalogs, schemas and grants

| Concept | Mapping |
|---|---|
| Domain | A set of schemas named `<domain>_<layer>` within each entity catalog |
| Domain ownership | `dom-owner-<domain>` group holds `MANAGE` on those schemas |
| Product publication | A gold table or view, tagged `product.name` and `product.version`, with `system.certification_status` set once the steward signs off |
| Contract | A YAML contract file versioned in the domain's repository alongside the bundle, generating (a) the table comment, (b) the expectation set, (c) the monitoring thresholds. **The contract is the source, the table properties are the output** |
| Consumption | `SELECT` granted to `cons-<entity>-<function>` groups on the product only, never on silver or bronze |
| Cross-domain dependency | Declared in the consuming domain's contract; visible in `system.access.table_lineage`; a breaking change requires the consuming owner's sign-off |
| Cross-entity dependency | Only via OpenSharing, which makes the dependency an approvable object rather than an implicit grant |
| Deprecation | Minimum two quarters' notice; the metric view or table stays live with a deprecation tag; lineage is used to prove who still reads it before it is removed |

## 6.4 The federated operating model, honestly

Full data mesh is not achievable at SMB in the programme window, and proposing it would be a
misjudgement. What is achievable:

| Aspect | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Pipeline build | Central platform team builds; domains review | Domains build for their own silver and gold; platform owns bronze and the framework | Domains own end to end within their catalog |
| Contracts | Platform authors, domain signs | Domain authors | Domain authors, with a published change process |
| Governance | Central Data Council approves every product | Council approves the pattern; domains self-certify against it | Exception-based review |
| Access approval | Central | Domain owner, with audit | Domain owner, with automated attestation |

The constraint is not technology. It is that the bank currently has roughly 6–10 people who can write
production Spark and none of them sit in a business domain. §9 addresses that directly.

---

# 7. Governance, risk and compliance

This is the section a bank buys. Everything above is architecture; this is whether the architecture
survives an examination.

## 7.1 Lineage as regulatory evidence

| Question the examiner asks | How the platform answers it |
|---|---|
| "Where did this number come from?" | Unity Catalog captures lineage automatically to **column level**, across tables, views, notebooks, jobs, pipelines, queries, dashboards, UDFs and models. Queried from `system.access.table_lineage` and `system.access.column_lineage` |
| "Who ran the job that produced it?" | `system.lakeflow` job run tables plus `system.access.audit`, which carries `user_identity`, `identity_metadata.run_by` / `run_as`, `request_id` and `statement_id` |
| "What code version was used?" | The bundle deployment is a Git commit. The job run records the bundle target and version; the submission snapshot records the commit SHA |
| "Who approved the change?" | The pull request approval record, linked to the commit, linked to the deployment (§7.8) |
| "Show me the data as it was when you submitted" | The submission snapshot table, plus the bitemporal `as_of_knowledge_ts` re-run (§5.4.4) |
| "What else reads this data?" | Downstream lineage from the same system tables. This is also how we prove a decommission is safe |

### Lineage limitations we must engineer around, and state plainly

| Limitation | Our response |
|---|---|
| Only objects registered in Unity Catalog are covered | Nothing in the regulatory path may live outside UC. External locations and volumes are registered; raw cloud paths are prohibited by policy and by compute configuration |
| RDD operations are not captured; **path-based references break column lineage**; renaming an object loses its lineage | Coding standard: table names only, never paths, in any pipeline. Enforced in CI by a static check. Renames go through a documented migration that preserves the audit trail separately |
| Lineage system tables keep a **rolling one-year window** | **Insufficient for a 7–10 year retention obligation.** A monthly job snapshots lineage into an immutable `governance.lineage_archive` table in the entity's catalog, with its own retention matching the regulatory period. This is a build item, not an assumption |
| Viewing lineage requires `BROWSE` on the parent catalog | Examiner-facing access is via an exported evidence pack, not a workspace login. Auditors get a read-only role scoped to the governance schema |
| Whether federated queries appear in lineage is **not documented** | We therefore do **not** rely on federation in any attested path. Federation is parallel-run and ad hoc only. This is a governance reason for the architectural decision in §5.2 |

### What we will not claim

Lineage shows that column A fed column B. It does not show that the transformation between them was
*correct*. Correctness is established by the reconciliation and test suites (§8.5, §9.5). Presenting
lineage as proof of correctness is a claim that will not survive a competent examiner, and we do not make
it.

## 7.2 Immutability, audit and retention

| Control | Implementation |
|---|---|
| **Bronze immutability** | Append-only by pipeline design. Production write is by service principal only; no human holds `MODIFY`. Any deviation appears in `system.access.audit` |
| **Submission immutability** | Submission snapshot tables are written once and then have their grants reduced to `SELECT` for the reporting group and the auditor group. Owner is a governance service principal, not a person |
| **Audit trail** | `system.access.audit` (Public Preview). Filter on `event_date` for performance. Note two operational facts: **account-level events record `workspace_id` as 0**, and **most audit logs are only accessible from the region in which they are recorded** — so the audit query set is per-region and the archive is consolidated by a job |
| **Audit archive** | System tables retain 365 days (lineage one year). Every retention obligation in this bank exceeds that. A monthly export into `governance.audit_archive`, immutable, with retention set per jurisdiction. **This is the single most commonly missed requirement in bank lakehouse builds** |
| **Verbose audit logging** | Enabled in production workspaces — it adds notebook and `runCommand` events, which is what lets us evidence that no one ran an ad hoc query against a restricted table |
| **Masked audit fields** | Four `request_params` keys (`function_info`, `view_definition`, `definition_json`, `managed_definition`) are masked unless the reader is an account admin or in `databricks_pii_access`. The audit archive job runs under a principal with that access; the analyst-facing copy does not |

### Retention schedule (illustrative structure — the values are for Legal to set)

| Data class | Illustrative period | Driver | Where the real number comes from |
|---|---|---|---|
| Core banking customer and account records | 7–10 years post closure | Banking and tax law per jurisdiction | Legal, per entity |
| Payment messages | 5–7 years | Payments regulation | Legal, per corridor |
| Card transactions | ~7 years | Scheme rules plus regulation | Payments + Legal |
| Order and execution records | 5–7 years | Market conduct regime | Compliance, per venue and regulator |
| Financial crime cases and filings | 5–7 years post relationship | Financial crime regime | MLRO |
| Credit decision evidence | Facility life plus a statutory tail | Consumer credit regime | Credit Risk + Legal |
| Clickstream and digital telemetry | 13–25 months | Privacy regimes | DPO, per country |
| Market data (raw ticks and reference) | **Contractual, not regulatory** | Vendor licence | Market Data Services |
| Audit and lineage evidence | Matching the longest data retention it evidences | Supervisory expectation | Group Compliance |

Retention is implemented as: a `retention.class` governed tag on every table → a scheduled Lakeflow Job
per class → deletion executed via the erasure runbook (§7.4) so that deletion vectors do not leave
physical data behind → the deletion itself logged to the audit archive.

## 7.3 Immutability versus VACUUM and predictive optimization

A tension that must be surfaced rather than discovered:

| Tension | Resolution |
|---|---|
| Predictive optimization runs `VACUUM` automatically on UC managed tables, and `VACUUM` destroys time travel beyond the retention threshold | Time travel is **not** our evidence mechanism (§5.4.3). Evidence is the bitemporal model plus the submission snapshots plus the audit archive, none of which depend on the Delta file history. PO is therefore safe to leave on, and we document that this is a deliberate decision |
| `delta.logRetentionDuration` defaults to 30 days and `delta.deletedFileRetentionDuration` to 7 days | Both are set explicitly per table class rather than left at default, and the setting is part of the contract. On DBR 18.0+, `logRetentionDuration` must be `>=` `deletedFileRetentionDuration` |
| An examiner asks to see the table as of a date 3 years ago | Answered from the bitemporal model with `as_of_knowledge_ts`, or from the submission snapshot. **Never** from time travel. If anyone answers "we'll time travel to it", that is a control failure, because the answer depends on whether a maintenance job has run |

## 7.4 Right to erasure versus regulatory retention

The genuine conflict, and how it is resolved.

### The conflict

A customer exercises an erasure right under a privacy regime. The same customer's records are subject to
a financial-crime retention obligation, a banking records obligation and possibly an ongoing
investigation whose existence cannot be disclosed. These cannot all be satisfied by deleting the data.

### The resolution

| Step | Action |
|---|---|
| 1. Intake | Erasure requests land in a **deletion-request control table** — the documented pattern — with the requester, the legal basis, the receipt timestamp and the statutory response deadline |
| 2. Classification | An automated assessment joins the request to `retention.class` and `legal_hold` tags across the customer's data, producing three buckets: **erasable now**, **retained under obligation**, **under legal hold** |
| 3. Legal determination | A named privacy officer records the determination per bucket. This is a human decision with an audit record, not a rule engine output |
| 4. Erasure of the erasable bucket | `MERGE … WHEN MATCHED THEN DELETE` for bulk (the documented recommendation for deleting many records at once), **delete in bronze first**, then propagate downstream. Then `REORG TABLE … APPLY (PURGE)` and `VACUUM`, because deletion vectors otherwise leave the data physically present |
| 5. Suppression of the retained bucket | Data retained under obligation is moved behind a **suppression flag** that removes it from every processing purpose except the one the obligation requires. Enforced by an ABAC row filter, not by convention |
| 6. Response | The customer receives a response stating what was erased and that other data is retained under a legal obligation, without disclosing the existence of any filing |
| 7. Evidence | The whole chain — request, classification, determination, execution, verification — is a row set in `governance.erasure_log`, immutable, retained for the statutory period |

### The awkward parts we name up front

| Issue | Position |
|---|---|
| **Streaming tables are append-only.** Deleting from an upstream source does not propagate | The documented options are (a) delete from source and from the streaming table with DML and add `skipChangeCommits` on the streaming read, or (b) delete from source and **fully refresh** the streaming table — which clears state and reprocesses everything and risks data loss if source retention has expired. **We adopt (a) as the standard and prohibit (b) in the erasure runbook** |
| **Materialized views** handle source deletions automatically | Good, but it must be verified per view in the erasure test suite rather than assumed |
| **OpenSharing shares default to `WITH HISTORY`** on DBR 16.2+, so a recipient can time-travel to versions before a delete | Outbound shares publish purpose-built gold views with a short history and an explicit contract term on the recipient's deletion obligation. **Reviewed by Legal per recipient** |
| **Shallow clones** break when the source is vacuumed, and ABAC-protected tables cannot be cloned at all | Constrains the test-data strategy (§9.5) |
| Upstream systems are out of scope for Delta-level erasure | The Databricks guidance is explicit that privacy regimes apply to all data, including Kafka, files and databases outside Delta. The erasure runbook therefore includes upstream tickets, and the lakehouse deletion is not marked complete until they are confirmed |
| **Masking is not erasure** | The documented position is that complete deletion is preferable to obfuscation, because masking does not eliminate re-identification risk. We follow it |

## 7.5 MNPI handling and information barriers

| Control | Detail |
|---|---|
| **Structural separation** | Separate catalogs, separate workspaces, separate metastore where the entity is in another region (§5.6.2) |
| **Tagging** | `mnpi.class` governed tag, applied at schema level and inherited, with column-level tags applied explicitly because **column tags do not inherit** |
| **Enforcement** | ABAC row filter and column mask policies at catalog level. Because a policy set at catalog or schema level **cannot be overridden or removed by a table owner**, the desk cannot unmask its own data |
| **Wall-crossing** | Time-boxed group membership with a recorded approval and an expiry job. The approval record is a row in `governance.wall_crossing_log` linked to the deal or the reason |
| **Surveillance of the barrier** | Daily query over `system.access.audit` for cross-barrier access attempts, run per region, alerting Compliance. False negatives are the risk: the query must cover `unityCatalog` service events including `getTable`, not just query history |
| **Research and pre-announcement embargo** | Pre-announcement group results in the GL are tagged `mnpi.class = pre_announcement` for a defined window by a scheduled job driven by the results calendar. The tag is applied *before* the data exists, on the schema, so inheritance protects the new rows on arrival |
| **The failure mode we design against** | An analyst joins a non-MNPI table to an MNPI table and materialises the result into a non-restricted schema. Prevented by: no cross-catalog read grant in the first place; plus the secure-by-default `review_status = pending` control-tag policy, which masks every column in a newly created schema until a steward reviews it |

## 7.6 Vendor data licensing as a governance control

| Control | Detail |
|---|---|
| `licence.class` governed tag on every vendor-sourced object, with values such as `internal_only`, `derived_only`, `no_redistribution`, `unrestricted` | The licence is data about data, so it belongs in the catalog, not in a contract folder |
| ABAC GRANT policy preventing `no_redistribution` objects entering an outbound share | The control operates at the moment of the mistake, not at the annual review |
| Retention enforced per licence, independently of regulatory retention | Several vendor contracts require deletion on termination. The retention job reads `licence.class` as well as `retention.class` and applies the **shorter** of the two unless a regulatory hold overrides, in which case the conflict is escalated rather than resolved silently |
| Derived-data rules | Where a licence permits derived data only, the raw feed lands in a restricted schema and only the derived gold product is grantable. This is enforced by grant, not by guidance |

## 7.7 Model governance

| Control | Implementation |
|---|---|
| Model registry | Models registered in Unity Catalog, so a model is a securable with lineage to the tables and features that trained it |
| Feature lineage | Feature tables are UC tables with a primary key; `FeatureLookup` and `create_training_set` record which features a model version consumed. **This is what closes the training/serving skew finding** — the same definition serves both |
| Approval gate | No model reaches a serving endpoint without a Model Risk Management sign-off recorded as a deployment approval on the bundle release |
| Inference evidence | Inference tables enabled on every production endpoint. These are the record of what the model was asked and what it answered, which is what an adverse-action challenge requires |
| Monitoring | Databricks data quality monitoring (formerly Lakehouse Monitoring) on the feature tables and on the inference tables, producing profile and drift metrics tables with an auto-created dashboard. Drift beyond threshold raises a model-risk event, not just an engineering alert |
| Reproducibility | A model decision must be reproducible from the feature values **as at the decision timestamp** — which is a bitemporal requirement on the feature tables, not an ML platform feature |
| Endpoint access | Endpoint ACLs: CAN VIEW / CAN QUERY / CAN MANAGE. Decision engines get CAN QUERY via a service principal. No human holds CAN MANAGE in production outside the release process |
| Explainability | Reason codes derived from the same feature set and stored with the decision. Where the jurisdiction requires an adverse-action explanation, the explanation is a stored artefact, not a re-derivation |

## 7.8 Segregation of duties and four-eyes on production change

| Principle | Mechanism | Evidence artefact |
|---|---|---|
| No human writes production data | Production jobs and pipelines `run_as` a service principal; no individual holds `MODIFY` on a production schema | UC grant listing; `system.access.audit` showing no human write events |
| No self-approval | Branch protection requires a review from a different identity; the author cannot approve | Pull request record with distinct author and approver |
| Production deployment is not a human action | CI deploys the bundle using a service principal with workload identity federation. No stored Databricks secret | Pipeline run log linked to the merge commit |
| Environment separation is enforced by the tool | Bundle `mode: production` validates that pipelines have `development: false`, that the Git branch matches the target's configured branch, and — when not using a service principal — that paths are not user-specific. It prohibits cluster overrides | `bundle validate` output archived per release |
| Change is traceable end to end | Ticket → branch → commit → PR approval → bundle deploy → job run id → table version → submission snapshot | The evidence pack chain (§7.9) |
| Emergency change | A break-glass path exists with a named approver, a time-boxed elevated group, and a mandatory post-hoc review within 2 business days | `governance.breakglass_log` |
| Access review | Quarterly attestation per domain owner, generated from UC grants and `system.access.audit` usage, so that unused grants are visible and removable | Attestation record |

## 7.9 The evidence pack for an examiner

A single, generated, versioned artefact per return and reporting period. Produced by a Lakeflow Job, not
assembled by an analyst.

| Section | Contents | Source |
|---|---|---|
| 1. Scope | Return, entity, reporting date, submission timestamp, `as_of_knowledge_ts` | Submission snapshot metadata |
| 2. Data flow | Column-level lineage graph from source table to reported cell | `system.access.column_lineage`, plus the lineage archive for prior periods |
| 3. Source provenance | For each source: extraction mechanism, extract timestamps, record counts, the reconciling anchor result | Pipeline event logs, `_ops` tables |
| 4. Transformation inventory | Every transformation applied, with the code version and the commit SHA | Bundle manifest, Git |
| 5. Data quality | Expectation results per run: rows passed, rows dropped, rows quarantined, with the quarantine table reference | `details:flow_progress.data_quality.expectations` from the pipeline event log |
| 6. Reconciliation | Every reconciliation control, its tolerance, its result, and every break with its disposition | `reconciliation_results` product |
| 7. Change control | All changes to the pipeline in the period, with author, approver, date and ticket | Git plus deployment log |
| 8. Access | Who read the reported data, who could have, and any exception | `system.access.audit`, audit archive |
| 9. Restatement | Difference between the as-submitted and current-knowledge computation, with the driver of each difference | Two parameterised runs of the same gold query |
| 10. Attestation | The named officer, the date, the scope of the attestation | Manual, signed; everything above is the support for it |

**The claim we make:** producing this pack goes from 200–600 person-hours to a job run plus a review.
**The claim we do not make:** that the pack makes the bank compliant. It is evidence for the bank's
attestation, and the attestation remains the bank's.

## 7.10 Residency

| Question | Position |
|---|---|
| Where is table data stored? | In the cloud storage account of the workspace's region. Entity-to-region mapping is a **Legal decision recorded in an approved topology document** before any workspace is created |
| Where are audit logs? | **Most audit logs are only accessible from the region in which they are recorded.** The consolidated audit archive is therefore assembled by region-local jobs writing into a region-appropriate archive, with any cross-region consolidation explicitly reviewed |
| Where is identity data? | Databricks stores identity data in the United States and in each workspace's region. **This must be reviewed against each jurisdiction's requirements by Legal.** We state it rather than work around it |
| What about cross-border analysis? | Aggregates that cross a residency boundary are produced by sharing **aggregated, non-identifying** products via OpenSharing, with the aggregation level agreed by the DPO. Raw cross-border movement requires a documented transfer basis |
| Broader residency guarantees | **None are claimed.** Beyond the two documented statements above, residency behaviour is [TBC] and must be confirmed with Databricks in writing for each region in scope before the topology is fixed |

---

# 8. Delivery plan

## 8.1 Principles

1. **One report, end to end, before anything else.** Breadth before depth is how bank data programmes
   spend two years and deliver a platform nobody has attested against.
2. **Dual-run to the penny.** Nothing is cut over on a tolerance. The tolerance is zero, and every
   difference is explained before it is accepted or the legacy is found to be wrong.
3. **Decommission is a gate, not a hope.** Each decommission has named criteria, a named approver, and a
   date that slips only with an executive decision.
4. **Nothing reaches production except through a bundle.**

## 8.2 Phase plan

| Phase | Weeks | Objective | Key deliverables | Exit gate |
|---|---|---|---|---|
| **0 — Mobilise** | 1–6 | Prove the hardest assumptions before committing | Region and entity topology approved by Legal; UC metastores created; first mainframe extract landed in a governed volume; CDC product selected and MIPS impact measured; `STORED AS BITEMPORAL` Beta evaluated against the GL hierarchy; CMK and hardened-profile requirements confirmed | Mainframe data in a UC volume, decoded and row-count-matched to a DB2 count; topology signed |
| **1 — Thin regulated slice** | 7–22 | One statutory return, end to end | Bronze/silver/gold for the 3–4 sources that return needs; bitemporal model live; lineage capture; reconciliation framework; first bundle-deployed pipelines; submission snapshot mechanism | The return is produced from the lakehouse and matches the incumbent for one cycle |
| **2 — Reconcile and attest** | 23–34 | Make it trustworthy | Three consecutive cycles reconciled; break register; expectation suite; evidence pack v1 generated; examiner walkthrough rehearsal; access model and ABAC policies in production | Three clean cycles; evidence pack accepted by Internal Audit; first cutover approved |
| **3 — Domain build-out** | 35–70 | Breadth | Customer, Payments, Positions, Risk, Finance, Market data products with contracts; three further returns; finance close reconciliation; metric views; OpenSharing inbound for vendor reference data | Six products published with contracts and named owners; four returns in production |
| **4 — Real-time and decisioning** | 55–86 | The high-value cases | Fraud feature tables and online store; fraud model through Model Risk approval and serving; intraday exposure; credit features; surveillance sweep; client reporting via OpenSharing | Fraud model in production with inference tables; intraday exposure live for two desks |
| **5 — Decommission** | 78–104 | Retire the cost | Teradata risk mart retired; Hadoop landing zone retired; two bespoke marts retired; Informatica mappings in scope decommissioned | All decommission gates passed; run-rate savings booked |

Phases 3 and 4 overlap deliberately. Phase 4 starts as soon as Payments and Customer silver are stable,
because the fraud model-approval tail is long and must start early.

## 8.3 Choosing the thin slice

| Criterion | Requirement |
|---|---|
| Regulatory materiality | High enough that success is noticed; not so high that a failure is a supervisory event |
| Source breadth | Touches the mainframe **and** at least one modern source, so the hard integration is proven |
| Bitemporal exposure | Must involve at least one entity that restates — the GL hierarchy or the counterparty hierarchy |
| Reconcilability | A clean incumbent output exists to dual-run against |
| Sponsor | A named regulatory reporting owner who will attest |
| Size | Producible by a 9-person pod in 16 weeks |

**Recommendation:** a **large-exposures-style counterparty concentration return for one entity**. It needs
core banking balances, positions, collateral, the counterparty hierarchy and the legal-entity hierarchy;
it exercises bitemporality on the hierarchy; it has a clean incumbent output; and its aggregation logic is
the same logic UC-2 (intraday exposure) needs, so Phase 1 builds Phase 4's foundation. **Final selection
is the client's, taken in week 2 against these criteria.**

## 8.4 The mainframe extraction strategy

This is the highest-risk workstream and it gets its own plan.

| Step | Detail |
|---|---|
| **1. Establish the contract with Mainframe Services** | Before any technology choice: what MIPS budget exists, what the change freeze calendar is, who owns the copybooks, and what the batch window really is per LPAR |
| **2. Select the capture mechanism** | Candidates: IBM's own log-capture products, or a third-party CDC product with DB2 for z/OS log support. Selection criteria: MIPS overhead measured not quoted; delivery to object storage or Kafka; restart and gap-detection semantics; support for the LPAR topology; licence cost. **Selection and cost [TBC in Phase 0]** |
| **3. Decode once, in bronze** | EBCDIC, COMP-3, REDEFINES and OCCURS DEPENDING ON are handled by a version-controlled decoder driven by the copybook. The copybook version used is recorded per batch. **~15% of copybooks are stale — reconciling copybook to reality is a Phase 0 deliverable, not a Phase 1 surprise** |
| **4. Two-track by design** | Log-based CDC for the ~90 high-velocity tables; daily extract for the remaining ~250 and as the reconciling anchor for all of them |
| **5. Prove the anchor before trusting the stream** | Every day, for every CDC table, the batch anchor's row count and control totals are compared to the CDC-derived state. A divergence is a P2 incident. **This runs permanently, not only during migration** |
| **6. Never query DB2 directly from the lakehouse** | No federation, no JDBC pull against the production core. The mainframe team will refuse, and they are right to |
| **7. Plan for the change freeze** | Core release trains are 14 weeks. Any schema change we need on the mainframe side must be requested one train ahead. The programme plan carries these as fixed dates |

**Fallback if log-based CDC proves infeasible or too expensive in MIPS:** revert to enhanced batch
extracts at a higher frequency (for example, four times daily for the high-velocity tables), accept a
degraded latency for UC-2, and re-scope the intraday exposure case to a 4-hour cadence. **This fallback is
priced in Phase 0 so the decision is made with numbers.**

## 8.5 Dual-run and reconciliation

| Element | Detail |
|---|---|
| **Comparison mechanism** | A reconciliation job reads the lakehouse gold result and the legacy result — the latter live via **Lakehouse Federation** over Teradata, so no bulk copy is required — and produces a typed break record |
| **Tolerance** | **Zero on monetary values.** A difference is either explained and attributed (usually to a legacy defect) or it blocks cutover. "Within tolerance" is how a bank inherits a legacy error into a new platform |
| **Break taxonomy** | Every break is classified: `source_timing`, `source_defect`, `legacy_defect`, `new_logic_defect`, `rounding`, `scope_difference`, `hierarchy_version`. The taxonomy is fixed in week 8 and each class has a standard disposition path |
| **Granularity** | Reconcile at the **lowest published grain**, not at the total. Two errors that cancel at the total are two errors |
| **Duration** | Minimum **three consecutive reporting cycles clean** before cutover is proposed. For a quarterly return this means three quarters, which is a reason to pick a monthly return as the thin slice |
| **Evidence** | The break register is a published product (`reconciliation_results`), not a spreadsheet, and it feeds section 6 of the evidence pack |
| **When the legacy is wrong** | Expected, and it has happened on every programme of this type. A legacy defect found in dual-run goes to the reporting owner as a potential prior-period issue. **This must be flagged to the sponsor at kick-off**: finding legacy errors is a likely outcome and the bank needs a decided response before the first one appears, not after |

## 8.6 Decommission gates

| Gate | Target | Criteria | Approver |
|---|---|---|---|
| **G1** | First report cut over from Teradata | 3 clean cycles; evidence pack accepted; runbook and on-call in place; rollback tested | Head of Regulatory Reporting + Internal Audit |
| **G2** | Teradata risk mart retired | All consuming reports migrated (proven by lineage plus federated query log, not by asking); 11 years of submitted history archived and readable; 2 full reporting cycles with no fallback | Group CRO + CFO |
| **G3** | Hadoop landing zone retired | Every downstream consumer migrated or confirmed dead; no read activity for 90 days; data retained under obligation copied to a governed archive with retention set | Group CDO |
| **G4** | Informatica mappings in scope retired | Replacement pipelines in production for 2 cycles; mapping-to-pipeline coverage matrix signed | Head of Data Engineering |
| **G5** | Controlled spreadsheets retired | Each retired spreadsheet's control is replaced by an automated reconciliation with an owner; the end-user-computing register updated | Group Financial Controller + Operational Risk |

**Anti-pattern we refuse:** running the legacy "just in case" indefinitely. Each gate has a date. If a
gate slips, the cost of the extension is reported to the steering committee monthly so the decision to
extend is an economic one taken visibly.

## 8.7 What the bank must provide

| Item | Why | When needed |
|---|---|---|
| Cloud landing zone with the agreed region topology | Nothing starts without it | Week 1 |
| Mainframe Services engagement and a MIPS budget | The critical path | Week 1 |
| Copybook inventory with named owners | Decoding is impossible without it | Week 2 |
| Legal determination on entity-to-region mapping and CMK policy | Topology cannot be created twice | Week 3 |
| Named regulatory reporting owner for the thin slice, with attestation authority | The programme's purpose | Week 2 |
| Access to the incumbent's logic and its known defects | Dual-run is otherwise archaeology | Week 6 |
| Four-eyes approver capacity | Two approvers per domain, or deployment queues | Week 8 |
| Model Risk Management engagement for the fraud and credit models | Longest approval tail in the programme | Week 20 (Phase 4 starts week 55) |
| Vendor licence review for all market-data and reference feeds | Blocks any persistence of vendor data | Week 4 |
| Decisions on the eight open [TBC] items in §14.2 | Each blocks a design decision | Per the register |

---

# 9. Team, ways of working and enablement

## 9.1 Pod shape

| Role | Responsibility |
|---|---|
| Engagement lead | Commercials, steering, the difficult conversations |
| Solution architect | The decisions in §5, and defending them |
| Platform / DevOps engineer | Workspaces, bundles, CI/CD, networking, identity, cost controls |
| Governance engineer | Unity Catalog model, ABAC policies, governed tags, audit and lineage archive, evidence pack |
| Data engineers | Pipelines, per domain |
| Mainframe integration engineer | The DB2 extraction workstream. A specialist, not a generalist |
| Reconciliation / QA engineer | The break framework, test suites, dual-run |
| Analytics engineer | Gold models, metric views, BI enablement |
| ML engineer | Feature tables, model serving, inference evidence (from Phase 4) |
| Business analyst (regulatory) | Translates the return's rules into testable specifications |

## 9.2 FTE by phase (illustrative, consultancy side)

| Role | P0 | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|---|
| Engagement lead | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.3 |
| Solution architect | 1.0 | 1.0 | 0.8 | 1.0 | 0.8 | 0.4 |
| Platform / DevOps | 1.5 | 1.5 | 1.0 | 1.5 | 1.5 | 1.0 |
| Governance engineer | 0.5 | 1.0 | 1.5 | 1.5 | 1.0 | 0.8 |
| Data engineers | 1.0 | 4.0 | 4.0 | 8.0 | 6.0 | 3.0 |
| Mainframe integration | 1.5 | 1.5 | 1.0 | 1.0 | 0.5 | 0.3 |
| Reconciliation / QA | 0.5 | 2.0 | 3.0 | 3.0 | 2.0 | 2.0 |
| Analytics engineer | 0 | 1.0 | 1.0 | 3.0 | 2.0 | 1.0 |
| ML engineer | 0 | 0 | 0 | 1.0 | 3.0 | 1.0 |
| BA (regulatory) | 0.5 | 2.0 | 2.0 | 3.0 | 1.5 | 1.0 |
| **Total** | **7.0** | **14.5** | **14.8** | **23.5** | **18.8** | **10.8** |

## 9.3 Client roles required

| Client role | Commitment | Why it is non-negotiable |
|---|---|---|
| Programme sponsor (Group CDO) | 4 h/week | Unblocks cross-divisional disputes |
| Risk sponsor (Group CRO delegate) | 4 h/week | Without risk ownership, the attestation gate has no owner |
| Regulatory reporting SME | 0.8 FTE | The specification of every return |
| Mainframe Services lead | 0.5 FTE in P0–P1 | The critical path |
| Data stewards, one per domain | 0.3 FTE each | Contracts, classification, secure-by-default review |
| Compliance — MNPI and surveillance | 0.3 FTE | The barrier design and the wall-crossing process |
| Model Risk Management | 0.4 FTE from P3 | The fraud and credit approval path |
| Data Privacy Officer | 0.2 FTE | Retention schedule, erasure determinations, residency |
| Internal Audit liaison | 0.2 FTE | Reviews the evidence pack before an examiner does |
| Security architecture | 0.3 FTE | CMK, network, hardened profile |
| Four-eyes approvers | 2 per domain | Or deployments queue behind one person's calendar |

## 9.4 CI/CD with four-eyes and evidence

```
  feature branch ──► PR ──► review by a different identity ──► merge to main
        │                        │                                  │
        │                   automated checks                        │
        │              · unit tests (transformations)               │
        │              · expectation tests                          │
        │              · bitemporal boundary suite                  ▼
        │              · ABAC policy conflict check          CI deploys bundle
        │              · no-path-references static check     (service principal,
        │              · bundle validate                      workload identity
        │              · reconciliation regression            federation)
        │                                                           │
        └── dev target (mode: development) ◄───────────────────────┘
                   │
                   ▼
            test target ──► reconciliation gate ──► prod target (mode: production)
                                                      · development: false enforced
                                                      · git branch validated
                                                      · no cluster overrides
                                                      · run_as service principal
```

| Practice | Detail |
|---|---|
| One repository per domain | Pipelines, bundle config, contracts, tests and runbook together. Pipeline source files live alongside the bundle config in Git, which is the documented recommendation |
| Bundle targets | `dev`, `test`, `prod` with `mode: development` and `mode: production` doing the enforcement rather than a reviewer's memory |
| Deployment identity | Service principals for CI/CD, with workload identity federation so no Databricks secret is stored |
| Binding, not recreating | `bundle deployment bind` links a bundle resource to an existing workspace resource so it is updated rather than recreated — which matters because recreating a materialized view means recomputing it |
| Release evidence | `bundle validate` and `bundle plan` output archived per release, alongside the PR record |
| Engine | Direct deployment engine, which is GA. Note the behaviour change: **removing a set field from `databricks.yml` reverts the value to the resource default** (Terraform left it unchanged). This is called out in the engineering standard because it is a quiet way to lose a production setting |
| Rollback | Redeploy the prior tagged bundle version. For data, the recovery path is a documented reprocess from bronze, **not** a restore from time travel |

## 9.5 Testing and reconciliation gates

| Gate | What it tests | Blocks |
|---|---|---|
| Unit | Transformation functions on synthetic fixtures | Merge |
| Expectation | Pipeline expectations with `ON VIOLATION DROP ROW` to quarantine, or `FAIL UPDATE` for contract-breaking conditions such as a PAN-shaped value in the card stream | Pipeline run |
| **Bitemporal boundary suite** | Half-open interval correctness; no overlapping knowledge versions; no gaps; as-of reproducibility at the boundary timestamp; late-arriving correction produces a new version rather than an update | Merge. **Mandatory for every bitemporal entity** |
| ABAC conflict | That no principal can have two distinct row filters or two distinct column masks resolve on the same object — which the platform treats as an error and blocks access | Merge |
| Static | No path-based table references (they break column lineage); no hardcoded environment values; no PAT usage | Merge |
| Reconciliation regression | The break register for a fixed historical period must not grow | Promotion to prod |
| Dual-run | Zero monetary difference against the incumbent for three cycles | Cutover |
| Erasure | That a test subject's data is removed from bronze, propagated, purged and vacuumed, and that a `skipChangeCommits` streaming read behaves as designed | Quarterly |
| Restore | That a domain can be reprocessed from bronze within its stated RTO | Quarterly |

**Test data.** Production-like test data is a real problem in a bank. ABAC-protected tables cannot be
cloned, and shallow clones break when the source is vacuumed. The strategy is therefore: synthetic
generation for volume and edge cases, plus a governed, masked subset produced by an approved pipeline into
a separate test catalog with its own retention. **This is a Phase 0 design item, not an afterthought.**

## 9.6 Runbooks

| Runbook | Trigger |
|---|---|
| Mainframe extract failure or gap detected | Anchor mismatch, missing CDC sequence |
| Streaming lag beyond SLO | Consumer lag alert |
| Late-arriving data beyond the watermark | Side-output volume threshold |
| Reconciliation break | Any break, with the taxonomy driving the path |
| Erasure request | §7.4 |
| Wall-crossing request and expiry | Compliance request |
| MNPI access exception detected | Audit query alert. **Escalates to Compliance within 1 hour, not to engineering** |
| Vendor licence change | Market Data Services notification |
| Regulatory information request | Evidence pack generation |
| Emergency production change | Break-glass, with a 2-day post-hoc review |
| Cost anomaly | Budget threshold alert |
| Full refresh request | Requires named approval, because a full refresh of a streaming table discards all data and restarts from the beginning, and upstream retention may make that unrecoverable |

## 9.7 Enablement

| Track | Audience | Content |
|---|---|---|
| Platform foundations | ~60 engineers | Unity Catalog object model and security, Delta internals, medallion, ingestion routes. Mapped to the poster series at `D:\NBS_DataBricks_Data_Associate\MASTER_Databricks_Study_Series\` — posters 03, 04, 06–12, 13, 19 |
| Pipeline engineering | ~30 engineers | Lakeflow Spark Declarative Pipelines, AUTO CDC and SCD, streaming triggers, expectations, exactly-once. Posters 16–18, 37, 38, 41, 42, 45 |
| Regulated delivery | ~20 engineers and leads | Bundles, CI/CD, four-eyes, testing, deployment modes, observability. Posters 29, 30, 40, 46, 47 |
| Governance | ~25 stewards, Compliance, Privacy, Audit | ABAC, governed tags, masking, purging, lineage, audit, system tables. Posters 32, 44 |
| Analytics | ~80 analysts | Databricks SQL, dimensional models, metric views, the as-of query pattern. Posters 25, 43 |
| Cost ownership | ~15 owners and finance partners | DBU attribution, tagging, budgets, entity recharge. Poster 39 |
| Bitemporality masterclass | Everyone touching silver or gold | The four axes, the half-open interval, the failure modes. **Bespoke to this engagement — no poster covers it, and it is the single highest-value training in the programme** |

Delivery is pair-building during Phases 1–3 (the consultancy pairs with a named client engineer on every
story), not classroom-only. The target is that by the Phase 3 exit, client engineers author the majority
of new pipelines and the consultancy reviews.

---

# 10. Cost model and commercials

**No Databricks prices appear in this document.** Databricks pricing is contract-specific and changes;
quoting a rate in a business case is how a programme acquires a number it cannot defend. What follows is
the cost *structure*, the drivers, the control mechanisms, and an explicit statement of where each real
number must come from.

## 10.1 Cost drivers

| Driver | What moves it | Relative weight (illustrative) |
|---|---|---|
| **Streaming pipelines running continuously** | Number of always-on flows × their trigger cadence. Payments, cards, FIX, digital and market data are five always-on domains | High — typically the largest single line in a bank lakehouse |
| **Bitemporal silver merges** | Volume of change rows × SCD2 merge frequency. Core banking at ~41 m changed rows/day is the driver | High |
| **Lakeflow Connect ingestion gateways** | One per CDC'd database. **These run on classic compute in the workspace network, continuously, and bill even when the ingestion pipeline is idle** | Medium, and often missed in an estimate |
| **SQL warehouse concurrency** | Number of analysts × query pattern × warehouse sizing. Month-end and close spike hard | Medium-high, and the most controllable |
| **Market data ingest** | ~210 GB/day of conflated ticks. Conflation rate is the lever, and it is set upstream | Medium |
| **Model serving** | Endpoint provisioning and request volume; fraud scoring is high-volume | Medium |
| **Storage** | Bronze immutability plus bitemporal history: expect **1.6× – 2.4×** the current-state footprint | Low unit cost, high absolute volume |
| **Cloud infrastructure** | Object storage, network, private connectivity, and — for classic compute — VMs and disks billed by the cloud provider on top of DBUs. **Serverless runs in the Databricks-managed serverless compute plane with no compute resources in your cloud account**, so it is one invoice, not two | Medium |
| **Non-production** | Dev and test environments, especially if masked production-like data is generated | Low-medium, and routinely underestimated |
| **Enhanced security and compliance add-on** | If the compliance security profile is required | **[TBC]** — a real line item if the CISO requires it |

## 10.2 Cost control mechanisms

| Mechanism | Implementation | Documented behaviour to respect |
|---|---|---|
| **Tagging** | Minimum tag set on every taggable resource: `legal_entity`, `domain`, `environment`, `cost_centre`, `use_case`. Enforced on classic compute via `custom_tags.<name>` in a compute policy (`fixed` or `allowlist`) | Max 20 tags per workspace resource; keys colliding with default keys are prefixed `x_`; **never use the key `Name` on a cluster**; workspace tag changes take up to 1 hour; cluster and pool changes need a restart. **Pool-created clusters inherit only workspace and pool tags, not cluster tags** — a real attribution trap |
| **Serverless usage policies** | Auto-apply custom tags to serverless notebooks, jobs, pipelines, model serving and apps. Join key `usage_metadata.usage_policy_id` | **Public Preview.** One policy auto-applies; with several the user picks, and a scheduled notebook job falls back to the alphabetically first. A pipeline triggered by a job does not inherit the policy |
| **Budgets** | Per legal entity and per domain, with threshold alerts | Budgets are in **USD at list price including platform add-ons** — so a budget is a *usage signal*, not a contract-price forecast. Up to 4 shared thresholds; alerts can lag up to 24 hours. Unity Gateway budgets are near real-time, support per-user thresholds and can approximately block usage |
| **Attribution for internal recharge** | The documented temporal range join: `system.billing.usage` joined to `system.billing.list_prices` on `sku_name` and the price validity window, using `pricing.effective_list.default`, grouped by `custom_tags.legal_entity` | `usage_quantity` is DBUs; **there is no price column in `system.billing.usage`**. Usage data has ~12 h latency. `list_prices` is list, not contract price — **the recharge model must substitute SMB's contracted rate, which is a Procurement input** |
| **Recharge caveat** | Jobs cost attribution **excludes** SQL warehouses and all-purpose compute, because those are not billed as jobs | So warehouse cost is attributed by tag, and all-purpose compute is minimised by policy |
| **Compute policies** | Enforce autotermination, max workers, instance families and tags on classic compute | No compute policies and no init scripts on serverless — the environment spec is the only route there |
| **Serverless performance mode** | Standard rather than performance-optimised for non-latency-critical jobs | Documented: standard adds "4 to 6 minutes" of startup latency; **both modes use the same SKU, but standard consumes fewer DBUs**. Measured via `product_features.performance_target` |
| **Predictive optimization** | On for UC managed tables | Runs `OPTIMIZE`, `VACUUM` and `ANALYZE`; billed on a serverless jobs SKU; **does not run `ZORDER`** |
| **Overspend protection** | Serverless notebook execution timeout, default 2.5 hours (9,000 s), admin-configurable | GA |
| **Warehouse discipline** | Auto-stop, right-sized warehouses per workload class, separate warehouses for BI and for the close-window spike so one does not starve the other | Serverless starts in 2–6 seconds, so aggressive auto-stop costs nothing in user experience |

## 10.3 Cost transparency for a bank

Internal recharge by legal entity is a regulatory and tax matter in a group of this shape, not a
management convenience. Three requirements follow:

1. **Every DBU must be attributable to a legal entity.** Achieved by the tag set, enforced by policy on
   classic compute and by serverless usage policies on serverless — with the documented gaps (pool tag
   inheritance, pipeline-triggered-by-job policy inheritance) explicitly monitored by an exception query
   for untagged usage.
2. **The attribution must be reproducible for a prior period.** `system.billing.usage` retains 365 days;
   `list_prices` is retained indefinitely. Anything older than a year must be archived by a monthly job,
   like the audit archive.
3. **Shared platform cost must have a documented allocation basis.** Bronze ingestion serving all entities
   cannot be attributed to one. The basis (we recommend proportional to that entity's row volume in the
   shared bronze tables) must be agreed with Group Finance and Tax in Phase 1, because retrofitting it is
   a transfer-pricing conversation nobody wants.

## 10.4 Illustrative effort profile

Consultancy effort only; client effort is in §9.3. Figures are person-months.

| Phase | Person-months | Share |
|---|---|---|
| P0 Mobilise (6 wks) | ~10 | 6% |
| P1 Thin slice (16 wks) | ~54 | 30% |
| P2 Reconcile and attest (12 wks) | ~41 | 23% |
| P3 Domain build-out (36 wks, overlapping) | ~79 | — |
| P4 Real-time and decisioning (32 wks, overlapping) | ~50 | — |
| P5 Decommission (27 wks, overlapping) | ~27 | — |
| **Total (overlap-adjusted, ~104 weeks)** | **~190** | — |

The shape to note: **53% of effort lands in Phases 0–2**, producing one report. That is the correct shape
for a regulated programme and it is the number most likely to be challenged. The answer is that Phases 3–5
are fast *because* Phases 0–2 were slow: the framework, the bitemporal model, the reconciliation harness
and the evidence pack are built once.

## 10.5 Payback logic

| Step | Illustrative |
|---|---|
| Year-1 cost (platform + cloud + SI + internal) | USD 26 – 34 m |
| Year-1 benefit realised | USD 16 – 24 m (Q3 and Q4 only) |
| Year-2 cost | USD 19 – 25 m |
| Year-2 benefit | USD 58 – 95 m |
| Year-3 run cost | USD 11 – 16 m |
| Year-3 benefit including decommission | USD 103 – 175 m |
| **Cumulative breakeven** | **Month 14 – 20** |

**The three assumptions the whole case rests on, stated so they can be attacked:**

1. **Partial release of the data-uncertainty add-on.** Worth ~USD 11.5 m/yr at the midpoint. This is a
   supervisory judgement the bank does not control. **Model the case both with and without it.** Without
   it, breakeven moves to month 19–26 and the case still stands.
2. **Fraud loss reduction of 12–18%.** Depends on model approval and on operational adoption. If the
   model lands six months late, Year-2 benefit drops by ~USD 11 m.
3. **Decommission actually happens.** If Teradata runs for three more years "just in case", USD 14–19 m/yr
   of savings never arrive and the bank pays for two platforms. This is why §8.6 makes each gate a dated
   decision with a named approver.

## 10.6 Where the real numbers must come from

| Number | Source | Needed by |
|---|---|---|
| DBU rate per SKU | SMB's Databricks contract, via Procurement. **Do not use list price** | Week 4 |
| Cloud infrastructure rate | SMB's cloud enterprise agreement | Week 4 |
| Enhanced Security and Compliance add-on cost and availability | Databricks account team, once the CISO confirms whether it is required | Week 6 |
| Mainframe CDC product licence and MIPS cost | Phase 0 measurement, not a vendor quote | Week 6 |
| Teradata and Cloudera run cost and contract exit terms | SMB IT Finance and Vendor Management | Week 3 |
| Current regulatory reporting FTE cost | Head of Regulatory Reporting | Week 2 |
| Fraud loss baseline and false-positive cost | Head of Financial Crime | Week 3 |
| The add-on quantum and the supervisory dialogue on its release | Group CRO and Regulatory Affairs | Week 4 |
| Internal cost of equity for the capital carry calculation | Treasury | Week 3 |

---

# 11. Risks and mitigations

The ten that actually kill bank data programmes. Likelihood and impact on a 1–5 scale.

| # | Risk | L | I | Mitigation | Owner |
|---|---|---|---|---|---|
| **R1** | **Mainframe access and MIPS cost.** Mainframe Services cannot or will not provide log-level access; or CDC overhead exceeds the MIPS budget and the CFO refuses the uplift | 4 | 5 | Phase 0 exists for this. Measure actual MIPS with a candidate product before Phase 1 commits. Priced fallback to higher-frequency batch extracts with a re-scoped intraday case. Engage Mainframe Services as a named workstream owner, not a stakeholder. Escalation path agreed at kick-off | Mainframe Services lead + Solution architect |
| **R2** | **CDC on DB2 proves unreliable.** Gaps on LPAR failover, sequence loss on restart, silent drift between the change stream and reality | 4 | 4 | The daily batch anchor is permanent, not transitional: every CDC table is row-count and control-total reconciled daily. Divergence is a P2 incident with a defined runbook. Never attest a number that came only from the stream | Data engineering lead |
| **R3** | **Reconciliation fails and cutover slips.** Breaks cannot be explained; the legacy turns out to be wrong in ways nobody will own | 4 | 4 | Zero tolerance on monetary values with a fixed break taxonomy from week 8. Reconcile at the lowest grain. **Decide at kick-off what happens when the legacy is found to be wrong** — the first legacy defect must not be the first time that conversation happens. Escalation to the reporting owner, not to engineering | Reconciliation lead + Head of Regulatory Reporting |
| **R4** | **Regulator timing.** A supervisory visit, a new return, or a deadline on an existing finding lands mid-programme and consumes the team | 3 | 4 | Reserve 15% of Phase 2–3 capacity for regulatory interrupts. Keep the evidence pack generation working from Phase 2 so a request is a job run rather than a fire drill. Regulatory Affairs sits on the steering committee and gives early warning of the supervisory calendar | Programme sponsor + Regulatory Affairs |
| **R5** | **An MNPI incident.** Order flow or pre-announcement data becomes visible across the barrier, in the platform the programme just built | 2 | **5** | Structural separation (separate catalogs, separate metastore where the entity is in another region, no cross-barrier grant) rather than masking. ABAC policies at catalog level that table owners cannot remove. Secure-by-default control tag so a new schema is masked until reviewed. Daily cross-barrier audit query with a 1-hour escalation to Compliance. **Impact is 5 because the consequence is regulatory and personal, not financial** | Compliance (MNPI) + Governance engineer |
| **R6** | **Residency.** A jurisdiction's requirement turns out to be stricter than assumed after the topology is built | 3 | 4 | Legal determination in Phase 0, before any workspace exists. Region-per-metastore topology so an entity can be relocated without re-architecting. Confirm in writing with Databricks the residency behaviour for each region in scope. Design cross-border analysis as aggregate sharing from the outset, not as a later retrofit | Legal + DPO + Platform lead |
| **R7** | **Vendor data licensing.** A market-data contract prohibits the storage, derivation or redistribution the design assumes; discovered after build | 3 | 4 | Licence review of every feed in week 4, before persistence. `licence.class` governed tag on every vendor object with an ABAC GRANT policy blocking `no_redistribution` data from outbound shares. Prefer OpenSharing inbound where the vendor offers it, which removes the local-copy question. Renegotiation lead time is months — start early | Market Data Services + Legal |
| **R8** | **Model approval.** Model Risk Management does not approve the fraud or credit model, or approves it 6–9 months late | 4 | 3 | MRM engaged from week 20, nine months before the model needs approval. Feature lineage and inference tables designed as MRM evidence from the first line of code. Reproducibility of a decision from features as at the decision timestamp is a build requirement, not a documentation exercise. **Sequence UC-3 in Wave 2 so it is never on the critical path of the first credibility milestone** | Model Risk Management + ML engineer |
| **R9** | **Skills.** The bank has ~6–10 people who can write production Spark and none in a business domain; delivery becomes permanently consultancy-dependent | **5** | 3 | Pair-building on every story from Phase 1, not classroom training. Named client engineer per pod with a target of majority authorship by the Phase 3 exit. Enablement path mapped to the poster series (§9.7). Bespoke bitemporality masterclass. Retention risk is real in a hot market — **the bank should expect to re-hire and should budget for it** | Client engineering leadership + Engagement lead |
| **R10** | **Change fatigue.** Two years, six phases, five decommission gates, 185 reporting FTE whose work is changing. Adoption stalls and the legacy stays alive | 4 | 4 | Ship the thin slice in 16 weeks so there is a visible win early. Make each decommission gate a dated executive decision with the cost of extension reported monthly. Move reporting FTE into the new process as owners, not as displaced staff — the break register needs the people who currently know where the bodies are. Communicate the legacy-defect finding as expected and normal, so the first one does not become a scandal | Programme sponsor + COO |

### Risks we are not listing, and why

| Not listed | Why |
|---|---|
| "The platform doesn't scale" | It is not a credible risk at these volumes and listing it would be padding |
| "Cloud outage" | Real, but it is a standing operational risk with an existing bank-wide control, not a programme risk |
| "Data quality is poor" | It is certain, not a risk. It is a work item, sized in §3 |

---

# 12. Success metrics

## 12.1 Business KPIs

| KPI | Baseline (illustrative) | Target | When | How measured |
|---|---|---|---|---|
| Time to produce a regulatory return | 4 – 11 days | < 1 day | Phase 2 exit for slice 1 | Job run duration from upstream completion to submission snapshot |
| New report lead time | 9 months | < 10 weeks | Phase 3 exit | Ticket open to first production submission |
| Cost per supervisory information request | 200 – 600 person-hours | < 40 person-hours | Phase 2 exit | Timesheet against request id |
| Open findings relating to data lineage | 2 | 0 | Phase 3 exit | Supervisory correspondence |
| CET1 held against data uncertainty | ~USD 240 m | Partial release | Year 2–3 | Supervisory dialogue. **Outside the bank's unilateral control** |
| Gross fraud loss | ~USD 128 m/yr | −12% to −18% | 6 months post model live | Financial Crime loss ledger |
| Fraud alert false-positive ratio | 18:1 | < 12:1 | 6 months post model live | Case management dispositions |
| AML alert median age | 26 days | < 12 days | Phase 4 exit | Case management |
| Commercial onboarding median | 47 days | < 33 days | Phase 4 exit | CRM onboarding milestones |
| Group close | 11 working days | 6 – 7 | Phase 3 exit | Finance calendar |
| Intraday exposure availability | T+1 | 15 min | Phase 4 exit | Product freshness monitor |
| Analyst time on sourcing and reconciliation | ~62% | < 30% | Year 2 | Quarterly survey plus query-history analysis |
| Controlled spreadsheets in the regulatory path | ~1,900 | < 300 | Phase 5 exit | End-user-computing register |

## 12.2 Platform SLOs

| SLO | Target | Measured from |
|---|---|---|
| Core banking bronze freshness | 15 min, p95 | Pipeline event log vs source commit timestamp |
| Payments and cards stream lag | < 60 s, p99 | Structured Streaming progress metrics |
| FIX stream lag | < 30 s, p99 | Same |
| Market reference data loaded and validated | By 06:15 local, 99.5% of trading days | Job completion with a hard SLA alert |
| `position_eod_authoritative` published | By 06:00, 99.5% | Product freshness monitor |
| Regulatory extract job success | 99.9% first-run success | `system.lakeflow` job run tables |
| SQL warehouse p95 query latency, BI workload | < 8 s | `system.query.history` |
| Expectation pass rate, silver | > 99.7% | Pipeline event log `data_quality.expectations` |
| Reconciliation breaks per cycle, post-cutover | 0 monetary; < 5 non-monetary | `reconciliation_results` |
| Lineage coverage of regulatory gold columns | 100% | `system.access.column_lineage` vs the reported-field register |
| Untagged DBU usage | < 1% | `system.billing.usage` exception query |
| Cross-barrier access exceptions | 0 | Daily audit query, per region |
| Evidence pack generation time | < 4 h | Job duration |
| Recovery: reprocess a domain from bronze | Within stated RTO, proven quarterly | Restore test |

## 12.3 Leading indicators (the ones that predict failure early)

| Indicator | Warning threshold | Why it predicts failure |
|---|---|---|
| Break register growth rate in dual-run | Growing after week 4 of a cycle | Means the logic is not converging, and cutover will slip |
| Proportion of pipelines authored by client engineers | < 25% by Phase 3 midpoint | Predicts permanent consultancy dependency |
| Four-eyes approval turnaround | > 2 business days | Approver capacity is the bottleneck; deployments will queue and someone will ask for an exception |
| Quarantine table volume | Growing month on month | Upstream quality is degrading, or an expectation is miscalibrated. Either way it will surface at attestation |
| Untagged DBU usage | > 5% | Recharge will not be defensible, and cost ownership has not landed |
| Days since the last restore test | > 120 | The recovery path is theoretical |

---

# 13. What we would draw next

The diagrams this case needs, in the order they would be drawn.

| # | Diagram | One-line description |
|---|---|---|
| D1 | **Current-state estate** | Mainframe, Teradata, Hadoop, the reconciliation layer and the four consumer groups, with the spreadsheet layer drawn as the load-bearing wall it actually is |
| D2 | **Target logical architecture** | Sources → ingest mechanism → medallion → serving, with the ingestion mechanism labelled per source and the barrier drawn as a physical division of the canvas |
| D3 | **Source-to-pattern decision tree** | The chooser: managed connector → Lakeflow pipeline → Structured Streaming → federation → OpenSharing, with the decision criterion on each branch and the 14 sources placed on it |
| D4 | **Bitemporal data model** | The four time axes, a single entity shown with two effective versions and three knowledge versions, and the as-of query resolving to exactly one row |
| D5 | **The late-arriving correction sequence** | A payment reversal arriving on day 5: what bronze does, what the AUTO CDC flow does, what the as-of report returns before and after, and what the restatement disclosure is |
| D6 | **Unity Catalog topology** | Metastores per region, catalogs per environment × entity, schemas per domain × layer, with the markets catalog visually isolated and the grant arrows that do not cross it |
| D7 | **Information barrier enforcement** | Governed tags → ABAC policies → grants → audit, showing where a cross-barrier access is stopped and where it is detected |
| D8 | **Medallion contract per domain** | Six swimlanes (customer, payments, positions, risk, finance, market data) with the bronze/silver/gold contract stated in each |
| D9 | **The regulatory report pipeline** | One return, end to end, from four sources to a submission snapshot, with the two job parameters and the reconciliation branch shown |
| D10 | **Evidence pack assembly** | The ten sections of the pack and the system table or artefact each is generated from |
| D11 | **Erasure decision flow** | Request → classification → three buckets → delete / suppress / hold, with the `REORG`/`VACUUM` step and the `skipChangeCommits` streaming propagation drawn explicitly |
| D12 | **CI/CD with four-eyes** | Branch → PR → checks → bundle targets → production, with the evidence artefact emitted at each step |
| D13 | **Streaming vs batch map** | The 10 workloads plotted against true latency need and cost, showing why five are streaming and five are not |
| D14 | **Mainframe extraction two-track** | Log capture and batch anchor converging on bronze, with the daily reconciliation loop as a closed circuit |
| D15 | **Phase and gate timeline** | 104 weeks, six phases, five decommission gates, with the dual-run overlap and the model-approval tail shown as the two long poles |
| D16 | **Cost attribution chain** | Tag → usage → list price join → entity recharge, with the three documented attribution gaps marked as leaks to monitor |

---

# 14. Appendix

## 14.1 Glossary

### Banking and regulatory

| Term | Meaning |
|---|---|
| **APP scam** | Authorised push payment scam — the customer is deceived into authorising the payment themselves |
| **As-of reporting** | Producing a figure as it stood at a specified point in the bank's knowledge, not as it stands now |
| **Attestation** | A named officer's formal statement that a regulatory submission is accurate and complete |
| **Banking book / trading book** | The regulatory split between positions held to maturity and positions held for trading; different capital treatment |
| **Bitemporality** | Modelling both when a fact was true (effective time) and when the bank knew it (knowledge time) |
| **CET1** | Common Equity Tier 1 — the highest-quality regulatory capital |
| **CIF** | Customer Information File — the mainframe's customer master |
| **CSA** | Credit Support Annex — the collateral agreement attached to a derivatives master agreement |
| **EAD / LGD / PD** | Exposure at Default, Loss Given Default, Probability of Default — credit risk parameters |
| **FIX** | Financial Information eXchange — the standard messaging protocol for order and execution flow |
| **ICAAP** | The bank's internal assessment of the capital it needs |
| **Information barrier** | The control separating those who may hold MNPI from those who may not; historically "Chinese wall" |
| **ISO 8583** | The card transaction messaging standard used between switches and schemes |
| **ISO 20022** | The structured XML standard for payment messaging |
| **KYC / CDD** | Know Your Customer / Customer Due Diligence |
| **LEI** | Legal Entity Identifier — the global identifier for parties to financial transactions |
| **LPAR** | Logical Partition — an isolated instance on a mainframe |
| **MIPS** | Millions of Instructions Per Second — the mainframe capacity unit, and the unit mainframe cost is charged in |
| **MLRO** | Money Laundering Reporting Officer |
| **MNPI** | Material Non-Public Information |
| **Netting set** | A group of trades that may be offset against each other under a master agreement |
| **OMS / EMS** | Order Management System / Execution Management System |
| **PEP** | Politically Exposed Person |
| **PCI** | The payment card industry data security standard; PAN is the primary account number it protects |
| **Prudential add-on** | Additional capital a supervisor requires a bank to hold, sometimes for data-quality uncertainty |
| **Restatement** | Revising a previously reported figure after new information |
| **RWA** | Risk-Weighted Assets — the denominator of the capital ratio |
| **Surveillance** | Monitoring trading and communications for market abuse |
| **Wall-crossing** | Formally bringing a person inside an information barrier for a specific purpose and period |

### Platform

| Term | Meaning |
|---|---|
| **ABAC** | Attribute-Based Access Control in Unity Catalog — policies matching on governed tags via `has_tag()` / `has_tag_value()`, attachable at catalog, schema or table (metastore attachment is Beta) |
| **AUTO CDC flow** | The Lakeflow Spark Declarative Pipelines construct that applies change data to a target, including SCD Type 1 and Type 2 (`STORED AS BITEMPORAL` is Beta). `SEQUENCE BY` is required |
| **Auto Loader** | Incremental file ingestion with exactly-once file tracking in RocksDB within the checkpoint; directory listing or file-notification detection |
| **Declarative Automation Bundles** | The Databricks infrastructure-as-code format for jobs, pipelines and resources, with `development` and `production` deployment modes |
| **Deletion vectors** | Delta feature that marks rows deleted in metadata rather than rewriting files; requires `REORG … APPLY (PURGE)` then `VACUUM` for physical removal |
| **Governed tag** | An account-level tag with its own access controls, used by ABAC policies. Inherits from catalog and schema to table; **column tags do not inherit** |
| **Lakeflow Connect** | Managed connectors producing UC-governed ingestion pipelines on serverless compute; database CDC connectors cover MySQL, PostgreSQL, SQL Server and Oracle |
| **Lakeflow Jobs** | Databricks orchestration — tasks, dependencies, triggers, parameters |
| **Lakeflow Spark Declarative Pipelines** | The declarative pipeline framework: flows, streaming tables, materialized views, sinks, expectations |
| **Lakehouse Federation** | Read-only governed access to external systems via UC foreign catalogs with query pushdown; nothing is copied |
| **Liquid clustering** | Delta data-layout technique that adapts clustering keys without repartitioning |
| **Metric view** | A UC securable defining measures and dimensions once; measures are evaluated with `MEASURE()` |
| **OpenSharing** | The open protocol for zero-copy data sharing, formerly Delta Sharing; no egress cost within a region |
| **Predictive optimization** | Automatic `OPTIMIZE`, `VACUUM` and `ANALYZE` on UC managed tables; does not run `ZORDER` |
| **Streaming table** | An append-only incrementally-maintained table; the only valid target of an AUTO CDC flow |
| **System tables** | Read-only operational tables in the `system` catalog: billing, audit, lineage, jobs, query history. Most retain 365 days |
| **Unity Catalog** | The governance layer: catalogs, schemas, tables, volumes, models, functions, grants, tags, lineage, audit |
| **Zerobus Ingest** | A push-based API writing directly into UC Delta tables with no message bus |

## 14.2 Assumptions register

Every assumption that, if wrong, changes a design decision or a number.

| # | Assumption | If wrong | Owner | Status |
|---|---|---|---|---|
| A1 | Log-based CDC from DB2 for z/OS is technically and commercially feasible within the MIPS budget | Intraday cases re-scoped to a 4-hour cadence; UC-2 value falls by ~40% | Mainframe Services | **Open — Phase 0** |
| A2 | `STORED AS BITEMPORAL` (Beta) is usable for the GL hierarchy and collateral agreements | Fall back to explicit four-column bitemporal model maintained by MERGE; adds ~4 person-months | Solution architect | **Open — Phase 0** |
| A3 | CMK is required; scope (managed services vs workspace storage) to be confirmed | Changes workspace provisioning and possibly tier | CISO | **Open** |
| A4 | The Enhanced Security and Compliance add-on / compliance security profile is required, and is available in all in-scope regions | Cost and region availability change; PCI-adjacent workloads may need re-siting | CISO + Databricks account team | **Open** |
| A5 | Entity-to-region mapping satisfies every residency obligation | Topology rebuild; potentially an additional metastore and workspace set | Legal + DPO | **Open — week 3** |
| A6 | Market-data and reference licences permit the storage and derivation the design assumes | Some feeds become federation-only or must be re-negotiated; client reporting via OpenSharing may be blocked | Market Data Services + Legal | **Open — week 4** |
| A7 | Zerobus Ingest is suitable for the digital event volume (~310 m events/day) and available in the target regions | Remain on Kafka; no design change, only a cost difference | Platform lead | **Open — Phase 0 evaluation** |
| A8 | A clean incumbent output exists to dual-run the chosen thin-slice return against | Thin slice changes; selection criteria in §8.3 re-applied | Head of Regulatory Reporting | **Open — week 2** |
| A9 | The supervisor will engage on partial release of the data-uncertainty add-on once lineage and reconciliation evidence exists | Payback moves to month 19–26; the case still stands | Group CRO + Regulatory Affairs | **Open** |
| A10 | ~15% stale copybooks is the true figure | Phase 0 extends; decoding effort scales roughly linearly with the stale proportion | Mainframe Services | **Open — week 2** |
| A11 | Four-eyes approver capacity of two per domain is available | Deployment throughput drops; exceptions get requested; SoD evidence degrades | Domain owners | **Open — week 8** |
| A12 | System table retention (365 days, one year for lineage) is insufficient and an archive is required | If a jurisdiction accepts 365 days, the archive job is simpler. **We assume it does not** | Group Compliance | Assumed, low risk |
| A13 | Bitemporal storage multiplier is 1.6× – 2.4× | Storage cost line moves; not material to payback | Solution architect | Assumed |
| A14 | The bank has ~6–10 production-Spark-capable engineers | Enablement plan and consultancy ramp change materially | Client engineering leadership | **Open — week 2** |
| A15 | Teradata and Cloudera contracts can be exited on the Phase 5 timeline | Decommission savings delay; the USD 14–19 m/yr benefit shifts right | Vendor Management | **Open — week 3** |
| A16 | Model Risk Management can approve a fraud model within 9 months of first engagement | UC-3 benefit shifts right by the difference; sequencing in Wave 2 absorbs some of it | Model Risk Management | **Open** |
| A17 | All regulatory-path data can live inside Unity Catalog with no path-based access | Lineage coverage gaps appear; some attestation claims weaken | Platform lead | Assumed, enforced in CI |
| A18 | Cross-region OpenSharing egress cost is acceptable for the entity topology chosen | Cross-region sharing patterns re-designed toward regional aggregation | Platform lead + IT Finance | **Open — [TBC in cloud cost model]** |

## 14.3 Open items flagged "to be confirmed"

| Item | Section | Why it is not asserted here |
|---|---|---|
| Mainframe CDC product, its MIPS overhead and its licence cost | §3.2, §8.4 | Must be measured, not quoted |
| Retention periods per jurisdiction for every data class | §3 (all), §7.2 | These are legal determinations per entity, not facts we can supply |
| Residency requirements per country, and Databricks' residency behaviour per region | §3.2, §5.8, §7.10 | Only two residency statements are documented (audit logs are regional; identity data is stored in the US and in each workspace's region). Anything beyond that must be confirmed in writing |
| Whether the compliance security profile is required, in which workspaces, at what cost, in which regions | §5.8 | Contract and CISO decision |
| CMK scope and whether workspace-storage CMK is needed given a serverless-first design | §5.8 | CISO decision |
| Zerobus Ingest fit, throughput at 310 m events/day, and regional availability | §3.13, §5.2 | Documented as a capability; not benchmarked at this volume |
| Whether the identity provider can enforce time-boxed group membership for wall-crossings | §5.6.2 | IAM capability question |
| Whether federated queries appear in Unity Catalog lineage | §7.1 | Not documented. This is why federation is excluded from attested paths |
| Lakeflow Connect per-connector release states (GA / Preview / Beta) and region availability | §5.2 | The docs state only that connectors are "in various release states"; the specific state must be confirmed with the account team per connector |
| Cross-region OpenSharing egress charges | §5.2, §14.2 A18 | Cloud-provider dependent |
| All Databricks pricing | §10 | Contract-specific. Procurement input |
| Vendor market-data licence terms per feed | §3.7, §3.14, §7.6 | Contractual, and they differ per feed |
| Specific regulatory rule references and their exact requirements | Throughout | Deliberately generic. The client's own regulatory interpretation governs |

---

## Document control

| Field | Value |
|---|---|
| Version | 1.0 |
| Series | Design Patterns — Deep-Dive Business Cases |
| Companion | `01_Global_Omnichannel_Retail_Lakehouse.md` (retail sector) |
| Capability sources | `D:\NBS_DataBricks_Data_Associate\MASTER_Databricks_Study_Series\` posters 13, 25, 32, 35, 39, 42, 43, 44, 46 and their `*_SOURCES.md` |
| Intended use | Consulting business case template and solution-design teaching material |
| Nature | **Fictional composite. All figures illustrative.** |
