# Meridian Retail Group — Global Omnichannel Lakehouse

**Deep-dive business case · Case 01 of the Lakehouse Design Pattern series**
Prepared for: Group Executive Committee and the Data & Technology leadership team
Version 1.0 · Status: for decision

---

> ## Illustrative case — please read first
>
> **Meridian Retail Group is fictional.** It is a composite drawn from engagements with large grocery, general-merchandise and own-brand CPG organisations. **Every number in this document — revenue, volumes, timelines, benefits, effort and cost — is illustrative** and exists to make the reasoning concrete and the arithmetic checkable. Nothing here is a quotation, a commitment or a statement of any real client's estate.
>
> **No Databricks list prices appear in this document.** Commercials are expressed as *drivers, ratios and ranges*. Any real estimate must be built from the client's own workload profile and the current Databricks and cloud price lists at the time of the proposal.
>
> Where a platform behaviour or limit is material to the design and has not been re-verified against the current documentation, it is marked **[TBC against current docs]**.

---

## How to read this document

This case is written for two readers at once. They should not read all of it.

| If you are… | Read | Skip |
|---|---|---|
| **The executive sponsor** (CEO, CFO, COO, CDO) | §1 Executive summary, §4 Use cases and value, §8 Delivery plan, §10 Cost model, §11 Risks, §12 Success metrics | §3, §5, §6, §7 detail |
| **The delivery architect / lead engineer** | §2 Current state, §3 Data inventory, §5 Target architecture, §6 Data products, §7 Governance, §9 Team and ways of working, §13 Diagrams | §1 and §10 headline framing (useful context, not instruction) |
| **The programme director / PMO** | §8, §9, §10, §11, §12 | §3, §5 |
| **Security, Legal, DPO** | §3 (classification columns), §7 in full, §11 | §4, §10 |

Two conventions run through the document:

1. **Executive sections contain no platform jargon.** Where a product name is unavoidable in an executive section it is glossed in §14. Architect sections are deliberately specific — a solution architect should be able to open §3 and §5 and start building without a further discovery cycle.
2. **Every architectural choice is written as a DECISION**, with the alternative that was rejected and the reason. A decision without a rejected alternative is not a decision; it is a preference. Challenge them: they are the point of the document.

This case is the first in a series. The flow diagrams listed in §13 will be drawn from it, so the naming, the zone boundaries and the per-source ingestion choices in §3 and §5 are written to be drawn literally.

---

## 1. Executive summary

### 1.1 The business problem, in five bullets

1. **Meridian cannot see its own customer.** A loyalty member who buys in a Lisbon store, browses on the app in Madrid and returns an item through the German call centre is three unrelated records. 40 million loyalty members are managed as 9 disconnected regional lists.
2. **Stock is in the wrong places.** Replenishment runs on a weekly, country-level forecast produced from data that is between 24 hours and 6 days old. On-shelf availability sits around 94.1% against a 97.0% sector benchmark; the gap is worth an estimated $160–265m of lost sales a year.
3. **The close takes nine days and the answer is contested.** Finance, Commercial and Supply Chain each reconcile from a different extract. Month-end consumes roughly 14 FTE of manual reconciliation and the Board sees trading numbers when they are already history.
4. **The platform is out of road.** The central warehouse runs at 91% of capacity, the overnight batch frequently lands after the 07:00 business deadline, and the analytics cluster is two major versions behind support. Growth in e-commerce and own-brand manufacturing has nowhere to go.
5. **The data team is firefighting, not building.** Approximately 70% of the 48-person data engineering capacity is consumed by incident response, re-runs and manual reconciliation. The BI backlog stands at 340 requests with a median age of 11 months.

### 1.2 The proposed outcome

A single governed data platform — a **lakehouse** — that holds Meridian's trading, customer, supply chain and finance data once, in one shape, with one set of access rules, and serves it to every consumer: dashboards, forecasting models, the replenishment engine, the app, suppliers and auditors.

The programme replaces the central warehouse and the ageing analytics cluster over 24 months using a **strangler** approach — new consumers are pointed at the new platform first, the old systems are drained rather than lifted, and each decommission is gated on a proven reconciliation. Nothing is switched off on faith.

### 1.3 Headline benefits — order of magnitude

These are **illustrative ranges**, expressed as annual run-rate at steady state (end of Year 3), with the assumption that drives each one. §4 carries the full working. They are a case for doing the work, not a business plan: each must be re-based on Meridian's own actuals in Phase 0.

| Value driver | Mechanism | Annual run-rate (illustrative) | Confidence |
|---|---|---|---|
| Inventory reduction | Daily SKU/store forecast replaces weekly country forecast; safety stock re-cut | $50–75m P&L (on $270–410m working capital release) | Medium-high |
| On-shelf availability | Real-time inventory position and exception-driven replenishment | $45–75m gross margin | Medium |
| Markdown optimisation | Price and markdown decisions on daily elasticity rather than calendar rules | $55–110m gross margin | Medium |
| Personalisation and loyalty | Unified customer view drives offer targeting across 9 e-commerce markets | $25–45m gross margin | Medium-low |
| Supplier performance recovery | OTIF and quality claims evidenced from shared, agreed data | $15–30m | Medium-high |
| Waste and shrink (cold chain) | Sensor-driven intervention before an excursion becomes a write-off | $10–20m | Medium |
| Finance close and reporting effort | 9-day close to 4-day close; reconciliation automated | $6–9m cost, plus decision speed | High |
| Legacy run-cost avoidance | Warehouse and cluster decommission; licence and hardware exit | $9–14m | High |
| **Indicative total** | | **$215–378m** | |

**Programme investment (illustrative):** $28–42m across 24 months, including services, platform consumption, dual-run and client-side backfill. Payback on the *credible lower half* of the benefit range falls inside Year 2. The logic is in §10.6.

### 1.4 Timeline

| Phase | Weeks | What the business gets |
|---|---|---|
| 0 — Mobilise and prove | 1–6 | Foundations live; access, security and network resolved; benefits re-based on actuals |
| 1 — Thin slice | 7–16 | **First value at week 10**: daily store-level sales and stock position for one region, with a governed dashboard replacing four spreadsheets |
| 2 — Core domains | 17–40 | Customer 360, unified sales, inventory and product; forecasting in pilot |
| 3 — Scale and migrate | 41–72 | All 14 countries; warehouse consumers migrated; dual-run and reconciliation |
| 4 — Decommission and hand over | 73–96 | Legacy warehouse and cluster off; client team running the platform |

### 1.5 The ask

| # | Decision requested | By |
|---|---|---|
| 1 | Approve Phase 0 and Phase 1 (weeks 1–16) at an illustrative **$3.4–4.3m** of services plus platform consumption, with a formal gate at week 16 before Phase 2 is committed. | ExCo |
| 2 | Name a single accountable **executive sponsor** with authority across Commercial, Supply Chain, Finance and IT. A steering committee is not a sponsor. | CEO |
| 3 | Mandate **SAP data access** for the programme, including the basis team's time. This is the single most common cause of delay in this class of programme (§11, R2). | CFO / CIO |
| 4 | Start the **network and connectivity work in week 1** (private connectivity, firewall rules, identity federation). Lead times here, not engineering, set the critical path (§11, R8). | CIO |
| 5 | Accept the **decommission gates in §8.6** as binding — including the commitment that the legacy warehouse is switched off, not left running "just in case". The benefit case depends on it. | CFO |

---

## 2. Current state

### 2.1 The estate

| Layer | System | Scale | Condition |
|---|---|---|---|
| Central warehouse | On-premises MPP appliance (Teradata-class) | 480 TB, ~11,000 tables, ~2,900 registered reports | 91% capacity; next hardware refresh due in 14 months; support renewal in 9 |
| Analytics cluster | Hadoop (CDH-lineage), 120 nodes, HDFS + Hive + Spark 2.x | 2.1 PB raw, ~60% cold | Two major versions behind support; no clear upgrade path; 3 of 5 original engineers have left |
| ETL | Legacy graphical ETL tool | 43 point-to-point job streams, ~2,700 individual jobs | No version control on 60% of jobs; change lead time 6–8 weeks |
| ERP | SAP ECC 6.0, single global instance, 3 company-code groups | ~8,500 active tables; finance, inventory, procurement, own-brand production | Stable; heavily customised; the extraction conversation is political |
| CRM | Salesforce (Sales + Service Cloud) — B2B wholesale and franchise | ~4.2m records | Well run; API limits are the constraint |
| POS | Three regional POS platforms (EU, APAC, Americas) | 2,400 stores | Different schemas, different close-of-day timing, different offline behaviour |
| Digital | Homegrown clickstream pipeline, Kafka to HDFS | ~360m events/day | Built by a team that no longer exists; no schema registry discipline |
| Last mile | Excel and Google Sheets | ~1,400 "critical" spreadsheets identified in a 2025 audit | This is where most decisions are actually made |

### 2.2 The pain, in business terms

**Month-end close takes nine working days.** Days 1–4 are spent waiting for the overnight batch to produce a clean trial position; days 5–7 are reconciliation between the warehouse, SAP and the regional POS totals; days 8–9 are commentary. Roughly 14 FTE across Group and regional finance are consumed each month, and the Board's trading review discusses a month that closed nine days ago.

**Stock-outs are structural, not incidental.** Replenishment proposals are generated weekly from a country-level forecast. A store that sells out on a Tuesday is not corrected until the following Monday's run. Measured on-shelf availability is 94.1%; the top-500 SKUs sit at 96.3% and the long tail at 91.8%. Commercial estimates — and the programme should validate — that closing half the gap to the 97.0% benchmark is worth 0.6–1.0% of store revenue.

**There is no single customer view.** Loyalty is administered per country. A member's e-commerce identity is an email address; their store identity is a card number; their service identity is a Salesforce contact. Match rates between the three are unknown because nobody has ever computed them. Marketing spends an estimated $18–24m a year on audiences it cannot deduplicate.

**The data team spends 70% of its time firefighting.** The 48-person team logged 1,190 production incidents in the last 12 months. The top three causes are upstream schema changes arriving without notice, late-arriving POS files from stores with poor connectivity, and batch windows overrunning into business hours. None of these are hard problems; they are unmanaged ones.

**Everything important ends in a spreadsheet.** The trading pack, the markdown decision, the supplier scorecard and the availability review are all assembled by hand. The numbers in them do not always agree, and no two are assembled the same way twice.

### 2.3 The pain, in engineering terms

| Symptom | What it actually means | Consequence |
|---|---|---|
| **No lineage** | Nobody can answer "what feeds this number" without reading ETL job definitions by hand | Impact analysis for any change takes 2–3 weeks; most changes are therefore not made |
| **No tests** | Fewer than 5% of pipelines have any automated data assertion; none have unit tests | Defects are found by business users, in production, at month-end |
| **Overnight batch only** | Every pipeline is a nightly full or delta extract; the window is 22:00–06:30 and frequently breaches | No use case needing data more recent than yesterday can be built at all |
| **Cost opacity** | On-premises capital cost is not attributed to workload; the Hadoop cluster has no chargeback | No one can say what any report costs, so nothing is ever retired |
| **Point-to-point sprawl** | 43 job streams connect ~19 systems directly to ~11 consumers | Every new consumer adds N new integrations, not one |
| **No environment discipline** | Two environments (dev, prod); dev has 4% of prod data and a different schema on 200+ tables | "It worked in dev" is not evidence of anything |
| **Schema drift is unmanaged** | Source changes arrive as overnight failures | ~11 incidents/month, each 2–6 hours to triage |
| **No reprocessing capability** | Fixing a bad day means a manual, hand-written backfill script | Corrections take days and sometimes introduce new errors |

### 2.4 What is genuinely good, and must be preserved

Not everything must be replaced. The programme explicitly protects three things:

- **The SAP finance chart of accounts and the company-code hierarchy.** These are correct, governed and auditable. The lakehouse conforms to them; it does not reinvent them.
- **The Salesforce B2B process.** The wholesale team's way of working is effective. The platform reads Salesforce; it does not attempt to re-platform it.
- **The store-level merchandising hierarchy** maintained in the PIM. It is imperfect, but it is the one dimension the whole business already agrees on. It becomes the conformed product dimension.

---

## 3. The data inventory

This is the section the delivery architect builds from. Each source is characterised with the same attribute set so that the ingestion map (§13, diagram 2) can be drawn directly from it.

**Reading the tables.** *Change rate* is the volume of new or changed records per period, not the total. *Latency requirement* is the **business** requirement, established with the consuming use case — not the technically achievable figure. *Ingestion pattern* is the decision, justified in §5.3.

Classification key: **P0** = no personal data · **P1** = internal, no personal data, commercially sensitive · **P2** = personal data (GDPR Art. 4) · **P3** = special category or payment data.

### 3.0 Inventory at a glance

| # | Source | Domain | Landing volume/day | Latency need | Class | Ingestion pattern |
|---|---|---|---|---|---|---|
| 1 | SAP ECC | Finance, Inventory, Procurement, Production | ~45 GB | 4 h (inventory), daily (finance) | P1/P2 | CDC via managed database connector + gateway |
| 2 | Salesforce | B2B wholesale, franchise, service | ~1.5 GB | 1 h | P2 | Lakeflow Connect managed SaaS connector |
| 3 | POS (3 platforms) | Sales transactions | ~12 GB | 15 min (two regions), 4 h (one) | P2/P3 | Auto Loader on landing volumes; Kafka streaming for one region |
| 4 | E-commerce clickstream | Digital | ~90 GB compressed | 1–5 min | P2 | Structured Streaming from Kafka |
| 5 | Product / PIM | Product | ~0.4 GB | 1 h | P0 | Lakeflow Connect database connector |
| 6 | Supply-chain EDI | Supply chain | ~2 GB | 30 min | P1 | Auto Loader on SFTP-landed files |
| 7 | IoT — DC and cold chain | Supply chain, Quality | ~8 GB | 1 min (alerting) | P0 | Streaming ingest (Kafka / direct push) |
| 8 | Marketing platforms (6) | Marketing | ~3 GB | Daily (hourly for suppression) | P2 | Lakeflow Connect where available; Auto Loader otherwise |
| 9 | Third-party market data | Commercial | ~1 GB | Weekly / daily | P1 | OpenSharing where supported; COPY INTO otherwise |
| 10 | HR (Workday) | People | ~0.1 GB | Daily | P2/P3 | Lakeflow Connect managed SaaS connector |
| 11 | Legacy EDW | All (historical) | One-off, plus daily delta during dual-run | Daily | P1/P2 | Lakehouse Federation for read; bulk export for history |
| 12 | Reference and finance master | Finance, Reference | <0.1 GB | Daily | P0 | COPY INTO from a governed volume |

Steady-state landing is therefore **~165 GB/day compressed**, or roughly **60 TB/year** of bronze growth before history migration. History migration adds an estimated **190 TB** (the EDW subset worth keeping, plus 5 years of POS and 3 years of clickstream from the Hadoop cluster). Sizing for the first three years should assume **~500 TB** of managed storage under a retention policy, not the 2.6 PB that exists today — a substantial part of the Hadoop estate is duplicate and expired data that should be left behind, not migrated. That triage is a Phase 0 deliverable.

---

### 3.1 SAP ECC — Finance, Inventory, Procurement, Own-brand Production

| Attribute | Detail |
|---|---|
| **Business domain** | Finance (GL, AP, AR), Inventory and stock movements, Procurement, Production orders |
| **What it holds** | ~8,500 active tables; **~350 in scope**. Core: BKPF/BSEG (documents), MARA/MARC/MBEW (material master and valuation), MSEG/MKPF (movements), EKKO/EKPO (purchasing), AUFK/AFKO (production orders), plus the company-code and profit-centre hierarchies |
| **Format / protocol** | Oracle-backed SAP ECC, on-premises. Extraction candidates: log-based CDC from the underlying database, SAP-native extractors (ODP/SLT), or a batch table export |
| **Volume** | ~60 TB in the underlying database; in-scope subset ~14 TB |
| **Change rate** | ~40m changed rows/day, concentrated in MSEG/MKPF (stock movements, ~26m/day) and BSEG (~6m/day). Month-end multiplies finance volumes by ~4x for two days |
| **Latency requirement** | **Inventory movements: 4 hours** (drives availability and replenishment). **Finance: daily, by 06:00 local** (drives the close). Master data: daily |
| **Quality issues** | Heavy custom fields (Z-fields) with no documentation; three company-code groups use different posting conventions; MBEW valuation is restated retrospectively at period close, so "yesterday's" figure can change; deleted-flag semantics differ by module |
| **PII / regulatory** | **P1** mostly. **P2** in vendor and employee-linked records (HR postings, expense). Finance data is in scope for statutory audit and SOX-equivalent controls |
| **Ingestion pattern** | **Log-based CDC through a managed database connector** (ingestion gateway plus ingestion pipeline, landing into streaming tables). See DECISION D-03 |
| **Risks** | The SAP basis team owns the decision and has historically resisted log-based CDC on the production database. Mitigation and escalation path in §11, R2. Licensing implications of third-party extraction **[TBC with the client's SAP account team]** |

### 3.2 Salesforce — B2B wholesale, franchise and service

| Attribute | Detail |
|---|---|
| **Business domain** | B2B wholesale accounts, franchise partners, service cases |
| **What it holds** | ~4,200 wholesale accounts, ~19,000 contacts, ~230k opportunities (lifetime), ~1.4m service cases, plus custom objects for franchise agreements |
| **Format / protocol** | Salesforce REST/Bulk API, via a managed connector |
| **Volume** | ~4.2m records total; ~1.5 GB/day of change payload |
| **Change rate** | ~180k record changes/day; spikes around quarter-end |
| **Latency requirement** | **1 hour** for service cases (feeds the supplier and customer-issue view); daily is sufficient for accounts and opportunities |
| **Quality issues** | Free-text account naming; duplicate accounts across country orgs (estimated 6–9%); the franchise custom object is maintained by hand |
| **PII / regulatory** | **P2** — named contacts, email, phone, business address. GDPR applies |
| **Ingestion pattern** | **Lakeflow Connect managed SaaS connector** into Unity Catalog streaming tables. See §5.3, row "Salesforce" |
| **Risks** | The API call budget is shared with three other integrations. Incremental behaviour depends on source-side change tracking; confirm per-object coverage **[TBC against current connector docs]** |

### 3.3 Point of Sale — three regional platforms

| Attribute | Detail |
|---|---|
| **Business domain** | Sales transactions, tender, promotions applied, loyalty card capture |
| **What it holds** | Basket header and line, tender line, promotion line, void/refund, till and operator reference. ~4.0m baskets/day, ~23m line items/day across 2,400 stores |
| **Format / protocol** | **EU (1,050 stores):** close-of-day compressed JSON pushed to object storage, one file per store per day, plus intraday partial files every 15 min. **Americas (780 stores):** near-real-time publish to a managed Kafka topic. **APAC (570 stores):** nightly fixed-width flat files via SFTP |
| **Volume** | ~12 GB/day compressed; ~4.4 TB/year. Peak trading (late December) is ~2.4x |
| **Change rate** | Append-only, but **late arrivals are routine**: ~1.5% of store-days arrive 1–3 days late (connectivity); a further ~0.2% arrive as corrections up to 14 days later |
| **Latency requirement** | **15 minutes** for the Americas and EU intraday feeds (real-time availability, fraud); **4 hours** post-close for APAC. Trading dashboards need the prior day complete by **06:00 local** |
| **Quality issues** | Three schemas and three basket-identity schemes; store clocks drift (observed up to 40 minutes); the EU platform re-sends a whole day's file when a single line is corrected, so **idempotency is mandatory**; tender detail is masked inconsistently across regions |
| **PII / regulatory** | **P2** (loyalty card number links to an identified person). **P3** where truncated PAN or tender tokens are present — these must be dropped or tokenised at the boundary and must never land in bronze in the clear. PCI scope must be actively kept *out* of the lakehouse |
| **Ingestion pattern** | **Auto Loader with file-event notification** on a Unity Catalog external location for EU and APAC; **Structured Streaming from Kafka** for the Americas. Idempotency on basket business key plus source file identity. See §5.3, rows "POS" |
| **Risks** | The three-schema problem is the largest single silver-layer modelling effort in the programme. Budget a dedicated conforming workstream, not a mapping spreadsheet |

### 3.4 E-commerce clickstream

| Attribute | Detail |
|---|---|
| **Business domain** | Digital experience, personalisation, merchandising analytics, attribution |
| **What it holds** | Page view, product view, search, add-to-basket, checkout step, order confirmation, app screen events, plus a consent event stream. 9 e-commerce markets |
| **Format / protocol** | JSON over **Kafka** (self-managed, three clusters, one per cloud region), ~40 topics, no enforced schema registry today |
| **Volume** | ~360m events/day; ~14.3m sessions/day; ~430 GB/day raw, ~90 GB/day compressed. Sustained ~4,200 events/sec, peak ~22,000/sec, Black Friday ~3x peak |
| **Change rate** | Append-only. Event schemas change 2–4 times a month per squad, unannounced |
| **Latency requirement** | **1–5 minutes** for personalisation and on-site merchandising; **1 hour** for trading dashboards; daily for attribution modelling |
| **Quality issues** | No schema registry, so malformed payloads are common; bot traffic is ~19% of events and is not flagged; session stitching across devices is unreliable; consent state is captured on a *separate* topic and must be joined before any personal use |
| **PII / regulatory** | **P2** — device ID, IP address, hashed email, logged-in customer ID. GDPR and ePrivacy apply; **consent state governs downstream use**, which is an architectural constraint, not a policy note |
| **Ingestion pattern** | **Structured Streaming from Kafka into a bronze streaming table**, schema-on-read with a rescued-data column so malformed events are captured rather than dropped. See §5.3, row "Clickstream" |
| **Risks** | Introducing a schema registry is a client-side prerequisite with its own change programme. Until then, the rescued-data column is the contract. Kafka retention (currently 3 days) must be raised to survive a weekend outage — **7 days minimum** is the ask |

### 3.5 Product catalogue / PIM

| Attribute | Detail |
|---|---|
| **Business domain** | Product, merchandising hierarchy |
| **What it holds** | ~1.4m active SKUs, ~9m SKU-by-locale combinations, the 5-level merchandising hierarchy, supplier linkage, pack and dimension data, allergen and regulatory attributes, digital-asset metadata |
| **Format / protocol** | Commercial PIM on PostgreSQL; a read replica is available |
| **Volume** | ~900 GB total; ~0.4 GB/day of change |
| **Change rate** | ~250k attribute changes/day; seasonal range changes create bursts of ~2m changes over 48 hours, four times a year |
| **Latency requirement** | **1 hour.** Product is a conformed dimension — a new SKU missing from the dimension breaks every downstream join |
| **Quality issues** | Locale records are incomplete for smaller markets (~14% of SKU-locale rows have no description); the hierarchy has 3,100 SKUs parked in a "to be classified" node; supplier linkage is one-to-one in the model but many-to-one in reality |
| **PII / regulatory** | **P0**. Allergen and regulatory attributes carry consumer-safety obligations — accuracy matters more than latency |
| **Ingestion pattern** | **Lakeflow Connect database connector (PostgreSQL) against the read replica.** See §5.3, row "PIM" |
| **Risks** | The "to be classified" node must be a **blocking data-quality gate** in the silver layer, not a warning. Downstream reporting silently misattributes those SKUs today |

### 3.6 Supply-chain EDI feeds

| Attribute | Detail |
|---|---|
| **Business domain** | Supply chain, procurement, logistics |
| **What it holds** | Purchase order acknowledgements (855), advance ship notices (856), invoices (810), inventory advice (846), functional acknowledgements (997), from ~1,200 trading partners |
| **Format / protocol** | EDIFACT and X12, delivered to an SFTP endpoint by a VAN; ~14,000 documents/day |
| **Volume** | ~2 GB/day; small files, high count (~14k files/day) |
| **Change rate** | Append-only; ~3% of documents are re-sent corrections |
| **Latency requirement** | **30 minutes** for ASNs (drives DC inbound planning and the store availability projection); daily for invoices |
| **Quality issues** | Partner-specific dialect variation is the norm; ~6% of documents fail strict parsing today and are handled manually by an operations team; date and unit-of-measure conventions differ by partner |
| **PII / regulatory** | **P1** — commercially sensitive supplier terms. No personal data other than incidental contact names |
| **Ingestion pattern** | **Auto Loader on the SFTP landing zone** (registered as a Unity Catalog external location), parsing in a bronze-to-silver declarative pipeline, with a quarantine table for parse failures. See §5.3, row "EDI" |
| **Risks** | High file count at small file size is the classic Auto Loader cost trap — file-event notification rather than directory listing, plus compaction on the bronze table, is mandatory here |

### 3.7 IoT — distribution centres and cold chain

| Attribute | Detail |
|---|---|
| **Business domain** | Supply chain, food quality, sustainability |
| **What it holds** | Temperature and humidity from 38 DCs (~14,000 sensors), 2,600 refrigerated trailers (GPS plus temperature), and ~28,800 in-store refrigerated cases. Plus DC conveyor and sortation telemetry |
| **Format / protocol** | MQTT to a gateway to Kafka for DC and store; cellular telemetry via a vendor API for trailers |
| **Volume** | ~66m readings/day at 1-minute intervals; small payloads (~120 bytes); ~8 GB/day |
| **Change rate** | Append-only, constant rate; gaps during connectivity loss are themselves signal |
| **Latency requirement** | **1 minute for excursion alerting.** This is the only genuinely sub-minute requirement in the estate, and it exists for food-safety reasons. Analytical use is daily |
| **Quality issues** | Sensor drift and failure (~1.5% of sensors report implausible values at any time); trailer telemetry drops out in transit and backfills in bursts; DC sensors are named inconsistently across the 38 sites |
| **PII / regulatory** | **P0**. Subject to **food-safety record-keeping obligations** (HACCP-equivalent) — retention and immutability of the evidence trail matter more than query performance |
| **Ingestion pattern** | **Streaming ingest into a bronze streaming table**, with alerting computed on a separate low-latency stream rather than on the analytical path. See §5.3, row "IoT" |
| **Risks** | Do not let a food-safety alert depend on the analytical platform's availability. The alerting path must be independently survivable; the lakehouse is the **system of record and of evidence**, not the safety interlock |

### 3.8 Marketing platforms

| Attribute | Detail |
|---|---|
| **Business domain** | Marketing, customer engagement |
| **What it holds** | Campaign, send, open, click and conversion from the email/CRM platform; paid media spend and performance from three ad platforms; app push and in-app messaging; the consent and preference store |
| **Format / protocol** | Mixed: two platforms have managed connectors, two expose REST APIs with daily export, one delivers scheduled CSV to object storage, one requires a vendor-side export job |
| **Volume** | ~3 GB/day combined |
| **Change rate** | Daily batch for spend and performance; near-continuous for send/open/click (~40m events/day at campaign peak) |
| **Latency requirement** | **Daily** for spend and attribution. **Hourly** for suppression lists — a suppression that arrives late is a compliance incident, not a reporting delay |
| **Quality issues** | Campaign taxonomy is inconsistent across markets; spend is reported in platform currency with platform-defined FX; identity keys differ per platform (hashed email, device ID, platform user ID) |
| **PII / regulatory** | **P2**, and this is the highest-risk personal-data domain in the estate because it is where personal data is *acted upon*. Consent and suppression state are load-bearing |
| **Ingestion pattern** | **Lakeflow Connect managed connectors where one exists; Auto Loader on delivered files otherwise.** The consent/preference store is treated as a first-class source, not a marketing attribute. See §5.3, row "Marketing" |
| **Risks** | Resist bespoke API pollers. Every bespoke poller is a future incident. Where no connector exists, prefer a vendor-side scheduled export to a landing zone |

### 3.9 Third-party market and reference data

| Attribute | Detail |
|---|---|
| **Business domain** | Commercial, category management, planning |
| **What it holds** | Market share and category panel data (weekly), competitor pricing (daily, collected by a vendor), weather actuals and forecast (hourly, by postcode district), public-holiday and school-term calendars, FX rates |
| **Format / protocol** | Varies by vendor: one panel vendor supports open data sharing natively; competitor pricing arrives as daily CSV to object storage; weather is a REST API; FX arrives from Treasury as a daily file |
| **Volume** | ~1 GB/day |
| **Change rate** | Weekly (panel), daily (pricing, weather, FX) |
| **Latency requirement** | **Daily.** Weather-forecast refresh is 4-hourly and materially improves the demand forecast in fresh categories |
| **Quality issues** | Panel data is restated retrospectively for up to 6 weeks; competitor pricing has ~8% match failure against Meridian SKUs; weather geography does not align to store catchments without a mapping table Meridian must own |
| **PII / regulatory** | **P1**. **Licence terms constrain redistribution** — panel data typically may not be shared outside the licensed entity, which is a grant-model constraint (§7.6), not a footnote |
| **Ingestion pattern** | **OpenSharing where the vendor supports it** (zero-copy, no pipeline to run); **COPY INTO from a governed volume** for the low-volume file feeds. See §5.3, row "Third-party data" |

### 3.10 HR — Workday

| Attribute | Detail |
|---|---|
| **Business domain** | People, store operations, labour planning |
| **What it holds** | Worker, position, organisation, cost centre, contract type, absence, and the store-roster interface. ~85,000 employees, ~210,000 historical workers |
| **Format / protocol** | Workday, via a managed connector (HCM and Reports) |
| **Volume** | ~0.1 GB/day |
| **Change rate** | ~9,000 changes/day; monthly payroll cycles create spikes |
| **Latency requirement** | **Daily.** Labour scheduling is a separate operational system; the lakehouse serves analytics and cost allocation |
| **Quality issues** | Cost-centre mapping to SAP profit centres is maintained in a spreadsheet; contractor populations are partially outside Workday |
| **PII / regulatory** | **P2**, with **P3** elements (absence reason can imply health data; some jurisdictions treat union membership as special category). **Works-council consultation is required in at least 5 of the 14 countries before any employee-level analysis.** Treat this as a dependency with a lead time |
| **Ingestion pattern** | **Lakeflow Connect managed SaaS connector**, into a dedicated restricted catalog with no default grants |
| **Risks** | HR data is the most likely source of a privacy incident and the least likely to deliver value in Year 1. Recommend ingesting **organisation and cost-centre structures only** in Phases 1–2, deferring worker-level data until the works-council process completes |

### 3.11 The legacy EDW

| Attribute | Detail |
|---|---|
| **Business domain** | All — this is where 20 years of business logic lives |
| **What it holds** | ~11,000 tables, of which ~1,900 are referenced by a report in the last 12 months and ~400 weekly. ~2,900 registered reports, of which ~620 have been opened in the last 90 days |
| **Format / protocol** | On-premises MPP appliance; JDBC access; bulk export to object storage is possible but constrained by appliance egress throughput (~4 TB/day sustained without harming the batch window) |
| **Volume** | 480 TB. The **worth-keeping subset is estimated at 60–90 TB** — conformed history that cannot be rebuilt from source |
| **Change rate** | The whole warehouse is rebuilt nightly by the legacy ETL; during dual-run it continues to do so |
| **Latency requirement** | During dual-run: daily, for reconciliation comparison |
| **Quality issues** | Business logic is embedded in ETL, not documented. Several critical measures exist in three variants with different filters. Slowly-changing dimension history is inconsistent — some dimensions are Type 1 where they should be Type 2, which means **some history is simply gone** and cannot be recovered |
| **PII / regulatory** | **P1/P2** mixed, and poorly mapped. A discovery pass is required before any of it is migrated (§11, R7) |
| **Ingestion pattern** | Two distinct mechanisms, deliberately: **Lakehouse Federation** for read-only governed access during migration and reconciliation (no copy, no pipeline, immediate), and **a one-off bulk export** of the worth-keeping history subset. See DECISION D-12 (§5.8) |
| **Risks** | The instinct to "migrate the warehouse" must be resisted. The programme migrates **consumers and business logic**, re-derived from source, and keeps only history that cannot be rebuilt. §8.6 makes this a gate |

### 3.12 Reference and finance master data

| Attribute | Detail |
|---|---|
| **Business domain** | Finance, Reference |
| **What it holds** | Store master (opening dates, formats, catchments, square footage), calendar (fiscal, retail 4-5-4, trading day), FX rate table, company-code and profit-centre hierarchy, country and tax reference |
| **Format / protocol** | A mix of SAP extracts, a Finance-owned SharePoint workbook, and three spreadsheets |
| **Volume** | <0.1 GB/day |
| **Change rate** | Low — tens of rows per day — but **disproportionately impactful**. A store-master error misstates a region |
| **Latency requirement** | Daily |
| **Quality issues** | This is the least-governed and most-depended-on data in the estate. Store master exists in four places with three different store-code formats |
| **PII / regulatory** | **P0** |
| **Ingestion pattern** | **COPY INTO from a governed Unity Catalog volume**, with the spreadsheet replaced in Phase 2 by a small governed entry application. See §5.3, row "Reference" |
| **Risks** | Do not automate the ingestion of an ungoverned spreadsheet and call it solved. Reference data needs an **owner and a maintenance process** before it needs a pipeline |

---

## 4. Use cases and value

Eight use cases are carried into the plan. They were selected because each one is (a) owned by a named executive, (b) measurable against an existing KPI, and (c) dependent on data the programme is already ingesting for another reason. Use cases that fail any of those three tests are parked, not refused.

**A note on latency.** The column "freshness it truly needs" is the most commonly over-specified number in a programme like this. Every stakeholder asks for real time. Only two of these eight use cases genuinely require it; asking for it elsewhere converts a cheap batch pipeline into an expensive streaming one for no decision benefit. The figures below are the ones the programme will defend.

### UC-1 — Unified Customer 360

| | |
|---|---|
| **Business question** | Who is this customer across every channel and country, what have they bought, what have they returned, what have they been sent, and what have they consented to? |
| **Consumers** | Marketing (campaign and audience build), Customer Service, Loyalty, Digital product teams, Group Commercial |
| **Freshness truly needed** | **Daily** for the analytical profile; **within 1 hour** for consent and suppression state; **near-real-time** only for the subset of attributes used by on-site personalisation (UC-6) |
| **Depends on** | POS (3.3), clickstream (3.4), Salesforce (3.2), marketing platforms and consent store (3.8), loyalty master (within POS/SAP), reference (3.12) |
| **Value driver** | Removes duplicate audience spend; makes every other customer-facing use case possible. **It is the enabling asset, and its value is mostly realised through UC-4 and UC-6.** |
| **Value range** | $8–14m direct (deduplicated media spend and service efficiency), plus it is a hard dependency for $25–45m in UC-6 |
| **Key assumption** | Identity resolution achieves a 70–80% match rate between store loyalty card and e-commerce account within the loyalty population. If the true rate is below 55%, UC-6's value halves. **Measure this in Phase 0 on a sample — do not assume it.** |

### UC-2 — Demand forecasting and replenishment

| | |
|---|---|
| **Business question** | How many units of each SKU will each store sell tomorrow, and what should be ordered today? |
| **Consumers** | Supply Chain planning, the replenishment engine (as an automated consumer), store operations |
| **Freshness truly needed** | **Daily, completed by 04:00 local** so the order cut-off is met. Intraday is not required; the order is placed once |
| **Depends on** | POS (3.3), SAP inventory and purchasing (3.1), PIM (3.5), EDI ASN (3.6), weather and calendar (3.9), promotional calendar (marketing, 3.8) |
| **Value driver** | Forecast error reduction lets safety stock be re-cut. Inventory is ~$3.4bn; carrying cost ~18% |
| **Value range** | **$50–75m annual P&L**, on a working-capital release of $270–410m |
| **Key assumption** | Forecast accuracy (WMAPE at SKU-store-day) improves from ~38% to 26–30%, and Supply Chain actually re-cuts safety-stock parameters on the back of it. **The second half of that sentence is where these programmes fail: a better forecast that nobody acts on is worth zero.** Make the parameter re-cut an explicit, owned deliverable |

### UC-3 — Real-time inventory availability

| | |
|---|---|
| **Business question** | What is actually on the shelf, in the back room, in the DC and in transit, right now, for this SKU at this store? |
| **Consumers** | E-commerce (click-and-collect promise), store colleagues (app), the availability exception process, customer service |
| **Freshness truly needed** | **15 minutes.** This is one of the two genuine near-real-time cases. A collect promise made on 24-hour-old stock is a broken promise |
| **Depends on** | POS intraday (3.3), SAP goods movements (3.1), EDI ASN (3.6), PIM (3.5) |
| **Value driver** | On-shelf availability, plus reduced failed click-and-collect orders (currently ~3.1% of collect orders substitute or cancel) |
| **Value range** | **$45–75m gross margin**, from recovering 0.6–1.0% of store revenue on a 28% gross margin, phased over Years 2–3 |
| **Key assumption** | The stock position derived in the lakehouse is accurate enough to be trusted operationally. It will not be on day one — book stock accuracy is estimated at 88% at SKU-store level. **Phase 2 must include a stock-accuracy measurement and a correction loop, or this use case will be rejected by stores** |

### UC-4 — Markdown and promotional optimisation

| | |
|---|---|
| **Business question** | For this SKU in this store, what price or markdown maximises margin over the remaining life of the stock? |
| **Consumers** | Commercial / category managers, Pricing, regional trading teams |
| **Freshness truly needed** | **Daily.** Markdown decisions are taken on a weekly cycle with daily exception review |
| **Depends on** | POS (3.3), SAP inventory and valuation (3.1), PIM (3.5), competitor pricing and panel data (3.9), UC-2 forecast output |
| **Value driver** | Markdown spend is estimated at ~5.6% of store revenue ($1.5bn). Sector experience suggests 3–6% improvement is achievable when decisions move from calendar rules to measured elasticity |
| **Value range** | **$55–110m gross margin** |
| **Key assumption** | Category managers accept a recommendation engine in the loop. Recommend a **recommend-and-override** design, not automation — adoption is the binding constraint, not model quality |

### UC-5 — Supplier performance and claims recovery

| | |
|---|---|
| **Business question** | Which suppliers are delivering on time and in full, at what quality, and what are we owed? |
| **Consumers** | Procurement, Supply Chain, Finance (claims), and **the suppliers themselves** |
| **Freshness truly needed** | **Daily**, with a weekly published scorecard |
| **Depends on** | EDI (3.6), SAP purchasing and goods receipt (3.1), DC IoT and quality events (3.7), PIM supplier linkage (3.5) |
| **Value driver** | OTIF penalties and quality claims that are currently not raised because they cannot be evidenced |
| **Value range** | **$15–30m**, of which roughly half is claims recovery and half is behavioural improvement once suppliers see the same scorecard |
| **Key assumption** | Suppliers can be given governed read access to their own slice of the scorecard without a per-supplier integration project. This is the case that justifies OpenSharing (§7.6) |

### UC-6 — Personalisation and offer targeting

| | |
|---|---|
| **Business question** | What should we show or offer this customer, now, given what they have bought, browsed and consented to? |
| **Consumers** | Digital product, Marketing, the app and website, the loyalty offer engine |
| **Freshness truly needed** | **Session-level (seconds) for on-site behavioural signals**; daily for the profile attributes. This is the second genuine real-time case, and only for a narrow feature set |
| **Depends on** | UC-1 Customer 360, clickstream (3.4), POS (3.3), PIM (3.5), consent store (3.8) |
| **Value driver** | Incremental revenue on loyalty-attributed sales, currently ~44% of store revenue |
| **Value range** | **$25–45m gross margin** |
| **Key assumption** | Incremental lift of 1.5–3% on targeted segments, proven by holdout testing. **Require a holdout on every campaign from day one.** Without holdouts the value is unprovable and the programme will be argued about rather than extended |

### UC-7 — Finance close acceleration

| | |
|---|---|
| **Business question** | What did we earn, where, and can we prove it — by day 4 rather than day 9? |
| **Consumers** | Group Finance, regional controllers, Investor Relations, external audit |
| **Freshness truly needed** | **Daily by 06:00 local**, with a flash trading position available intraday |
| **Depends on** | SAP finance (3.1), POS (3.3), reference and FX (3.12), legacy EDW history (3.11) during dual-run |
| **Value driver** | Reconciliation effort, decision latency, and the audit-evidence burden |
| **Value range** | **$6–9m cost**, principally 14 FTE of monthly reconciliation reducing to 4–5, plus a materially cheaper audit cycle. The larger, unquantified benefit is that the Board argues about the business rather than about the numbers |
| **Key assumption** | Finance accepts lakehouse-derived figures as the reporting basis after a **3-month parallel run with zero unexplained variance**. Do not promise a shorter parallel |

### UC-8 — Cold-chain compliance and waste reduction

| | |
|---|---|
| **Business question** | Was this product held within temperature specification along its whole journey, and where are we losing product to excursions? |
| **Consumers** | Quality and food safety, DC operations, store operations, external auditors and regulators |
| **Freshness truly needed** | **1 minute for alerting** (operational, on the streaming path); daily for analysis and evidence |
| **Depends on** | IoT (3.7), EDI ASN (3.6), SAP movements (3.1), PIM product attributes (3.5) |
| **Value driver** | Product written off after an excursion, plus the cost of manual compliance evidence gathering |
| **Value range** | **$10–20m**, plus a materially reduced regulatory risk that is not monetised here |
| **Key assumption** | Alerts reach a person who can act within the product's thermal tolerance. **An alert with no owner is a log line.** The operating-model change is bigger than the engineering |

### 4.9 Prioritisation matrix

Scores are 1–5. **Value** is annual run-rate benefit. **Effort** is delivery effort (5 = least effort). **Data readiness** is how usable the required sources are today (5 = ready). **Priority score** = Value x (Effort + Readiness) / 2, rounded. This is a conversation starter for the sponsor, not an algorithm; the sequencing in §8 also reflects dependency order.

| Use case | Value | Effort (5 = easy) | Data readiness | Priority score | Phase |
|---|---|---|---|---|---|
| UC-7 Finance close | 2 | 4 | 4 | 8 | 1–2 |
| UC-3 Real-time availability | 5 | 2 | 3 | 13 | 2–3 |
| UC-2 Demand forecasting | 5 | 2 | 3 | 13 | 2–3 |
| UC-4 Markdown optimisation | 5 | 3 | 3 | 15 | 3 |
| UC-5 Supplier performance | 3 | 4 | 3 | 11 | 2 |
| UC-1 Customer 360 | 3 | 3 | 2 | 8 | 2 |
| UC-6 Personalisation | 4 | 2 | 2 | 8 | 3–4 |
| UC-8 Cold chain | 2 | 3 | 4 | 7 | 3 |

**How to read this.** UC-4 scores highest but depends on UC-2's forecast, so it cannot go first. UC-7 scores modestly but is sequenced early because it is the **credibility purchase**: a finance close that lands on day 4 is the outcome that buys the programme its Phase 3 budget. UC-1 scores lower than its strategic importance because its data readiness is genuinely poor — that is a finding, not a reason to skip it.

**Deliberately excluded from Phase 1–3 scope**, with the reason:

| Parked use case | Why not now |
|---|---|
| Store labour optimisation | Depends on worker-level HR data, which is blocked by works-council consultation (§3.10) |
| Assortment and space planning | Requires planogram data that is not currently captured digitally in 6 of 14 countries |
| Dynamic pricing (as opposed to markdown) | Regulatory and brand risk in grocery; a separate decision, not a data decision |
| Scope-3 emissions reporting | Real and coming, but the data standard is still moving; revisit at the Phase 3 gate |
| Generative assistants over the estate | Becomes cheap and safe **after** the governed semantic layer exists, not before. Sequence it into Phase 4, not Phase 1 |

---

## 5. Target architecture

### 5.1 The shape, in one paragraph

Every source lands **once**, in its original grain, into a **bronze** zone owned by the platform team. Domain teams transform bronze into **silver** — conformed, deduplicated, quality-gated business entities with stable keys. **Gold** holds the consumption-shaped products: dimensional models, metric definitions, feature tables and extracts. One catalog per environment, one schema per domain, one owner per schema. Consumption is through governed SQL, dashboards, a natural-language interface and model serving. Nothing reads a source system directly except an ingestion pipeline, and nothing writes to gold except a pipeline in version control.

### 5.2 Zones and the medallion contract

The medallion pattern is only useful if each layer has a *contract* — a statement of what a consumer may and may not assume. Without contracts, "silver" becomes "wherever the last engineer stopped".

| | **Bronze** | **Silver** | **Gold** |
|---|---|---|---|
| **Purpose** | Faithful, replayable capture of the source | Conformed, quality-gated business entities | Consumption-shaped products |
| **Grain** | Source grain, unaltered | Business entity grain (one row per basket line, per customer, per SKU-location-day) | Consumption grain (fact/dimension, aggregate, feature vector) |
| **Schema** | Source schema plus ingestion metadata; permissive, with a rescued-data column | Explicit, declared, versioned | Explicit, declared, versioned |
| **Transformation allowed** | None beyond decoding and metadata enrichment | Typing, deduplication, conforming, key assignment, SCD handling, quality enforcement | Joins, aggregation, business rules, derived measures |
| **Quality** | Recorded, never enforced (nothing is rejected) | **Enforced.** Expectations drop or quarantine failing rows; violations are counted and alerted | Assumed clean; assertions verify invariants only |
| **Personal data** | Present, restricted to the platform team and the ingestion identity | Pseudonymised; direct identifiers isolated in a separate restricted schema | Personal data only where a use case justifies it, under attribute-based policy |
| **Who may read** | Platform team, domain data engineers | Domain team, downstream domain engineers | Analysts, applications, partners, agents |
| **Who may write** | Ingestion pipelines only | The owning domain's pipeline only | The owning domain's pipeline only |
| **Retention** | Source-defined, typically 13–25 months; IoT evidence longer per food-safety obligation | Full history for entities requiring it; SCD2 where the business needs as-was reporting | Driven by the consuming use case |
| **Reprocessing** | Replayable from bronze without touching the source | Rebuildable from bronze | Rebuildable from silver |

**The bronze rule that matters most:** bronze must be sufficient to rebuild everything downstream without going back to the source system. In this estate, that rule is what makes it safe to take a cautious extraction approach from SAP — one careful extract, replayed many times, rather than repeated extraction pressure on a production ERP.

**Per-domain variations from the standard contract:**

| Domain | Variation | Why |
|---|---|---|
| Finance | Silver is **append-only with a restatement flag**; no in-place correction | Audit evidence — the as-reported figure must remain recoverable |
| Cold chain | Bronze retention extended to meet the food-safety record-keeping period | Regulatory obligation; confirm the exact period per country **[TBC with Legal]** |
| Clickstream | Bronze carries a **consent-state join key**; silver is filtered by consent at the point of creation | Personal data may not reach a usable shape before consent is checked |
| Customer | Direct identifiers live in a single restricted schema; silver and gold carry only a pseudonymous key | Makes erasure tractable (§7.3) |
| POS | Silver conforms three source schemas to one; the mapping is a versioned, reviewed artefact, not code comments | Three-way conforming is the highest-risk logic in the estate |

### 5.3 Ingestion — the decision per source

The decision rule is a ladder, applied in order: **use the most managed option that meets the requirement, and drop a rung only when it does not.** Dropping a rung buys control and costs engineering time forever after.

1. **Managed connector (Lakeflow Connect)** — a source with a supported connector and no unusual requirement.
2. **Lakeflow Declarative Pipelines over Auto Loader / COPY INTO** — files arriving in object storage.
3. **Structured Streaming** — message buses, or anything needing sub-minute latency or custom stateful logic.
4. **Lakehouse Federation** — read the source in place, when copying is not justified.
5. **OpenSharing** — the data is already in someone else's lakehouse and can be shared without copying.

| Source | Mechanism | Why | Rejected alternative, and why |
|---|---|---|---|
| SAP ECC (3.1) | **Managed database connector with CDC** (ingestion gateway plus ingestion pipeline) | Log-based CDC gives 4-hour inventory latency without repeated full extracts against production; schema evolution and retries are handled by the connector rather than by us | **Nightly full-table export:** cannot meet 4 hours, and the export window already competes with the ERP batch. **SAP-native extractors (ODP/SLT):** viable and may be politically easier, but adds an SAP-side component the client must license, operate and change-manage; keep it as the fallback if basis refuses log access (§11, R2) |
| Salesforce (3.2) | **Lakeflow Connect managed SaaS connector** | Supported source, modest volume, incremental by default; zero pipeline code to maintain | **Bespoke Bulk API extraction:** we would own pagination, throttling, soft deletes and schema drift forever, for no benefit |
| POS — EU and APAC (3.3) | **Auto Loader with file-event notification**, into a declarative pipeline | Millions of files over time at high file count; directory listing does not scale and costs more per file discovered. Exactly-once file processing removes the duplicate-file problem created by the EU platform's whole-day re-sends | **COPY INTO:** appropriate for thousands of files, not millions, and re-sent files would need manual handling. Keep COPY INTO available for targeted re-loads of a specific store-day |
| POS — Americas (3.3) | **Structured Streaming from Kafka** into a bronze streaming table | The source is already a stream and the 15-minute requirement is real | **Land to files first, then Auto Loader:** adds a hop and 10+ minutes of latency for no gain when the bus already exists |
| Clickstream (3.4) | **Structured Streaming from Kafka**, one stream per topic family, rescued-data column enabled | 22k events/sec peak with unannounced schema change; the rescued-data column converts a nightly outage into a data-quality metric | **A managed streaming connector:** reduces code, but we need custom sessionisation and bot-flagging close to ingest and per-topic checkpoint control. Re-evaluate at the Phase 3 gate **[TBC against current connector capabilities]** |
| PIM (3.5) | **Lakeflow Connect database connector (PostgreSQL)** against the read replica | Supported source, read replica already exists, 1-hour latency easily met | **Federation:** product is joined in almost every downstream query; reading it remotely on every query would push repeated load onto the PIM database and give no history |
| EDI (3.6) | **Auto Loader on the SFTP landing location**, parsing in a declarative pipeline, failures to quarantine | 14k small files a day is exactly the file-count profile Auto Loader exists for; parsing belongs in our code because the dialect variation is Meridian-specific | **A commercial EDI translation product:** the client already owns the VAN relationship; adding a second translation layer duplicates cost. **COPY INTO:** file count is too high |
| IoT (3.7) | **Streaming ingest into bronze**, plus a **separate low-latency alerting stream** | Two different consumers with two different availability requirements should not share one pipeline | **One pipeline serving both:** couples a food-safety alert to analytical platform availability. Rejected on risk, not cost |
| Marketing (3.8) | **Managed connector where one exists; Auto Loader on vendor-delivered files otherwise** | Six platforms, six different integration surfaces; standardising on "connector or file drop" keeps the count of bespoke components at zero | **Bespoke REST pollers per platform:** six components to own, each breaking independently |
| Third-party data (3.9) | **OpenSharing** for the panel vendor that supports it; **COPY INTO** for the small file feeds | Sharing avoids a copy, avoids a pipeline, and the restated history simply appears. COPY INTO is right for thousands of small files a year with occasional targeted re-load | **Building a pipeline for shared data:** copying data that is already accessible adds cost, latency and a new failure mode. **Auto Loader for the file feeds:** correct but heavier than needed at this file count |
| HR (3.10) | **Lakeflow Connect managed SaaS connector**, restricted catalog | Supported source, low volume, tight access control matters more than throughput | **Ad-hoc report exports to a share:** how HR data leaks |
| Legacy EDW (3.11) | **Lakehouse Federation** for reconciliation reads; **one-off bulk export** for retained history | Federation is available in days, needs no pipeline, and is exactly right for the temporary reconciliation workload. The retained history is a one-time move, so it does not deserve a pipeline either | **Building CDC from the appliance:** weeks of work on a system with a known end date. **Migrating all 480 TB:** migrates the problem |
| Reference (3.12) | **COPY INTO from a governed volume** | Tens of small files, occasional re-load, human-in-the-loop upload | **Auto Loader:** an always-on stream for a file that changes weekly is operational overhead without benefit |

> **DECISION D-01 — Ladder-first ingestion policy.** Every new source must justify *not* using the most managed available mechanism, in writing, in the design review. **Rejected:** a single standard pattern for all sources (typically "everything via Kafka" or "everything via files"), which is simple to describe and expensive to run — it forces every source through infrastructure it does not need and hides per-source cost.

> **DECISION D-02 — Declarative pipelines as the default transformation framework.** Bronze-to-silver and silver-to-gold transformations are built as **Lakeflow Spark Declarative Pipelines**, with expectations as the quality mechanism, orchestrated by **Lakeflow Jobs**. **Why:** dependency resolution, incremental processing, data-quality expectations and lineage come from the framework rather than from convention; a new engineer reads the transformation, not the plumbing. **Rejected:** hand-written notebook pipelines orchestrated by job dependencies — maximum flexibility, but it reproduces exactly the situation described in §2.3, where every pipeline is a bespoke artefact and quality is whatever each author remembered to add.

> **DECISION D-03 — SAP extraction via log-based CDC, with an ODP/SLT fallback held in reserve.** **Why:** it is the only option that meets the 4-hour inventory requirement without adding load to the ERP batch window. **Rejected:** nightly export (too slow), and SAP-native extraction as the primary route (adds a licensed, client-operated component and a change-control dependency). The fallback is documented and estimated now, in Phase 0, so that a basis-team refusal costs a re-plan and not a re-architecture.

### 5.4 Streaming versus batch, per use case

Streaming is chosen where a decision is made faster than daily. Everywhere else, scheduled incremental batch is chosen because it is cheaper to run, easier to reason about and much easier to reprocess.

| Use case | Mode | Trigger | Justification |
|---|---|---|---|
| UC-3 Real-time availability | Streaming | Continuous on the POS Americas and IoT paths; 5-minute micro-batch for the EU intraday path | The decision (promise a collect slot) is made in seconds |
| UC-8 Cold-chain alerting | Streaming | Continuous | Food safety |
| UC-6 Personalisation (behavioural features) | Streaming | Continuous, narrow feature set only | Session relevance decays in minutes |
| UC-1 Customer 360 | Batch | Scheduled incremental, several times daily; hourly for consent | Profiles do not change in seconds; consent does matter within the hour |
| UC-2 Demand forecasting | Batch | Daily, completed by 04:00 | One order cut-off per day |
| UC-4 Markdown | Batch | Daily | Weekly decision cycle |
| UC-5 Supplier performance | Batch | Daily; weekly publication | Weekly scorecard |
| UC-7 Finance close | Batch | Daily by 06:00, plus an intraday flash | The ledger is not a stream |

> **DECISION D-04 — Streaming pipelines run on a scheduled available-now trigger unless a use case demands continuous.** Only the three continuous cases above run always-on. Everything else that *reads* a stream runs on a schedule, processing all newly available data and stopping. **Why:** it gives streaming semantics (exactly-once, checkpointed, incremental, replayable) at batch cost, and it is a single configuration change to promote a pipeline to continuous if the business later needs it. **Rejected:** always-on streaming for everything — conceptually tidy, and it bills for idle time on pipelines whose consumers look at a dashboard once a morning.

### 5.5 Unity Catalog design

> **DECISION D-05 — Catalog per environment, schema per domain. Not catalog per domain.** Three catalogs: `mrg_dev`, `mrg_tst`, `mrg_prd`, each containing a schema per domain-and-layer. **Why:** the environment boundary is the one that must be absolutely impermeable — a development job must be structurally incapable of writing to production. Making environment the top-level securable makes that a property of the model rather than a matter of discipline. It also makes promotion a matter of substituting the catalog name, which keeps pipeline code identical across environments. **Rejected:** catalog-per-domain (`customer`, `sales`, `supply_chain`), which reads beautifully in a data-mesh diagram and then requires either a separate metastore per environment or a naming convention like `customer_prd` — at which point environment is in the name anyway, but is no longer enforced by the hierarchy. Also **rejected:** a single catalog with environment-prefixed schemas, which puts the most important boundary in a string.

**Schema naming:** `<layer>_<domain>`, lower snake case, no abbreviations that are not already enterprise vocabulary.

```
mrg_prd
├── bronze_sap              bronze_pos            bronze_clickstream
├── bronze_salesforce       bronze_pim            bronze_edi
├── bronze_iot              bronze_marketing      bronze_market_data
├── bronze_hr               bronze_reference
├── silver_sales            silver_inventory      silver_customer
├── silver_product          silver_supply_chain   silver_finance
├── silver_marketing        silver_people         silver_reference
├── silver_customer_pii     (restricted: direct identifiers only)
├── gold_trading            gold_customer_analytics
├── gold_supply_chain       gold_finance_reporting
├── gold_merchandising      gold_supplier_portal   (the OpenSharing surface)
├── ml_features             ml_models
└── ops_platform            (audit extracts, quality results, cost attribution, run metadata)
```

**Volumes.** Managed volumes for anything the platform itself writes (checkpoints in their own locations, quarantine payloads, export staging). External volumes for the three landing zones the client's systems write into: `landing_pos`, `landing_edi`, `landing_vendor_files`. A volume is the governed alternative to the mount paths and shared buckets that made the current estate unauditable.

**Groups.** Identity is federated from the corporate directory to the account and synchronised; groups are **account groups**, never workspace-local groups, so that any policy expression evaluates identically everywhere. The group taxonomy is deliberately small:

| Group pattern | Example | Purpose |
|---|---|---|
| `mrg-platform-admin` | — | Metastore and platform administration; a small, named, audited set |
| `mrg-<domain>-owner` | `mrg-sales-owner` | Owns the domain's schemas; a **group**, never an individual |
| `mrg-<domain>-engineer` | `mrg-supply-chain-engineer` | Writes the domain's pipelines |
| `mrg-<domain>-reader` | `mrg-finance-reader` | Reads the domain's gold products |
| `mrg-analyst-<region>` | `mrg-analyst-emea` | Regional analyst population; the residency filter hangs off this |
| `mrg-pii-approved-<domain>` | `mrg-pii-approved-marketing` | Explicit, time-bound, approved access to unmasked personal data |
| `mrg-sp-<pipeline>` | `mrg-sp-ingest-sap` | Service principals; one per pipeline family, never shared |

**Grants model — four rules, applied without exception.**

1. Grants are made **to groups, never to users**. An exception request becomes a group with one member and an expiry date, so it is visible.
2. Grants are made at **schema level** where possible, so new tables in a domain inherit access rather than requiring a new grant. Table-level grants are the exception, and each one should be explainable.
3. **Ownership is held by groups** — `mrg-<domain>-owner` — so that a leaver does not orphan a schema.
4. All grants are declared in configuration and applied by the deployment pipeline. **A grant made by hand in the UI is a defect**, and the weekly drift report treats it as one.

**Tags.** Governed tags, defined at account level, carry the classification that drives policy:

| Tag key | Values | What it drives |
|---|---|---|
| `data_classification` | `p0`, `p1`, `p2`, `p3` | Masking policy, sharing eligibility, retention |
| `pii_type` | `email`, `phone`, `name`, `address`, `card_ref`, `loyalty_id`, `device_id` | Which masking function applies |
| `data_residency` | `eu`, `uk`, `apac`, `us`, `global` | Row-level residency filtering and share eligibility |
| `domain` | `sales`, `customer`, `supply_chain`, … | Ownership, cost attribution, catalogue navigation |
| `product_tier` | `certified`, `curated`, `experimental` | Consumer expectation and SLO tier (§6.3) |
| `cost_centre` | client cost-centre code | Chargeback |

Note for the implementer: **column tags do not inherit from the parent table** and must be applied to the column directly. This makes column tagging a pipeline responsibility, not a one-off exercise — the declarative pipeline that creates a table also asserts its column tags.

> **DECISION D-06 — Attribute-based access control on tags, not per-table masks.** Masking and row filtering are implemented as **ABAC policies attached at schema level, matching on governed tags** (for example: mask any column tagged `pii_type = email` for everyone except `mrg-pii-approved-*`). **Why:** it scales. With ~2,000 gold and silver tables and 400+ analysts, attaching a mask to each table individually is a permanent backlog and a guaranteed gap — the table created next Tuesday is unprotected until someone remembers. Tag-driven policy means a correctly tagged new table is protected the moment it exists. **Rejected:** per-table row filters and column masks — they remain the right tool for a handful of genuine one-offs, and they are the fallback for anything ABAC cannot express, but they cannot be the primary mechanism at this scale. **Implementation constraints to respect:** ABAC requires serverless compute or a sufficiently recent runtime on classic compute; older runtimes cannot read ABAC-secured tables at all. Materialised-view and streaming-table refreshes evaluate policies as the **pipeline owner**, so a pipeline owner with broad access can permanently materialise unmasked data — pipeline service principals must therefore be scoped as narrowly as analysts, not exempted. Quotas on policies per schema and per table are documented and generous but finite; the policy count here should stay in the low hundreds by design. Verify the current compute requirements and quota figures at build time **[TBC against current docs]**.

### 5.6 The serving layer

| Consumer | Served by | Design note |
|---|---|---|
| ~400 analysts, ad-hoc SQL | **Databricks SQL warehouses**, serverless, sized per workload class | Three warehouse classes: `xs-adhoc` (auto-stop aggressive), `m-bi` (dashboard refresh), `l-finance` (close period, scheduled scale-up). Analysts never choose their own compute |
| Executive and operational dashboards | **AI/BI dashboards** on gold and metric views | Dashboards read gold or metric views only — never silver. A dashboard that needs silver is a missing gold product |
| Consistent business definitions | **Metric views** in Unity Catalog | Sales, margin, availability and markdown are defined once, in one place, and consumed identically by SQL, dashboards, the natural-language interface and external BI. This is what finally kills the "three versions of gross margin" problem |
| Self-service questions from non-analysts | **AI/BI Genie**, scoped per domain over certified gold products | Genie spaces are scoped to a curated set of certified tables with documented columns. An ungoverned Genie space over the whole catalog produces confident wrong answers, which is worse than no answer |
| Data science and ML | Notebooks, **feature tables in Unity Catalog**, MLflow | Feature tables are governed objects in `ml_features`, not project-local artefacts. Training and serving read the same definition |
| Operational model consumption (UC-2, UC-4, UC-6) | **Model serving endpoints** | The replenishment engine and personalisation call an endpoint; they do not read tables. This keeps the operational contract narrow and versionable |
| Existing enterprise BI tool | Direct connection to SQL warehouses over the governed layer | Existing investment is preserved; governance is not bypassed, because the warehouse enforces the same policies |
| Suppliers and agencies | **OpenSharing** from `gold_supplier_portal` | §7.6 |
| Operational applications needing low-latency lookups | A serving store fed from gold | Do not serve a store-colleague app by querying the analytical warehouse on every request. The pattern and product choice here should be confirmed against the current platform options **[TBC against current docs]** |

> **DECISION D-07 — Serverless SQL warehouses as the default, with classic compute only where a specific constraint requires it.** **Why:** an analyst population of 400 with bursty, unpredictable demand is the worst possible fit for provisioned capacity — it is either queuing or idling. Fast start-up removes the incentive for analysts to keep a warehouse running "just in case", which is the single largest source of waste we see in comparable estates. **Rejected:** provisioned classic warehouses sized to peak, which is cheaper per unit of work and much more expensive per unit of *useful* work, and which reintroduces capacity planning as a standing activity. Revisit for any workload found to be steady, predictable and large.

### 5.7 Platform layer

**Workspaces.** The workspace is a working environment, not a security boundary — Unity Catalog is the security boundary. Workspaces are therefore allocated for **operational and residency reasons only**.

| Workspace | Region | Purpose |
|---|---|---|
| `mrg-eu-prd` | EU | Production workloads for EU/UK data; the primary production workspace |
| `mrg-eu-nonprd` | EU | Dev and test; bound to `mrg_dev` and `mrg_tst` catalogs |
| `mrg-apac-prd` | APAC | Production for APAC-resident data where residency requires in-region processing |
| `mrg-amer-prd` | Americas | Production for Americas data |
| `mrg-eu-sandbox` | EU | Analyst and data-science exploration; separate cost centre, separate budget, aggressive policies |

> **DECISION D-08 — Three regional production workspaces, one metastore per region, one shared governance model.** **Why:** data residency in 14 countries cannot be met by a single-region deployment, and processing location — not just storage location — is what several regulators care about. A metastore is regional, so multi-region necessarily means multiple metastores; cross-region access is then provided by OpenSharing rather than by direct grants. **Rejected:** a single global workspace and metastore (simplest to operate, fails the residency test), and a workspace per country (14 workspaces, 14 sets of policies, and an operations team that spends its life on drift). Confirm the current cross-metastore access options at design time **[TBC against current docs]**.

**Compute strategy.**

| Workload | Compute | Reason |
|---|---|---|
| Scheduled pipelines and jobs | Serverless job compute | No cluster management, no idle, start-up cost is amortised over the run |
| Always-on streaming (3 pipelines) | Dedicated job compute, right-sized, autoscaling within narrow bounds | Continuous workloads are the one case where a persistent cluster is efficient |
| SQL and BI | Serverless SQL warehouses (§5.6) | Bursty demand |
| Data science exploration | Serverless notebook compute under a policy, in the sandbox workspace | Governed by policy and budget, not by asking people to be careful |
| Ad-hoc heavy engineering (migration backfills) | Job compute under a policy, spot workers with an on-demand driver, hard auto-termination | Interruptible work at a lower cost, without risking the driver |

**Cost controls — five, from the outset, not retrofitted.**

1. **Enforced tagging** via compute policies for classic compute and usage policies for serverless, so that every unit of consumption carries `cost_centre`, `domain` and `environment`. Untagged consumption is unattributable and therefore unmanageable; a policy that permits it is a bug.
2. **Budgets with alert thresholds** per domain and per environment, reviewed weekly in the first six months and monthly thereafter.
3. **Attribution reporting** built in Phase 0 from the billing and pricing system tables, joined correctly (a temporal range join on the price validity window — a plain equality join on the SKU fans out across historical price versions and silently inflates every figure).
4. **Aggressive auto-stop** everywhere, plus a standing report of the ten most expensive queries, pipelines and dashboards each week, with a named owner for each.
5. **Storage lifecycle and retention** applied per zone, with automated table maintenance enabled so that optimisation and file cleanup are not a task someone forgets.

> **DECISION D-09 — Cost attribution is built in Phase 0, before the first production pipeline.** **Why:** cost opacity is one of the named failures of the current estate (§2.3). A platform that cannot answer "what does this report cost" reproduces the problem in a new place, and retrofitting tags across hundreds of jobs is far more expensive than enforcing them from job one. **Rejected:** deferring cost management to Phase 3 "once there is something to measure", which is the normal approach and the reason the conversation is always uncomfortable.

### 5.8 Architecture decisions, consolidated

| ID | Decision | Rejected alternative |
|---|---|---|
| D-01 | Ladder-first ingestion: most managed mechanism that meets the need | One uniform pattern for all sources |
| D-02 | Declarative pipelines as the default transformation framework, orchestrated by Lakeflow Jobs | Hand-written notebook pipelines |
| D-03 | SAP via log-based CDC, ODP/SLT held as a costed fallback | Nightly full export; SAP-native extraction as primary |
| D-04 | Scheduled available-now triggers unless a use case demands continuous | Always-on streaming everywhere |
| D-05 | Catalog per environment, schema per domain | Catalog per domain; single catalog with prefixes |
| D-06 | ABAC policies on governed tags for masking and row filtering | Per-table masks and filters as the primary mechanism |
| D-07 | Serverless SQL warehouses by default | Provisioned classic warehouses sized to peak |
| D-08 | Three regional production workspaces, regional metastores, cross-region via sharing | Single global workspace; workspace per country |
| D-09 | Cost attribution built in Phase 0 | Cost management deferred to Phase 3 |
| D-10 | Infrastructure and workloads deployed as **Declarative Automation Bundles** from Git (§9.4) | UI-created jobs promoted by export/import |
| D-11 | Data products published as governed **schemas with contracts** (§6) | A central team owning all transformation |
| D-12 | Legacy EDW read by federation during migration; only unrecoverable history is copied | Full warehouse migration |
| D-13 | Pseudonymisation at the bronze-to-silver boundary (§7.2) | Full-estate masking policies over identifier-bearing tables |
| D-14 | Supplier exchange via OpenSharing (§7.6) | A supplier portal; 1,200 per-supplier extracts |

D-10 is stated in full in §9.4, D-11 in §6.1, D-13 in §7.2 and D-14 in §7.6, alongside the material they govern.

---

## 6. Data products and domain ownership

### 6.1 How the estate is carved

Meridian is not ready for a full data mesh and should not attempt one. There is no existing culture of domain data ownership, and pushing accountability onto teams that have never held it produces orphaned datasets with a domain label on them. The recommended model is **federated ownership with a strong platform core**:

- A **central platform team** owns ingestion to bronze, Unity Catalog structure, security policy, CI/CD, cost management and the shared reference domain. Bronze is *plumbing* and should be built once, by specialists.
- **Domain teams** own silver and gold within their domain: the business logic, the quality rules, the contract and the roadmap.
- Domain ownership is **earned, not assigned**. A domain graduates from platform-built to domain-owned when it has a named owner, a product manager and at least one engineer who has passed the enablement path (§9.6). Until then the platform team runs it on the domain's behalf, explicitly and with an end date.

> **DECISION D-11 — Federated ownership with a strong platform core, not a pure mesh and not a central monolith.** **Why:** the central-monolith model is the current state and it produced a 340-item backlog; the pure-mesh model presumes capability that does not exist yet. **Rejected:** full data mesh from day one (fails on capability), and a central team owning all transformation (fails on throughput, and re-creates the bottleneck we were hired to remove).

### 6.2 The domains

| Domain | Owner (client role) | Products published | Primary consumers |
|---|---|---|---|
| **Sales & Trading** | Director of Commercial Analytics | `gold_trading`: conformed sales fact (basket line), trading day aggregate, store performance, channel view, sales metric view | Finance, Commercial, Store Ops, Board reporting |
| **Customer** | Head of Loyalty & CRM | `gold_customer_analytics`: customer profile, segment assignment, lifetime value, consent state, audience sets | Marketing, Digital, Service, Loyalty |
| **Product & Merchandising** | Head of Master Data | `gold_merchandising`: conformed product dimension (SCD2), hierarchy, supplier linkage, price and markdown history | Every other domain — this is the most-depended-on product in the estate |
| **Supply Chain** | Director of Supply Chain Planning | `gold_supply_chain`: stock position by SKU-location, movement fact, inbound pipeline, forecast output, availability measure | Supply Chain, Store Ops, Commercial, E-commerce |
| **Finance** | Group Financial Controller | `gold_finance_reporting`: trial position, margin bridge, FX-converted reporting views, statutory hierarchy | Group Finance, regional controllers, Audit |
| **Supplier** | Head of Procurement | `gold_supplier_portal`: OTIF and quality scorecard, delivery detail, claims position — **shared externally** | Procurement, and ~1,200 suppliers via OpenSharing |
| **Marketing** | Marketing Operations Lead | `gold_customer_analytics` (shared with Customer): campaign performance, spend, attribution, suppression lists | Marketing, Agencies, Finance |
| **People** | HR Analytics Lead | `silver_people` only in Phases 1–3; gold deferred | Restricted; HR and Finance cost allocation |
| **Platform (shared)** | Head of Data Platform (services-led initially) | `silver_reference` (store, calendar, FX, hierarchy), `ops_platform` (quality results, cost attribution, lineage extracts, run metadata) | Everyone |

### 6.3 What a data product must publish

A schema is not a data product. To be listed as a product in the catalogue, a schema must publish all seven of the following. The platform team refuses to certify anything missing an item, and that refusal is the mechanism by which quality is maintained.

| # | Element | Form |
|---|---|---|
| 1 | **Owner** | A named group (`mrg-<domain>-owner`) and a named human product manager |
| 2 | **Purpose and grain** | One paragraph in the schema comment; one sentence per table stating its grain |
| 3 | **Schema contract** | Column names, types, nullability, and a documented change policy: additive changes are announced, breaking changes require a new version and a deprecation window (minimum 90 days) |
| 4 | **Quality guarantees** | The specific expectations enforced, the action on failure (drop, quarantine, fail), and the published pass rate |
| 5 | **Freshness SLO** | "Complete for day D-1 by 06:00 local, 99% of days", measured and published, not asserted |
| 6 | **Classification and residency** | Governed tags on every table and every personal-data column |
| 7 | **Tier** | `certified` (SLO-backed, supported, safe for executive reporting), `curated` (maintained, no SLO), `experimental` (no guarantees, no external consumption, auto-expiring) |

Tier is a `product_tier` tag and it is visible everywhere the table is: in the catalogue, in the natural-language interface's scope, and in dashboards. A consumer should never have to ask whether a number can be trusted — the platform should already have told them.

### 6.4 How ownership maps to the catalog

| Concept | Unity Catalog expression |
|---|---|
| Domain | A set of schemas (`silver_<domain>`, `gold_<domain>`) within each environment catalog |
| Domain ownership | `ALTER SCHEMA … OWNER TO mrg-<domain>-owner` — a group, always |
| Product contract | Schema and table comments, column comments, governed tags; machine-readable form generated into `ops_platform` for the catalogue |
| Publication | `GRANT USE SCHEMA, SELECT ON SCHEMA gold_<domain> TO mrg-<consumer>-reader` |
| Internal work | Silver schemas are granted only to the owning domain and to named downstream domain engineers, with each cross-domain grant recorded as a dependency |
| External publication | A share from `gold_supplier_portal` only; no other schema is shareable, enforced by policy and checked weekly |
| Deprecation | A table tagged `lifecycle = deprecated` with an end date in the comment; the weekly report names its remaining consumers from lineage |

**Cross-domain dependency rule.** A domain may read another domain's **gold** products freely. Reading another domain's **silver** requires an explicit, recorded agreement, because it couples the two teams' release cycles. Reading another domain's **bronze** is prohibited. This one rule prevents the slow collapse of a layered architecture back into point-to-point coupling — which is precisely what §2.3 describes happening to the current estate.

---

## 7. Governance, security and compliance

### 7.1 The obligation landscape

| Obligation | Where it bites | Architectural consequence |
|---|---|---|
| GDPR across 14 countries (plus UK GDPR) | Loyalty, clickstream, marketing, HR, Salesforce | Pseudonymisation, purpose limitation, erasure, records of processing |
| ePrivacy / consent | Clickstream, marketing, app | Consent state is a join condition, not a filter applied at the end |
| Data residency and transfer | EU, UK, and at least 3 APAC jurisdictions with local requirements | Regional metastores and regional processing (D-08); transfer mechanism documented per flow |
| Works councils | 5+ countries | Employee-level analysis is gated on consultation (§3.10) |
| Statutory audit / financial controls | Finance domain | Immutable as-reported history, evidenced lineage, segregation of duties |
| Food safety record-keeping | Cold chain | Extended retention, tamper-evident evidence trail |
| Payment card rules | POS tender data | Keep it **out of scope** — tokenise or drop at the boundary |
| Third-party data licences | Panel and competitor data | Redistribution restrictions expressed as grants and share exclusions |

### 7.2 PII handling and pseudonymisation

The design principle is **separate the identifier from the behaviour**.

1. Direct identifiers (name, email, phone, address, loyalty card number, device ID) are extracted at the bronze-to-silver boundary into a single restricted schema, `silver_customer_pii`, which is readable by two service principals and one small approval group. Nothing else reads it.
2. Everything downstream carries a **pseudonymous customer key** — a stable surrogate with no derivable relationship to the identifier. Analytics, features, models and shares use the surrogate.
3. Re-identification happens in exactly one place: a governed join, executed by an approved process, logged every time. Marketing's audience activation is such a process; an analyst's curiosity is not.
4. Where personal data must appear in an analytical table, the column is tagged and an ABAC policy masks it by default. Access to the unmasked value requires membership of a `mrg-pii-approved-<domain>` group with an expiry date and a recorded justification.
5. Bronze retains the source payload including identifiers, and is accessible only to the platform team and ingestion identities. This is deliberate: it is what makes the pipeline replayable, and it is why bronze access is the most tightly held privilege on the platform.

> **DECISION D-13 — Pseudonymisation at the bronze-to-silver boundary, not at the consumption layer.** **Why:** masking at consumption means the personal data is present in every downstream table, and the control is a policy that can be misconfigured. Separating identifiers at the boundary means most of the estate simply does not contain personal data — a structurally stronger position, and a much cheaper conversation with the DPO and with auditors. **Rejected:** full-estate masking policies over tables that contain identifiers everywhere (simpler to build, weaker to defend, and it makes erasure a search across the whole estate instead of a targeted operation).

### 7.3 Right to erasure — the mechanics

Erasure is a pipeline, not a ticket. The architect should treat the following as a design specification.

| Step | Mechanism | Note |
|---|---|---|
| 1. Request capture | Erasure requests land in a control table in `ops_platform` from the client's privacy request tool, with subject identifier, request timestamp and jurisdiction | A control table is required because requests arrive continuously and must be executed in batches |
| 2. Subject resolution | Resolve the request to the pseudonymous key(s) via `silver_customer_pii` | One person may hold multiple identifiers across countries; this is the step that most implementations get wrong |
| 3. Scope determination | Lineage from `silver_customer_pii` and the `data_classification = p2` tag enumerate every table holding the subject's data | Lineage is the evidence that the scope is complete; this is a governance capability, not a convenience |
| 4. Delete at the source layer first | Delete in **bronze**, then propagate downstream — Databricks guidance is explicit that complete deletion is preferable to obfuscation, and that deleting at the source layer first is the correct order | A `MERGE … WHEN MATCHED THEN DELETE` is the recommended form when deleting many subjects in one run |
| 5. Propagate | Materialised views handle source deletions automatically. **Streaming tables are append-only** — deletion requires either deleting from the streaming table with DML and configuring the downstream read to skip change commits, or a full refresh (which reprocesses everything and risks loss if source retention has expired). **Design for this now**: any streaming table holding personal data must have a documented erasure route agreed before it goes to production | This is the single most commonly missed detail in lakehouse GDPR designs |
| 6. Physically remove | Deletion vectors mark rows deleted without rewriting files, so a `REORG TABLE … APPLY (PURGE)` is required to rewrite the affected files, followed by `VACUUM` to delete them | Until `VACUUM` runs, the data is still physically present. The erasure SLA must account for the retention threshold |
| 7. Close the copies | Time travel (bounded by the log and deleted-file retention properties), clones, and **shares — which default to including history on current runtimes**, letting a recipient time-travel to a pre-deletion version | Shares carrying personal data must be created without history, and that must be a checked control, not a habit |
| 8. Evidence | Record request, resolution, tables affected, execution timestamps and completion in `ops_platform`; retain for the statutory period | The evidence is the deliverable. The deletion is assumed; the proof is what is audited |
| 9. Upstream | The obligation covers Kafka, source files and source systems too, not only the lakehouse | Kafka retention (7 days, §3.4) bounds the exposure; source-system erasure remains the source owner's obligation and must be tracked jointly |

**Committed SLA (illustrative):** erasure executed within **14 days** of a verified request, with physical removal complete within **21 days**, against a regulatory limit of one month. The gap between 14 and 21 days is the retention threshold, and it must be explained to the DPO up front rather than discovered during an audit.

### 7.4 Residency

| Control | Implementation |
|---|---|
| Storage residency | Managed storage per regional metastore; EU data in EU storage, and so on |
| Processing residency | Regional workspaces; jobs on EU-resident data run in the EU workspace |
| Cross-border analysis | Where a global view is required, it is built from **aggregated or pseudonymised** regional products shared cross-region, not from raw personal data |
| Enforcement | `data_residency` tag drives an ABAC row filter keyed on the analyst's regional group, so a cross-region query returns only permitted rows rather than failing opaquely |
| Evidence | Audit system tables record who read what, from where |

**An honest caveat:** residency has a real cost. It means some pipelines are built three times and some global questions are answered on aggregates rather than detail. Confirm with Legal, per country, which flows genuinely require in-region processing rather than in-region storage — the answer is usually narrower than the initial assumption, and each narrowing saves material effort.

### 7.5 Access model for 400+ analysts

The model must survive the arrival of the 401st analyst without anyone doing anything.

| Element | Design |
|---|---|
| Identity | Federated from the corporate directory; account-level groups synchronised; no local accounts |
| Provisioning | Directory group membership is the only entitlement mechanism. Joining `mrg-analyst-emea` grants a working set of access on the next sync, with no ticket |
| Default entitlement | Every analyst gets read on `certified` gold products in their region, plus the metric views. That default covers an estimated 80% of demand |
| Escalation | Additional access is a group join with an approver and an expiry, requested in the client's existing access tool |
| Personal data | Never in the default. Always a separate, expiring, justified group |
| Compute | Analysts are granted use of a warehouse class, never the ability to create compute |
| Review | Quarterly recertification driven from the audit tables — groups with no queries in 90 days are flagged for removal, and a group nobody uses is a group that should not exist |
| Onboarding | A new analyst is productive on day one via the default entitlement and the catalogue. If onboarding requires a conversation with the platform team, the model has failed |

### 7.6 Sharing with suppliers and agencies

| Recipient | Mechanism | Contents | Controls |
|---|---|---|---|
| ~1,200 suppliers | **OpenSharing** from `gold_supplier_portal` | Each supplier sees only its own OTIF, quality and claims rows | One recipient per supplier; a row filter keyed on the recipient's supplier identity; **share created without history**; no personal data; no competitor data |
| Media and creative agencies | **OpenSharing** of audience definitions and campaign performance | Pseudonymous keys and aggregate performance only | No direct identifiers cross the boundary; activation happens through the marketing platform, not through the share |
| Joint-venture partners (2 markets) | **OpenSharing**, Databricks-to-Databricks where the partner is on the platform | Agreed trading aggregates | Contractually scoped; reviewed quarterly |
| External auditors | Time-boxed read on `gold_finance_reporting` plus lineage and audit extracts | As-reported figures with provenance | Expiring group; every access logged |
| Third-party panel data received | **OpenSharing** inbound where the vendor supports it | — | The licence's redistribution restriction is expressed as an explicit exclusion from every outbound share, and tested |

> **DECISION D-14 — Supplier data exchange via OpenSharing, not a portal or per-supplier extracts.** **Why:** 1,200 suppliers times a file extract is an integration estate in its own right, and the current alternative (emailed spreadsheets) is both a governance failure and a source of disputes. Sharing is zero-copy, governed by the same access model, and within a region incurs no egress cost. **Rejected:** building a supplier web portal (a product with a roadmap, a support burden and an authentication estate, for a data-delivery problem), and per-supplier SFTP extracts (1,200 jobs and 1,200 ways to be wrong). Note that smaller suppliers will not consume a share directly; a thin UI over the same governed data serves them, reading the identical tables. Confirm cross-region and cross-cloud transfer cost implications for non-EU suppliers at design time **[TBC against current docs and cloud pricing]**.

### 7.7 Audit and lineage evidence

| Question an auditor will ask | Where the answer comes from |
|---|---|
| Who accessed personal data, and when? | The audit system table, filtered by event date, on the restricted schema |
| What feeds this reported figure? | Table and column lineage, automatically captured, down to column level, covering notebooks, jobs, pipelines, dashboards and queries |
| Was this control in place on 3 March? | Policy definitions held in version control, with the deployment history as evidence |
| Has this erasure request been completed? | The erasure control table plus the audit trail of the executing job |
| Who changed this permission? | Audit table, Unity Catalog service events |
| Can you prove the reported number was not altered afterwards? | Append-only finance silver with restatement flags, plus table history within the retention window |

Two practical limits the architect must design around: lineage covers objects registered in Unity Catalog — path-based access and renamed objects break it, which is another reason external paths are registered as volumes and external locations rather than accessed directly. And audit records are retained for a defined window by default; if the client's statutory obligation is longer, a scheduled export of the audit tables into `ops_platform` under the required retention is a **Phase 1 deliverable**, not an afterthought. Confirm current retention and any configurable options **[TBC against current docs]**.

---

## 8. Delivery plan

### 8.1 Shape of the programme

Four phases over 96 weeks. Each phase ends in a **gate**: a decision point with defined evidence, at which the programme can be stopped, re-scoped or continued. A programme without real gates is a programme that cannot be stopped, and one that cannot be stopped cannot be trusted.

| Phase | Weeks | Theme | Gate evidence |
|---|---|---|---|
| 0 | 1–6 | Mobilise, prove, re-base | Platform foundations live; three source connections proven end to end; benefits re-based on client actuals; Phase 1 plan confirmed |
| 1 | 7–16 | Thin slice | One region, one domain, in production, with a real consumer using it in anger; decommission of at least 4 spreadsheets |
| 2 | 17–40 | Core domains | Customer, Product, Sales, Supply Chain and Finance silver and gold live for all regions; forecasting in pilot; 3 use cases delivering measured value |
| 3 | 41–72 | Scale and migrate | All 14 countries; 80% of active EDW consumers migrated; dual-run reconciliation passing; Hadoop workloads migrated or retired |
| 4 | 73–96 | Decommission and hand over | EDW and Hadoop off; client team running the platform; services role reduced to advisory |

### 8.2 Phase 0 — Mobilise and prove (weeks 1–6)

| Week | Deliverable |
|---|---|
| 1 | Cloud accounts, network design signed off, **private connectivity requests raised** (the long pole — start on day one). Identity federation design agreed |
| 1–2 | Landing-zone triage: what in the Hadoop cluster is worth keeping. Expect to recommend leaving 60%+ behind |
| 2 | Unity Catalog metastore, catalogs, initial schemas, group taxonomy, governed tags defined |
| 2–3 | CI/CD skeleton: repository structure, bundle definitions, dev/test/prod targets, first automated deployment |
| 3–4 | Three proving connections: SAP (one table group), POS EU (one country), PIM. Each landing into bronze, end to end |
| 3–4 | Cost attribution reporting live (D-09) |
| 4–5 | Benefits re-based: identity match-rate sample for UC-1, forecast-accuracy baseline for UC-2, availability measurement basis for UC-3 |
| 5 | PII discovery pass over the in-scope EDW subset and the three proven sources |
| 5–6 | Phase 1 backlog agreed with named business owners; gate pack prepared |

**What "proven" means:** data lands, is queryable, has a quality expectation attached, has lineage, is tagged, appears in cost reporting, and was deployed by the pipeline rather than by hand. Anything less is a demonstration, not a proof.

### 8.3 Phase 1 — The thin slice (weeks 7–16), first value at week 10

The thin slice is **one region (EU), one business outcome (daily trading and stock position), one consumer group (regional Commercial and Supply Chain)**. It is deliberately narrow and deliberately vertical: it exercises every layer of the architecture rather than building one layer broadly.

| Week | Deliverable |
|---|---|
| 7–8 | POS EU ingestion at full country scope, bronze to silver conforming for one of three POS schemas |
| 7–9 | SAP inventory movements CDC into bronze and silver |
| 8–9 | `silver_reference` (store master, calendar, FX) with a named owner and a maintenance process |
| 9 | `gold_trading` first product: daily sales by store, SKU and day, with margin |
| **10** | **First value: the regional daily trading dashboard in production**, replacing four spreadsheets. Certified, SLO-backed, with published freshness |
| 10–12 | Stock position product; availability measure defined and agreed (expect a fortnight of argument about the definition — budget for it, it is real work) |
| 12–14 | Quality framework in anger: expectations, quarantine, alerting, the weekly quality report |
| 14–15 | Second POS schema conformed (proves the pattern generalises) |
| 15–16 | Gate pack: measured freshness, measured quality, measured cost per product, user adoption, and a candid list of what was harder than expected |

**Why week 10 and not week 6.** A dashboard can be produced in three weeks. A dashboard that is governed, tested, SLO-backed, cost-attributed, deployed from version control and owned by a named business team takes ten. The second one takes two. Phase 1 buys the *second* one.

### 8.4 Phase 2 — Core domains (weeks 17–40)

Five workstreams run in parallel, each with its own domain owner:

| Workstream | Weeks | Lands |
|---|---|---|
| Sales & Trading | 17–30 | All three POS schemas conformed; all 14 countries; e-commerce orders joined; `gold_trading` complete with metric views |
| Product & Merchandising | 17–26 | PIM ingestion; conformed SCD2 product dimension; the "to be classified" quality gate; hierarchy published |
| Supply Chain | 22–36 | SAP movements and purchasing; EDI; stock position; inbound pipeline; UC-3 in pilot; UC-2 forecast in pilot |
| Finance | 20–34 | SAP finance; FX; statutory hierarchy; trial position; **parallel run against the EDW begins at week 30** |
| Customer | 26–40 | Clickstream streaming ingest; identity resolution; `silver_customer_pii` and pseudonymisation; consent integration; UC-1 first release |

Cross-cutting in the same window: supplier scorecard and the first OpenSharing pilot with 20 suppliers (weeks 30–38); analyst onboarding at scale from week 24; the enablement programme (§9.6) running continuously from week 17.

**Gate at week 40:** three use cases delivering measured value; finance parallel run showing variance inside tolerance; at least two domains operating with genuine client-side ownership.

### 8.5 Phase 3 — Scale and migrate (weeks 41–72)

This is where the programme either succeeds or becomes permanent. Discipline is everything.

| Workstream | Weeks | Lands |
|---|---|---|
| Consumer migration | 41–68 | The ~620 active EDW reports triaged: migrate, rebuild, merge or retire. Expect **35–45% to be retired outright** — that is the normal finding and it must be presented as a win |
| Dual-run and reconciliation | 41–64 | Automated daily reconciliation between EDW and lakehouse for every migrated measure |
| Hadoop migration | 44–62 | Workloads migrated or retired; retained history moved; the cluster drained rather than lifted |
| Use case scale-out | 41–72 | UC-2 and UC-3 to production across all regions; UC-4 markdown to production; UC-6 personalisation pilot |
| Regional roll-out | 44–66 | APAC and Americas workspaces to full production; residency controls verified per country |
| Supplier sharing | 50–66 | Scale from 20 to 1,200 suppliers |

### 8.6 Migration approach — strangler, dual-run, decommission gates

**The strangler pattern, applied concretely.** The EDW is not migrated. Its *consumers* are migrated, one at a time, to products built from source. Each migration follows the same seven steps:

1. Identify the consumer (a report, an extract, a downstream system) and its true owner.
2. Determine whether it should exist at all. Roughly 40% should not.
3. Trace its business logic in the legacy ETL and document it. This is archaeology, and it is the expensive part — budget 3–5 days per non-trivial consumer, not 1.
4. Rebuild the logic against the lakehouse gold product. Not a lift of the SQL — a re-derivation, reviewed by the business owner.
5. **Dual-run** for a defined period: both systems produce the number daily, and an automated reconciliation job compares them, records the variance, and explains every difference above tolerance.
6. Cut over the consumer. The legacy job keeps running.
7. When all consumers of a legacy job have cut over, the legacy job is disabled — not deleted — for 30 days, then removed.

**Reconciliation is a product, not an activity.** Build it in Phase 2, before it is needed: an automated job, a reconciliation results table in `ops_platform`, a dashboard showing every migrated measure's variance over time, and a rule that a measure must show **zero unexplained variance for 30 consecutive days** before its consumer may cut over. "Explained" means written down, agreed and attributed to a specific cause — usually a defect in the legacy logic, which is itself a valuable finding to publish.

**Decommission gates.** The legacy warehouse is switched off when, and only when, all five are met:

| Gate | Evidence |
|---|---|
| G1 — No active consumers | 90 consecutive days with zero queries from anything other than the reconciliation job |
| G2 — Reconciliation clean | Every migrated measure at zero unexplained variance for 30+ days |
| G3 — History preserved | The retained history subset exported, validated by row and checksum, and readable |
| G4 — Regulatory retention satisfied | Legal has confirmed, in writing, what must be kept and for how long, and where it now lives |
| G5 — Rollback expired | 60 days since the last cutover with no rollback invoked |

The same five gates apply to the Hadoop cluster, assessed separately.

**Dual-run cost is a named, budgeted line item**, not an overrun. Running both platforms for 24 weeks is expensive and entirely predictable; §10.4 carries it explicitly. The failure mode here is not the cost — it is a dual-run with no end date, which is why G1–G5 are dated and owned.

### 8.7 What the client must provide

The programme cannot deliver these, and each one has a lead time that starts when it is asked for, not when it is needed.

| # | Client obligation | Needed by | Consequence of delay |
|---|---|---|---|
| 1 | Executive sponsor with cross-functional authority | Week 1 | Prioritisation stalls; every decision escalates |
| 2 | Named business owners for each of the 8 use cases | Week 4 | Value is unmeasurable and unattributable |
| 3 | SAP basis team availability and an extraction decision | Week 2 | Critical path; a 4-week delay here is a 4-week delay to Phase 2 |
| 4 | Network and private connectivity, firewall and DNS | Week 1 request, week 6 delivery | Everything is blocked. This is the most common cause of a late Phase 0 |
| 5 | Identity federation and group provisioning | Week 3 | Access model cannot be implemented; workarounds become permanent |
| 6 | Source system credentials and read access, all 12 sources | Rolling, per phase | Per-source slip |
| 7 | Data protection impact assessment and DPO engagement | Week 2 | Customer domain (Phase 2) blocked |
| 8 | Works-council consultation initiated | Week 4 | HR domain deferred (already assumed) |
| 9 | Client-side engineers embedded in pods, from Phase 1 | Week 7 | Knowledge transfer fails; the programme never ends |
| 10 | Legacy ETL documentation and access to the people who wrote it | Week 20 | Migration archaeology cost doubles |
| 11 | Decision authority to retire reports | Week 40 | Migration scope grows by 40% |
| 12 | Kafka retention increase to 7 days and a schema-registry commitment | Week 12 | Clickstream reliability capped; incidents recur |

---

## 9. Team, ways of working and enablement

### 9.1 Pod shape

The delivery unit is a **pod**: 6–8 people, one domain, end-to-end accountability from source to consumer. Pods do not hand work between themselves. A pod that cannot deliver a product without another pod's sprint capacity is wrongly drawn.

| Role | Per pod | Responsibility |
|---|---|---|
| Pod lead / senior data engineer | 1 | Technical accountability, design review, mentoring |
| Data engineer | 2–3 | Pipelines, quality, tests |
| Analytics engineer | 1 | Silver-to-gold modelling, metric definitions, dashboards |
| Client-side engineer (embedded) | 1–2 | Learns by building; owns the product after handover |
| Business analyst / product owner (client) | 0.5–1 | Requirements, acceptance, adoption |

Plus a standing **platform pod** (not per-domain): 4–6 people owning Unity Catalog, CI/CD, security policy, cost, observability and the shared reference domain. The platform pod's customers are the other pods, and its success measure is how little the other pods have to think about the platform.

### 9.2 Rough FTE by phase (illustrative)

| Role | Ph 0 (w1–6) | Ph 1 (w7–16) | Ph 2 (w17–40) | Ph 3 (w41–72) | Ph 4 (w73–96) |
|---|---|---|---|---|---|
| Engagement lead / principal architect | 1.0 | 1.0 | 1.0 | 0.8 | 0.5 |
| Solution architect | 1.0 | 1.0 | 1.5 | 1.5 | 0.5 |
| Platform engineers | 2.0 | 3.0 | 4.0 | 4.0 | 2.0 |
| Data engineers | 2.0 | 5.0 | 14.0 | 16.0 | 6.0 |
| Analytics engineers | 0.5 | 2.0 | 5.0 | 6.0 | 2.0 |
| ML engineers / data scientists | 0 | 0 | 3.0 | 4.0 | 1.0 |
| Data governance / security specialist | 1.0 | 1.0 | 1.5 | 1.5 | 0.5 |
| Migration specialists (EDW/Hadoop) | 0.5 | 0.5 | 2.0 | 5.0 | 2.0 |
| Delivery manager / scrum | 0.5 | 1.0 | 2.0 | 2.0 | 1.0 |
| Enablement lead | 0 | 0.5 | 1.0 | 1.0 | 1.0 |
| **Services total** | **8.5** | **15.0** | **35.0** | **41.8** | **16.5** |
| **Client-side (required)** | **4.0** | **8.0** | **18.0** | **24.0** | **28.0** |

The crossover matters more than the totals. Client-side FTE overtakes services FTE during Phase 3 by design. **If that crossover does not happen, the engagement has failed regardless of what was built.**

### 9.3 Client-side roles to be filled

| Role | FTE | Note |
|---|---|---|
| Head of Data Platform | 1 | Accountable owner from week 1. Hire or appoint before the programme starts, not during it |
| Domain data owners | 8 x 0.3 | Existing business leaders, part-time, named |
| Domain product managers | 5 | New or repurposed; the most commonly missing role |
| Data engineers (embedded, then owning) | 12–16 | Largely from the existing 48-person team, retrained |
| Platform / DevOps engineers | 4 | Own CI/CD, cost and infrastructure after handover |
| Data governance lead | 1 | Works with the DPO; owns the tag taxonomy and access model |
| Analytics engineers | 6–8 | Sit with the domains, not in a central pool |

### 9.4 CI/CD and environments

> **DECISION D-10 — All platform objects and workloads are deployed as Declarative Automation Bundles from Git.** Jobs, pipelines, schemas, volumes, dashboards, quality monitors and grants are defined in configuration in the repository and deployed by the pipeline. **Why:** the current estate's inability to answer "what changed" (§2.3) is the root cause of most of its incidents; code in version control with a deployment history answers it by construction, and it makes the three environments genuinely identical in shape. **Rejected:** creating jobs in the UI and promoting by export/import — faster on day one, and it guarantees environment drift, undocumented production changes, and a platform nobody can rebuild.

| Element | Design |
|---|---|
| Repository | Monorepo, one directory per domain, shared libraries in `common/`; trunk-based with short-lived feature branches |
| Targets | `dev` (development mode: prefixed resources, paused schedules, per-developer isolation), `tst`, `prd` (production mode: service principal identity, Git branch validation, no cluster overrides) |
| Identity | Deployment to test and production runs as a service principal using workload identity federation from the CI system — **no long-lived tokens in CI** |
| Promotion | Merge to main deploys to test automatically; production deployment is a gated action from the same commit |
| Environment data | Dev holds a representative, masked subset — not 4% of prod with a different schema (§2.3). Producing that subset is a Phase 0 deliverable |
| Drift detection | A weekly job compares deployed state against the repository and against the declared grant model; drift is a defect with an owner |

### 9.5 Testing and quality gates

| Level | What | Gate |
|---|---|---|
| Unit | Transformation functions tested in isolation against fixtures | Must pass to merge |
| Contract | Bronze schema assertions; a source schema change fails the build rather than production | Must pass to merge |
| Data quality | Pipeline expectations on every silver table: uniqueness of the business key, referential integrity to conformed dimensions, domain-value validity, volume anomaly | Failing rows quarantined or dropped by declared policy; violation rates published |
| Reconciliation | Migrated measures compared to the legacy system daily | Zero unexplained variance for 30 days before cutover |
| Freshness and completeness | Automated monitoring on every certified product | Breach pages the owning pod |
| Performance | Critical dashboard and query response times tracked over time | Regression beyond threshold blocks release |
| Security | Grant model validated against the declared model; a hand-made grant is flagged | Weekly; exceptions require sign-off |

**The one rule that carries the most weight:** a table may not be tagged `certified` unless it has expectations, a freshness monitor, an owner and a published contract. Certification is the platform team's only real lever, and it must be used.

### 9.6 Runbooks

Written during Phase 1, not after go-live, and rehearsed:

| Runbook | Covers |
|---|---|
| Late or missing source file | Detection, tolerance, backfill, communication to affected consumers |
| Source schema change | Triage, rescued-data inspection, contract update, downstream impact from lineage |
| Streaming pipeline failure | Checkpoint inspection, restart, replay, gap verification |
| Quality expectation breach | Quarantine review, root cause, reprocess, consumer notification |
| Erasure request execution | The nine steps in §7.3 |
| Access request and revocation | Group model, approval, expiry |
| Cost anomaly | Attribution query, top-consumers report, throttle and escalate |
| Peak trading readiness | Pre-peak checklist, capacity review, freeze window, on-call rota |
| Reconciliation variance | Investigation protocol, explanation register, escalation |
| Disaster recovery | RPO/RTO per zone, restore procedure, verification. Targets **[TBC with the client]** |

### 9.7 Enablement and certification path

Capability transfer is a deliverable with an acceptance criterion, not a goodwill gesture.

| Stage | Audience | Content | Timing |
|---|---|---|---|
| Foundation | All 48 data team members, plus analysts | Lakehouse concepts, Unity Catalog, Databricks SQL, the catalogue and how to find things | Weeks 8–16 |
| Practitioner | 16 embedded engineers | Declarative pipelines, Auto Loader and streaming ingest, testing, bundles and CI/CD, cost engineering | Weeks 17–30, paired with real delivery work |
| Specialist | 6–8 engineers | Streaming at scale, performance and cost optimisation, security and ABAC, migration patterns | Weeks 30–56 |
| Owner | Domain owners and product managers | Data product thinking, contracts, SLOs, quality, the certification process | Weeks 20–40 |
| Certification | Target: 20 engineers certified (Associate level) by week 40; 8 at Professional level by week 72 | | |

Enablement is delivered **in the pods, on the real backlog** — classroom training on a sample dataset produces people who can pass an exam and not a change. The reference poster series (47 verified visual references covering the platform, ingestion, Delta Lake, governance, cost and production engineering) is used as the standing desk reference and as the backbone of the certification track.

**Acceptance criterion for handover:** for three consecutive months, more than 80% of production changes are authored, reviewed and deployed by client engineers, with services in review-only capacity.

---

## 10. Cost model and commercials

> **No list prices appear in this section.** Databricks and cloud pricing change, vary by region, cloud, commit level and contract, and are the wrong thing to hard-code into a business case. What follows is the **structure** of the cost: the drivers, the ratios we typically observe, and the controls. A real estimate is produced by applying the client's measured workload profile to the current price lists during Phase 0 — and it is produced jointly with the Databricks account team and the cloud provider, because commit structure materially changes the answer.

### 10.1 The cost drivers

| Driver | What moves it | Typical share of run cost |
|---|---|---|
| **Platform consumption — data engineering** (pipelines, jobs, streaming) | Volume ingested, transformation complexity, streaming vs batch, trigger frequency, whether pipelines are always-on | 35–50% |
| **Platform consumption — SQL and BI** | Number of analysts, dashboard refresh frequency, query efficiency, warehouse auto-stop discipline, how much gold is pre-aggregated | 25–40% |
| **Platform consumption — ML** (training, features, serving) | Model count, retraining frequency, serving request volume and latency target | 5–15% |
| **Cloud storage** | Total retained volume, retention policy, file layout, how aggressively maintenance runs | 5–10% |
| **Cloud egress and networking** | Cross-region replication, cross-cloud sharing, private connectivity | 2–8%, and the most commonly forgotten |
| **Ingestion-specific fixed costs** | A CDC ingestion gateway runs on classic compute in the client's network and is **billed continuously, including while the ingestion pipeline is idle** — this makes the SAP connector a standing cost, not a per-run one | Material for SAP; budget it explicitly |
| **Migration effort** (one-off) | Number of consumers, archaeology depth, reconciliation scope | See §10.4 |
| **Dual-run** (one-off, time-boxed) | Legacy platform run cost for the overlap period, plus the reconciliation workload | See §10.4 |

The three levers that move platform consumption most, in our experience, in order:

1. **Trigger frequency and always-on pipelines.** The gap between a continuously running stream and the same pipeline on a scheduled available-now trigger is very large, and for most workloads the business cannot tell the difference. This is D-04, and it is the single biggest lever.
2. **Bytes scanned.** Good file layout (clustering on the real filter columns), automatic table maintenance, and materialising the aggregates that dashboards actually query. A dashboard that scans a year of basket lines on every refresh is the classic and expensive mistake.
3. **Idle compute.** Auto-stop, serverless where demand is bursty, and never letting analysts create their own long-running compute.

### 10.2 How we estimate

| Step | Method |
|---|---|
| 1 | Profile actual volumes per source (§3 gives the shape; Phase 0 measures the reality) |
| 2 | Classify each pipeline by mode and frequency from §5.4; count always-on pipelines separately, because they are priced by wall-clock, not work |
| 3 | Benchmark a representative pipeline per class in Phase 0, on real data, and measure consumption directly |
| 4 | Extrapolate by volume, with a peak factor (2.4x for POS at Christmas; 3x for clickstream at Black Friday) applied to the streaming and SQL classes |
| 5 | Model the analyst population's query behaviour from the legacy warehouse's query logs — not from a guess about "400 analysts" |
| 6 | Apply the current price lists per SKU, per cloud, per region, with the client's commit structure |
| 7 | Add cloud storage on the retained-volume projection and egress on the cross-region flows |
| 8 | Add a 25% contingency in Year 1, reducing to 10% in Year 3 as measurement replaces estimation |

Steps 3 and 5 are what separate a defensible estimate from a guess. **Do not price this engagement without them**, and say so to the client.

### 10.3 How we control cost

Five controls, all from §5.7, restated here as commercial commitments:

| Control | Commitment |
|---|---|
| Enforced tagging | 100% of consumption attributable to a cost centre, domain and environment from week 4. Untagged consumption is treated as a defect |
| Budgets and alerts | Per-domain budgets with threshold alerts; reviewed weekly for six months, monthly thereafter |
| Attribution reporting | A cost-per-data-product report, published monthly to domain owners. Owners who see their bill manage it; owners who never see it never do |
| Efficiency review | A monthly review of the ten most expensive pipelines, queries and dashboards, with a named owner and an action for each |
| Retirement | Products with no consumption for 90 days are flagged; certified products with no consumers are decertified. **Retirement is a cost control, and nobody does it unless it is scheduled** |

### 10.4 Illustrative effort and cost profile

Effort in person-weeks from §9.2. **Cost columns are illustrative placeholders** for the shape of the profile, not a quotation.

| Phase | Weeks | Services person-weeks | Platform consumption (relative) | Legacy dual-run | Notes |
|---|---|---|---|---|---|
| 0 | 6 | ~51 | 0.1x | — | Small footprint; benchmarking workloads only |
| 1 | 10 | ~150 | 0.3x | — | One region, one domain |
| 2 | 24 | ~840 | 1.0x (baseline) | Legacy continues at 100% | Five parallel workstreams; the peak of services effort |
| 3 | 32 | ~1,340 | 2.2x | Legacy at 100%, reducing from week 60 | **Peak total cost.** Both platforms running, migration at full rate |
| 4 | 24 | ~396 | 2.6x | Legacy retiring to zero by week 88 | Consumption rises as adoption rises; services fall sharply |
| Run (Yr 3+) | — | ~4 FTE advisory | ~2.8x, then flattening | Zero | Steady state |

Two things to say plainly to the sponsor:

- **Phase 3 is the expensive one**, because both platforms run at once. This is visible, planned and time-boxed by the gates in §8.6. A programme that hides this is a programme that will have an uncomfortable conversation in month 14.
- **Platform consumption keeps rising after delivery stops**, because success means more people using more data. That is the right outcome, and it is why per-product cost attribution matters more than a total budget number. The metric to manage is **cost per unit of consumption**, not total cost.

### 10.5 The commercial construct we would propose

| Phase | Construct | Rationale |
|---|---|---|
| 0 | Fixed price | Scope is well defined; the client should not carry discovery risk |
| 1 | Fixed price against a defined thin slice | We should carry the risk of our own first-delivery estimate |
| 2 | Capped time and materials per workstream, with per-product acceptance | Scope genuinely emerges; a fixed price here is priced with a risk premium the client pays regardless |
| 3 | Capped time and materials, plus a decommission-linked element | Aligns our incentive with the client's actual goal, which is switching the legacy platform off |
| 4 | Reducing retainer, stepped down quarterly against the handover criterion in §9.7 | Makes our exit a contractual event rather than a conversation |

### 10.6 Payback logic

Illustrative, and deliberately conservative — it uses the **lower** end of the benefit range, delays benefit realisation by two quarters against the delivery plan, and assumes only 60% of the identified benefit is actually captured.

| | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Benefit realised (60% of low case, phased) | ~$18m | ~$79m | ~$129m |
| Programme cost (services + platform + dual-run) | ~$16m | ~$18m | ~$8m |
| Net | ~+$2m | ~+$61m | ~+$121m |
| Cumulative | ~$2m | ~$63m | ~$184m |

**Cumulative payback falls in the first half of Year 2** even on this conservative basis. The sensitivity that matters most is not cost — cost is reasonably predictable — it is **whether the business changes its decisions**. A perfect forecast that does not change a safety-stock parameter is worth nothing. That is why §12 measures business outcomes, not platform outputs, and why §8.7 asks for named business owners in week 4.

---

## 11. Risks and mitigations

Likelihood and impact on a 1–5 scale. These are the ten that actually kill programmes of this shape — not a generic register.

| # | Risk | L | I | Mitigation | Owner |
|---|---|---|---|---|---|
| **R1** | **Source access is not granted in time.** Credentials, firewall rules and read permissions arrive weeks after they were promised, and Phase 0 becomes Phase 0 plus six | 4 | 4 | A source-access RACI agreed in week 1 with named owners and dates; access tracked as a standing agenda item; a blocked source is escalated to the sponsor within 5 working days, automatically, not by judgement | Client CIO / Engagement lead |
| **R2** | **SAP extraction politics.** The basis team refuses log-based CDC on the production ERP; the conversation runs for months | 4 | 5 | Engage basis in week 1, not week 8, and bring the cost of the alternative with you. Cost and design the ODP/SLT fallback in Phase 0 so a refusal is a plan change, not a re-architecture. Escalation path pre-agreed to the CFO (§1.5, ask 3) | Client CIO / Solution architect |
| **R3** | **Data quality is materially worse than believed.** Match rates, book-stock accuracy and hierarchy completeness turn out well below assumption, and use-case value collapses | 4 | 4 | Measure the three load-bearing assumptions in Phase 0 (identity match rate, forecast accuracy baseline, stock accuracy) on real samples. Re-base the benefit case at the week-6 gate and say so publicly. Quality remediation is scoped as its own workstream with a business owner, not absorbed silently | Solution architect / Domain owners |
| **R4** | **Dual-run cost triggers a budget crisis in month 12–16.** Both platforms running at peak, with benefits not yet fully landed | 3 | 4 | Budget dual-run explicitly from day one (§10.4) and show the peak on the first cost slide. Bind the decommission gates (§8.6) with dates and owners. Report the legacy platform's remaining consumer count monthly, so the end is visibly approaching | CFO / Programme director |
| **R5** | **Skills gap.** The client team cannot absorb the platform at the rate the plan assumes; handover slips and the services engagement becomes permanent | 4 | 4 | Embed client engineers in pods from week 7, not week 40. Enablement runs on the real backlog (§9.6). Make the 80%-client-authored-changes criterion a contractual handover gate. Accept that 10–15 of the 48 existing team members will not make the transition, and plan for that honestly rather than discovering it | Client Head of Data Platform / Enablement lead |
| **R6** | **Scope creep from the BI backlog.** The 340-item backlog arrives in Phase 2 disguised as requirements; the programme becomes a report factory | 5 | 3 | Backlog triage is an explicit Phase 3 workstream with a retirement target, not a Phase 2 intake. A new request must attach to one of the eight use cases or wait. Publish the retirement count as a headline metric so that *not* building something is visibly a success | Programme director / Domain product managers |
| **R7** | **PII discovery finds more than expected**, particularly in the legacy EDW and in clickstream, triggering a DPO intervention mid-flight | 3 | 4 | Automated classification scan in Phase 0 across the in-scope EDW subset and every source before it is ingested. DPO engaged from week 2 and attends the phase gates. Assume the answer is "more than we thought" and build the pseudonymisation boundary (§7.2) before Phase 2, not after | Data governance lead / DPO |
| **R8** | **Private connectivity and network lead times.** Circuits, endpoints, firewall change windows and DNS take 8–14 weeks in a large enterprise, and nobody counted them | 4 | 5 | Raise every network request in week 1 (§8.7, item 4). Design a temporary, security-approved path for Phase 0 proving work so that engineering is not idle. Track connectivity as a critical-path item on the programme plan with its own RAG | Client CIO / Platform lead |
| **R9** | **Vendor lock-in concerns stall the decision**, usually raised late and by someone not previously in the room | 3 | 3 | Address it in the architecture, not in a slide: open table format, data in the client's own cloud storage account, open sharing protocol for external exchange, transformation logic in SQL and Python in the client's own repository, infrastructure as code. State plainly what *is* proprietary and what exit would actually cost. A credible, costed exit path is more persuasive than a claim that lock-in does not exist | Principal architect |
| **R10** | **Change fatigue.** 2,400 stores, 85,000 employees, and a business already absorbing other change. Adoption stalls and the platform becomes a well-built thing nobody uses | 4 | 4 | Sequence the thin slice at a team that has actively asked for it. Retire the replaced spreadsheet on cutover day — do not leave both running, because both running means neither is trusted. Measure adoption weekly (§12) and treat a flat adoption curve as a delivery defect. Name a business change lead, funded, from Phase 1 | Executive sponsor / Business change lead |

**Two risks worth watching that are not in the top ten:** peak-trading readiness (the first Christmas on the new platform is a real event and needs a rehearsal, a freeze window and an on-call rota), and key-person dependency on the two or three people who understand the legacy ETL — interview and document them early, because they are the most likely to leave during the programme.

---

## 12. Success metrics

Two panels. The executive panel measures whether the business changed. The platform panel measures whether the platform is trustworthy. Both are published; the second is the leading indicator of the first.

### 12.1 Business KPIs

| KPI | Baseline | Target (by) | How measured |
|---|---|---|---|
| On-shelf availability | 94.1% | 96.0% (end Yr 2), 96.8% (end Yr 3) | Existing availability audit process, unchanged, so the comparison is honest |
| Inventory value | $3.4bn | $3.05–3.15bn at constant sales | SAP inventory valuation, monthly average |
| Forecast accuracy (WMAPE, SKU-store-day) | ~38% | 26–30% (end Yr 2) | Held-out backtest on a fixed evaluation set, re-run monthly |
| Markdown as % of revenue | 5.6% | 5.2–5.4% at constant sell-through | Finance reporting; sell-through controlled for |
| Month-end close | 9 working days | 4 working days (end Yr 2) | Date of final signed trial position |
| Finance reconciliation effort | ~14 FTE/month | 4–5 FTE/month | Time recording, existing process |
| Customer identity match rate | Unknown | Measured in Phase 0, then 70–80% | Match rate between store loyalty and e-commerce identity within the loyalty population |
| Loyalty-attributed sales share | 44% | 48% (end Yr 3) | POS loyalty capture rate |
| Supplier OTIF | 87.4% | 92% (end Yr 3) | Scorecard, shared with suppliers, so the number is agreed rather than argued |
| Cold-chain excursion write-off | Baseline in Phase 2 | -30% | Quality system, linked to sensor evidence |
| Active reports in use | ~620 of 2,900 | ~400 certified products, 2,900 retired | Catalogue and usage telemetry. **Fewer is the target** |
| Time from question to answer (new analysis) | Median 11 months (backlog age) | Median under 5 working days for self-service; under 6 weeks for a new product | Request tracking |

### 12.2 Platform SLOs

| SLO | Baseline | Target | How measured |
|---|---|---|---|
| Certified product freshness | Not measured | Day D-1 complete by 06:00 local, 99% of days | Freshness monitoring on every certified product; breaches logged |
| Real-time inventory latency | 24 h+ | Under 15 min, 99th percentile | End-to-end timestamp from POS event to queryable stock position |
| Cold-chain alert latency | Not measured | Under 60 s, 99.9% | Sensor timestamp to alert dispatch |
| Pipeline success rate | ~89% (est.) | 99.5% first-run success | Job run telemetry |
| Data quality pass rate | Not measured | Over 99.5% of rows passing expectations on certified products; 100% of breaches investigated | Pipeline expectation metrics, published weekly |
| Incidents per month | ~99 | Under 15 by end Yr 2 | Incident management |
| Firefighting share of engineering time | ~70% | Under 25% by end Yr 2 | Time allocation. **This is the metric the engineering team will care about most, and it should be published** |
| Mean time to restore (P1) | Not measured | Under 2 h | Incident management |
| Cost attribution coverage | 0% | 100% of consumption tagged | Billing telemetry; untagged consumption reported as a defect |
| Cost per certified product | Not measurable | Published monthly; trending down per unit of consumption | Attribution reporting |
| Analyst self-service rate | ~15% (est.) | Over 70% of questions answered without engineering involvement | Request telemetry vs query telemetry |
| Time to onboard a new analyst | 3–4 weeks | Under 1 day | Group membership to first successful query |
| Lineage coverage | 0% | 100% of certified products with end-to-end column lineage | Lineage system tables |
| Erasure SLA | Manual, unmeasured | 100% executed within 14 days; physical removal within 21 | Erasure control table |
| Deployment lead time | 6–8 weeks | Under 2 days from merge to production | CI/CD telemetry |
| Changes authored by client engineers | 0% | Over 80% for three consecutive months (handover gate) | Repository telemetry |

---

## 13. What we would draw next

Six diagrams, in this order. Each is drawn from the sections named, so they stay consistent with the case rather than drifting into decoration.

| # | Diagram | It must show | Drawn from |
|---|---|---|---|
| 1 | **End-to-end flow** | All 12 sources on the left, the three medallion zones, the serving layer, and the consumer groups on the right. Streaming paths visually distinct from batch. Each arrow labelled with its latency requirement, so the picture answers "how fresh is this" without a legend | §3.0, §5.2, §5.4, §5.6 |
| 2 | **Per-source ingestion map** | One row per source: source, protocol, ingestion mechanism, landing object, volume and latency. This is the architect's build sheet and should be readable as a checklist. Colour-code by mechanism (managed connector / Auto Loader / streaming / federation / sharing / COPY INTO) | §3.1–3.12, §5.3 |
| 3 | **Unity Catalog object model** | The three environment catalogs, the schema-per-domain layout, volumes and external locations, the group taxonomy, and which grants flow where. Overlay the governed tags and show which ABAC policy attaches at which level | §5.5, §6.4 |
| 4 | **Environment and promotion** | Repository to dev to test to production, with the bundle deployment path, the identity used at each step, and the gates between. Show what is deployed (jobs, pipelines, schemas, grants, dashboards) and what is not | §9.4, §9.5 |
| 5 | **Security zones and data flow for personal data** | The pseudonymisation boundary, the restricted PII schema, which zones contain personal data and which do not, the erasure path through all nine steps, and the residency boundaries between the three regions. This is the diagram Legal and the DPO will actually read | §7.2, §7.3, §7.4 |
| 6 | **Delivery timeline** | The four phases on a week axis, the five workstreams as swim lanes, the gates as vertical markers, the thin-slice milestone at week 10, the dual-run window with its cost peak, and the five decommission gates. Client obligations (§8.7) shown as dependency markers with their lead times | §8.1–8.7, §9.2 |

Two further diagrams worth drawing if the audience warrants them: a **use-case dependency graph** (which use case needs which data product, and therefore what the true build order is — §4, §6.2), and a **cost-driver model** (where consumption arises and which control governs each driver — §10.1–10.3).

---

## 14. Appendix

### 14.1 Glossary — client-facing terms

| Term | Plain meaning |
|---|---|
| **Lakehouse** | One place that holds all the data, from raw to reporting-ready, with one set of access rules. It replaces the separate "data lake for everything" and "warehouse for reporting" split |
| **Medallion (bronze / silver / gold)** | Three stages of refinement. Bronze is data exactly as it arrived. Silver is cleaned, deduplicated and conformed. Gold is shaped for a specific business use |
| **Data product** | A dataset treated like a product: it has an owner, a documented meaning, a quality guarantee, a freshness promise, and consumers who depend on it |
| **Certified / curated / experimental** | How much a dataset can be trusted. Certified is safe for executive reporting; experimental is not safe for anything that leaves the analyst's screen |
| **Unity Catalog** | The platform's single register of what data exists, who owns it and who may see it. One access model for every tool |
| **Governed tag** | A controlled label on data (for example, "contains personal data") that automatically triggers the right protection wherever it is applied |
| **ABAC (attribute-based access control)** | Access rules written against labels rather than against individual tables, so a correctly labelled new table is protected automatically |
| **Pseudonymisation** | Replacing a person's identifiers with a meaningless key, so analysis can happen without the analysis containing personal data |
| **Right to erasure** | The legal right of an individual to have their personal data deleted, and our obligation to prove we did it everywhere |
| **Data residency** | The requirement that certain data is stored, and sometimes processed, inside a particular country or region |
| **Lineage** | The automatically recorded map of where every number came from and what it feeds |
| **Streaming vs batch** | Streaming processes data as it arrives (seconds to minutes). Batch processes it on a schedule (hourly or daily). Streaming costs more and is only worth it when a decision is made that fast |
| **Strangler migration** | Replacing an old system by moving its users to a new one piece by piece and draining the old one, instead of a single switchover |
| **Dual-run** | A period during which old and new systems both produce the same numbers so they can be compared before the old one is switched off |
| **Reconciliation** | The automated daily comparison that proves the new number equals the old one, or explains why it should not |
| **Decommission gate** | A defined, evidenced condition that must be met before an old system is switched off |
| **SLO (service level objective)** | A published, measured promise — for example, "yesterday's sales are complete by 06:00 on 99 days out of 100" |
| **Thin slice** | A narrow but complete first delivery that goes through every layer, from source to a real user, so the whole approach is proven before it is scaled |
| **OpenSharing** (formerly Delta Sharing) | Giving an external party live, read-only access to a specific slice of data without sending them a copy or building them a portal |
| **Metric view** | A single, central definition of a business measure such as gross margin, used identically by every report and every tool |
| **Feature table** | A governed table of model inputs, so that a model is trained and run on identical definitions |
| **DBU** | The unit in which Databricks platform consumption is measured. Analogous to a metered utility unit |

### 14.2 Assumptions register

Every assumption below is illustrative, is load-bearing somewhere, and must be tested. The "test in" column names the phase in which it stops being an assumption.

| # | Assumption | Affects | Test in | If wrong |
|---|---|---|---|---|
| A1 | Client is fictional; all figures illustrative | Everything | — | — |
| A2 | 2,400 stores, 14 countries, e-commerce in 9, $34bn revenue, 40m loyalty members, 85,000 employees | Sizing, value case | Phase 0 | Re-base entirely |
| A3 | ~4.0m baskets and ~23m POS line items per day | Ingestion sizing, compute | Phase 0 | Linear effect on ingestion cost |
| A4 | ~360m clickstream events/day, 22k/sec peak, 3x Black Friday | Streaming design, compute | Phase 0 | Streaming architecture and cost scale directly |
| A5 | ~40m changed SAP rows/day, 4-hour inventory latency requirement | SAP extraction decision (D-03) | Phase 0 | A looser latency requirement permits a cheaper extraction route |
| A6 | Log-based CDC on the SAP source database is obtainable | D-03, Phase 2 plan | Phase 0 | Fall back to ODP/SLT; add 4–6 weeks and client-side licence cost |
| A7 | Identity match rate between store loyalty and e-commerce reaches 70–80% | UC-1, UC-6 value | Phase 0 (sample) | Below 55%, UC-6 value roughly halves and should be resequenced |
| A8 | Book stock accuracy ~88%, improvable to 95%+ | UC-3 | Phase 2 | UC-3 will be rejected by stores; a stock-accuracy programme becomes a prerequisite |
| A9 | Forecast accuracy improves from ~38% to 26–30% WMAPE | UC-2 value | Phase 2 pilot | Inventory benefit scales roughly with the improvement delivered |
| A10 | Supply Chain re-cuts safety-stock parameters on the improved forecast | UC-2 value realisation | Phase 3 | The largest single benefit does not land. **This is an operating-model risk, not a data risk** |
| A11 | ~620 active EDW reports, of which 35–45% can be retired | Migration effort (§8.5) | Phase 2 | Each 10 percentage points of retirement shortfall adds roughly 8–10 weeks of migration effort |
| A12 | 60–90 TB of EDW history is worth retaining | Storage, migration | Phase 0 | Storage and export effort scale directly |
| A13 | Hadoop estate is ~60% cold and largely not worth migrating | Migration scope | Phase 0 | Migrating more adds effort and permanent storage cost |
| A14 | Kafka retention can be raised to 7 days and a schema registry adopted | Clickstream reliability | Phase 1 | Reliability capped; incident rate stays high; rescued-data volumes grow |
| A15 | 400+ analysts, bursty query pattern | D-07, SQL cost | Phase 0 (from legacy query logs) | A steady, predictable pattern would favour provisioned compute for part of the load |
| A16 | Residency requires in-region processing in EU, UK and 3 APAC jurisdictions | D-08, workspace count | Phase 0 (Legal) | Fewer regions materially simplifies and reduces cost; more regions does the reverse |
| A17 | Works-council consultation gates worker-level HR data in 5+ countries | §3.10, scope | Phase 0 | People domain resequences |
| A18 | ~1,200 suppliers can consume a data share, with a thin UI for the smallest | D-14 | Phase 2 pilot (20 suppliers) | A light portal becomes a funded workstream |
| A19 | 12–16 of the existing 48-person team can transition into platform roles | Handover, §9.3 | Phase 2 | Handover slips; either hire or extend the services engagement |
| A20 | Dual-run window is 24 weeks, ending at week 88 | Cost peak, §10.4 | Phase 3 | Every additional quarter of dual-run is a material, visible cost |
| A21 | Inventory ~$3.4bn, carrying cost ~18%, gross margin ~28%, markdown ~5.6% of revenue | Value case arithmetic | Phase 0 (Finance) | Benefit ranges scale directly |
| A22 | Benefit capture at 60% of the identified low case, delayed two quarters | §10.6 payback | Continuously | Payback moves, but remains inside Year 2 down to roughly 40% capture |

### 14.3 Items marked to be confirmed

| Item | Where | Confirm with |
|---|---|---|
| SAP third-party extraction licensing implications | §3.1 | Client's SAP account team |
| Per-object incremental support in the Salesforce managed connector | §3.2 | Current connector documentation |
| Whether a managed streaming connector now covers the clickstream requirement | §5.3 | Current documentation, at the Phase 3 gate |
| Current ABAC compute requirements and policy quotas | §5.5, D-06 | Current documentation, at build time |
| Low-latency operational serving pattern and product choice | §5.6 | Current documentation |
| Cross-metastore access options for multi-region deployments | §5.7, D-08 | Current documentation, at design time |
| Audit log retention and any configurable retention options | §7.7 | Current documentation |
| Cross-region and cross-cloud sharing transfer costs for non-EU suppliers | §7.6, D-14 | Current documentation and cloud pricing |
| Food-safety record-keeping retention periods per country | §5.2, §7.1 | Client Legal |
| Disaster recovery RPO and RTO targets per zone | §9.6 | Client |
| All platform consumption pricing | §10 | Current price lists, with the Databricks account team and the cloud provider, in Phase 0 |

---

*End of case 01. Prepared as a teaching and selling artefact. The client is fictional; the figures are illustrative; the architecture decisions are real positions and are meant to be argued with.*

