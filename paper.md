# Iterative leak-surface peeling

*A falsifiability-anchored methodology for ML detection of blockchain validator infrastructure attacks*

**Author**: Simon Morley, NullRabbit

**Status**: working draft, 2026-05-06

---


# Abstract

Public-internet-reachable blockchain validator
infrastructure is an inviting target for asymmetric
resource-consumption attacks; validator-DoS findings have
accumulated steadily across Sui, Solana, Ethereum, Aptos,
and Cosmos-family chains through 2024–2026 coordinated-
disclosure pipelines. Detection that survives the cleartext
/ TLS-fronted boundary, the cross-chain transfer, and the
lab / mainnet fidelity tier is non-optional for operators
standing up monitoring on this threat surface. Yet ML-based
detection of these attacks routinely ships with median
ROC-AUC at or near 1.000 across cross-validation folds,
which on audit prove artefactual rather than reflecting
underlying network behaviour
[sommer2010outside, arp2022dosdonts]. Our V1 trainer's
first TrainReport against an initial 1,092-bundle Sui
validator-DoS corpus is a fresh data point in this pattern:
ROC = 1.000 across all 17 leave-one-primitive-out folds,
driven by random-Gaussian-feature ROC = 1.000 (LOPO
benign-holdout contamination) and `resp.count` ROC = 1.000
(capture-pipeline co-linearity).

This paper presents **iterative leak-surface peeling**: a
methodology that pre-registers numerical thresholds,
structural predictions, and outcome-band composition rules
before headline numbers land, then surfaces and closes its
own failure modes through multi-layer falsifiability
discriminators and audit-driven iteration. Across V1 →
V7-narrow on a 2,103-bundle Sui+Solana corpus, the
methodology has surfaced and closed eight distinct leak
surfaces in sequence. Two open pillars substantiate the
methodology: **Bundle v1**, a multi-modal capture format
with controlled-vocabulary provenance fields, demonstrated
through three landed schema-additive extensions; and a
chain-agnostic family taxonomy of ten attack families plus
benign that classifies post-cycle attacks without extension.

The technical centerpiece is the V7-narrow multi-mechanism
finding: cross-chain mechanism non-transfer in this domain
is **feature-localised, not whole-feature-space**. The
headline outcome at the V7-narrow evaluation gate is Joint C
(cross-chain mechanism claim at the rate-invariant
13-feature manifest layer falsified at lab fidelity).
Subsequent Step-11 V1 + V8 retrain cycles deliver Joint A on
the cipher-agnostic claim: 100% retention vs the
pre-registered Step-11 V1 cleartext baseline across both
chains in both LOPO regimes (Step-11 V1 retrain), and
124–191% retention post-trim (Step-11 V8 retrain) once the
V7-narrow §SE3-affected `pcap.mean_packet_size`
distribution-mismatch source is removed from the manifest.
The encryption boundary itself does not introduce additional
accuracy degradation.

The methodology contributions persist independently of any
single evaluation-gate outcome. Since v1 the corpus has grown
along the additional-chains axis v1 pre-registered as a v2
trigger: from the two-chain Sui+Solana base to a **nine-chain,
47-primitive public-CVE known-class corpus** (Bitcoin,
Ethereum, Solana, Sui, Cosmos, Monero, Dogecoin, Litecoin,
libp2p) in which every attack faithfully reproduces a specific
public disclosure - a CVE, a GHSA, or a named third-party
audit - recorded in `provenance.public_source`. A per-bundle
`provenance.source_class` field (`public-cve-replication` vs
`original`, ratified in `nr-bundle-spec` v0.1.3) separates
these publishable reproductions from our own disclosure-gated
measurement, and an automated, guarded pipeline (daily CVE
triage → node-crash-gated attack forge → nightly retrain →
publish-guard → self-updating model card) reproduces the
corpus end-to-end. The scale-up sharpens the cross-chain
result rather than softening it: a binary attack-vs-benign
detector separates attack-*use* from benign-*use* of the same
wire messages at ~0.96 within-chain held-out ROC (GroupKFold
by primitive; diagnostic, not a deployment claim), while
**cross-chain family recovery stays near the floor on
protocol-distinct chains** - leave-one-chain-out macro-F1 of
0.16-0.46 when a protocol-distinct chain (Monero, Bitcoin,
Ethereum, Cosmos, libp2p) is held out, and high only where the
held-out chain is a wire-identical fork inheriting another
chain's exact primitives (Dogecoin, Litecoin). The two-chain
V7-narrow non-transfer finding thus generalises to nine
chains: the mechanism-class signal is real and within-chain;
whole-taxonomy cross-chain transfer remains an open problem we
state as one, not a result.


# §1 Introduction

Public-internet-reachable blockchain validator infrastructure
is an inviting target for asymmetric resource-consumption
attacks. Validator-DoS findings have accumulated steadily
across 2024–2026 in coordinated-disclosure pipelines covering
Sui, Solana, Ethereum, Aptos, and Cosmos-family chains.
Detection that survives the cleartext / TLS-fronted boundary,
the cross-chain transfer, and the lab / mainnet fidelity tier
is non-optional for operators standing up monitoring on this
threat surface. This paper presents a methodology that
surfaces and closes its own failure modes - **iterative
leak-surface peeling** - together with two open pillars that
the methodology runs against: **Bundle v1**, a multi-modal
capture format with controlled-vocabulary provenance fields
(§3), and a **chain-agnostic family taxonomy** of ten attack
families plus benign that classifies post-cycle attacks
without extension (§4). The paper is pitched at ML-security
researchers as primary audience; blockchain protocol security
engineers will find the family taxonomy and bundle format
directly applicable.

The methodological stakes are familiar from the broader
reproducibility-crisis literature. ML-based detection systems
for security domains routinely ship with high headline
accuracy numbers - median ROC-AUC at or near 1.000 across
cross-validation folds - which on audit prove artefactual
rather than reflecting underlying network behaviour
[sommer2010outside, arp2022dosdonts]. The discipline that
addresses this - pre-registration of analytical decisions
and outcome thresholds before observing data, multi-layer
falsifiability discriminators, and audit-trail frameworks
that drive iteration - descends from the Ioannidis /
Errington / Munafò / Open Science Framework lineage in
clinical and behavioural science (§2.5). This paper applies
that discipline to ML training cycles for blockchain validator
infrastructure detection: each cycle pre-registers numerical
thresholds, structural predictions, and outcome-band
composition rules before headline numbers land; multi-layer
falsification discriminators run against the trained model;
audit findings drive the next cycle's design delta; the
closed-leak set grows monotonically.

We have lived this pattern. Our V1 trainer's first
TrainReport against a 1,092-bundle Sui validator-DoS corpus
produced median ROC = 1.000 across all 17
leave-one-primitive-out folds. Two compounding artefacts
drove the headline: random-Gaussian-feature ROC = 1.000
(leave-one-primitive-out benign-holdout contamination) and
`resp.count` ROC = 1.000 (capture-pipeline co-linearity
between attack and synthetic-client benign pipelines). The
methodology carried this through six subsequent iterations
on a 2,103-bundle Sui + Solana corpus (decomposition in
Appendix A.0), surfacing and closing eight distinct leak
surfaces in sequence; full inventory in §5.4 + §8.5. The two
months since v1 extended the same discipline to a nine-chain,
47-primitive **public-CVE known-class corpus** and an
automated, guarded training pipeline; §4.6 and §5.6 integrate
those results, including where they update v1's claims.

We make three contributions:

1. **Iterative leak-surface peeling methodology** (lead
   contribution, §5–§6). Pre-registered cycles + multi-layer
   falsifiability + per-chain holdout direction (D-018) +
   methodology-auditor agent gate. The V7-narrow disambiguation
   sub-experiment design (SE1/SE2/SE3) hardens a
   hypothesis-grade chain-asymmetry finding to finding-grade
   multi-mechanism evidence: cross-chain mechanism non-transfer
   in this domain is feature-localised, not whole-feature-space.
   Subsequent Step-11 V8 retrain delivers empirical Joint A
   on the cipher-agnostic claim (§7) and scopes the
   V7-narrow §SE3 reframe to the cipher-agnostic byte-count
   manifest layer; the `resp.status_*_frac` chain-asymmetric
   pattern at the rate-invariant 13-feature manifest layer
   remains live as a finding (Step-11 V8 does not test it;
   §6.4; §8.7 MC-2).

2. **Bundle v1 as documented format pillar with falsification
   clause on additive extensibility** (pillar, §3). Six-modality
   bundle (packets.pcap + responses / host / app / protocol /
   vectors parquet slots) plus controlled-vocabulary manifest
   plus decomposed-provenance schema. Format-additive
   extensibility across fidelity tiers and modality slots
   without breaking changes; this paper documents the
   format-stability claim and its falsification clause (§3.5).
   §3 frames Bundle v1 as evidence; the canonical normative
   specification (JSON Schema, parsers in Python and Rust, five
   reference example bundles) ships as `nr-bundle-spec` v0.1.0
   ([github.com/NullRabbitLabs/nr-bundle-spec][nrbundle], MIT-
   licensed) per §3.4.

[nrbundle]: https://github.com/NullRabbitLabs/nr-bundle-spec

3. **Chain-agnostic family taxonomy as documented pillar with
   falsification clause on generativity** (pillar, §4). Ten
   attack families plus benign in the controlled vocabulary
   (nine populated at lab fidelity); chain-agnostic `family_id`
   and chain-specific `primitive_id`. Generative under
   post-cycle discovery: three Sui validator attacks (IA01,
   IA02, IA02b) discovered after the V4 cycle close classified
   into the existing `response_amp` family without taxonomy
   extension (§4.3), and, at nine-chain scale, dozens of
   public-CVE primitives classify into existing families
   (§4.6). This paper documents the taxonomy-generativity claim
   and its falsification clause (§4.5); the canonical
   normative specification routes to the companion format
   paper per §4.

What would falsify each contribution:

- **Methodology** falsifies if a future cycle surfaces a
  load-bearing finding the audit-trail framework cannot
  honestly frame as Joint A / B / C - i.e., a finding that
  exceeds the falsifiability-layers framework's expressive
  capacity rather than fitting one of its outcome bands.
  Across V1 → V7-narrow, the audit-trail framework has framed
  every load-bearing finding as Joint A / B / C; no finding
  has required framework extension to date.
- **Format** falsifies if a future fidelity tier or modality
  slot requires a breaking schema change rather than additive
  extension. The cumulative pattern across D-007
  (FidelityClass enum), D-009 (vectors.parquet sixth modality
  slot), and D-020 (lab-tls-fronted fidelity tier added
  2026-05-03) has produced three landed additive extensions
  and zero breaking changes to date. A fourth schema-design
  question - D-015 (decomposed-provenance with `substrate` +
  `traffic_origin` fields) - sits adjacent under deliberation;
  whichever path it resolves to (decomposition vs single-axis
  enum extension vs free-form notes), prior precedent makes
  additive resolution available.
- **Taxonomy** falsifies if a post-cycle attack requires family
  extension, where "family extension" means adding a new family
  member rather than classifying into an existing one. At v1
  submission, three post-cycle attacks (IA01/IA02/IA02b) had
  produced zero taxonomy modifications. The nine-chain scale-up
  since updates this record honestly (§4.5, §4.6): dozens of
  cross-chain public-CVE primitives classified into existing
  families without extension, while one new network family
  (`rpc_handler_cpu`) and a separate six-family economic-attack
  layer (D-035) were added - documented family-extension
  events, forward-tracked under this clause rather than elided.

These falsification conditions are forward-tracking
commitments, not resolved questions. This paper documents
the methodology against the conditions explicitly so
subsequent cycles can register their findings against them.
A future cycle that surfaces a finding the audit-trail
framework cannot frame as Joint A / B / C, a fidelity tier
or modality slot requiring breaking schema change, or a
post-cycle attack requiring family extension is reportable
substrate-paper material in a subsequent revision per
principle 4 (methodology contributions are first-class
artefacts).

The paper proceeds as follows. §2 positions the methodology
against ML-security, blockchain-DoS, and dataset-publication
prior art. §3 specifies Bundle v1 (format pillar). §4 defines
the chain-agnostic family taxonomy (taxonomy pillar) with
the post-cycle generative-not-bounding evidence. §5 describes
the methodology in full: pre-registration discipline,
multi-layer falsifiability framework, LOPO with
per-chain holdout direction, the methodology-auditor agent
gate, and the V1 → V7-narrow iteration arc. §6 presents the
V7-narrow multi-mechanism finding as the technical
centerpiece. §7 documents the cipher-agnostic feature-subset
framework, the Step-11 V1 + V8 empirical Joint A (closed
2026-05-04), and the 2026-05-09 multi-class softmax POC
over the V8-V14 detector inventory (§7.6). §8 covers
limitations,
scope, production-deployment companion, reproducibility,
prior-cycle leak-surface closures, and methodology
contributions about agent-discipline patterns. §9 concludes.
Appendices A and B provide V7-narrow numerical evidence and
the decisions-log summary. The paper text and figures are
CC-BY-4.0; reproduction artefacts (corpus tags, run tags,
commit SHAs) are pinned at
`github.com/NullRabbitLabs/nr-substrate`.


# §2 Related work + background

This paper sits at the intersection of four prior-art
threads: ML methodology for network-traffic security
detection; cross-validation discipline in security ML;
capture-format and dataset publication; and the broader
reproducibility / pre-registration movement. We summarise each
thread and then position our contribution against the closest
named prior art along four differentiation axes.

## §2.1 ML for network security detection

ML-based network-traffic classifiers have been studied for
two decades - DDoS detection (whose attack-mechanism
taxonomy is canonically anchored at [mirkovic2004taxonomy];
ML-based detection prior art at [sommer2010outside,
buczak2016survey]), intrusion detection on the CIC and KDD
benchmark families, and more recently encrypted-traffic
classification using TLS fingerprints (JA3 [althouse2017ja3]
and JA4 [althouse2023ja4]) and statistical flow features
[anderson2017machine, wang2017endtoend]. The recurring
methodological criticism of this literature is that benchmark
datasets often contain capture-pipeline or class-distribution
artefacts that inflate published headline accuracy
[sommer2010outside]. Our V1 contamination story
(§1) is a fresh data point in this critique tradition; the
methodology this paper presents is positioned as a response,
not a refutation.

For blockchain validator infrastructure specifically, ML
detection is comparatively under-published. Existing work
either (a) treats the validator as a generic HTTP/RPC service
and applies general-purpose flow classifiers, missing the
chain-specific request-shape signal; or (b) targets
chain-specific attack mechanisms (e.g., Solana QUIC gossip
flooding, Ethereum eth_call abuse) without the cross-chain
generalisation framing we require here. We are
not aware of prior published work that combines pre-registered
multi-cycle iteration, cross-chain LOPO with per-chain holdout
direction, and cipher-agnostic feature-subset robustness
measurement - these are the four differentiation axes we
return to in §2.7.

## §2.2 LOPO + cross-validation discipline in security ML

Leave-one-out and leave-one-primitive-out cross-validation are
standard in domains where independent evaluation requires
holding out classes of related observations rather than random
samples. Roberts et al. [roberts2017crossvalidation]
formalised cross-validation strategies for data with
temporal, spatial, hierarchical, or phylogenetic structure; the LOPO discipline
this paper applies to attack primitives is a security-ML
adaptation of that broader framework. Stratified holdout
discipline - partitioning the held-out class along an
orthogonal axis to surface contamination - is established
practice in clinical-trial methodology and has migrated into
ML through the reproducibility-crisis discourse (§2.5).

What has been less developed in the security-ML literature is
**per-chain holdout direction** as the load-bearing
generalisation regime for cross-chain claims. Per-primitive
LOPO with by-chain summary aggregates can saturate at median
ROC = 1.000 while per-chain holdout (train on one chain,
evaluate on the other) collapses to anti-classification on the
same trained model and same feature set. Our V6 → V7-narrow
arc surfaces this distinction empirically; §5 generalises it
as a methodology contribution applicable beyond this project.

## §2.3 Blockchain validator DoS / CVE prior art

Validator-DoS findings have accumulated steadily in
coordinated-disclosure pipelines for Sui, Solana, Ethereum,
Aptos, and Cosmos-family chains across 2024–2026. Public CVE
references span byte amplification ([cve-2024-32972],
go-ethereum header-replay), compute amplification
([cve-2026-26314], go-ethereum p2p), memory abuse
([cve-2026-26313], go-ethereum p2p), and consensus / network
abuse ([cve-2025-24371], CometBFT blocksync;
[cve-2025-24883], go-ethereum RLPx). These supply the
chain-validator-DoS substrate that the family taxonomy of §4
organises (F10 / IA01 / IA02 in our taxonomy correspond to
the byte-amplification family; F14 to compute amplification).

Public CVE coverage in 2024–2026 is uneven across chains: the
HIGH-confidence CVE record above is concentrated on
go-ethereum and CometBFT, while Sui, Solana, and Aptos have
no validator-DoS CVEs assigned in the period despite
disclosed vendor advisories (e.g., the HackenProof Sui
CompiledModule OOM disclosure, 2024; the Anza/Agave ELF
CALL\_REG patch, 2024-08-08; multiple CometBFT GHSAs without
CVE assignment). We do not make claims about the relative
severity of disclosed CVEs or the completeness of any
vendor's disclosure backlog; we cite the prior art to anchor
the threat surface, not to extend the disclosure record
itself.

## §2.4 Capture-format and dataset publication discipline

Open dataset publication in network security has a
two-decade history: the CIC IDS datasets
[sharafaldin2018cicids, sharafaldin2019ddos] from the
Canadian Institute for Cybersecurity, the MAWI traffic
archive maintained by WIDE [cho2000mawi], and the broader
NDSS / USENIX dataset-paper tradition. These
publications established that open datasets accelerate
methodological progress in the field. The same era also
surfaced a recurring critique tradition: subsequent literature
documented dataset capture pipelines introducing features that
ML models exploit instead of the underlying network behaviour.
The CIC datasets in particular have been critiqued for
header-field artefacts and class imbalance issues
[engelen2021troubleshooting, lanvin2023errors]. Our V1
audit-finding (the `resp.count` capture-pipeline co-linearity)
is a fresh instance of this pattern; Bundle v1's controlled-
vocabulary provenance fields (`traffic_source`,
`fidelity_class`, `target_authorisation`) and the multi-modal
parquet design (§3) are the format pillar's response to the
capture-pipeline-feature failure mode.

Bundle v1 differs from prior open formats along three axes:
(1) **multi-modal capture by construction** - six modality
slots (packets.pcap + responses / host / app / protocol /
vectors parquet) plus a manifest, capturing wire-level
network traffic + RPC request/response pairs + host-level
OS metrics + application metrics + protocol/consensus
time-series + vector-modality features simultaneously,
where prior formats are predominantly pcap-only or
single-modality; (2)
**controlled-vocabulary manifest fields** including
`fidelity_class`, `traffic_source`, and `target_authorisation`,
which let downstream consumers filter datasets by deployment
provenance and lab-vs-production distinction without
reverse-engineering capture metadata; (3) **format-additive
extensibility** verified through three landed extensions
(D-007 FidelityClass enum → D-009 vectors.parquet sixth
modality slot → D-020 lab-tls-fronted enum addition) without
breaking schema changes. A fourth schema-design question -
D-015 (decomposed-provenance with `substrate` +
`traffic_origin` fields) - is adjacent under deliberation;
its resolution can land additively without precedent
violation.

## §2.5 Adversarial-ML reproducibility and pre-registration

The reproducibility crisis literature outside ML provides the
methodological discipline this paper applies. Ioannidis (2005,
"Why Most Published Research Findings Are False"
[ioannidis2005why]) framed the underlying statistical issue;
Errington et al.'s Reproducibility Project: Cancer Biology
[errington2021reproducibility] documented empirical failure
rates in pre-registered replications; and Munafò et al.'s
"A manifesto for reproducible science" (2017,
*Nature Human Behaviour* [munafo2017manifesto]) systematised
the methodological response. The Open Science Framework's
pre-registration discipline - committing analytical decisions
and outcome thresholds before observing data - is the explicit
methodological precedent for the per-cycle pre-registration
discipline this paper applies to ML training cycles
(§5.1).

ML reproducibility specifically has its own emerging
discipline: model cards, datasheets for datasets
[gebru2021datasheets], and the broader MLOps-reproducibility
movement.
Our methodology contribution sits adjacent to these efforts
but emphasises the falsifiability-layer framework
(§5.2) - pre-registered numerical thresholds, structural
predictions, and outcome-band composition rules - as the
mechanism by which a cycle's audit findings drive the next
cycle's design rather than as an after-the-fact reporting
discipline.

## §2.6 Position vs the architectural-layer companion

This paper is the data-layer companion to the earned-autonomy
paper [morley2026earnedautonomy] - Zenodo DOI
`10.5281/zenodo.18406828`, published as the architectural
framework for graduated trust in autonomous security systems.
The earned-autonomy paper covers the deployment architecture
(detection-only → operator-reviewed enforcement → bounded
autonomous response), the capability ladder for autonomous
security agents, and the trust-earning protocol governing
each transition. This paper covers the data layer that the
earned-autonomy architecture runs against: how the corpus is
captured, how the model is trained and evaluated, how
methodology contributions are surfaced, and what the
detection system's evaluation-gate outcome is at the current
fidelity tier.

The two papers are independently readable. Where the
earned-autonomy paper assumes a working data-layer
methodology, this paper builds it. Where this paper references
production-deployment architecture, it cites the earned-
autonomy paper rather than re-developing the framework.
Section 8.3 documents the production-deployment workstream
explicitly out of scope for v1, gated on the v2 Step-11
empirical retention numbers.

## §2.7 Closest prior art and differentiation

We differentiate against the closest named prior art along
four axes:

1. **Pre-registered multi-cycle iteration**. Our V1 → V7-narrow
   arc pre-registers each cycle's outcome triggers before
   training. The closest prior precedent for pre-registration
   discipline applied to predictive ML evaluation is
   [hofman2023preregistration]; differentiation is the
   per-cycle Section A / B / C pre-registration structure
   plus the methodology-auditor gate enforcing pre-registered
   evaluation against locked thresholds.

2. **Cross-chain LOPO with per-chain holdout direction**.
   Prior cross-dataset and cross-domain ML evaluation in
   network intrusion detection [cantone2024crossdataset,
   dhooge2020interdataset] uses per-sample or per-dataset
   holdout. Our per-chain holdout direction (D-018) - train
   one chain, evaluate the other, on a chain-agnostic feature
   set - surfaces feature-level chain-asymmetric mechanism
   that per-primitive LOPO with by-chain aggregation alone
   cannot.

3. **Cipher-agnostic feature-subset boundary derivation**.
   Encrypted-traffic classification literature
   [anderson2017machine, wang2017endtoend] builds models on
   observable TLS-frame features but, to our knowledge, no
   prior published work pre-registers the exact
   cipher-agnostic feature subset before measurement. Our
   CIPHER_AGNOSTIC_V1 manifest
   (D-020 + §7) pre-registers the 8-feature subset - three
   pcap features plus five resp.* byte-count features -
   before the Step-11 retention measurement, and the
   pre-registered outcome bands lock before any TLS-fronted
   bundle emits.

4. **Falsifiability-layers framework**. Numerical thresholds
   (Layer 1), structural predictions (Layer 2), outcome-band
   composition rules (Layer 3), and the methodology-auditor
   gate (Layer 4) compose into a pre-registration framework
   that prior security-ML methodology work, to our knowledge,
   does not formalise. The framework is this paper's
   transferable contribution beyond the specific Sui + Solana
   evidence base.

Of the four differentiation axes, axes 1 and 2 have close
prior art (cited above); axes 3 and 4 - cipher-agnostic
feature-subset boundary *pre-registration* and the
falsifiability-layers framework as a composed
operationalisation in security-ML - have no close published
prior art at this paper's submission, to our knowledge. Our
contribution claim is structural - these are the four axes -
and bibliometric anchoring is the v1 final-draft-gate
output, not the contribution itself.


# §3 Bundle v1 - open multi-modal capture format

The format pillar of this paper is **Bundle v1**: a multi-
modal parquet-plus-manifest capture format for adversarial-ML
research on validator infrastructure. The publication strategy
locked at decision D-012 (`nr-bundle-spec` MIT-licensed format
repo plus `nr-bundles-public` HuggingFace dataset of 20-50
sample bundles plus this paper) opens the unit of measurement
without giving away the proprietary corpus that took months to
capture. This section specifies the format, traces its
extension history, and states the falsification condition
on the format-stability claim.

## §3.1 Six-modality structure

A Bundle v1 bundle is a directory containing a manifest and
six modality slots; the network-capture slot is a `.pcap`
file, the others are parquet. The directory naming convention
`crp_<corpus_id>` provides per-bundle content-addressable
identity:

```
crp_a1b2c3d4e5f6/
├── manifest.json          # BundleManifest pydantic schema
├── packets.pcap           # Network capture (modality 1)
├── responses.parquet      # RPC request/response pairs (modality 2)
├── host.parquet           # Host-level OS metrics (modality 3)
├── app.parquet            # Application-level Prometheus scrapes (modality 4)
├── protocol.parquet       # Consensus / protocol time-series (modality 5)
└── vectors.parquet        # Vector-modality features (modality 6, slot reserved)
```

Each modality captures a different fidelity dimension of the
attack-validator interaction:

- **`packets.pcap`** captures wire-level network traffic
  (snaplen-256 default). TCP/IP-header observable regardless
  of cleartext; payload observable when capture vantage is
  post-TLS-termination.
- **`responses.parquet`** captures application-level RPC
  request/response pairs (one row per call) - request bytes,
  response bytes, status code, RPC method, error frame.
  Populated only when the capture pipeline observes the
  application layer (post-TLS-termination or unencrypted).
- **`host.parquet`** captures host-level OS time-series
  (CPU, memory, IO, file descriptors) sampled on the
  validator host during the capture window.
- **`app.parquet`** captures application-level metrics
  scraped from the validator's Prometheus or equivalent
  metrics endpoint during the capture window.
- **`protocol.parquet`** captures consensus / protocol
  time-series - chain-agnostic where possible
  (`checkpoint_height`, `committed_round`, queue depth,
  peer count) and chain-specific where the protocol exposes
  it. Sampled across the capture window in lock-step with
  the metric scrapes.
- **`vectors.parquet`** (D-009 sixth-modality slot added
  at Step-5.7) reserves a vector-modality features slot -
  embedding representations of structured payloads
  (bytecode, transaction blobs, query ASTs) suitable for ML
  feature extraction without rehydration of the raw
  payload. The slot is reserved as part of the v1.0 contract
  per D-009; the slot is currently unpopulated across the
  corpus, with first-population landing alongside the
  deferred TRS ingest pipeline.

All four parquet time-series modalities (`responses`, `host`,
`app`, `protocol`) carry a monotonic `t_ns` column referenced
to the same `started_at` instant in the manifest, making
cross-modality joins a merge-asof.

The six-modality design is load-bearing for two distinct
claims of this paper. First, **multi-fidelity feature
extraction**: the cipher-agnostic feature subset (§7) draws
from `packets.pcap` byte counts and TCP/IP-header fields alone,
while the full-fidelity feature surface draws from all five
modalities. The format supports both surfaces from the same
bundle without re-capture. Second, **modality-population
audit**: the V2 capture-pipeline-co-linearity leak (§1, §5.4)
was diagnosed by comparing modality population shapes between
attack and benign bundles - `responses.parquet` populated for
attack reproducer bundles and unpopulated for synthetic-client
benign bundles. The format makes this comparison mechanical;
audit discriminators surface modality-population asymmetry
without per-cycle bespoke tooling.

## §3.2 Manifest controlled-vocabulary fields

`BundleManifest` is the bundle's controlled-vocabulary schema,
defined as a pydantic model. The decisions log entries D-007,
D-008, and D-009 added the load-bearing structured fields;
strict-tightening at Step 5.7 (2026-04-25) removed staging-
tolerance fallbacks so every bundle now declares its fields
explicitly at manifest-construction time, with legacy bundles
backfilled via `scripts/step5_7_backfill.py`.

**`fidelity_class` (D-007 + D-020 extension)**: enumerates
how faithfully the bundle reproduces the real attack on the
wire. Six members at this paper's submission:

- `stub` - placeholder reproducer with hand-crafted or
  test-vector-derived input; shape-only.
- `proxy` - wire shape reproduced via a substitute mechanism
  (e.g., TCP flood proxying for a binary anemo protocol).
- `lab` - full reproducer producing genuine attack traffic in
  a controlled localnet / private-testnet environment.
  Majority of the corpus.
- `lab-tls-fronted` - full reproducer against a TLS-
  terminating proxy (nginx) in front of a localnet validator,
  captured at two vantage points: pre-termination wire (TLS
  frames; cipher-agnostic feature surface) and post-
  termination loopback (cleartext; full-feature surface).
  Step-11 evidence tier (see §7).
- `production-captured` - sample directly from a production-
  deployed adversarial sensor (reserved for future TRS ingest;
  no bundles currently carry this value).
- `production-derived` - lab reproduction parametrised by
  patterns observed in production deployment.

**`traffic_source` (D-007)**: enumerates how the captured
traffic was produced. Six members:

- `synthetic-client` - non-attacker traffic generated
  by a passive recorder, no `record_response()` calls.
  `responses.parquet` modality unpopulated. Initial
  `corpus_v1.0` benign capture pipeline.
- `mainnet-organic` - captured from a mainnet-synced fullnode
  serving real third-party clients.
- `mixed` - mainnet fullnode with synthetic probes interleaved.
- `reproducer-attack` - attack traffic driven by a reproducer;
  CaptureSession wired, `record_response()` populated.
- `reproducer-benign` - synthetic clients producing benign
  traffic captured through the **same CaptureSession pipeline**
  as `reproducer-attack` (added in `corpus_v1.1` to close the
  V2 capture-pipeline-co-linearity leak; §1, §5.4).
- `validator-under-load` - Sui-bearing benign that does NOT
  scrape Sui metrics (added in `corpus_v1.3` as a sixth
  stratum for LOPO stratified holdout).

**`target_authorisation` (D-008)**: enumerates the
authorisation scope governing the captured target. Four
members: `self-owned`, `customer-authorised` (with engagement
ID required), `public-mainnet-passive`, `synthetic`. This
field gates downstream publication: a bundle without explicit
authorisation cannot enter the public dataset (§3.4) without
violating the publication chain.

The enum-with-strict-tightening pattern is a deliberate
methodology choice. Free-form provenance fields drift across
contributors and across reproducer iterations; enum-typed
fields with controlled vocabularies surface mismatch at
manifest-construction time rather than at downstream
filtering time. The `pydantic.ValidationError` raised on a
missing or off-vocabulary value blocks the bundle from
landing in the corpus at all - the contract is enforceable,
not advisory.

## §3.3 Format-additive extensibility

We claim that Bundle v1 generalises across fidelity tiers
and modality slots without breaking schema changes. Three landed extensions substantiate the claim:

| extension | decision | what changed | breaking? |
|---|---|---|---|
| FidelityClass enum (initial) | D-007 (Step 5.7, 2026-04-25) | Six-member fidelity tier vocabulary; defaults removed; legacy bundles backfilled via migration script | No (additive - enum-typed field added to manifest) |
| `vectors.parquet` sixth modality slot | D-009 (Step 5.7) | New parquet file slot for vector-modality features (embeddings, ASTs); slot reserved cleanly with empty-population convention for bundles without vector data | No (additive - new file in bundle directory) |
| `lab-tls-fronted` enum value | D-020 (2026-05-03, Step 11 paired commit) | Sixth FidelityClass enum member; trainer integration paired (`INCLUSIVE_FIDELITY` extended; `TLS_FRONTED_FIDELITY` constant; `--include-tls-fronted` CLI flag) | No (additive - new enum member; existing values unchanged) |

A fourth schema-design question sits adjacent under
deliberation: **D-015** (decomposed-provenance with
`provenance.substrate ∈ {lab, mainnet}` and
`provenance.traffic_origin ∈ {synthetic, organic, hybrid}`).
The Step-7 plan surfaced that the existing `FidelityClass`
enum doesn't have a clean fit for "synthetic clients against
a real mainnet fullnode" - the enum conflates two orthogonal
axes (substrate authenticity, traffic origin) into one
fidelity tier. D-015 proposes three resolution paths:
extending the enum with a single combinatorial value (Path A,
single-axis but inflates with combinatorial growth);
keeping `lab` plus free-form `provenance.notes` (Path B,
rejected on Step-5.7 strict-tightening grounds); or
decomposing into two structured fields (Path C, two-binary-
times-ternary = six cells of which four map to existing
`fidelity_class` values plus two capture the Step-7 cases).
The decision is pending review and not yet taken; whichever
path resolves it, prior precedent makes additive resolution
available - Path A is a single enum value addition (parallels
D-020), Path C is two new structured fields with `model_validator`
deriving the existing `fidelity_class` from the decomposed
pair. This paper documents the format-stability claim against
the three landed extensions and treats D-015 as load-bearing
test-case for the claim's forward applicability.

## §3.4 Companion artefacts

The format publication strategy (D-012) decomposes this
paper's contribution into five live external artefacts plus
this preprint (status as of 2026-05-13):

- **`nr-bundle-spec` v0.1.0** [bundle_spec_v0_1_0] - live
  at [github.com/NullRabbitLabs/nr-bundle-spec][nrbundle]
  under MIT license. JSON Schema + Pydantic reference +
  Python and Rust parsers + 5 example bundles + CI for
  schema regen and cross-language consistency. The spec is a
  separate repo from any corpus; a researcher can adopt the
  format on their own data.
- **`nr-bundles-public`** dataset - live at
  [huggingface.co/datasets/NullRabbit/nr-bundles-public][nrhf-data]
  under CC-BY-4.0. 31 curated bundles spanning multiple
  primitives across Sui + Solana, designed to demonstrate
  the format's utility on real bundles; the full corpus
  remains the moat-via-data differentiator.
- **`v8-cipher-agnostic`** binary detector model - live at
  [huggingface.co/NullRabbit/v8-cipher-agnostic][nrhf-v8]
  under Apache-2.0 (reference detector for the
  cipher-agnostic-v2 7-feature manifest).
- **`multiclass-folded`** unified detector model - live at
  [huggingface.co/NullRabbit/multiclass-folded][nrhf-mc]
  under Apache-2.0 (8-class softmax in the 2026-05-11
  baseline, 9-class in v2 with V16 absorbed; see §8.7 MC-22).
- **`nr-bundle-classifier`** interactive Space - live at
  [huggingface.co/spaces/NullRabbit/nr-bundle-classifier][nrhf-space]
  under Apache-2.0; loads both models for inline scoring of
  user-supplied bundles.
- **This paper** - the working preprint. Documents the
  methodology, the format, the family taxonomy, and the
  V7-narrow technical centerpiece.

[nrbundle]: https://github.com/NullRabbitLabs/nr-bundle-spec
[nrhf-data]: https://huggingface.co/datasets/NullRabbit/nr-bundles-public
[nrhf-v8]: https://huggingface.co/NullRabbit/v8-cipher-agnostic
[nrhf-mc]: https://huggingface.co/NullRabbit/multiclass-folded
[nrhf-space]: https://huggingface.co/spaces/NullRabbit/nr-bundle-classifier

Adoption beyond NullRabbit's corpus is the long-term play.
If researchers cite Bundle v1 on their own data, the format
becomes a reference standard for adversarial-ML research on
blockchain validator infrastructure, which compounds the
moat: the network-effect lives in the format adoption, not
in the corpus itself.

## §3.5 Falsification clause

Our format-stability claim is **falsifiable under additive-
vs-breaking-change semantics**: format-
generalisation holds as long as future fidelity tiers and
modality slots land via additive extensions (new enum members,
new parquet files, new structured fields with deriving
validators), and **falsifies** if a future fidelity tier or
modality slot requires a breaking schema change - for
example, a fidelity tier that requires renaming an existing
manifest field, or a modality that requires repartitioning
the existing parquet schema. To date, three extensions have
landed across the project's V1-through-V7-narrow iteration
arc (D-007 + D-009 + D-020), all additive, with zero breaking
changes. D-015 is the next test case; whichever path it
resolves to, the resolution will either substantiate the
claim further (additive landing) or challenge it (breaking
landing). We document the claim against the empirical
record, not against an asserted property.


# §4 Chain-agnostic family taxonomy

The taxonomy pillar of this paper is the **family-level
controlled vocabulary** that makes cross-chain claims
testable: a model trained on Sui `response_amp` primitives
should detect a Solana `response_amp` primitive at usable
accuracy, and the cross-chain holdout regime (§5) operates at
family granularity. Two decisions land the contract: D-001
fixes the family enumeration; D-002 separates chain-agnostic
family identity from chain-specific primitive identity.

## §4.1 Family enumeration

`FamilyId` is the controlled vocabulary at family granularity:
**11 members - 10 attack families plus 1 benign** (D-001
initial 9 attack families plus benign; D-006 added the
`reconnaissance` family as a 10th attack member, scaffolded
but currently unpopulated). The vocabulary:

| family | mechanism class | corpus population |
|---|---|---|
| `response_amp` | request-to-response byte amplification (response-size-cap mitigation absent) | populated (F10, P05, IA01/IA02/IA02b post-cycle disclosure, SOL_F10) |
| `compute_amp` | small request → large CPU response (devInspect, simulateTransaction wedge) | populated (F14, D03, P06, P07, SOL_F14, SOL_P07) |
| `memory_amp` | small request → large memory allocation | populated (D02) |
| `connection_exhaustion` | TCP / RPC connection-pool depletion | populated (P01) |
| `consensus_abuse` | consensus-layer attack mechanisms (backpressure, randomness manipulation) | populated (D01) |
| `gossip_abuse` | anemo / gossip-layer flooding | populated as `proxy` fidelity (H02) |
| `auth_bypass` | unauthenticated admin / RPC route exposure | populated (H01; H03 as `stub` fidelity) |
| `rate_limiter_bypass` | rate-limiter desync / fail-open mechanisms | populated (GR01, GR02) |
| `service_misconfig` | misconfigured ancillary services (Prometheus, Redis, ES, Grafana, SSH) on validator hosts | populated (5 misconfig primitives) |
| `reconnaissance` | port scans, JSON-RPC method discovery, timing-resonance fingerprints - D-006 | **scaffolded, corpus-bundle unpopulated** (D-014 lab-recon reproducer scaffold landed; bundle population + TRS ingest pipeline deferred per `BACKLOG.md`) |
| `benign` | non-attack traffic (passive recorder, reproducer-benign pipeline, validator-under-load) | populated |

**Bundle-level corpus population state**: 9 of 10 attack
families populated at lab fidelity (with H02 at `proxy` and
H03 at `stub`); 1 family (`reconnaissance`) scaffolded with
deferred bundle population per D-006 + D-014. The benign
family is populated across three TrafficSource strata
(passive recorder, reproducer-benign pipeline,
validator-under-load).

The `reconnaissance` slot is deliberate and methodologically
load-bearing per principle 2 (honest framing). Our
threat-model coverage claim would be dishonest if the slot
didn't exist in the taxonomy - adding it later would be a
v1.0 → v1.1 schema change disturbing reader code, and the
claim would imply the taxonomy missed reconnaissance as a
threat surface. D-006 carved out an explicit exception to
the "tight enum, every member backed by primitive" rule:
threat-model coverage is allowed to declare slots before
population, with the population work tracked in
`BACKLOG.md` (three sub-items: TRS production data ingest, lab
reconnaissance primitives, vector-modality featuriser).

## §4.2 Chain-agnostic family vs chain-specific primitive

D-002 separates two identity axes:

- **`family_id`** is chain-agnostic. The 11-member enum
  applies across Sui, Solana, Cosmos-family, Ethereum, and
  any future chain the format extends to.
- **`primitive_id`** is chain-specific by convention:
  `<chain>_<identifier>`, e.g., `sui_F10_multi_get_objects_amp`,
  `SOL_F10_multi_get_accounts_amp`. The naming convention is
  informal - no validator enforces the `<chain>_*` prefix -
  but the convention is consistent across the corpus and
  carries forward into trainer fold-construction logic.

This separation is what makes the cross-chain claim testable.
Without family-level identity, a model trained on
Sui-only primitives could only ever evaluate against
Sui-only primitives at fold granularity. With family-level
identity, the cross-chain holdout regime (§5.3) trains on
one chain's `response_amp` primitives and evaluates on
another chain's `response_amp` primitives - the same family
acting as the same mechanism-class, manifested in two
chain-specific implementations. Our "family taxonomy is
generative" claim depends structurally on this separation:
`response_amp` as a family means something at the
cross-chain level only if the same `family_id` labels
mechanism-equivalent primitives on different chains.

## §4.3 Generative-not-bounding: IA01/IA02/IA02b post-cycle disposition

Our claim is that the taxonomy is **generative for novel
attacks discovered post-cycle**, not exhaustively bounding
the originally surveyed primitives. The empirical
test: do post-cycle-discovery attacks classify into the
existing taxonomy without extension?

Three Sui validator attacks were discovered after the V4
cycle close (2026-04-30), against Sui's
`sui-indexer-alt-jsonrpc` and `sui-indexer-alt-graphql`
replacement stacks (the legacy JSON-RPC's planned 2026-07-31
sunset replacements). The IA01/IA02/IA02b bundles are
**disclosure bundles** (`disclosure/bundles/sui-pending-IA/`),
not corpus_v1.0 training bundles; the generative claim is that
the existing taxonomy classified them without retraining or
extension, not that they participated in the V7-narrow
trainer. Each was classified into the existing taxonomy
without modification:

| finding | endpoint | mechanism shape | empirical headline | family classification | taxonomy delta |
|---|---|---|---|---|---|
| IA01 | `:6000` JSON-RPC `sui_multiGetObjects` + full show-flags | byte amplification (1,540× per-request, 350 MB/s sustained 8-worker) - F10-mechanism cross-endpoint transfer with traffic-control-machinery absent on replacement stack | 1,540× (F10 was 1,539× on legacy) | `response_amp` | none |
| IA02 | `:7000` GraphQL `multiGetObjects(keys:){objectBcs}` (simple) | byte amplification with GraphQL-CPU throughput ceiling | 272× (1.67 MB/s sustained) | `response_amp` | none |
| IA02b | `:7000` GraphQL `multiGetObjects(keys:){asMovePackage{modules{bytes,disassembly}}}` (rich) | byte amplification via rich GraphQL fragment | 1,277× (7.95 MB/s sustained) | `response_amp` | none |

Three post-cycle attacks classified as `response_amp`
without taxonomy modification. The mechanism-shape table-row
for each - byte amplification on the request/response
boundary - is the F10 mechanism transferring across endpoints
of the indexer-alt replacement stack. This is the
generative-not-bounding evidence our claim requires: the
taxonomy was built from 19 surveyed primitives
on the legacy fullnode JSON-RPC; three primitives discovered
on the replacement stack months later fit the existing
family-level vocabulary without extension. The full
disposition with empirical-measurement provenance is in
`disclosure/bundles/sui-pending-IA/bundle/FINDINGS.md
§"Family classification"`. The claim is corroborated far more
broadly at nine-chain public-CVE scale in §4.6, where dozens of
external CVE / GHSA / audit primitives classify into the
existing families.

## §4.4 Cross-chain family-abstraction empirical evidence

The taxonomy's chain-agnostic `family_id` decision (§4.2) is
design-rationale until the family-level abstraction is
shown to *hold empirically* across chains - i.e., that two
primitives sharing a `family_id` produce detectable
family-level wire signatures even when their chain-specific
implementations differ structurally. `corpus_v1.6` through
`corpus_v1.10` (2026-05-10 / 2026-05-11) populate Solana
analogues across 7 of the 10 attack families (10 primitives,
541 attack bundles); three of those primitive pairs probe
the abstraction at materially different mechanism-similarity
distances.

| Pair | Family | Sui primitive | Solana primitive | Mechanism-similarity |
|---|---|---|---|---|
| A | `response_amp` | `sui_F10_multi_get_objects_amp` | `SOL_F10_multi_get_accounts_amp` | Same mechanism (multi-key RPC batch read), structurally-similar JSON-RPC endpoints |
| B | `auth_bypass` | `sui_H01_admin_interface_no_auth` (HTTP GET/POST on REST routes of a separate admin TCP port; 16 known paths) | `SOL_H01_admin_rpc_probe` (JSON-RPC POST on the main RPC port enumerating admin-class method names; 12+ admin methods) | Same family, structurally-different mechanisms |
| C | `rate_limiter_bypass` | `sui_GR_gasless_rate_fail_open` (programmable transactions with gas-price=0 that the rate-limiter fails-open on) | `SOL_GR01_simulate_compute_flood` (`simulateTransaction` RPC that is gasless by design - the fee market does not apply) | Same family, completely-different mechanisms exploiting the same architectural weakness |

Pair A is the bounded case (similar mechanisms, similar
endpoints) - V8 binary detector transfers at 100% recall
cross-chain (Phase A, 2026-05-10). Pairs B and C are the
mechanism-divergent cases: despite the chain-specific
mechanisms differing structurally, both produce family-level
wire signatures consistent with the family's defining
weakness - high-rate enumeration of admin-class endpoints
with low success rate (Pair B), high request rate against a
free / unmetered path with no fee-market backpressure
(Pair C). Pair B is the strongest case in the chain because
it is the least mechanically-similar pair - REST-route
probing vs JSON-RPC method enumeration; if family-level
signatures survive that much mechanism-diversity, the
abstraction is real.

The framework's family taxonomy is therefore
**mechanism-abstraction-class** rather than
implementation-class: two primitives belong to the same
family when they exploit the same architectural weakness
regardless of chain-protocol mechanism. §8.7 MC-19 frames
the methodology contribution; the load-bearing claim is
that the schema is empirically anchored rather than
design-rationale-only.

**Scope at v1 submission**: this evidence is **taxonomy-
level + mechanism-trace empirical** - the family-level wire
signatures across the three pairs are consistent with the
shared architectural weakness, established via per-primitive
disposition + capture-pipeline traces. **Detector-transfer
empirical** confirmation across Pairs B and C (V10-trained
on Sui H01 evaluated against SOL_H01; V11-trained on Sui
GR evaluated against SOL_GR01 + SOL_P07) is queued forward
work (~½ day from the existing cross-chain cache);
deferred outside v1. The MC-18 v3 three-mode transferability
framework (§8.7) predicts which families' detectors will
generalise cross-chain in terms of feature-semantic
composition; this section establishes that the family
abstraction itself is empirically well-founded as the
substrate the predictions sit on.

## §4.5 Falsification clause

The taxonomy-generative claim falsifies if a post-cycle
attack requires **family extension** - defined precisely as
adding a new family member rather than classifying into an
existing one. Two distinct cases substantiate the falsification
condition:

1. **Strong falsification**: a post-cycle attack whose
   mechanism is genuinely novel relative to the existing
   family vocabulary. Example failure mode: a TLS-handshake-
   layer abuse mechanism that doesn't map to any of the 10
   attack families. If this lands, the taxonomy is bounded
   by the originally surveyed primitives, not generative.

2. **Weak falsification**: a post-cycle attack that fits
   awkwardly into an existing family - multiple plausible
   classifications, no clean mechanism-shape match, or
   forced classification into the closest family at the
   cost of mechanism-class coherence. If this becomes the
   common case for post-cycle classifications, the claim
   weakens from "generative" to "stretchable but
   coherence-degraded."

At v1 submission, three post-cycle Sui attacks (IA01/IA02/IA02b)
classified cleanly into `response_amp` without competing
candidate families and without coherence stress (§4.3). The
falsification record is empirical and forward-trackable, and
the nine-chain scale-up (§4.6) has since exercised it at much
larger scale, returning a split verdict recorded here rather
than elided. Classification-without-extension is the common
case: dozens of public-CVE primitives across Bitcoin, Ethereum,
Cosmos, Monero, libp2p, Dogecoin, and Litecoin folded into the
existing families without competing candidates - strong
generativity evidence well beyond the three-Sui base. But the
clause also fired twice: the Sui Move-VM disassemble-panic
primitive took a **new** network family, `rpc_handler_cpu` (an
RPC handler driven to a crash / CPU-halt state by a malformed
request - a mechanism class distinct from amplification and
exhaustion), and a separate **six-family economic / DeFi attack
layer** (`oracle_manipulation`, `liquidation_abuse`,
`amm_value_extraction`, `governance_capture`,
`protocol_logic_exploit`, `bridge_message_abuse`; D-035,
schema-additive at BUNDLE_VERSION 2 → 3) extended the vocabulary
into a new attack domain. Neither is the "weak",
coherence-degraded stretch the clause warns about - both are
clean new mechanism classes - but under the clause as written
each is a family-extension event. The honest verdict is
therefore that the generativity claim holds as a strong
tendency, not as an absolute: the taxonomy generalises broadly
across chains without extension, and extends cleanly
(additively, not by stretching an existing family) when a
genuinely new mechanism class arrives. Revisions reflect the
cumulative record per principle 4 (methodology contributions
are first-class).


## §4.6 Post-v1 scale-up: the nine-chain public-CVE known-class corpus

v1's two-chain corpus was calibrated to the "additional chains"
v2 trigger (§8.2). That axis has since been exercised directly.
The **public-CVE known-class corpus** spans nine chains -
Bitcoin, Ethereum, Solana, Sui, Cosmos, Monero, Dogecoin,
Litecoin, and libp2p (the shared gossipsub infrastructure
layer, where one model reaches many host chains) - with 47
attack primitives over 53 chain×primitive instances and 966
attack bundles across the nine chains. The load-bearing negative
class brings the trained cut to 1,442 bundles (476 benign); 8 of
those benign bundles are Zcash P2P captures retained as extra
negative traffic - Zcash's own attack primitives are
content-only and excluded from the model cut (§5.6), so Zcash
contributes benign traffic but is not one of the nine attack
chains. The organising discipline is
provenance, not scale: **every attack primitive faithfully
reproduces a specific external public disclosure** - a CVE, a
GHSA, or a named third-party audit - and carries that
disclosure's URL in `provenance.public_source`. Sourcing
strength is uneven and stated as such: Bitcoin is strongest
(21 Bitcoin Core P2P disclosure reproductions - formal CVEs,
bitcoincore.org security disclosures, and a public third-party
DoS disclosure - several inherited on the shared wire by
Dogecoin and Litecoin), then GHSAs (Cosmos SDK,
libp2p / gossipsub) and named audits (Neodyme's Firedancer
reports for the Solana TPU-QUIC primitives, CertiK's Skyfall
write-ups for the Sui Move-VM primitives). The weakest-sourced
RPC-amplification primitives, for which no CVE exists, are our
own `original` measurement and are **excluded** from the
published cut (§5.6).

The negative class is load-bearing and inherits the V1 → V2
co-linearity lesson (§5.4) at nine-chain scale: benign traffic
**exercises the same methods and wire messages the attacks
abuse**, at normal rate and volume. The detector must therefore
separate attack-*use* from benign-*use* of a message type, not
merely "large request" or "high rate". A single multi-family
`HistGradientBoostingClassifier` with isotonic calibration runs
over the `network-v1` feature manifold (pcap aggregates + RPC
response aggregates; NaN-native, degenerate columns dropped by
a per-fit robust-column guard, D-050); inference is
scoreability-gated, so a record with no network signal returns
no verdict rather than a false one.

Three evaluation results, named separately so the binary signal
is not read as more than it is:

- **Within-chain binary attack-vs-benign** (GroupKFold held out
  by primitive): ROC **0.9641** (82 primitive groups). This is
  the detector's usable signal - and it is diagnostic, on
  synthetic lab traffic, not a deployment number.
- **Zero-shot leave-one-chain-out binary** (train the other
  eight chains, test the held-out one): **0.67-1.00** - Dogecoin,
  Litecoin, and Sui 1.00, Ethereum 0.99, Cosmos 0.90, Bitcoin
  0.90, libp2p 0.87, down to Monero 0.78 and Solana 0.67. A HARD
  transfer probe, not a deployment metric. What sets the tail is
  protocol-distinctness, not primitive count: Monero (its unique
  Levin/epee wire) and Solana (QUIC) share the fewest wire-level
  near-neighbours with the rest of the corpus and sit lowest,
  whereas chains with equally few primitives still separate
  cleanly when their wire is well-represented elsewhere - the
  Bitcoin-forks Dogecoin and Litecoin trivially, and Sui because
  its amplification attacks are starkly separable from benign.
- **Cross-chain family recovery** (leave-one-chain-out, macro-F1
  over the families the held-out chain shares with the rest):
  **uneven, and near the floor exactly where transfer would be
  non-trivial**. Holding out a protocol-distinct chain collapses
  it - 0.16 (Monero, 3 shared families), 0.18 (Bitcoin, 6), 0.36
  (Ethereum, 3), 0.42 (Cosmos, 3), 0.46 (libp2p, 2); it is high
  (1.00 Dogecoin, 0.70 Litecoin; 3 shared families each) only
  where the held-out chain is a wire-identical
  fork running Bitcoin Core's exact primitives on a renamed wire,
  so "transfer" there is trivial rather than evidence of
  generalisation. Sui and Solana each share too few families
  with the rest of the corpus (one apiece) for the question to be
  posed at n=9 at all; the n=2 joint-trained Sui ↔ Solana
  characterisation (§8.2) is where those two are quantified.
  Recovering *which* family a held-out, protocol-distinct chain's
  attack belongs to, zero-shot, is near chance.

The three answer different questions. Binary transfer asks only
whether held-out traffic *looks like an attack at all* - a gross
traffic-shape question that survives moderate wire-distinctness
(Sui tops it at 1.00) - whereas family recovery asks *which
mechanism*, which does not; that gap is why a chain can lead the
binary axis yet be unposable on the family axis. The within-chain
binary signal is real; the cross-chain family-recovery collapse
on the protocol-distinct held-out chains is the two-chain V7-narrow
non-transfer finding (§6) reproduced at nine-chain scale, and is
the harder zero-shot regime beyond the joint-trained n=2
Sui ↔ Solana multi-class results of §8.2. Conflating them -
letting the ~0.96 binary ROC stand in for cross-chain
generalisation - is exactly the overclaim the methodology exists
to prevent. Mechanism-class detection is a within-chain result;
whole-taxonomy cross-chain transfer remains an open problem.

Two ceilings bound the corpus, stated per principle 2. It is
**diagnostic, not a deployment claim**: bundles are synthetic
localnet reproductions at lab fidelity; detection is on traffic
*shape* (rate, size, connection-churn), not deep wire
semantics, so it would not separate two attacks with identical
traffic profiles; and there are no host-load features (the
containerised lab node is root-owned). A deployment claim needs
a real-traffic validation gate - real mainnet RPC plus real
attack instances - the network analogue of the economic
detector's held-out real-data ladder (D-049). Until that gate
exists the corpus is a worked, public-provenance reference, not
a turnkey IDS.


# §5 Iterative leak-surface peeling methodology

The methodology centerpiece of this paper is **iterative
leak-surface peeling**: a discipline for surfacing and closing
ML-detection failure modes one cycle at a time, with each
cycle's audit findings driving the next cycle's design. Five
sub-sections specify the discipline. §5.1 covers
pre-registration structure. §5.2 enumerates the multi-layer
falsifiability framework. §5.3 specifies the LOPO regime
including the per-chain holdout direction (D-018) that the
V6 → V7-narrow arc identifies as load-bearing for
cross-chain claims. §5.4 walks the V1 → V7-narrow iteration
arc as empirical demonstration. §5.5 states the methodology's
falsification clause.

## §5.1 Pre-registration discipline

Each retraining cycle pre-registers against a structured
design document with three sections, in order:

- **Section A - corpus composition**: which corpus version,
  which chains, which fidelity tiers, which exclusions, with
  rationale per excluded primitive or fidelity class. The
  corpus delta versus the previous cycle is named explicitly;
  if no corpus delta, that's stated. Corpus-side decisions
  are locked here, not at training time.
- **Section B - feature filter**: which features are excluded
  before fold construction (e.g., `V3_REMOVED_FEATURES` =
  `{app.scrape_duration_s, app.row_count, host.duration_s,
  host.sample_count}` - the 4 capture-config features the
  V2 → V3 transition removed, per Section 5.4). Feature-set
  iteration happens at the manifest level (`RATE_INVARIANT_V1`,
  `RATE_INVARIANT_V2`, `CIPHER_AGNOSTIC_V1`); each manifest
  pre-registers before training.
- **Section C - outcome triggers**: numerical thresholds,
  structural predictions, outcome-band composition rules. The
  thresholds are locked **before** the headline numbers land
  - the ROC bands defining Outcome A / B / C, the
  per-feature single-feature-ROC red triggers, the joint
  composition rule for multi-dimensional findings.

The Section A / B / C separation is methodologically
load-bearing. Confusing the levels - moving an outcome band
to fit a number, or treating a corpus delta as a feature
filter - is how methodology drift starts. Each cycle's
design doc commits before any retrain executes; the locked
artefact is what the auditor reviews at the gate, not the
design-after-the-numbers.

The auditor itself is operationalised as a methodology-
discipline agent. The agent reviews each cycle's design,
each TrainReport, and each cycle-close artefact against the
pre-registered structure and outcome triggers; verdicts at
gates enforce evaluation against locked thresholds. The
agent's verdict discipline includes a pre-ESCALATE
self-check (escalation list exhaustive; runway / paper /
customer implications do not transmute methodology into
strategy; clear methodology read commits) added 2026-05-02
in response to documented agent-discipline incidents - the
Phase-6a addendum cycle surfaced falsifiability-layer
conflation + decision-citation confabulation
(`AUDITOR-PROTOCOL.md` operational provenance); the
V6-auditor-close meta-correction surfaced over-escalation
patterns (`DECISIONS.md` D-019 references). Both clusters
are detailed in §8.6 as transferable agent-discipline
contribution.

### §5.1.1 Seven methodological principles

Seven foundational commitments anchor the methodology.
Subsequent sections refer to them as "principle N":

1. **Pre-registration discipline.** Each cycle's analytical
   decisions and outcome triggers commit before headline
   numbers land; the locked design-doc is what the auditor
   reviews at the gate.
2. **Honest framing.** A cycle's verdict reports the
   load-bearing finding accurately - including null,
   sub-chance, or falsified outcomes - rather than
   reframing post-hoc to favour a positive result.
3. **Outcome pre-commitment before headline numbers land.**
   ROC bands, sanity-floor thresholds, and outcome-band
   composition rules lock at design-doc time; subsequent
   numbers either substantiate or falsify the
   pre-registered prediction.
4. **Methodology contributions are first-class artefacts.**
   A cycle's methodology output (closed leak surface,
   feature-filter rule, holdout-regime refinement) persists
   as substrate-paper material independently of the
   evaluation-gate outcome.
5. **Distinguishing corpus-design failures from
   lab-fidelity limits.** A finding traceable to
   capture-pipeline asymmetry between attack and benign is
   a corpus-design failure (closeable in the next cycle); a
   finding traceable to the lab environment's intrinsic
   reproduction limits is a fidelity-tier limit (reframed
   as a scope constraint, not as a model failure).
6. **The model is not the variable.** Trainer
   hyperparameters (HGB `max_iter=200, learning_rate=0.05,
   max_depth=8`, isotonic-calibrated, K=20% stratified
   benign holdout) inherit unchanged across V4 → V5 → V6 →
   V7-narrow; iteration variables are corpus + manifest +
   holdout regime. This isolates methodology effects from
   model-architectural confounds.
7. **Pre-registration anchor specificity.** Pre-registered
   thresholds anchored on prior-cycle measurements or
   baseline-behaviour assumptions specify the anchor
   explicitly. Anchors that equate retention to absolute via
   baseline-substitution, or that set thresholds "deeper
   than" a prior cycle without naming the prior value, are
   pre-registration-anchoring failures. Cycle evidence:
   §8.7 MC-1 (Layer-1 baseline-substitution at the Step-11
   V1 outcome-band rationale) + MC-5 (Layer-2 §C.3-bis
   "deeper than V7-narrow" threshold without explicit
   anchor).

## §5.2 Multi-layer falsifiability framework

Falsifiability operates at four layers; each layer's
discriminator is independent of the others, so a leak that
escapes one layer can surface at another:

- **Layer 1 - numerical thresholds + sanity floors**. ROC
  bands compose per cycle outcome. Sanity floors:
  `random_features` median ROC < 0.55 (audit-doc green band;
  trainer red threshold `RED_RANDOM_FEATURE_MAX = 0.65` per
  `lopo_v2.py:69`; observed 0.49–0.54 across V2 → V7-narrow);
  `shuffled_labels` median ROC < 0.55 (analogous 0.65 red
  threshold; observed 0.50–0.55); single-feature stress
  red threshold = 0.90 (`SF_YELLOW_MAX` per `lopo_v2.py:66`;
  the V1 / V2 / V3 / V5 single-feature reds at 1.000 fire
  well above).
  V1's contamination - `random_features` ROC = 1.000 -
  surfaced via this layer; V2's
  `app.distinct_metric_names` capture-pipeline-metadata leak
  surfaced as single-feature ROC = 1.000.
- **Layer 2 - structural predictions** (per-feature efficacy
  table). Pre-registered predictions of how specific features
  behave under cross-chain composition, with per-feature
  falsification conditions. The v5-pre taxonomy
  (`STEP-8-AUDIT-FINDINGS-V2.md §v5-pre`) pre-registered five
  per-feature predictions before the V5 retrain; V6 expanded
  to six features after V5 surfaced
  `host.io_write_delta` modality-population asymmetry
  unpredicted by v5-pre. The disambiguation experiments
  (SE1/SE2/SE3 in §6) are layer-2 falsifiability applied at
  the feature granularity.
- **Layer 3 - outcome-band composition**. Joint A / B / C
  rules compose across multiple load-bearing
  dimensions. V6's joint-outcome rule had three dimensions
  (rate-invariant ROC per chain × per-chain feature efficacy
  predictions × Sui rate-mask floor); V6's Joint-C verdict
  triggered on dimension 1 alone (per-chain Sui ROC = 0.34
  < 0.65). Layer-3 composition prevents single-dimension
  pass / fail from dominating the multi-dimensional
  evaluation.
- **Layer 4 - auditor-protocol gate**. Cycle-close verdicts
  enforce pre-registered outcome-band evaluation against
  locked thresholds. The agent reviews the TrainReport, runs
  the pre-ESCALATE self-check, and produces an explicit
  verdict (APPROVED / APPROVED WITH REFINEMENTS / NOT
  APPROVED - HALT / ESCALATE). The §8.6 agent-discipline
  contribution documents this layer as a transferable
  pattern beyond this project.

The four layers operate as independent discriminators against
the same artefact. A leak that fits noise (caught at Layer 1
via shuffled-labels) is structurally distinct from a leak
that's a single dominant feature (caught at Layer 1 via
single-feature stress); both are distinct from a leak that
manifests as cross-chain anti-transfer of specific
feature-class semantics (caught at Layer 2 + Layer 3 via the
per-chain holdout direction). Multi-layer falsifiability is
this paper's methodological generalisation: a single
falsification gate is brittle; layered gates surface leaks
the others miss.

## §5.3 LOPO + per-chain holdout direction

Cross-validation regime decisions are pre-registered as part
of Section A / B / C structure. Three regimes operate:

- **Per-primitive LOPO** (V2 baseline). Each fold holds out
  all bundles of one attack primitive; the model trains on
  the remaining 18 primitives plus stratified benign and
  evaluates on the held-out primitive's bundles plus
  stratified benign. Standard leave-one-X-out with attack
  primitive as the X.
- **Stratified benign holdout (Regime A)** - closes V1 LOPO
  contamination. V1 left out one attack primitive per fold
  but kept all 61 benign rows in both train and test (the
  contamination that produced random-feature ROC = 1.000).
  Regime A partitions benign across folds with a stratified
  hold-out matched to the attack primitive's expected size;
  random-feature ROC drops to chance immediately.
- **Per-chain holdout direction (D-018)** - load-bearing for
  cross-chain claims. Train on one chain entirely; evaluate
  on the other entirely. The V5 cross-chain LOPO trained on
  Sui + Solana primitives jointly with per-primitive folds;
  the result was per-chain saturation of the headline at ROC
  = 1.000 carried by chain-deterministic features (V5
  `pcap.top_dst_port_fraction` Joint C). V6 added the
  per-chain holdout direction explicitly: train Sui only,
  evaluate Solana; train Solana only, evaluate Sui. The
  per-chain holdout regime is what surfaced V6's
  hold-out-Sui ROC = 0.34 sub-chance (anti-classification),
  the empirical evidence for the V7-narrow multi-mechanism
  finding (§6).

The D-018 per-chain holdout direction is a substrate-paper-
grade methodology contribution beyond this project: any
cross-chain ML evaluation using per-primitive LOPO with
by-chain summary aggregation alone can saturate to ROC = 1.000
on chain-deterministic features without surfacing the
underlying cross-chain mechanism non-transfer. Per-chain
holdout direction surfaces it.

## §5.4 The iteration arc V1 → V7-narrow

The methodology's empirical demonstration is the V1 → V7-
narrow arc. Each cycle's audit-finding drove the next cycle's
design; the closed-leak set grew monotonically.

| cycle transition | leak surface surfaced | response (next-cycle design) |
|---|---|---|
| V1 → V2 | LOPO benign contamination (`random_features` ROC = 1.000); capture-pipeline co-linearity (`resp.count` ROC = 1.000 on 14 of 17 folds; attack reproducers populate the response modality, synthetic-client benign do not) | Stratified benign holdout (Regime A) closes contamination; sanity-floor discriminators added; corpus_v1.0 → v1.1 delta adds `BENIGN_reproducer_pipeline` primitive (synthetic-load reproducer that calls `record_response()`) - closes capture-pipeline-co-linearity at corpus level per `STEP-8-AUDIT-FINDINGS.md` lines 225–234 |
| V2 → V3 | `app.distinct_metric_names` single-feature ROC = 1.000 (capture-pipeline metadata leak surviving the V2 corpus fix; the feature counted Prometheus-scraped distinct metric names which differs systematically between attack and benign capture pipelines) | Section B feature filter - drop 4 capture-config features (`app.scrape_duration_s`, `app.row_count`, `host.duration_s`, `host.sample_count`) before fold construction |
| V3 → V4 | `pcap.mean_packet_size` carries headline at lab fidelity; KDE-overlap ~0.05 across two driver hypothesis-tests (corpus_v1.3 connection-per-RPC + corpus_v1.4 HTTP-keepalive); the lab-fidelity reproducers cannot produce mean-packet-size distributions overlapping with benign | Lab-fidelity-bound demonstration complete; `pcap.mean_packet_size` reframed as Step-7 mainnet-capture requirement (D-013 deferred Step-7); methodology contributions persist independent of headline |
| V4 → V5 | Lab-fidelity-bound finding generalises target; cross-chain extension to Solana required for substrate claim's chain-portability dimension | V5 design pre-registration (D-017): cross-chain LOPO across Sui + Solana corpus per D-016 scope; RATE_INVARIANT_V1 manifest pre-registered (17 features post-Section-B) |
| V5 → V6 | V5 Joint-C: chain-deterministic port leak in RATE_INVARIANT_V1 (`pcap.top_dst_port_fraction` ROC = 1.000); per-chain holdout direction missing; `host.io_write_delta` modality-population red unpredicted by v5-pre taxonomy | V6 design: RATE_INVARIANT_V2 (port features removed; D-018 dec 1); per-chain holdout direction added (D-018 dec 2); v5-pre taxonomy expanded to include modality-population asymmetry |
| V6 → V7-narrow | V6 Joint-C: per-chain holdout collapse (hold-out-Sui ROC = 0.3399 sub-chance, hold-out-Solana ROC = 0.5000 boundary); finding-#3 hypothesis-grade with three competing hypotheses (chain-asymmetric mechanism / undertraining artefact / lab-fidelity-mediated false transfer) | V7-narrow disambiguation sub-experiments SE1/SE2/SE3 (D-019); SE2 falsifies undertraining (hold-out-Sui ROC 0.3399 → 0.3207 with bootstrap-upsampled Solana training); SE1 partial-recovers (`pcap.mean_packet_size` exclusion lifts hold-out-Sui ROC 0.3399 → 0.6298; hypothesis (iii) partially supported, lab-fidelity-bound feature contributes ~83% of gap but doesn't fully explain - multi-mechanism finding hardens per `STEP-8-AUDIT-FINDINGS-V2.md §v7-narrow` lines 1913-1928); SE3 confirms chain-asymmetric mechanism at feature-level (resp.status_*_frac + resp.amp_ratio_max anti-transfer) |

The table compresses V2 → V2.5 → V3 and V3 → V3.5 → V3.6
→ V4 sub-iterations into single rows for exposition; the
eight-entry full-fidelity inventory is in §8.5.

Each transition demonstrates the methodology working as
designed. Pre-registered outcome triggers fired correctly
at each cycle close - V1's contamination per Layer 1
(random-features sanity floor); V2's residual leak per
Layer 1 (single-feature stress); V3's lab-fidelity-bound
finding per Layer 2 (KDE-overlap structural prediction); V5's
chain-deterministic leak per Layer 1 + Layer 3 (single-feature
stress + outcome-band composition); V6's per-chain holdout
collapse per Layer 1 (per-chain ROC threshold); V7-narrow's
multi-mechanism finding per Layer 2 (per-feature anti-transfer
structural prediction with concrete falsification conditions
disambiguating three competing hypotheses).

The methodology contributions across the arc - Regime A
stratified benign holdout, Section B feature filter, the
lab-fidelity-bound demonstration framing,
RATE_INVARIANT_V1/V2/CIPHER_AGNOSTIC_V1 manifest discipline,
the per-chain holdout direction, the V7-narrow disambiguation
sub-experiment design - persist forward into Step-11 + future
cycles independently of any single cycle's headline outcome.
The closed-leak set is the methodology's evidence; §6 walks
V7-narrow as the technical centerpiece in detail.

## §5.5 Falsification clause

The methodology's load-bearing falsification clause is stated
in §1 and §9: methodology falsifies if a future cycle
surfaces a load-bearing finding the audit-trail framework
cannot honestly frame as Joint A / B / C - i.e., a finding
that exceeds the falsifiability-layers framework's expressive
capacity rather than fitting one of its outcome bands. The
four-layer framework specified in §5.2 substantiates the
claim; §5.4 walks the V1 → V7-narrow arc demonstrating that
each cycle's audit findings fit one of the framework's
outcome bands.

**Four-layer-coverage falsification clause (pre-registered
in v1).** The framework also falsifies at a coverage level
distinct from the per-layer expressive-capacity clause above:
methodology falsifies at the coverage clause if a future
cycle produces clean Layer 1–4 verdicts while a leak surface
escapes via **canonical fact-check** - defined as line-level
cross-check of cited claims against the canonical source
artefact (`DECISIONS.md` Status fields, audit-doc section
citations, or run-tag-pinned TrainReport JSON). The four
layers gate against expressive-capacity escape; canonical
fact-check gates against citation-vs-canonical drift. A
clean-four-layers verdict that survives canonical fact-check
substantiates the methodology; a clean-four-layers verdict
that fails canonical fact-check falsifies the coverage
claim and triggers reframe under principle 4 (methodology
contributions are first-class).

The auditor-failure-mode incident documented at
`STEP-8-AUDIT-FINDINGS-V2.md §"Auditor failure mode"`
(2026-05-03) is the documented instance against this
pre-registered clause: structural review approved a
four-extension cumulative claim that line-level fact-check
against canonical `DECISIONS.md` Status fields reduced to
three. The incident did not falsify the coverage clause
(canonical fact-check surfaced the drift before the claim
landed publicly), and the cycle-close response - agent
system prompt + AUDITOR-PROTOCOL upgraded with §"On citing
project decisions" requiring exact source citation (§8.6) -
is the principle-4 methodology contribution the clause
generated.

A Layer-1-instance pre-registration-anchoring failure
documented at the Step-11 V1 close - the §C.2 outcome-band
rationale anchored against an empirical assumption that
didn't hold under the cycle's actual numbers - is treated as
substrate-paper material at §8.7 MC-1; the Layer-2-instance
counterpart (§C.3-bis falsification clause anchored on an
arbitrary threshold rather than the explicit prior-cycle
measurement) is documented at §8.7 MC-5.


## §5.6 Provenance-class publishability discipline + the automated guarded cycle

Two disciplines added since v1 operationalise the same
pre-registration-and-honest-framing commitments at corpus
scale, and both are methodology contributions in their own
right per principle 4.

**Provenance-class discipline (publishable vs disclosure-gated).**
Security-detection corpora mix two kinds of attack: faithful
reproductions of someone else's *already-public* disclosure,
and one's *own* undisclosed findings. Publishing the first is
safe; publishing the second burns a coordinated-disclosure
window. We make the distinction a first-class, machine-checked
bundle property rather than a per-artefact judgement call.
Every attack bundle carries a `provenance.source_class`:
`public-cve-replication` (a faithful reproduction of an
external CVE, GHSA, named third-party audit, or published
post-mortem, referenced by URL in `provenance.public_source` -
nothing of ours is revealed, so it is publishable) or
`original` (our own finding or measurement - disclosure-gated,
not for publication until it has cleared the disclosure track).
The decision rule is one line: *if removing the thing from the
world would remove a NullRabbit secret it is `original`; if it
only re-states what is already public it is
`public-cve-replication`.* A per-primitive registry
(`known_class_provenance.py`) is the authoritative map and a
stamper writes the field into every manifest and **errors on
any unclassified attack** - an attack cannot ship unlabelled.
The field is ratified in `nr-bundle-spec` v0.1.3 as an additive
optional field (no `BUNDLE_VERSION` change). The **published
cut is `public-cve-replication`-only**: the `original`
RPC-amplification primitives are dropped from *training*, not
merely from the tables, so the model card's claim to be
"trained entirely on reproductions of publicly-disclosed
issues" is literally true.

**The automated, guarded cycle (reproducibility as code).**
The corpus is no longer hand-tended; it is produced by a
pipeline in which each discipline above is enforced by a
program, not per-session diligence. (1) *Research* - a daily
CVE feed pulls public disclosures from OSV, NVD, and GitHub and
triages each with a cheap model (DeepSeek-v4-flash, measured
~$0.00008/advisory) into a local store, replacing a costly
weekly hand-run research pass. (2) *Forge* - a stronger model
(DeepSeek-v4-pro, ~$0.002/draft) drafts an attack driver from
the disclosure; the draft is executed against a **live
vulnerable node**, and a reproduced crash confirms the driver
is faithful (auto-accepted) while a non-crash routes to human
review. (3) *Train* - a nightly job retrains each detector's
full corpus behind a standing quality gate (Cleanlab
label-issue scan + exact-duplicate count + held-out ROC via
GroupKFold-by-primitive, D-051). (4) *Package* - the public cut
is auto-selected (public-cve-replication attacks + all benign),
trained, clean-gated, and built into an HF bundle with a
release certificate. (5) *Guard* - a **publish-guard** enforces
the release rules before anything ships: no author-attribution
strings, no disclosure-gated identifiers, no secrets or local
paths, every shipped attack `public-cve-replication` *and*
registered, the release-cert fully passing, and the card's
declared counts matching the cut; on any violation the cut is
built but **not pushed**, and the operator is escalated. (6)
*Card* - the model card is regenerated from the same cut the
model trained on, so the published numbers cannot lag the
shipped model.

The forge is framed honestly, because its limits are the
reason the node-crash-plus-human gate is load-bearing rather
than decorative. On a blind benchmark (the model given only the
CVE text and unrelated style references, its output diffed
against the hand-written driver) it was **excellent on
templated single-message CVEs** - "functionally identical to
the human version" - and **unsafe on hard ones**: on a vague,
multi-message CVE it was "plausible but WRONG on three counts"
- wrong root cause, a hallucinated library API, and a dropped
follow-up message. The honest verdict is "yes for cheap
templated single-message CVEs (near-identical to hand-written),
but it confidently hallucinates on hard cases", so the model is
wired as a first-draft generator behind the existing
deterministic gate ("does the traffic actually reproduce
against a node?"), never as hands-off autogen. The methodology
contribution is not the model but the arrangement: cheap
generation is admissible *only* because a deterministic
reproduction check plus a human capture gate catches the
confident-but-wrong cases it produces.


# §6 V7-narrow multi-mechanism finding

The V7-narrow cycle is this paper's technical centerpiece. Where §5 specifies the methodology and §5.4 walks
the iteration arc compressed into a six-row table, §6 unpacks
the V6 → V7-narrow transition in detail: what V6's per-chain
holdout direction surfaced, how V7-narrow's three sub-experiments
disambiguated three competing hypotheses, and what the
hardened multi-mechanism finding implies for cross-chain ML
detection at lab fidelity. Numerical detail in tables A.1–A.4
(Appendix A); main-text framing emphasises the structural
finding.

## §6.1 Setup

V6 added the per-chain holdout direction (D-018 dec 2) to the
cross-chain LOPO regime: train on one chain entirely, evaluate
on the other entirely. Run D - `RATE_INVARIANT_V2` manifest
(13 features post-port-removal) under per-chain holdout -
produced two folds with materially distinct outcomes
(`STEP-8-AUDIT-FINDINGS-V2.md §v6 (actual)` lines 1597–1615):

- **hold-out-Sui** (n_train=605 Solana bundles, n_test=1343
  Sui bundles): ROC = **0.3399** - *sub-chance*. The model
  trained on Solana ranks Sui benigns above Sui attacks more
  than half the time. Anti-classification.
- **hold-out-Solana** (n_train=1343 Sui, n_test=605 Solana):
  ROC = **0.5000** - chance. The B/C-band boundary; Joint C
  trips on the Sui side alone. Solana boundary is
  informational.

Joint-C verdict: the cross-chain mechanism claim falsifies at
the V6 evaluation gate. But the Sui-side anti-classification
specifically is hypothesis-grade: a sub-chance ROC could arise
from at least three mechanisms, and which one drives V6's Run
D outcome materially shapes the claim. Three competing
hypotheses entered V7-narrow:

- **(i) Chain-asymmetric mechanism** - the Sui shape-signal is
  structurally different from the Solana shape-signal at the
  rate-invariant manifest layer; a model trained on Solana
  features the wrong feature distributions for Sui evaluation,
  inverting the label-feature relationship cross-chain.
- **(ii) Undertraining artefact** - n_train=605 Solana bundles
  is small relative to the 13-feature manifest; bootstrap
  upsampling Solana to ~1343 might recover the Sui-side ROC.
- **(iii) Lab-fidelity-mediated false transfer** -
  `pcap.mean_packet_size` is a known V4 lab-fidelity-bound
  red (`§v4 (actual)` lines 1133–1155); the feature's
  distribution-shape mediates an artificial Sui-vs-Solana
  separation that doesn't reflect attack-mechanism transfer.

Each hypothesis has a concrete falsification condition in the
trainer's reach. V7-narrow pre-registered three sub-experiments
(D-019) targeting the three hypotheses individually.

## §6.2 Disambiguation design (D-019)

V7-narrow's three sub-experiments are designed orthogonally:
each isolates one hypothesis's falsification condition without
the others.

- **SE1 - `pcap.mean_packet_size` excluded** (12-feature
  manifest, per-chain holdout, otherwise identical to V6 Run
  D). Tests hypothesis (iii). If `pcap.mean_packet_size` is
  the dominant driver of the anti-classification, removing
  it should recover Sui-side ROC toward chance or above. If
  it isn't dominant, the ROC stays sub-chance.
- **SE2 - Solana training upsampled (n_train 605 → 1343 via
  bootstrap)** with the full 13-feature `RATE_INVARIANT_V2`
  manifest, per-chain holdout. Tests hypothesis (ii). If
  undertraining is the cause, doubling the training-side
  bundle count should lift the Sui-side ROC. If it's not the
  cause, the ROC stays sub-chance.
- **SE3 - per-feature single-feature ROC sweep** (13 single-
  feature classifiers per fold direction). Tests hypothesis
  (i) at feature granularity. If the chain-asymmetric
  mechanism is real, specific features should anti-transfer
  cross-chain (single-feature ROC < 0.45 on at least one fold
  direction); features that transfer symmetrically should
  cluster around chance to weakly-positive on both directions.

The three sub-experiments are pre-registered before any
retrain executes - outcome triggers locked at design-doc
landing per §5.1 Section A/B/C discipline.

## §6.3 Results (headline)

The three sub-experiments produced cleanly distinguishable
outcomes (`§v7-narrow (actual)` table at lines 1846–1848):

| sub-experiment | hold-out-Sui ROC | trigger | verdict |
|---|---:|---|---|
| SE1 (mps excluded) | **0.6298** (V6 was 0.3399; +29 percentage-point lift) | [0.55, 0.65) → partial recovery | hypothesis (iii) **partially supported** |
| SE2 (Solana upsampled) | **0.3207** (V6 was 0.3399; effectively unchanged) | < 0.55 → persist | hypothesis (ii) **FALSIFIED** |
| SE3 (per-feature sweep) | feature-level pattern (Table A.3) | mixed: anti-transfer features + most-symmetric reference | hypothesis (i) **CONFIRMED at specific feature subset** |

SE2 falsifies undertraining cleanly: bootstrap-upsampling
Solana training from 605 → 1343 bundles produced no
material lift (0.3399 → 0.3207, well within fold noise).
Hypothesis (ii) is out.

SE1 partially supports lab-fidelity-mediation: removing
`pcap.mean_packet_size` lifts hold-out-Sui ROC from 0.3399 to
0.6298 - a 29-percentage-point lift, ~83% of the gap from
the original sub-chance to the chance line. But 0.6298 is
in the [0.55, 0.65) partial-recovery band, not above the
0.65 threshold for full recovery; the lab-fidelity-bound
feature is not the *only* driver. Hypothesis (iii) is in,
but it doesn't fully explain the anti-classification.

SE3 confirms the chain-asymmetric mechanism at feature
granularity (Table A.3 per-feature ROCs). Specifically,
four features have single-feature ROC < 0.45 on **both**
fold directions:

- `resp.status_2xx_frac`: 0.2508 (one fold) / 0.3333 (other)
- `resp.status_4xx_frac`: 0.2508 / 0.3333
- `resp.status_5xx_frac`: 0.2508 / 0.3333
- `resp.amp_ratio_max`: 0.1834 / 0.3808

A single feature with sub-chance ROC on both fold directions
means the feature's relationship to the attack/benign label
*inverts* cross-chain - Sui attacks and Solana attacks
produce systematically different distributions on these
features, such that a model trained on one chain classifies
the other chain in the wrong direction. By contrast,
`resp.amp_ratio_median` shows ROC = 0.5820 / 0.6227 across
the two fold directions - the most-symmetric rate-invariant
signal, transferring modestly cross-chain at chance-or-better
both ways.

## §6.4 Structural finding: cross-chain mechanism non-transfer is feature-localised

The substrate-paper-grade V7-narrow claim is **structural,
not a single ROC retention number**: cross-chain mechanism
non-transfer in this domain is **feature-localised, not
whole-feature-space**. The methodology produces feature-level
mechanism boundaries; a single ROC retention number would
have given far less information.

Three disambiguated mechanisms are evidence supporting the
structural claim:

- **Lab-fidelity mediation** (~83% of V6 Run D Sui ROC deficit
  per `STEP-8-AUDIT-FINDINGS-V2.md §v7-narrow (actual)` line
  1917; SE1 lift 0.3399 → 0.6298, +29 percentage points):
  `pcap.mean_packet_size` carries asymmetric false transfer
  cross-chain in cleartext-trained → cleartext-evaluated
  regime; the V4 lab-fidelity-bound finding generalises to
  the cross-chain composition.
- **Chain-asymmetric mechanism, feature-localised**: anti-
  transfer concentrates in `resp.status_*_frac` (HTTP status
  fractions) + `resp.amp_ratio_max` - first instance of
  feature-level cross-chain non-transfer evidence in this
  project. SE3 per-feature single-feature ROC: each of the
  four features cited has ROC < 0.45 on **both** fold
  directions - well below the chance band, evidencing
  systematic anti-transfer (Appendix A Table A.3).
- **Symmetric cross-chain transfer** in `resp.amp_ratio_median`
  (most-symmetric V7-narrow finding) - the residual genuine
  cross-chain shape signal at modest signal strength.

The structural finding distinguishes mechanism classes that a
single-number Outcome A / B / C verdict on retention alone
would have collapsed. Cross-chain methodology that produces
*"detection retention ROC = 0.34"* is brittle - the headline
number doesn't separate "lab-fidelity bug masking real
mechanism" from "chain-asymmetric mechanism" from "small
training corpus." V7-narrow's disambiguation produces three
distinguishable mechanisms with concrete per-feature
falsification conditions, layered onto the multi-layer
falsifiability framework (§5.2).

**Scope qualifier**: the subsequent Step-11 V8 retrain
(§7.2) reframes the cipher-agnostic byte-count manifest
layer specifically; the `resp.status_*_frac` chain-
asymmetric pattern at the rate-invariant 13-feature manifest
layer remains live as a finding (§8.7 MC-2 details the
auditor-scoped reframe).

## §6.5 Implications

The feature-localised non-transfer pattern has three
methodologically load-bearing consequences:

1. **Pre-registered sequencing prevents ill-founded corpus
   expansion.** V7-broader (Solana corpus expansion to
   `solana_corpus_v1.1`) was pre-registered as conditional
   on SE2 producing clean recovery (D-019 dec 2 sequencing).
   SE2 falsified hypothesis (ii); V7-broader does NOT fire.
   The methodology saved ~1–2 weeks of wallclock on a
   corpus-iteration cycle that the falsification result
   tells us would not have produced new evidence. Choosing
   not to expand because pre-registered evidence said it
   wouldn't help is itself a methodology contribution per
   principle 4 (methodology contributions are first-class).
2. **The cipher-agnostic feature subset (D-020 + §7)
   removes the anti-transfer features by construction.**
   `CIPHER_AGNOSTIC_V1` excludes `resp.status_*_frac` and
   the rest of the body-parse-required features, retaining
   only TLS-frame-level observables. The cipher-agnostic
   boundary derivation (D-020 dec 2) is consistent with
   V7-narrow's feature-level anti-transfer evidence - Step-11
   Component 1's empirical retention numbers test this
   consistency claim. Cipher-agnostic ROC retention ≥ 80%
   on both chains validates V7-narrow's localisation-to-
   status-fields Layer-2 structural prediction; < 80%
   retention with status-fields-included higher than
   status-fields-excluded would falsify the localisation
   claim.
3. **Methodology contributions persist regardless of
   evaluation-gate outcome.** V7-narrow's headline outcome is
   Joint C (cross-chain mechanism claim falsified at lab
   fidelity); the multi-mechanism finding is the V7-narrow
   contribution. §8.1 frames the methodology-as-finding
   thesis canonically.

V7-narrow's reproducibility commitment: SE1 run-tag
`step10_v7_se1_run_20260502T214310Z_seed42`; SE2
`step10_v7_se2_run_20260502T220513Z_seed42`; SE3
`step10_v7_se3_run_20260502T222723Z_seed42` per
`STEP-8-AUDIT-FINDINGS-V2.md §v7-narrow (actual)`. Numerical
evidence in Appendix A. The §6 main-text framing prioritises
the structural finding over per-cell number recitation; the
appendix carries the full per-fold ROCs, cohen_d landscape
across V4 → V5 → V6 → V7-narrow manifest progression, and
SE3 per-feature single-feature ROC table.


# §7 Fidelity-tiers framework + Step-11 empirical Joint A

Our fidelity-tiers framework derives a **cipher-agnostic
feature subset** - a manifest restricted to features
observable at the TLS-frame level without cleartext body
parsing - pre-registers an empirical retention measurement
(Step-11 Component 1), and reports the Step-11 V1 + V8
retrain results that close the cycle. v1 ships the framework
+ pre-registration + **empirical Joint A on the
cipher-agnostic claim**; §7.2 carries the V1 and V8 retrain
numbers, §7.5 explains the >100% retention mechanism, and
§7.6 carries the 2026-05-09 multi-class softmax POC over
V8-V14 + benign that resolves the binary-vs-rest cross-fire
ceiling. The v2 update path becomes V9-or-later cycles plus
cipher-suite variation, not Step-11 closure.

## §7.1 Cipher-agnostic feature subset (D-020)

The cipher-agnostic feature subset is derived from
`RATE_INVARIANT_V2` (V6/V7-narrow's 13-feature post-port-
removal manifest) by removing features that require cleartext
HTTP/JSON-RPC body parsing. The boundary principle is **no
body parse required at all**: a feature qualifies if and only
if it can be computed from TCP/IP headers and TLS frame sizes
alone, with no decryption of the application-layer payload.

Five features are excluded under this principle:
`resp.rpc_error_frac`, `resp.rpc_error_distinct_codes`
(JSON-RPC `error` field; body parse required);
`resp.status_2xx_frac`, `resp.status_4xx_frac`,
`resp.status_5xx_frac` (HTTP status line; encrypted in TLS
body). The resulting `CIPHER_AGNOSTIC_V1` manifest is **8
features** (3 pcap + 5 resp byte-count features):

```python
CIPHER_AGNOSTIC_V1 = frozenset({
    # pcap (3 - TCP/IP-header-derived; cleartext on TLS wire)
    "pcap.mean_packet_size",
    "pcap.unique_dst_ports",
    "pcap.unique_src_ports",
    # resp (5 - byte-count-derived; TLS-frame-size-observable)
    "resp.amp_ratio_mean",
    "resp.amp_ratio_median",
    "resp.amp_ratio_max",
    "resp.req_bytes_max",
    "resp.resp_bytes_max",
})
```

The boundary derivation is methodologically load-bearing in
two distinct ways. First, it **pre-registers the cipher-
agnostic feature subset before any TLS-fronted bundle emits**
- per principle 1 (pre-registration discipline applied at
manifest level), the boundary is locked at design-doc landing,
not derived post-hoc to fit retention numbers. Second, it
**reinforces V7-narrow's feature-localised anti-transfer
evidence**: SE3 surfaced four features as anti-transfer
cross-chain (§6.4) - `resp.status_2xx_frac`,
`resp.status_4xx_frac`, `resp.status_5xx_frac`,
`resp.amp_ratio_max`. The body-parse-required exclusion
principle removes three of the four (the `resp.status_*_frac`
triple) by construction; `resp.amp_ratio_max` is byte-count-
derivable and is retained in `CIPHER_AGNOSTIC_V1`. The
cipher-agnostic boundary thus excludes three SE3 anti-transfer
features by principle - yielding a coherent prediction:
cipher-agnostic ROC retention should be *higher* than
rate-invariant-v2 ROC retention on the per-chain holdout
regime, because the cipher-agnostic manifest removes the bulk
of the anti-transfer feature class by construction. The
retained `resp.amp_ratio_max` becomes a Layer-2-prediction-
grade observable in §7.2 - the prediction that anti-transfer
persists cross-chain in the cipher-agnostic regime tests
SE3's chain-asymmetric mechanism finding under TLS
termination directly.

Per D-020 decision 2 (auditor-adjudicated 2026-05-03 broader
interpretation): the principle "no body parse required at
all" applies uniformly to JSON-RPC error fields and HTTP
status codes - both require cleartext-body-parsing. Treating
`resp.rpc_error_*` as cipher-agnostic-removable reinforces
V7-narrow §SE3 evidence; the narrower interpretation
(removing only status_*_frac → 10 features) is rejected as
methodologically incoherent.

The cipher-agnostic boundary's cardinality features
(`pcap.unique_dst_ports`, `pcap.unique_src_ports`) interact
with reproducer-pipeline connection-pooling semantics in
ways that downstream feature analysis must account for:
HTTP/1.1 keep-alive collapses per-worker requests onto a
single client-side socket, so naive ports-per-direction
counting can be fooled by reproducer-side connection
pooling. §8.7 MC-7 + MC-10 document the L7 interaction
surfaced at the Phase-1 close-gate.

## §7.2 Step-11 empirical retention measurement (V1 + V8)

Step-11 Component 1 ran the empirical measurement of the
cipher-agnostic boundary's retention claim across two retrain
cycles, both closed 2026-05-04 per AUDITOR-PROTOCOL gate.
Pre-registered design in `STEP-11-DESIGN.md` Section C +
D-020 decision 3 + `STEP-11-DESIGN-V8.md` (V8 manifest trim
per §C.5 Branch 1 trigger):

- **Lab nginx HTTPS termination** in front of Sui localnet
  (port 9000 → :443) and Solana test-validator (port 8899 →
  :443). Same nginx config across both chains for cross-chain
  parity; TLS 1.3 only; default cipher suites.
- **Dual-vantage capture**: pre-termination wire pcap (TLS
  frames; cipher-agnostic feature surface) + post-termination
  loopback pcap (cleartext; full-feature surface). The
  schema delta `Provenance.pcap_path_pre_termination`
  optional field supports the dual-pcap layout per D-020
  decision 1.
- **Pre-registered outcome bands**: cipher-agnostic ROC
  retention vs cleartext baseline (column-header semantics
  governs per V1 close-out auditor verdict 2026-05-04; see
  §8.7 MC-1). Outcome A clean ≥ 80% retention on both chains;
  Outcome B partial 50–80%; Outcome C limit < 50%. Per-chain
  joint composition rule carries forward from V6/V7 (either
  chain at C → Joint C).
- **Layer-2 per-feature structural predictions** (parallel
  to §5.2 Layer 2): high-confidence prediction
  (`pcap.mean_packet_size` retains as highest-cohen_d
  feature) plus medium-confidence predictions
  (`resp.amp_ratio_max` anti-transfers cross-chain;
  `resp.amp_ratio_median` retains most cleanly).

**V1 retrain results** (`step11_cipher_agnostic_run_*`,
2026-05-04). Cipher-agnostic ROC retention vs cleartext
baseline:

| chain × slice | A2 (cleartext) | B2 (cipher-agnostic) | retention |
|---|---:|---:|---:|
| Sui-holdout, lab-only | 0.3197 | 0.3197 | **100%** |
| Sui-holdout, inclusive | 0.3793 | 0.3793 | **100%** |
| Solana-holdout, lab-only | 0.5646 | 0.5629 | **99.7%** |
| Solana-holdout, inclusive | 0.5000 | 0.5000 | **100%** |

The V1 retrain matched cleartext rate-invariant-V2 to four
decimals on both chains. Per-primitive LOPO regime (B1 vs
A1) likewise produced 100% retention (both 1.0000 medians).
**Joint A on the cipher-agnostic claim**: the encryption
boundary itself does not introduce additional accuracy
degradation. The Sui-holdout sub-chance ROC is V7-narrow
§SE3 carry-forward (chain-asymmetric anti-classification
mechanism) at the rate-invariant manifest layer, NOT a
Step-11 finding.

**V8 retrain results** (`step11_cipher_agnostic_v2_run_*`,
2026-05-04). V8 dropped `pcap.mean_packet_size` from V1's
manifest (CIPHER_AGNOSTIC_V2 = 7 features) per §C.5 Branch 1
trigger after V1 surfaced the feature as single-feature-
dominant in per-primitive LOPO. V8 B2' retention vs A2
baseline:

| chain × slice | A2 (cleartext) | B2' (V8 cipher-agnostic) | retention |
|---|---:|---:|---:|
| Sui-holdout, lab-only | 0.3197 | 0.6124 | **191%** |
| Sui-holdout, inclusive | 0.3793 | 0.6702 | **177%** |
| Solana-holdout, lab-only | 0.5646 | 0.6976 | **124%** |
| Solana-holdout, inclusive | 0.5000 | 0.7088 | **142%** |

**Joint A by wide margin** (all four chain × slice cells
well above the 80% Outcome A threshold; the four cells span
124-191% retention, with the closest cell at 1.55× the
threshold and the strongest at 2.39×). V8 lifts the cross-chain
accuracy floor on the Sui-holdout side from V7-narrow §SE3
sub-chance (0.32–0.38) to clearly above-chance (0.61–0.67) by
removing the `pcap.mean_packet_size` distribution-mismatch
source. The V7-narrow §SE3 chain-asymmetric anti-classification
floor at the cipher-agnostic byte-count manifest layer was
load-bearing on a single feature, not an intrinsic
chain-asymmetric mechanism - V7-narrow §SE3 reframe scoped to
this layer (§8.7 MC-2). The `resp.status_*_frac` chain-
asymmetric pattern at the rate-invariant 13-feature manifest
layer remains live (V8 does not test it).

V8 surfaced single-feature dominance recurring on
`resp.req_bytes_max` (per-primitive single-feature ROC
0.9521–0.9930) - the next dominant feature in the trimmed
manifest. Per V6 D-018 dec 1 single-trim precedent + auditor
verdict 2026-05-04, V9 does NOT fire; the recurring-pattern
finding is the methodology contribution, not a defect to
iterate away (§8.7 MC-3).

## §7.3 V9-or-later v2 trigger

v1 (this preprint) ships the framework, the cipher-agnostic
feature subset pre-registration, and the Step-11 V1+V8
empirical Joint A. v2 trigger and timing are pre-committed:

- **v2 trigger**: lands when subsequent cycles extend the
  Step-11 measurement along orthogonal axes - cipher-suite
  variation (TLS 1.2 vs TLS 1.3 vs ECDHE-PSK vs ChaCha20),
  mTLS / client-cert deployments, additional chains beyond
  the Sui+Solana corpus, or a closure hypothesis on the
  cipher-agnostic-manifest single-feature-dominance
  brittleness pattern (§8.7 MC-3). Auditor-approved
  cycle-close verdicts gate the v2 trigger.
- **v2 timing target**: cycle-driven, not date-driven. Per
  the methodology-as-finding framing (principle 4), v2
  lands when the next cycle produces substrate-paper-grade
  evidence - not at an arbitrary calendar offset.
- **Slippage clause**: if no v2-trigger cycle closes within
  6 months of v1, an interim methodology-supplement note
  lands acknowledging the absence of a trigger event +
  revised v2 horizon. The slippage clause is principle-1
  discipline applied to publication timing - pre-registering
  what triggers an interim note prevents goalpost moves on
  publication scheduling.
- **Versioning convention**: v1 = current preprint
  post-draft (Step-11 V1+V8 empirical Joint A);
  v1-supplement = interim methodology-supplement note if no
  v2-trigger cycle closes within 6 months; v2 = v1 +
  next-cycle evidence along one or more orthogonal extension
  axes per the v2-trigger list.

This pre-commitment makes the v1/v2 split honest
pre-registration rather than aspirational scheduling.
Reviewers of v1 evaluate the empirical Joint A directly;
v2's evidence either substantiates the next-cycle
predictions (e.g., cipher-suite variation preserves
retention) or falsifies them, with falsification conditions
locked before each next-cycle measurement.

## §7.4 v1 honest scope summary

Five claims v1 makes:

- The cipher-agnostic feature subset boundary is principle-1-
  derivable from V7-narrow §SE3 anti-transfer evidence + the
  body-parse-required exclusion principle (§7.1).
- The boundary derivation pre-registered before any TLS-
  fronted bundle emitted, locking the manifest before
  measurement (§7.1).
- **Joint A on the cipher-agnostic claim** across both chains
  in both LOPO regimes: Step-11 V1 retrain delivers 100%
  retention vs cleartext baseline; Step-11 V8 trim manifest
  (CIPHER_AGNOSTIC_V2) delivers 124–191% retention on the
  per-chain holdout regime (§7.2). The encryption boundary
  itself does not introduce additional accuracy degradation.
- The V7-narrow §SE3 reframe is scoped to the
  cipher-agnostic byte-count manifest layer (§8.7 MC-2 carries
  the auditor-adjudicated scope statement).
- The cipher-agnostic byte-count manifest family exhibits
  structural single-feature-dominance brittleness; Step-11
  V1 and V8 both surface a single-feature-dominant
  cross-chain observable (`pcap.mean_packet_size` and
  `resp.req_bytes_max` respectively); the recurring pattern
  is structural, not a defect to iterate away (§8.7 MC-3).

Three claims v1 explicitly does NOT make:

- The cipher-agnostic feature subset retains predictive
  accuracy under cipher-suite variation (TLS 1.2, ECDHE-PSK,
  ChaCha20). v1 measures TLS 1.3 default cipher suite only;
  v2 evaluates variation.
- Cipher-agnostic retention generalises beyond the Sui+Solana
  two-chain corpus. Cosmos-family / Aptos / Ethereum
  extension is v2 / v3 material per the family-taxonomy
  generative claim (§4) plus chain-specific reproducer
  development.
- Cipher-agnostic retention holds under mTLS / client-cert
  deployments. v1 measures server-only TLS termination; mTLS
  is queued as a follow-on workstream.

The cycle's Joint A empirical evidence is what v1 ships;
the orthogonal-axes deferral is what v2 will ship.

## §7.5 >100% retention: baseline mechanism

V8's Sui-holdout retention of 177–191% and Solana-holdout
retention of 124–142% are above the 100% reference in three
of four cells. The honest framing is mechanism-anchored, not
artefactual.

The baseline used in the retention calculation is the
Step-11 V1 A2 cleartext-fidelity per-chain holdout regime:
the RATE_INVARIANT_V2 13-feature manifest including
`pcap.mean_packet_size`, evaluated 2026-05-04 at Sui-holdout
ROC = 0.3197 (lab-only) / 0.3793 (inclusive) and
Solana-holdout ROC = 0.5646 / 0.5000. The Sui-holdout
baseline is itself V7-narrow §SE3-affected: the
chain-asymmetric anti-classification floor documented at the
V6 → V7-narrow gate carries forward into the Step-11 V1
cleartext baseline measurement (per
`STEP-11-RETRAIN-CLOSE-OUT.md` A2 row).

Step-11 V8 dropped `pcap.mean_packet_size` from the
cipher-agnostic manifest and lifted the Sui-holdout
cross-chain accuracy floor 28–30 percentage points
(0.32–0.38 → 0.61–0.67). The mechanism: removing a feature
whose distribution mismatches chain-asymmetrically across
Sui and Solana eliminates a source of cross-chain
false-transfer in the trained model. The 177–191% retention
is the ratio of the post-removal ROC to the pre-removal ROC
- both empirical Step-11 V1+V8 measurements - not a
comparison against an idealised cleartext baseline that
excludes leak features by construction.

The retention measurement compares Step-11 V8 cipher-agnostic
to the literal pre-registered Step-11 V1 baseline. Step-11
V1 surfaced the distribution-mismatch source; Step-11 V8
removed it; the resulting retention reflects the Step-11 V8
manifest's empirical superiority over the Step-11 V1
manifest at the per-chain holdout regime. We do not claim
a retrained-cleartext baseline (which we have not measured)
would behave identically; we claim Step-11 V8 cipher-agnostic
empirically outperforms Step-11 V1 cleartext-with-the-
feature-included on the load-bearing per-chain holdout
regime.

## §7.6 Multi-class architecture (POC, 2026-05-09)

The framework's "different-attack-class generalisation"
hypothesis (§8.7 MC-12) was tested across five additional
detector cycles (V10-V14) trained against the lab corpus
2026-05-09. Together with V8 (response_amp / F10) and V9
(reconnaissance), V8-V14 cover the corpus's full
attack-primitive set. Per-detector outcomes:

| Detector | Family | Recall | Cross-fire ceiling | Outcome |
|---|---|---:|---|---|
| V8 | response_amp (F10) | 100% | (deployed) | A - deployed |
| V9 | reconnaissance | 100% | (deployed 2026-05-08) | A - deployed |
| V10 | auth-bypass (H/GR/F-family) | 100% | clean | A - trained |
| V11 | application-layer DoS (P-family) | 100% | V12 99%, V10 48% | B - cross-fire |
| V12 | consensus / gossip (D/H02) | 100% | V8 21% | A - trained |
| V13 | service-misconfig (MC-family) | 100% | ≤1.4% across all | A - trained |
| V14 | compute-amp / sync-wedge (F14) | 93% (n=54) | 13% other-attack | A - trained |

V10-V14 are trained on the offline corpus but
deployment-blocked on IBSR feature-surface extension (§8.3);
the methodology evidence below is offline-corpus complete.

**Binary-vs-rest cross-fire (architectural finding).** V11's
close-out surfaced a structural property: when attack classes
share signal regions, the per-class binary trained on
"V11 vs (everything else)" cannot distinguish V11 from
*specific* alternative classes that occupy similar feature
regions. Cross-fire is not an inherent limit of binary
detection nor of the feature surface; it is a property of
the *training-objective shape* - binary-vs-rest collapses
all non-positive classes into one negative class, losing
the distinctions among them. V13/V14's clean ≤1.4% isolation
is the counter-evidence: when an attack class occupies a
genuinely orthogonal signal region, binary-vs-rest hits
A-grade. §8.7 MC-13 frames this as a measurable
architectural property; the paired-class cross-fire rate is
the load-bearing diagnostic.

**Multi-class softmax POC (resolves cross-fire).** One
`CalibratedClassifierCV(HGB, isotonic, cv=5)` was trained
2026-05-09 on the unified V8 + V9 + V10-V14 + benign corpus
(2014 lab-fidelity samples, 8 classes, 107-feature surface,
no manifest filter). Stratified 5-fold OOF results:

- **Overall OOF accuracy: 99.95%** (2013 / 2014 correct).
- Per-class recall: 1.000 across the board EXCEPT V11 at
  0.995 (one V11 → benign miss in fold 3).
- Per-class precision: 1.000 across the board EXCEPT
  benign at 0.999 (the V11 miss landed there).
- Brier scores ≤ 0.0007 across all classes - excellent
  calibration.
- P(class | true=1) ≥ 0.974 across all classes.
- P(class | true=0) ≤ 0.008 across all classes.

OOF confusion matrix:

```
              benign      V8      V9     V10     V11     V12     V13     V14
benign          1085       0       0       0       0       0       0       0
V8                 0      54       0       0       0       0       0       0
V9                 0       0      45       0       0       0       0       0
V10                0       0       0     154       0       0       0       0
V11                1       0       0       0     221       0       0       0
V12                0       0       0       0       0     150       0       0
V13                0       0       0       0       0       0     250       0
V14                0       0       0       0       0       0       0      54
```

Cross-fire reduction vs binary baselines:

- V11 ← V12: binary 99% → multi-class **0%**
- V11 ← V10: binary 48% → multi-class **0%**
- V12 ← V8:  binary 21% → multi-class **0%**

The honest tradeoff: multi-class swaps binary's 100% V11
recall + 99% V12 cross-fire for 99.5% V11 recall + 0%
cross-fire. One false negative against zero cross-fire is
the right operational trade, and it is an operator-tunable
threshold adjustment per-class, not an architectural limit.

**Cipher-agnostic class generalisation.** V9 (recon,
pcap-only feature surface) coexists with V10-V14
(body-parse-required) in the same multi-class manifold
without confusing the model: V9 scores 100% recall + 0%
cross-fire across all 7 other classes. The cipher-agnostic
and body-parse-required detector classes are fully
resolvable in one softmax. §8.7 MC-14 frames the
production-architecture canon: binary stack as headline
(per-class explainability + threshold-tuning) plus
multi-class softmax as the cross-fire-resolution layer when
binary-pair ambiguity arises.

**Honest scope.** The 99.95% OOF number is lab-corpus,
in-distribution evaluation; it is *not* a zero-error
production claim.

**Cross-chain LOPO + joint-training multi-class
(2026-05-10).** With `corpus_v1.6` landing 141 new Solana
attack bundles (§8.2 cross-chain corpus depth), Phase A ran
Sui-trained binary detectors against Solana attack bundles;
Phase B trained a multi-class softmax with joint Sui+Solana
training over the unified corpus.

Phase A - Sui-trained binary detectors evaluated on Solana:

| Detector | Manifest type | Sui recall | Solana recall |
|---|---|---:|---:|
| V8 | cipher-agnostic-v2 (traffic-shape only) | 100% (54/54) | **100% (51/51)** |
| V14 | compute-amp-v1 (host telemetry) | 93% (50/54) | **0% (0/51)** |
| V11 | app-dos-v1 (host telemetry) | 100% (P-family avg) | **0% (0/52)** |

V8's cipher-agnostic-v2 manifest (7 features, all
pcap/resp byte-shape) transfers cross-chain at 100% with
zero retraining, zero feature engineering, zero manifest
changes. V14/V11's host-telemetry manifests (host.cpu_*,
host.num_*_delta, resp.duration_ns_*) hit 0% Solana
recall - host.* features capture chain-runtime-specific
process behaviour (sui-node vs agave: different async
runtimes, connection-handling patterns, FD lifecycles, RSS
baselines), so the model has no basis to fire on the
other chain's process distress patterns. Per-class manifest
composition *encodes* the cross-chain transferability story
as a hypothesis the train-on-A/eval-on-B evaluation tests
directly (§8.7 MC-17a / MC-17b).

Phase B - multi-class softmax with joint Sui+Solana
training (folded mode: V8/V11/V14 absorb their Solana
counterparts):

| Detector class | Binary cross-chain | Multi-class folded cross-chain |
|---|---:|---:|
| V8 (Sui+Sol) | 100% | 100% |
| V14 (Sui+Sol) | 0% | **100%** |
| V11 (Sui+Sol) | 0% | **100% (273/274)** |

Folded multi-class: 99.95% OOF across all 8 classes;
Brier ≤ 0.0008. Phase B separate-mode (11-class, with
SOL_F10/SOL_F14/SOL_P07 as their own classes): all classes
≥ 0.981 recall; SOL_F10 / SOL_F14 / SOL_P07 each at 100%;
zero cross-chain confusion - the model distinguishes
chain-of-origin perfectly when given the choice. The same
joint-training architecture that resolves binary-vs-rest
cross-fire (above) also resolves chain-specificity at the
binary-detector layer (§8.7 MC-18).

The two-axis architectural picture across V8-V14:

|  | Cross-class | Cross-chain |
|---|---|---|
| **Binary detector limit** | Cross-fire when classes share signal regions (V11/V12 99% on V11 model) | 0% recall when manifest is chain-runtime-specific (V14/V11 host.*) |
| **Multi-class softmax resolution** | Joint training with all classes resolves cross-fire (MC-14: 99.95% OOF) | Joint training across chains resolves chain-specificity (MC-18: 99.95% OOF folded) |
| **Headline architectural claim** | Both architectures coexist; binary is per-class explainable, multi-class is composition layer | Same operational pattern, same trade-offs |

The cross-fire problem and the chain-specificity problem
are the same problem at different boundaries; both resolve
via joint training, both characterise *which* features
carry the cross-cutting signal.

**Mechanistic refinement (zero-shot multi-class +
ablation; 2026-05-10 PM).** Beyond the folded-mode joint
training above, a Sui-only-trained multi-class softmax was
evaluated zero-shot against held-out Solana attack bundles.
Per-class zero-shot recall: V8 1.000, V11 0.981, V14 0.020.
Two complementary diagnostic protocols characterise the
mechanism: SHAP attribution (`TreeExplainer` on the inner
HGB[0] of the 5-fold `CalibratedClassifierCV`) measures
prediction-contribution intra-distribution; feature
ablation (re-train multi-class with one category removed,
measure cross-chain recall change) measures
transfer-necessity. The two diagnostics disagree
informatively for V11 - SHAP attributes `pcap.*` 22.5%
(rank 3 by contribution) but ablation reveals `pcap.*` is
rank 1 by causal necessity (removing it collapses V11
zero-shot recall 98% → 0%). §8.7 MC-18 lays out the
resulting three-mode taxonomy: V8 single-category clean
transfer (Mode 1); V11 multi-category causal-conjunctive
transfer with `pcap.*` necessary (Mode 2); V14
chain-specific-feature poisoning where ablating `pcap.*`
*lifts* recall 2% → 19.6% and ablating `host.*` + `resp.*`
lifts to 39.2% (Mode 3 - active harm, not signal absence).

**Honest scope (Phase A/B + zero-shot/ablation).**
Multi-class folded results are *in-distribution-fold across
both chains*, not zero-shot. The folded-mode "100%
per-chain recall" claim is the operational pattern when
adding a chain to coverage (joint training); the zero-shot
numbers above are the Sui-only-trained model's
out-of-distribution Solana recall. Single Solana
implementation (`agave` via `solana-test-validator`); other
implementations may surface different patterns. n_solana
per primitive at LOPO floor (51-52) is sufficient for the
headline findings but per-posture stratification would
strengthen them. Binary V8 benign FPR climbed to 15-17% on
the wider cross-chain cache (from V8 close-out's ~1-2%);
the multi-class folded V8 absorbs this issue (1.000
precision), but the binary deployment-claim cross-chain
remains qualified pending investigation of corpus-drift /
feature-distribution-shift / per-primitive-variation
hypotheses. Ablation is per-category, not per-feature;
finer-grained per-feature ablation would identify specific
poisoning features. `app.*` not ablated (53 features, low
SHAP attribution). TreeExplainer SHAP on inner HGB[0] of
`CalibratedClassifierCV` is an approximation (the
calibration ensemble can't be directly attributed); feature
ranks stable across folds.


# §8 Discussion + limitations

## §8.1 Honest framing of V7-narrow Joint C

V7-narrow's headline outcome at the V6 → V7-narrow evaluation
gate is **Joint C**: the cross-chain mechanism claim is
falsified at lab fidelity, on the per-chain holdout direction,
under the rate-invariant-V2 manifest. The Sui-side per-chain
holdout ROC = 0.3399 trips dimension-1 Outcome C alone (per
`STEP-10-DESIGN-V6.md` §C composition rule); Solana-side
0.5000 sits at the B/C boundary informationally.

Joint C does not falsify this paper's claim structure. The
methodology contributions (Section A/B/C pre-registration,
multi-layer falsifiability, LOPO with per-chain holdout, the
V1 → V7-narrow iteration arc, the V7-narrow disambiguation
sub-experiment design, the multi-mechanism finding's
feature-localised structure) persist regardless of any
single cycle's evaluation-gate outcome. This was the V4
lesson, formalised: "lab-fidelity-bound demonstration is
the cycle's contribution" (`STEP-8-AUDIT-FINDINGS-V2.md
§v4 (actual)` lines 1196-1199); V7-narrow generalises the
lesson - *the iteration arc IS the contribution*.

This paper's central thesis is methodology-as-finding under
principle 4 (methodology contributions are first-class
artefacts). A cycle that reaches Joint A (headline ROC
retention high; structural predictions hold) substantiates
the cross-chain mechanism claim empirically. A cycle that
reaches Joint B (partial retention) documents chain-portable
/ chain-specific framing. A cycle that reaches Joint C
(cross-chain mechanism claim falsified at evaluation gate)
reframes around the falsification's specific shape and adds
a methodology contribution (the iteration's leak-surface
closure). All three outcomes feed our contribution claim;
none of them falsifies it.

## §8.2 Limitations + scope

**Lab-fidelity ceiling.** All evidence in V1 → V7-narrow is
captured at lab fidelity (`fidelity_class ∈ {lab, stub,
proxy}`). The two `pcap.mean_packet_size` driver hypothesis-
tests (corpus_v1.3 connection-per-RPC + corpus_v1.4
HTTP-keepalive) demonstrated the lab-fidelity-bound limit
empirically - KDE-overlap ~0.05 across two distinct driver
mechanisms (`§v4 (actual)` lines 1133-1155). We do not
claim mainnet-fidelity coverage; Step-7 mainnet-organic
capture is deferred indefinitely (D-013) on operational-cost
grounds (~$620/mo droplet + 2 TB volume). The deferral is
honest: our claim is calibrated to the lab fidelity it
actually has.

**Two-chain coverage (n=2 ceiling, named).** The corpus
spans Sui and Solana - n=2 across the cross-chain claim
machinery. The chain-asymmetric mechanism finding (V7-narrow
§SE3 anti-transfer + Step-11 V8 reframe at the
cipher-agnostic byte-count manifest layer; §6.4, §7.2) is
hardened on n=2: SE3 surfaces feature-level anti-transfer
across one Sui ↔ Solana fold pair, and V8 reframes the
floor on the same chain pair. The family taxonomy's
generative-not-bounding claim has three post-cycle attacks on
record (IA01/IA02/IA02b per §4.3) - all on Sui, all classifying
into `response_amp`; the nine-chain public-CVE scale-up since
(§4.6) supplies dozens more, and the two documented
family-extension events are recorded in §4.5. The per-chain holdout direction methodology
contribution (D-018; §5.3) generalises beyond n=2 by
construction - the regime is "train on one chain entirely,
evaluate on the other entirely", which composes across any
n ≥ 2 chain set - but its empirical substantiation in this
paper is the n=2 Sui ↔ Solana evidence base.

This is honest scope, not a defect: the v2 / v3
chain-extension axis (§7.3) is the next-cycle path. Cosmos /
Aptos / Ethereum cross-chain extension is out of scope for
v1; each chain addition triggers the iteration discipline
under the family taxonomy's chain-agnostic family_id +
chain-specific primitive_id contract per D-002, and each
addition tests both the chain-asymmetric mechanism finding's
generalisation and the per-chain holdout direction's
empirical reach beyond n=2.

**Cross-chain corpus depth + LOPO + multi-class +
family-abstraction status (2026-05-10 / 2026-05-11).**
`corpus_v1.6` (2026-05-10) landed 141 new Solana attack
bundles bringing three primitives above the LOPO floor
(`SOL_F10_multi_get_accounts_amp` 51,
`SOL_F14_simulate_transaction_sync_wedge` 51,
`SOL_P07_get_program_accounts_filter_miss` 52); Phase C.1
through C.4 (`corpus_v1.7` - `corpus_v1.10`, 2026-05-11)
added 400 more bundles across four additional families -
`reconnaissance` (SOL_RC_nmap_slow, 50), `service_misconfig`
(5 SOL_MC_* primitives, 250), `auth_bypass`
(SOL_H01_admin_rpc_probe, 50), `rate_limiter_bypass`
(SOL_GR01_simulate_compute_flood, 50). Solana cross-chain
corpus now totals 541 attack bundles across 10 primitives
in 7 of 10 attack families. Cross-chain LOPO + multi-class
evaluations on the v1.6 primitives landed 2026-05-10 (Phase
A + B; §7.6): V8 cipher-agnostic-v2 transfers cross-chain
at 100% Solana recall with zero retraining; V14/V11
host-telemetry manifests hit 0% Solana recall
(chain-runtime-specific by design); multi-class softmax
with joint Sui+Solana training (folded mode) recovers
V14/V11 to 100%/100% on Solana while preserving V8's
100%/100%. Family-taxonomy mechanism-abstraction-class
empirically anchored across three primitive pairs (§4.4
Pair A/B/C). The n=2 Sui ↔ Solana evidence base thus
graduates from "taxonomy-mapping evidence" to "binary +
multi-class numbers landed at LOPO-floor corpus depth across
7 of 10 families, with family-abstraction empirically
anchored" - load-bearing for the §cross-chain headline of
v1's methodology pillar. Cross-chain extension beyond Sui
↔ Solana, detector-transfer empirical confirmation of MC-19
Pairs B and C (V10/V11 trained on Sui evaluated against
SOL_H01/SOL_GR01), C.5 (`consensus_abuse`, requires
multi-validator Solana cluster), and zero-shot Sui→Solana
multi-class characterisation, remain forward work; §4.4 /
§7.6 / §8.7 MC-19 carry the honest-scope caveats.

**Post-v1 update - the ceiling moved, the open problem did
not.** The n=2 Sui ↔ Solana scope above has since been extended
to nine chains (§4.6): the public-CVE corpus runs the per-chain
holdout direction over Bitcoin, Ethereum, Solana, Sui, Cosmos,
Monero, Dogecoin, Litecoin, and libp2p. Scale did not resolve
cross-chain transfer - it quantified its absence in the harder
zero-shot regime. Where the n=2 result above was joint-trained
(both chains in training) and recovered V11/V14 to 100%,
zero-shot leave-one-chain-out family recovery at n=9 sits near
the random-label floor on the protocol-distinct held-out chains
(macro-F1 0.16 Monero, 0.18 Bitcoin, 0.36 Ethereum, 0.42 Cosmos,
0.46 libp2p), rising to a trivial ~1.0 only for wire-identical
forks that inherit another chain's exact primitives (1.00
Dogecoin, 0.70 Litecoin) - the two-chain V7-narrow non-transfer
finding reproduced at n=9. (Sui and Solana share one family
apiece with the rest of the corpus at n=9, too few for the LOCO
question to be posed; they are the joint-trained n=2
characterisation above, not the LOCO sweep.) What the scale-up
does establish is that the *within-chain* binary attack-vs-benign
signal is real (~0.96 held-out ROC, GroupKFold by primitive;
§4.6) and that the per-chain holdout regime (D-018) composes to
n=9 exactly as its n=2 form predicted. The honest status is
therefore not "ceiling lifted" but "open problem now measured
across nine chains": whole-taxonomy zero-shot cross-chain
transfer is unresolved, and we report it as unresolved.

**Cipher-suite sensitivity not measured in v1.** Step-11
Component 1 (closed 2026-05-04; §7.2) measured cipher-agnostic
feature subset retention under TLS 1.3 default cipher suites only.
Cipher-suite variation (TLS 1.2 vs TLS 1.3, ECDHE-vs-PSK,
AES-GCM-vs-ChaCha20) is queued as a follow-on workstream,
not pre-registered as a locked component of v1 or v2.
mTLS / client-cert configurations are out of scope for v1.

**V7-narrow finding #3 hardened to finding-grade, not
field-tested.** The multi-mechanism finding is
methodologically established (§6.4) on a single cross-chain
holdout direction, evaluated against three pre-registered
sub-experiments. We do not claim the specific anti-transfer
features (`resp.status_*_frac` + `resp.amp_ratio_max`)
generalise beyond the Sui+Solana two-chain corpus; the
chain-asymmetric mechanism claim is specific to the corpus
and the manifest evaluated.

**Single-trainer-architecture coverage.** All cycles use the
same HGB hyperparameters (`max_iter=200, learning_rate=0.05,
max_depth=8`, isotonic-calibrated, K=20% stratified benign
holdout). Per principle 6 (the model is not the variable),
trainer hyperparameters inherit V4 → V5 → V6 → V7-narrow
unchanged; iteration variables are corpus + manifest +
holdout regime. Our methodology claim operates within this
trainer-architectural envelope; whether the methodology
generalises to other ML model families is an out-of-scope
question.

## §8.3 Production deployment

This paper covers the data layer; the architectural
framework for production deployment lives in the sister-paper
*Earned Autonomy* (Zenodo DOI `10.5281/zenodo.18406828`,
`@morley2026earnedautonomy`). Earned Autonomy specifies the
deployment architecture (detection-only → operator-reviewed
enforcement → bounded autonomous response), the capability
ladder for autonomous security agents, and the trust-earning
protocol governing each transition. This paper produces the
data-layer artefacts the architecture runs against: format,
taxonomy, methodology, V7-narrow technical centerpiece.

The streaming-feature-extraction workstream (XDP / eBPF
implementation computing the 8 `CIPHER_AGNOSTIC_V1` features
on live packets at line rate) has cleared its Phase-1
close-gate (2026-05-06; augmented 2026-05-07 per D-025;
joint-conditions verification 2026-05-08). The gate
verifies extractor numerical equivalence to the offline
reference (`PHASE_1_TOLERANCE`) AND model-side
prediction-class equivalence (`PHASE_1_SCORE_CLASS_MATCH`)
AND joint in-criterion-applicable-regime status (cardinality
envelope + saturation envelope + training-distribution-
coverage), with saturation-envelope verification delegated
to the operator's runtime monitoring runbook. Verified
empirically 2026-05-08 on paired live capture (offline
bundle + IBSR `collect-payload` snapshot) of an
attack-signature F10 window: 5/7 features exact-equivalent,
2/7 cardinality divergence consistent with the cardinality
envelope's known watched-port-filter scope, score-class-
match offline=production=class 1 ATTACK at score 1.0/1.0
in-regime. The production-extractor empirical-fidelity
envelope is characterised at §8.7 MC-6 (saturation upper
bound), MC-7 (cardinality lower bound), and MC-8
(training-distribution-coverage); the joint-conditions
architecture is documented at §8.7 MC-11. Production
deployment of the V8 cipher-agnostic-v2 detector at sui_F10
scope is empirically unblocked at deployment-claim level. A
follow-on V9 recon-detector cycle (§8.7 MC-12, 2026-05-08)
demonstrates the same close-gate framework + observation
substrate generalising to a different attack class without
architectural change. A 2026-05-09 cycle extends the binary
detector inventory to V8-V14 covering the full lab corpus
attack-primitive set (§7.6). The IBSR feature-surface
extension (Phase A schema v7 ResponseAggregates +
Phase B HostTelemetry blocks, nr-ibsr commits `a1ed02e` +
`26a5238`) landed 2026-05-11, lifting per-snapshot feature
extraction from 7 to 26 features and unblocking V10-V14
production deployment end-to-end (§8.7 MC-20). The demo
inference container now bundles the multi-class folded
model with an operator-flippable `--multiclass-primary` env
flag; idle-traffic smoke-test 2026-05-11 produced the
expected benign classification with the full feature surface
populated (vs the prior partial-surface failure mode that
routed idle traffic to V13 via class-prior collapse). The
IBSR shadow-mode architecture (deployment against own
validator infrastructure first; not customer infrastructure
yet) and the online inference latency budget remain queued
as production-architecture scoping work. The 2026-05-14 V1
mixed-traffic verification cycle (§8.7 MC-22 / MC-23 /
MC-24) characterises the deployment-fidelity gap under
realistic noisy-server conditions: binary attack-or-benign
verdicts hold under dilution; per-class identity drifts
toward a V11-class "garbage attractor" under OOD mixed-
traffic inputs. The recommended deployment policy is
therefore *trust the binary verdict, treat per-class
identity as advisory under mixed traffic* until Path 2
(mixed-traffic-positive retrain) or Path 3 (per-source-IP
IBSR aggregation) lands. Production engineering execution
beyond the extractor begins post-paper-preprint; the
scoping document drafts after the v1 outline lands and
uses the cipher-agnostic feature surface as the
production-required feature set per this paper's claims.

## §8.4 Reproducibility

Full reproducibility is committed at three levels:

- **Format spec at `nr-bundle-spec` v0.1.0**
  ([github.com/NullRabbitLabs/nr-bundle-spec][nrbundle],
  MIT-licensed; published 2026-05-13; D-012 publication
  strategy). JSON Schema + pyarrow schemas + reference
  parsers in Python and Rust + five reference example
  bundles. Cross-language guarantees pinned by tests:
  byte-equivalent wire enum strings, byte-equivalent
  `compute_genome_id` output, and identical Arrow schemas
  across both languages. Companion public artefacts (§3.4):
  `nr-bundles-public` dataset, `v8-cipher-agnostic` reference
  detector, `multiclass-folded` unified detector, and
  `nr-bundle-classifier` interactive Space all live on
  HuggingFace as of 2026-05-13.

[nrbundle]: https://github.com/NullRabbitLabs/nr-bundle-spec
- **Published detector + dataset on HuggingFace.** The
  nine-chain public-CVE network detector is published as
  `nr-network-known-class-detector` (Apache-2.0, made public
  2026-07-01); the `nr-bundles-public` sample dataset is live
  (CC-BY-4.0); the economic-attack detector is staged behind
  the publish-guard, private pending an operator flip. Each
  model card is auto-generated from the exact cut its model
  trained on, so a reader always sees numbers that match the
  shipped weights.
- **Full audit trail at `nr-substrate`** (private working
  repo, commit-pinned). Section-by-section commit-pin
  discipline: paper text cites specific `nr-substrate`
  commit SHAs at section-landing review per AUDITOR-PROTOCOL.

Audit-doc citation convention: V1 audit findings live in
`STEP-8-AUDIT-FINDINGS.md`; V2 → V7-narrow audit findings
live in `STEP-8-AUDIT-FINDINGS-V2.md`. The two-file split
preserves the V1 evidence record verbatim while V2-onward
findings accumulate against the post-V1-fix corpus.

V7-narrow run-tag pinning (per §6.5):

- SE1: `step10_v7_se1_run_20260502T214310Z_seed42`
- SE2: `step10_v7_se2_run_20260502T220513Z_seed42`
- SE3: `step10_v7_se3_run_20260502T222723Z_seed42`

V6 retrain run-tags + V5 retrain run-tags + V4 retrain
run-tags trace forward from Appendix A's per-fold ROC tables.
The reproducibility commitment is operationalised: a reader
can re-fetch the corpus version, re-run the trainer with the
pinned run-tag, and obtain numerically-equivalent ROC tables.

Phase-1 production-extractor close-gate pinning (per §8.3 +
§8.7 MC-6/MC-7):

- Union artefact (CLEARED) at `nr-substrate` commit
  `8df67f6`; third-round audit-verdict capture at `5014a23`.
- Same-run paired-bundle equivalence:
  `docs/PHASE-1-CLOSE-GATE-PAIRED-2026-05-06.{md,json}`,
  bundle `crp_79e6259fc635490a`.
- Held-out cross-run equivalence (Option D two-run independent
  capture; held-out bundle never observed by the production
  extractor):
  `docs/PHASE-1-CLOSE-GATE-HELDOUT-2026-05-06.{md,json}`,
  bundle `crp_ec87cdafda67412b`.
- Multi-window aggregation paths exercised:
  `docs/PHASE-1-CLOSE-GATE-MULTIWINDOW-2026-05-06.{md,json}`,
  bundle `crp_f6aa0452d2334c83`.
- Sub-cap cardinality regime (the cardinality-envelope
  surfacing artefact):
  `docs/PHASE-1-CLOSE-GATE-LOWCARD-2026-05-06.{md,json}`,
  bundle `crp_e0ae20e56add4be5`.
- Production-extractor enabling commit (port-cardinality
  closure): `nr-ibsr` commit `83878e7`.
- Reproduction harnesses: `scripts/ibsr_aggregate_features.py`
  (snapshot → 7-feature dict, multi-window weighted
  aggregations documented at lines 24-30, 94-111) +
  `scripts/phase1_cross_validate.py` (offline-vs-production
  per-feature comparison against `PHASE_1_TOLERANCE`).

A reader with the IBSR debug binary at the pinned commit, a
Sui localnet, and the F10 reproducer
(`chains/sui/findings/F10/reproducer.py`) can replay each of
the four sub-experiments and obtain numerically-identical
feature dicts within `PHASE_1_TOLERANCE` (cardinality + max-
byte exact, amp-ratio ±1e-4 absolute) - the same
reproducibility discipline applied to the training-side
run-tags above.

**Operational maturity + disaster recovery.** Reproducibility
is now backed operationally, not only documented. The
end-to-end pipeline of §5.6 (research → forge → nightly train →
package → publish-guard → self-updating card) *is* the
reproduction mechanism: the published cut is rebuilt and
re-gated on every training run rather than hand-assembled, and
nothing ships that the guard has not cleared. The irreplaceable
state behind it - the gitignored persistent training store
(~15 GB) and the working repository - is backed off-box to
S3-compatible object storage automatically after each nightly
run, and the repository is pushed to its origin on the same
cadence, so a single-host loss no longer costs the corpus or
its audit history.

## §8.5 Prior-cycle leak-surface closures

Methodology-as-evidence: each prior cycle closed a documented
leak surface, surfaced via the multi-layer falsifiability
framework's discriminators. We acknowledge these closures
honestly per principle 2:

- **V1 → V2** - LOPO benign contamination (`random_features`
  ROC = 1.000) + capture-pipeline co-linearity (`resp.count`
  ROC = 1.000 on 14 of 17 folds): closed via stratified
  benign holdout (Regime A) + `BENIGN_reproducer_pipeline`
  primitive (corpus_v1.0 → v1.1 delta) [`§v2 (actual)` +
  V1 audit findings doc].
- **V2 → V2.5** - `app.distinct_metric_names` single-feature
  ROC = 1.000 (capture-pipeline-metadata leak surviving the
  V2 corpus fix): tier reclassification of capture-config-
  derived features [`§v2.5`].
- **V2.5 → V3** - Section B feature filter; 4 capture-config
  features removed (`app.scrape_duration_s`, `app.row_count`,
  `host.duration_s`, `host.sample_count`) before fold
  construction [`§v3 (actual)`].
- **V3 → V3.5/V3.6** - interim sub-iteration cycles
  refining rate-feature decomposition and leak-surface
  compatibility (compressed into the V3 → V4 row of §5.4);
  details at `STEP-8-AUDIT-FINDINGS-V2.md §v3.5` + `§v3.6`.
- **V3 → V4** - `pcap.mean_packet_size` carries headline at
  lab fidelity (KDE-overlap ~0.0560 + 0.0536 across two
  driver hypothesis-tests): lab-fidelity-bound demonstration
  complete; reframed as Step-7 mainnet-capture requirement
  per D-013 [`§v4 (actual)`].
- **V4 → V5** - chain-deterministic port leak in
  RATE_INVARIANT_V1 (`pcap.top_dst_port_fraction` ROC =
  1.000 surfaced via cross-chain corpus composition):
  RATE_INVARIANT_V2 manifest revision drops 4 port features
  [`§v5 (actual)`].
- **V5 → V6** - V5 Joint-C three findings (chain-deterministic
  port leak; per-chain holdout direction missing;
  `host.io_write_delta` modality-population red unpredicted
  by v5-pre): per-chain holdout direction added (D-018);
  v5-pre taxonomy expanded to include modality-population
  asymmetry [`§v6 (actual)`].
- **V6 → V7-narrow** - V6 Joint-C per-chain holdout collapse
  (hold-out-Sui ROC = 0.3399 sub-chance; finding #3
  hypothesis-grade): SE1/SE2/SE3 disambiguation hardens
  finding to finding-grade multi-mechanism evidence
  (§6.4) [`§v7-narrow (actual)`].

Each closure is a methodology-discipline evidence point: the
audit-trail framework surfaced its own failure modes; the
next-cycle pre-registration responded against the surfaced
finding. The closed-leak set grows monotonically. Our claim
that "iterative leak-surface peeling catches its own failure
modes" rests on this empirical record.

The V7-narrow → Step-11 V8 transition (Step-11 cycle,
2026-05-04) is documented separately at §7.2 + §8.7 as a
mechanism reframe at the cipher-agnostic byte-count manifest
layer, not a leak-surface closure; the closed-leak inventory
above spans the V1 → V7-narrow Step-8 leak-surface arc
specifically.

The Phase-1 production-extractor close-gate (cleared
2026-05-06) is documented separately at §8.6 (D-021
criterion-wording-relaxation discipline as the third
agent-discipline upgrade incident) and §8.7 (MC-6 saturation
envelope + MC-7 cardinality envelope as production-extractor
fidelity-envelope companions to MC-2). Like Step-11 V8, it
is a methodology-contribution-bearing cycle rather than a
training-side leak-surface closure; the inventory above is
the training-side V1 → V7-narrow arc only.

## §8.6 Methodology contributions about agent-discipline patterns

The methodology-auditor agent + AUDITOR-PROTOCOL operate
routine methodology gates autonomously. The agent's verdict
discipline itself underwent a methodology iteration during
this project, and we document the iteration as transferable
methodology contribution.

**Three upgrade incidents** drove the agent-discipline
canonicalisation:

1. **Phase-6a addendum cycle (2026-05-02)** - surfaced two
   discriminator-conflation patterns: (a) "load-bearing"
   conflated with "single-ROC threshold" - reduced
   multi-layer falsifiability to one-layer numerical
   thresholds; (b) decision-citation confabulation -
   referenced "Locked Decision #3" as canonical when the
   project uses D-NNN numbering. Resolution: agent system
   prompt + AUDITOR-PROTOCOL upgraded with §"On
   falsifiability layers" (three layers operationalised) +
   §"On citing project decisions" (exact source citation
   required) + §"Authority and decision scope" (auditor as
   decision-maker on routine methodology, escalating
   strategic decisions only to Simon).

2. **V6 auditor-close meta-correction (2026-05-02)** -
   surfaced over-escalation patterns: V6 first-round audit
   returned VERDICT: ESCALATE with three Simon-questions
   (paper drafting timing, V7 scope, paper-shaped artefact
   landing); Simon flagged the over-escalation. Two of
   three were methodology questions the auditor had clear
   reads on but refused to commit to. Resolution: agent
   system prompt §"Authority and decision scope" upgraded
   with **pre-ESCALATE self-check** (escalation list
   exhaustive; runway/paper/customer implications do not
   transmute methodology into strategy; clear methodology
   read commits) + AUDITOR-PROTOCOL §"Specific anti-patterns
   to avoid" expanded with four over-escalation
   anti-patterns. Auditor re-invoked on V6 with tightened
   rules produced ESCALATE with **one** genuinely-strategic
   Simon-question (paper timing). The fix compressed
   Simon's decision space from 3 to 1 - directly testable
   methodology contribution.

3. **Phase-1 close-gate refinement-2 (2026-05-06)** -
   surfaced a criterion-wording-relaxation pattern: the
   original close-gate run was named "CLEARED" on a 5/7
   numerical result that materially narrowed the
   criterion-applicable scope without honest disclosure of
   the scope conditions. The auditor's NOT-APPROVED verdict
   drove a four-sub-experiment decomposition (paired-bundle,
   held-out, multi-window, low-cardinality) producing the
   union-of-evidence clearance plus three first-class
   methodology contributions (saturation envelope per §8.7
   MC-6, cardinality envelope per §8.7 MC-7, and the
   discipline documented here). Resolution: D-021's
   threshold-relaxation prohibition extended to
   **criterion-wording elision** - when a pre-registered
   criterion's wording is deliberate and remains achievable,
   paired-only evidence is principle-1-incomplete; the
   auditor's NOT-APPROVED verdict enforces the
   criterion-as-written rather than letting the artefact
   silently re-scope. Companion to the Step-11
   misspecification correction (`STEP-11-AUDIT-FINDINGS.md
   §"Phase 1 misspecification correction (2026-05-05)"`) at
   the opposite end of the pre-registration-discipline arc:
   that entry justifies criterion re-scoping under
   principle-1 misspecification discipline; this entry
   justifies refusing criterion re-scoping when the
   criterion remains achievable.

**Transferability**: agent-discipline patterns generalise
beyond this project. Any methodology-agent system gating
routine technical decisions can adopt the **pre-ESCALATE
self-check** + **escalation-list-as-exhaustive** discipline,
and any pre-registered close-gate criterion can adopt the
**criterion-wording-as-written** discipline (the auditor
refuses re-scoping when the criterion remains achievable).
We document the V6 over-escalation incident + Phase-6a
falsifiability-layer-conflation incident + Phase-1
criterion-wording-relaxation incident as concrete pattern
evidence; reviewers comparing automated-methodology-review
patterns may find the incident-driven discipline upgrades
useful as documented case studies.

## §8.7 Methodology contributions from the Step-11 V1 + V8 + Phase-1 cycles

The Step-11 cycle (V1 retrain + V8 retrain, both closed
2026-05-04) produced empirical Joint A on the cipher-agnostic
claim (§7.2). The Phase-1 production-extractor close-gate
(cleared 2026-05-06) verified the IBSR ShadowPayload mode's
numerical-equivalence criterion against the offline reference
extractor on the union of paired-bundle, held-out, and
multi-window evidence; the gate was augmented 2026-05-07
per D-025 (close-gate semantic-coverage rule) with a
higher-level prediction-class equivalence criterion
(`PHASE_1_SCORE_CLASS_MATCH`) layered on `PHASE_1_TOLERANCE`.
A 2026-05-08 follow-on cycle landed the joint-conditions
helper composing all three D-025 regime-scope conditions in
one assertion, paired-live-capture closure of the
SEMANTIC-EQUIV Branch 3 PASS path, and a V9 recon-detector
deployment alongside V8. A 2026-05-09 cycle extended the
detector-cycle evidence base from 2 (V8/V9) to 7 (V8 + V9 +
V10-V14, full lab-corpus attack-primitive coverage; §7.6)
and trained a multi-class softmax POC over the unified
corpus, demonstrating both the binary-vs-rest cross-fire
ceiling and its multi-class resolution. A 2026-05-10
follow-on landed `corpus_v1.6` (141 new Solana attack
bundles bringing three primitives - SOL_F10 / SOL_F14 /
SOL_P07 - above the LOPO floor) and ran the cross-chain
LOPO evaluation the same day: Phase A (Sui-trained binary
detectors against Solana attack bundles) surfaced
cipher-agnostic feature-surface generalisation (V8 100%
Solana recall) alongside host-telemetry chain-specificity
(V14/V11 0% Solana recall); Phase B (multi-class softmax
with joint Sui+Solana training) recovered V14/V11 to
100%/100% on Solana while preserving V8's 100%/100%, with
99.95% OOF and Brier ≤ 0.0008. A 2026-05-11 follow-on (Phase
C.1-C.4) expanded the Solana cross-chain corpus across four
additional attack families (reconnaissance,
service_misconfig, auth_bypass, rate_limiter_bypass; corpus
v1.7-v1.10), bringing Solana coverage to 541 attack bundles
across 10 primitives in 7 of 10 attack families and
empirically anchoring the family-taxonomy abstraction across
three mechanism-similarity-distinct cross-chain pairs (§4.4).
A 2026-05-11 / 2026-05-12 cycle landed the IBSR v7
feature-surface extension and end-to-end production
deployment (multi-class folded model on live IBSR
snapshots; §8.3). A 2026-05-12 / 2026-05-13 cycle ran the
V15 gossip-abuse detector through a worked-example
iterative-leak-surface-peeling pass (caveat named in
pre-registration, caveat empirically confirmed when the
UDP-gossip benign baseline landed, V16 corpus-augmented
retrain closing the caveat, multi-class folded v2
additively absorbing V16 as a 9th softmax column) - the
substrate paper's canonical worked example of the pattern
at the binary-detector layer. The same day landed the
public-artefact trio (`nr-bundle-spec` v0.1.0 +
`nr-bundles-public` dataset + `v8-cipher-agnostic` and
`multiclass-folded` models + `nr-bundle-classifier`
interactive Space; §3.4). A 2026-05-14 cycle ran the V1
mixed-traffic verification under realistic noisy-server
conditions, surfacing three load-bearing methodology
findings (bundle-level vs IBSR-level scoring divergence;
V11-class garbage-attractor under OOD mixed-traffic
inputs; binary-vs-multi-class deployment-policy
asymmetry). Together the cycles surfaced twenty-four
substrate-paper-grade methodology contributions per
principle 4 (plus a footnote-grade companion observation
paired with MC-7). The contributions are cycle-specific
learnings about pre-registration discipline,
manifest-family structure, cross-chain feature-quality
criteria, production-extractor fidelity-envelope bounds,
close-gate compositional coverage, joint-conditions
architecture, layered-detection generalisation,
binary-vs-rest cross-fire, multi-class softmax
architecture, family-taxonomy mechanism-abstraction,
production-deployment empirical anchoring,
iterative-leak-surface-peeling at the binary-detector
layer, bundle-vs-IBSR scoring divergence, multi-class
garbage-attractor structural properties, and binary-vs-
multi-class deployment-policy asymmetry; each generalises
beyond this project.

**MC-1: Reading-1 misspecification (V1 close).**
Step-11 V1 design's §C.2 outcome-band rationale was anchored
against an empirical assumption (cleartext baseline ≈ 1.0
cross-chain) that didn't hold under the cycle's actual
numbers. The auditor verdict (2026-05-04) committed to
column-header semantics (retention) over the
threshold-derivation-rationale prose. Generalisable insight:
**pre-registered outcome bands should be specified in
retention ratios, not absolute thresholds, when the baseline
regime itself is multi-mechanism**; threshold-derivation
prose that equates retention to absolute via baseline-
substitution is a misspecification risk point. Future cycles
that reuse the threshold-derivation pattern should explicitly
flag the baseline assumption as a separate falsifiability
item.

**MC-2: V7-narrow §SE3 single-feature-load-bearing reframe
(scoped).** Step-11 V8 retrain (CIPHER_AGNOSTIC_V2 =
CIPHER_AGNOSTIC_V1 minus `pcap.mean_packet_size`) lifted the
cross-chain accuracy floor on the Sui-holdout side from
0.32–0.38 (V7-narrow §SE3 sub-chance) to 0.61–0.67
(above-chance) across both report
slices. The cross-chain anti-classification floor at the
**cipher-agnostic byte-count manifest layer** was therefore
load-bearing on a single-feature distribution-mismatch
artefact, not an intrinsic chain-asymmetric mechanism at
that layer. **Scope of reframe (auditor-adjudicated
2026-05-04)**: V8 does not test `resp.status_2xx/4xx/5xx_frac`
(those features require cleartext body parse and are not in
CIPHER_AGNOSTIC_V1/V2 manifests). Their V7-narrow §SE3
anti-transfer pattern at the rate-invariant 13-feature
manifest layer remains live as a finding. The reframe is
methodology-contribution-grade scoping discipline: removing
one feature consumed one finding cleanly without overclaiming
consumption of related findings by association.

**MC-3: Cipher-agnostic-manifest single-feature-dominance
brittleness.** V1 was load-bearing on `pcap.mean_packet_size`
(per-primitive single-feature ROC 0.9954); V8 post-trim is
load-bearing on `resp.req_bytes_max` (per-primitive
single-feature ROC 0.9521–0.9930). Pattern is structural to
the cipher-agnostic byte-count manifest family - every trim
iteration surfaces the next dominant feature. Per the V6
D-018 dec 1 single-trim precedent + v1.3 fail-stop framing
+ auditor verdict 2026-05-04, V9 does NOT fire; recursive
trimming would violate principle 4 (the recurring-pattern
finding IS the methodology contribution, not a defect to
iterate away). **Substrate-paper material**: future
cipher-agnostic claims must either (a) accept the
recurring-pattern as structural and report aggregate
retention under the manifest family rather than defending
any single manifest, or (b) test a closure hypothesis
(e.g., "manifest trimmed below structural-redundancy floor
preserves cross-chain retention") rather than iterate.

**MC-4: High-confidence cohen_d features need not transfer
cross-chain.** `pcap.mean_packet_size` was V1
CIPHER_AGNOSTIC_V1's highest-cohen_d feature (V7-narrow §SE3
cohen_d = 1.089). Its V1 B1 single-feature ROC was 0.9954
(per-primitive LOPO; dominated). Its V1 B2 single-feature
ROC was 0.5000 (cross-chain holdout; no transfer). V8
demonstrates that retaining the feature in the
cipher-agnostic manifest **actively harmed** cross-chain
accuracy floor - removing it lifted Sui-holdout 28–30
percentage points. Methodology implication: per-primitive
cohen_d alone is insufficient feature-quality criterion for
cross-chain cipher-agnostic manifests; cross-chain
single-feature ROC must be a parallel selection criterion.
High-cohen_d features that anti-correlate cross-chain are
anti-features at the cipher-agnostic claim level.

**MC-5: Pre-registration-threshold-anchoring discipline
(Layer-2 §C.3-bis).** V1 design's §C.3-bis falsification
clause for `resp.amp_ratio_max` was: "Sui-side single-feature
ROC < 0.40 (deeper anti-classification than V7-narrow)."
V7-narrow's own Sui-side ROC was 0.18 - already below 0.40 -
meaning the threshold was set at 0.40 rather than at
V7-narrow's actual 0.18. V8 numbers (Sui-side 0.15) trigger
the literal pre-registration clause, but the underlying
prediction (anti-transfer confirmed) holds. Per principle 1,
literal pre-registration governs; per principle 4, the
threshold-anchoring miscalibration is itself substrate-paper
material. Generalisable insight: future falsification
thresholds anchored against prior-cycle measurements should
specify the prior-cycle measurement value explicitly (e.g.,
"X < 0.18 − ε, strictly deeper than V7-narrow's 0.18")
rather than an arbitrary threshold "deeper than" the prior;
the explicit-anchor pattern keeps the prior-cycle reference
self-evident at clause-read time. MC-5 is a Layer-2-instance
counterpart to MC-1's Layer-1 reading misspecification; both
are pre-registration-anchoring failures at different layers.

**MC-6: Production-extractor saturation envelope (Phase-1
close-gate, 2026-05-06).** The IBSR ShadowPayload mode ships
a hard "no drops on the network path" guarantee paired with
explicit lossy semantics on the kernel→userspace event
channel (`safety.md`): ring-buffer pressure cannot
backpressure XDP/TC, so under attack-rate saturation events
drop from userspace while packets do not. At the default
16 MiB ringbuf, saturation occurs at ~80 MB/sec sustained
payload (~3,400 RPCs/sec for F10-class amplification);
above this point the production extractor's byte-count
features (`resp.req_bytes_max`, `resp.resp_bytes_max`,
`amp_ratio_max`) undercount monotonically with the drop rate.
Pairs with MC-2 as the production-extractor side of the same
fidelity-envelope view: feature-localised brittleness shows
up at both ends of the V8 pipeline (training-side
single-feature dominance + production-side saturation-decay
on the same dominant features). Operator-actionable trade
space: ringbuf sizing (memory cost), per-CPU ringbufs
(complexity cost), or attack-rate-adaptive sampling
(different feature semantics). Substrate-paper material
under principle 4: bounds the production-deployment
empirical claim from above with operator-tunable parameters,
rather than treating undercounting as silent fidelity loss.

**MC-7: Production-extractor cardinality envelope (Phase-1
close-gate, 2026-05-06).** Companion lower bound to MC-6's
saturation-envelope upper bound. Below the criterion-applicable
attack regime (≥5 distinct client TCP source ports per
direction), IBSR's broader observation-window coverage
diverges from the offline tcpdump-narrow window by +1
distinct port; both extractors saturate at the cap-at-5
ceiling at-or-above the threshold. Together MC-6 + MC-7
specify the criterion-applicable regime as a band: lower
bound ≥5 distinct connections per direction (cardinality
envelope); upper bound ringbuf-fill rate < drain capacity
(saturation envelope). Saturating attacks live well inside
both bounds; benign-idle traffic with <5 connections lives
just below the cardinality bound. Substrate-paper material
under principle 4: bounds the production-deployment
empirical claim from below, and identifies operating-point
anchoring on attack-regime distributions (rather than
benign-idle distributions) as the principle-2-honest framing.

**MC-8: Close-gate semantic-coverage rule (D-025, Phase-1,
2026-05-07).** Pairs with and supersedes-of-scope MC-6 +
MC-7: MC-8 adds a third regime-scope condition to the
criterion-applicable regime band, training-distribution-
coverage. The pattern: a close-gate that verifies a
low-level property (production-extractor numerical
equivalence to offline reference, within `PHASE_1_TOLERANCE`)
on a held-out bundle is necessary but not sufficient for the
deployment claim's higher-level property (prediction-class
equivalence) when the verification configuration produces
traffic outside the model's training distribution. The
2026-05-06 Phase-1 close-gate cleared 7/7 numerical
equivalence on `--ids-per-request 1 --workers 1
--delay-ms 500` F10 traffic, but those bundles' offline-
extracted features sit 1000-10000× outside V8's sui_F10
training-distribution ranges; V8 scores both extractors'
features as BENIGN (class 0) on the cleared bundles -
honest OOD model uncertainty, not a regression - even though
both extractors agree numerically. The discipline:
production-extractor close-gates that verify a low-level
property must pre-register the deployment-claim-load-bearing
higher-level property when the two diverge. The Phase-1
close-gate is the worked-example anti-pattern; D-025 lands
the rule. The augmented harness (`PHASE_1_TOLERANCE` ⊕
`PHASE_1_SCORE_CLASS_MATCH`) lands the implementation, with
explicit OOD scope-condition handling (out-of-distribution
→ advisory, not gating; in-distribution + classes-equal →
gating). Three regime-scope conditions become mandatory
pre-registration items rather than implicit assumptions:
cardinality envelope (MC-7), saturation envelope (MC-6),
training-distribution-coverage (this MC). The empirical
anchor was strengthened 2026-05-08 by paired-live-capture
(offline bundle + IBSR `collect-payload` snapshot) of an
in-distribution F10 attack-window: 5/7 features
exact-equivalent, 2/7 cardinality divergence consistent
with MC-7's watched-port-filter scope, score-class-match
offline=production=class-1 ATTACK at 1.0/1.0;
`PHASE_1_SCORE_CLASS_MATCH` PASS in-criterion-applicable-
regime. This lifts MC-8 from "PoC plumbing demonstrated,
real-extractor verification queued" to fully empirically
anchored at deployment-claim level. Substrate-paper material
under principle 4: pairs with MC-1 (Reading-1
misspecification) and MC-5 (pre-registration-threshold-
anchoring) as a third "pre-registration is harder than it
looks" worked example, at compositional granularity rather
than threshold-anchoring granularity.

**MC-9: Three-check disambiguation pattern (Phase-1,
2026-05-07).** When a downstream observation contradicts an
upstream verification ("close-gate cleared but model says
BENIGN on what looks like attack traffic"), the natural
diagnostic question is: is this a model defect, an extractor
defect, or honest OOD uncertainty? The three-check
disambiguation answers cleanly: (1) does the model fire on
its training distribution? - for Phase-1, V8 mean score
0.9994 across the four sui_F10 lab-tls-fronted training
bundles, all > 0.80; (2) does the verification configuration
produce in-distribution features? - for Phase-1, 5/7
features 1000-10000× outside training-distribution F10
ranges; (3) is the divergence honest OOD uncertainty? -
combining (1)+(2): the model is correct on its training
distribution and the input is far outside that distribution;
BENIGN is the honest model output, not a defect. The default
"if low-level passed the high-level should too" reasoning
conflates verification of pipeline equivalence with
verification of deployment-claim properties. The three-check
disambiguation makes the conflation visible by interrogating
each layer separately. The right corrective action (compose
a new gate / pre-register a new condition) becomes obvious;
the wrong corrective actions (retrain the model / re-engineer
the extractor) are ruled out. Domain-independent: replace
"V8" with any model and "sui_F10" with any
training-distribution scope to apply. Substrate-paper
material under principle 4: methodology contribution at
diagnostic-pattern granularity; the worked-example provenance
is committed at
`nr-substrate/docs/PHASE-1-CLOSE-GATE-DISAMBIGUATION-2026-05-07.md`.

**MC-10 (footnote-grade): Cardinality posture under HTTP/1.1
keep-alive (Phase-1, 2026-05-07).** Companion observation to
MC-7. Reproducer-pipeline configurations interact with
HTTP/1.1 connection pooling in ways that defeat naive
cardinality envelopes. The demo F10 bundle
(`crp_aa695427249e42ec`, `--workers 2 --ids-per-request 10
--delay-ms 50 --duration 30`) produced offline
`pcap.unique_dst_ports = pcap.unique_src_ports = 2`, well
below MC-7's cardinality-envelope lower bound of 5. Cause:
aiohttp's HTTP/1.1 keep-alive collapses each worker's
requests onto a single client-side socket; 2 workers × 1
keep-alive socket each = 2 distinct client TCP source ports
across the capture window. Methodological consequence: a
close-gate using the cardinality envelope as a regime-
applicability condition must pre-register the reproducer's
connection-pooling configuration explicitly. Either (a)
require `--no-keepalive` (or equivalent) when cardinality
is gating, or (b) document keep-alive collapse as expected
behaviour and adjust the lower-bound rationale to "≥ N
distinct keep-alive sockets, equating to N distinct client
TCP source ports under default-keepalive HTTP/1.1."
Substrate-paper material at footnote granularity under
principle 4: corpus-design decisions about reproducer
pipelines have downstream consequences for which features
discriminate at the wire (§7.1 cross-refs).

**MC-11: Joint-conditions architecture for compositional
close-gates (2026-05-08).** Pairs with MC-8 as its
rigorous-implementation closure. The 2026-05-07
SEMANTIC-EQUIV harness verified D-025's
training-distribution-coverage condition only; cardinality
(MC-7) and saturation (MC-6) envelopes were assumed
out-of-band. The 2026-05-08 joint-conditions helper
(`_is_in_criterion_applicable_regime()` in
`training/src/nr_training/inference/cross_validate.py`)
composes all three regime-scope conditions in one
assertion. Three architectural choices: (1) cardinality
envelope is a feature-time gate for V8 / cipher-agnostic-v2
(`pcap.unique_dst_ports ≥ 5 AND pcap.unique_src_ports ≥ 5`),
but bypassed for V9 / recon-v1 because V9 USES port
cardinality as a primary detection signal rather than
gating on it - manifest-dispatch keeps the check
appropriately scoped per detector. (2) Saturation envelope
cannot be verified from feature values alone, so it is
treated as advisory: the harness emits a "verify out-of-band"
flag and the operator runbook owns runtime ringbuf
monitoring (per principle 5, the operator-tunable saturation
envelope's verification belongs in the deployment runbook,
not in the inference feature dict). (3)
Training-distribution-coverage delegates to the existing
`_is_in_training_distribution`. Score-class-match assertion
is gating ONLY when all three conditions hold (with
condition 2 operator-asserted); out-of-regime → advisory,
doesn't fail `all_passed`. Generalisable form: any
compositional close-gate that needs to verify multiple
regime-scope conditions jointly should name each condition
explicitly, separate gating-from-features from
gating-via-runtime-monitoring, and manifest-dispatch when a
condition is detector-specific (V9's port cardinality is
feature-not-gate where V8's is gate-not-feature).
Substrate-paper material under principle 4: at the
close-gate framework level, the joint-conditions
architecture is the principled way to compose multiple
regime-scope conditions without entangling their semantics.
Shows D-025 isn't a one-condition rule; it's a band-bounded
compose pattern, with MC-6 + MC-7 as the already-pre-
registered envelopes and D-025's contribution being the
third condition plus the assembly discipline.

**MC-12: V9 recon-detector cycle - layered detection on a
common substrate (2026-05-08).** Single-instance
demonstration that the close-gate framework + production
extractor + inference container that worked for V8
(byte-amplification at the cipher-agnostic-v2 manifest
layer) generalises to a different attack class
(reconnaissance) without architectural change. Same IBSR
sensor (StrictCounter mode added alongside ShadowPayload),
same offline extractor (pcap parser extended with TCP-flag
counters), same trainer template, same close-gate harness
via manifest-dispatch added 2026-05-08. The pattern:
detection at the substrate level (kernel-eBPF observation +
feature aggregation + ML scoring) admits multiple
specialised detectors layered on the same observation
foundation - V8 (cipher-agnostic-v2, 7 features,
byte-amplification) and V9 (recon-v1, 6 features, port-scan
reconnaissance). Honest training-distribution discipline
applied recursively: V9's first iteration trained on
full-bundle pcap totals produced a model that scored 0.000
on real per-window inference inputs (the same train/inference
distribution-mismatch failure mode D-025 named for V8);
iteration 2 added per-window slicing + watched-port
filtering at training time; iteration 3 reduced the
manifest from 14 features to 6 after discovering that ratio
features (`syn_to_handshake_ratio`, `rst_fraction`) get
diluted by baseline ACKs at inference time. Final V9 model
scores 1.000 on real per-window scans, 0.000 on baseline,
recovers within 1 window. **Honest scope**: this is a
single-instance demonstration at the recon family, not
"V9 generalises to all attack classes". Other attack
classes (auth-bypass, gossip-abuse, etc.) remain forward
work. Generalisable form: any time a detector trained on
offline-aggregated features deploys against a production
observer working at different aggregation granularity,
training-time feature extraction must mirror inference-time
feature extraction's cadence + filter exactly, OR features
must be chosen to be invariant under the aggregation
difference. The methodology contribution is the iterations
themselves - the failures discriminate which features are
robust. Substrate-paper material under principle 4: V9's
three-iteration history makes the train/inference
distribution discipline concrete in a way V8's single-shot
success couldn't. Pairs with MC-8 as a "what happens in
iteration N+1 when iteration N's lessons aren't yet
absorbed" worked example.

**MC-13: Binary-vs-rest cross-fire ceiling (V10-V14 cycle,
2026-05-09).** V10-V14 binary detectors trained against the
lab corpus extended the framework's attack-class coverage
from V8/V9 to V8-V14 (full lab-corpus primitive set; §7.6
detector table). V11's close-out surfaced a structural
property of the binary-vs-rest pattern: when attack classes
share signal regions, the per-class binary trained on
"V11 vs (everything else)" cannot distinguish V11 from
*specific* alternative classes that occupy similar feature
regions. Empirical numbers: V11 ← V12 99% (validator-stress
shared host.cpu/connection features), V11 ← V10 48%
(auth-related connection churn + CPU), V12 ← V8 21% (volume
features overlap), V14 ← other-attack 13% (connection-
collapse signature). V13/V14's clean ≤1.4% isolation is the
counter-evidence: when an attack class occupies a genuinely
orthogonal signal region, binary-vs-rest hits A-grade.
**Architectural finding**: cross-fire is not an inherent
limit of binary detection nor of the feature surface; it is
a property of the *training-objective shape* - binary-vs-
rest collapses all non-positive classes into one negative
class, losing the distinctions among them. Multi-class
softmax with the *same features* and *same corpus* recovers
those distinctions (MC-14). Generalisable form: any
framework that ships per-class binary detectors should
expect cross-fire when attack classes share signal regions;
the paired-class cross-fire rate *characterizes* how shared
the signal region is and is the load-bearing diagnostic.
Substrate-paper material under principle 4: the binary-stack
architecture is honest production primitive; its limit is
empirically measurable; both architectures have a place.

**MC-14: Multi-class softmax resolves cross-fire (POC,
2026-05-09).** Pairs with MC-13 as its
architectural-resolution closure. One
`CalibratedClassifierCV(HGB, isotonic, cv=5)` trained on
the unified V8 + V9 + V10-V14 + benign corpus (2014
lab-fidelity samples, 8 classes, 107-feature surface, no
manifest filter). Stratified 5-fold OOF: **99.95% accuracy**
(2013/2014 correct), per-class recall 1.000 across the
board except V11 at 0.995 (one V11 → benign miss in fold 3),
Brier scores ≤0.0007 across all classes. Cross-fire
reduction vs binary baselines: V11 ← V12 binary 99% →
multi-class **0%**; V11 ← V10 binary 48% → multi-class
**0%**; V12 ← V8 binary 21% → multi-class **0%**. The
honest tradeoff: multi-class swaps binary's 100% V11 recall
+ 99% V12 cross-fire for 99.5% V11 recall + 0% cross-fire -
one false negative against zero cross-fire is the right
operational trade, and an operator-tunable threshold
adjustment per-class, not an architectural limit.
Cipher-agnostic class generalisation: V9 (recon, pcap-only
feature surface) coexists with V10-V14 (body-parse-required)
in the same multi-class manifold without confusing the
model - V9 100% recall + 0% cross-fire across all 7 other
classes. **Production-architecture canon**: binary stack as
headline (per-class explainability + threshold-tuning) plus
multi-class softmax as the cross-fire-resolution layer when
binary-pair ambiguity arises. Multi-class is *additive*: no
taxonomy changes, no feature-extractor changes, no corpus
rebuild - the same framework supports both architectures.
Honest scope: 99.95% is lab-corpus + in-distribution
evaluation, not a zero-error production claim; cross-chain
extension to Solana is corpus-level banked. Full POC
readout (detector table, OOF confusion matrix, cross-fire
matrix) at §7.6. Substrate-paper material under principle 4.

**MC-15: Small-n binary detector lower bound (V14 cycle,
2026-05-09).** V14 (compute-amp / sync-wedge, n=54) is the
smallest binary training corpus in the V8-V14 cycle; outcome
93% recall at threshold 0.5 (50/54 fired) + 13%
other-attack cross-fire. The four V14 misses + the 13%
cross-fire are small-n artefacts: the model overfits to the
training distribution's specifics and generalises only as
well as the n=54 sample diversity allows. Compare V13
(n=250, 5 primitives) at 100% recall + 0.37% benign FPR +
0% V10/V12 cross-fire - the five-fold larger corpus
produces qualitatively better isolation. Generalisable form:
~50 bundles per attack primitive is the LOPO floor (D-001 +
Step-6 floor); ~250 bundles across multiple primitives in a
family is where binary-vs-rest isolation becomes tight.
Below ~50 per primitive (V14's 54 across one primitive),
binary-vs-rest hits its *data-side* lower bound: the model
lacks enough diversity to discriminate cleanly, and the
multi-class architecture (MC-14) becomes the only viable
path. Distinct from MC-13's *signal-overlap* upper bound,
MC-15 is a *corpus-scale* lower bound. Substrate-paper
material under principle 4 at corpus-sizing decision level:
this is the empirical floor below which binary-vs-rest needs
reinforcement (multi-class fallback or corpus expansion).

**MC-16: Generalised sweep-harness pattern (corpus_v1.6,
2026-05-10).** Methodology-tooling contribution at
infrastructure level, paired with the bundle-contract
discipline at output-format level. The Solana cross-chain
sweep harness landed alongside `corpus_v1.6` demonstrates a
per-primitive parameter-dispatch pattern: each attack
primitive's posture mapping has primitive-specific knobs
(F10 `--keys-per-request` for request-side amplification,
F14 `--n-memos` for compute-time amplification, P07
`--memcmp-bytes` for filter selectivity), and the harness
encapsulates the per-primitive flag mapping as configuration
data + dispatches generically over a single launcher. The
bundle contract abstracts the *output* format; this harness
abstracts the *sweep input*. Same operational principle.
Generalisable form: any framework that ships per-primitive
attack reproducers with primitive-specific parameter knobs
benefits from a sweep harness that data-drives the
per-primitive flag mapping, avoiding both per-primitive bash
sweep scripts (combinatorial growth) and per-primitive
Python launchers (duplication). The data-config + generic
launcher pattern scales as the primitive count grows.
Substrate-paper material under principle 4 at
methodology-tooling level: small but durable.

**MC-17a: Cipher-agnostic features generalise cross-chain
(Phase A LOPO, 2026-05-10).** V8 (cipher-agnostic-v2
manifest: 7 features, all pcap/resp byte-shape) trained on
Sui F10 fires identically on Solana F10 traffic - 100%
recall (51/51), median prediction 0.998 on both chains,
zero retraining + zero feature engineering + zero manifest
changes. The feature surface is *traffic-shape only*
(request/response byte ratios + port cardinalities), which
is chain-agnostic by construction (same TCP/HTTP/JSON-RPC
characteristics regardless of underlying chain protocol).
Generalisable form: any framework manifest composed purely
of traffic-shape features inherits chain-agnostic
generalisation *for free*; this paper's V8 deployment claim
across chains lands at corpus-evidence-quality level. Worked-example value: the bundle contract +
cipher-agnostic-v2 manifest combination is the framework's
strongest cross-chain transfer claim, and the empirical
anchor is 100% recall + 0% cross-chain confusion zero-shot.
Substrate-paper material under principle 4: §cross-chain
headline.

**MC-17b: Host-telemetry features are chain-specific
(Phase A LOPO, 2026-05-10).** Pairs with MC-17a as the
per-class manifest-composition diagnostic. V14
(`host.cpu_*`, `host.num_*_delta`, `resp.duration_ns_*`)
and V11 (`host.cpu_mean`, `host.num_connections_delta`)
trained on Sui hit **0% recall cross-chain on Solana** -
0/51 SOL_F14, 0/52 SOL_P07/etc. Sui-trained models trained
against `sui-node` validator process fire at 0% on `agave`
validator process even though attack semantics are identical
(compute-amp / app-DoS): host.* features capture
chain-runtime-specific process behaviour (different async
runtimes, connection-handling patterns, FD lifecycles, RSS
baselines), so the model has no basis to fire on the other
chain's process distress patterns. **This is a feature, not
a bug** - V14-DESIGN-V1.md predicted exactly this in "Open
methodology questions" *before* empirical evaluation. The
framework provides train-on-A / eval-on-B as a **first-class
diagnostic**: per-class recall pattern reveals the
manifest's chain-agnostic vs chain-specific composition,
and operators discover the boundary empirically without
architectural changes. Generalisable form: per-class
manifest composition *encodes* the cross-chain
transferability story as a hypothesis the train-on-A /
eval-on-B evaluation tests. The framework's design
deliberately separates these into testable units.
Substrate-paper material under principle 4: §cross-chain
section's nuance - the framework supports multiple
cross-chain transfer modes; manifest composition determines
which mode applies.

**MC-18: Cross-chain transfer in multi-class softmax is
feature-semantic (three-mode taxonomy, ablation-grounded;
2026-05-10).** Pairs with MC-17b as its
architectural-resolution closure and supersedes earlier
"cipher-agnostic features bridge" / "redundant signal
across feature categories" hypotheses with a stronger
ablation-grounded claim. Each attack class's transferability
is determined by what fraction of its load-bearing features
capture *chain-agnostic semantic patterns* versus
*chain-specific patterns* the trained model learned to
discriminate. Three empirically-distinguished modes apply,
characterisable per-class via three complementary
diagnostics (train-on-A/eval-on-B from MC-17b; SHAP
attribution; feature ablation):

- **Mode 1: single-category clean transfer** (V8 evidence).
  V8 transfers via its byte-shape feature surface entirely;
  ablating `host.*` or `pcap.*` has zero effect on recall.
  The original "cipher-agnostic bridges" framing was right
  *in spirit* (these are byte-shape invariants) but wrong
  about feature-prefix - chain-agnostic semantics live in
  some `resp.*` features (`resp.amp_ratio_*`,
  `resp.req/resp_bytes_max`) too, by manifest design.
  Maps to attack classes whose load-bearing features are
  chain-agnostic by semantic design.
- **Mode 2: multi-category causal-conjunctive transfer**
  (V11 evidence). V11 zero-shot recall on SOL_P07 is 98%;
  ablating any one major feature category causes recall
  drop (without `host.*`: 98% → 54%; without `resp.*`:
  98% → 60%; without `pcap.*`: 98% → **0%** collapse).
  This is *not* redundancy - the categories are causally
  conjunctive, with `pcap.*` causally necessary. SHAP and
  ablation disagree informatively here: SHAP attributes
  22.5% to `pcap.*` (rank 3 by contribution) but ablation
  reveals `pcap.*` is rank 1 by causal necessity. SHAP
  measures prediction-contribution intra-distribution;
  ablation measures transfer-necessity for cross-chain
  generalisation.
- **Mode 3: chain-specific-feature poisoning** (V14
  evidence; the most novel finding). V14 zero-shot recall
  on SOL_F14 is 2%; ablating `pcap.*` lifts it to **19.6%**
  (10× improvement); ablating `host.*` + `resp.*` lifts it
  to **39.2%** (20× improvement). The Sui-trained model
  learned chain-specific patterns (sui-node tokio TCP
  stack window sizes / packet pair patterns) that
  systematically *push SOL_F14 bundles AWAY from V14* with
  high discriminative weight. Removing those features
  removes the chain-specific decision pressure; the model
  defaults toward V14 when other features support it. This
  is **active harm, not signal absence**.

Joint training (Phase B's folded mode) achieves what
ablation does - removes chain-specific decision pressure
by training on both chains' values simultaneously - without
the manual feature-removal cost. The 100% folded recall on
V14 represents the upper bound the ablation experiment
approaches by removing the worst-poisoning features. The
framework supports two chain-coverage architectures without
taxonomy / feature-extractor / trainer changes: (1) binary,
per-chain retrain - N chains = N detectors per class,
per-detector explainability stays clean; (2) multi-class,
single joint model - one column per class in a softmax
trained jointly across chains. The choice is per-deployment
policy, not architectural. **Bonus observation banked**:
folded multi-class also resolves binary V8's benign-FPR
climb (15-17% on the wider cross-chain cache to 1.000
multi-class precision) - suggestive of a deeper property
where multi-class training across more diverse data
resolves binary calibration drift; not yet confirmed as a
framework claim. Pairs with MC-13 + MC-14 to give a clean
two-axis story: cross-class confusion (V11/V12 share signal
regions) and cross-chain transfer (chain-specific features
poison V14) *are the same problem at different boundaries* -
both resolve via joint training; in both cases multi-class
softmax stays the resolution layer and the binary stack
stays the headline.

**Methodology contribution at the diagnostic-surface
level**: this work elevates ablation-as-diagnostic to a
first-class methodology contribution alongside SHAP and
train-on-A/eval-on-B. The three diagnostics are
complementary, not redundant: train-on-A/eval-on-B (MC-17b)
characterises whether a manifest is chain-agnostic vs
chain-specific; SHAP attribution characterises what
features contribute to prediction intra-distribution;
feature ablation characterises which features are causally
necessary for cross-domain transfer. Together they let an
operator characterise any new attack class's cross-chain
transferability before deploying it. Substrate-paper
material under principle 4: §multi-class section's
strongest empirical anchor + a third diagnostic protocol
for the framework's transferability-characterisation
surface.

**MC-19: Family taxonomy abstracts over chain-specific
implementations (corpus_v1.6-v1.10, 2026-05-10 / 2026-05-11).**
The framework's chain-agnostic `family_id` decision (D-002;
§4.2) was design-rationale until the family-level
abstraction was shown to *hold empirically* across chains.
`corpus_v1.7` through `corpus_v1.10` populated Solana
analogues across four additional attack families
(reconnaissance, service_misconfig, auth_bypass,
rate_limiter_bypass) at LOPO floor; combined with
`corpus_v1.6` (response_amp, compute_amp,
rate_limiter_bypass), Solana cross-chain corpus now totals
541 attack bundles across 10 primitives in 7 of the 10
attack families. Three cross-chain primitive pairs probe
the abstraction at materially different mechanism-similarity
distances (§4.4): Pair A (`response_amp` / F10, same
mechanism), Pair B (`auth_bypass` / H01, REST routes vs
JSON-RPC method enumeration - radically different
mechanisms), Pair C (`rate_limiter_bypass` / GR,
programmable-transaction gas-price-0 vs
`simulateTransaction` gasless-by-design - completely
different mechanisms exploiting the same architectural
weakness). Pair A is the bounded case (V8 binary transfers
at 100% recall cross-chain, Phase A); Pairs B and C are the
mechanism-divergent cases where the family-level wire
signatures remain consistent with the shared architectural
weakness despite mechanism-structural divergence. Pair B is
the strongest case in the chain because it is the least
mechanically-similar pair. The framework's family taxonomy
is therefore **mechanism-abstraction-class** rather than
implementation-class: two primitives belong to the same
family when they exploit the same architectural weakness
regardless of chain-protocol mechanism. Generalisable form:
attack-family schemas in cross-chain ML detection should be
anchored on mechanism-abstraction-class (architectural-
weakness equivalence) rather than implementation-similarity
(protocol-mechanism similarity) - the former generalises
cross-chain by design, the latter by accident. Pairs cleanly
with MC-17a/17b/MC-18 v3: MC-17a/17b/MC-18 v3 characterise
*detector-level* cross-chain transferability per-class via
the three-mode taxonomy; MC-19 establishes that the
family-level *taxonomy substrate* on which the detector
predictions sit is itself empirically well-founded.
**Scope caveat**: MC-19 is currently taxonomy-level +
mechanism-trace empirical (per-primitive disposition + wire-
signature traces); detector-transfer empirical confirmation
across Pairs B and C (V10-trained on Sui H01 evaluated
against SOL_H01; V11-trained on Sui GR evaluated against
SOL_GR01 + SOL_P07) is queued forward work outside v1.
Single chain pair tested (Sui ↔ Solana); cross-chain
abstraction across ≥3 chains banked. C.5 (consensus_abuse,
multi-validator Solana cluster) not yet captured, so the
full 10-family schema has cross-chain corpus coverage for 7
of 10 families. Substrate-paper material under principle 4:
§family-taxonomy section's empirical anchor + the framework
generalises argument's strongest claim for non-Sui chains.

**MC-20: Production-deployment empirical anchor (IBSR v7,
2026-05-11 / 2026-05-12).** The IBSR feature-surface
extension blocker identified at the V10-V14 cycle close
(§7.6 / §8.3) resolved end-to-end on the production demo
stack. nr-ibsr schema v7 added `ResponseAggregates`
(`duration_ns_{mean,max}`, `status_{2xx,4xx,5xx}_frac`,
`rpc_error_{distinct_codes,frac}`, `req_bytes_mean`,
`resp_bytes_mean`) via Phase A (`a1ed02e`) and
`HostTelemetry` (`cpu_{mean,max}`, `rss_{delta,max,slope_bps}`,
`num_fds_delta`, `num_connections_{delta,max}`,
`io_write_delta`) via Phase B (`26a5238`); the inference
container's `features_from_ibsr_snapshot()` lifted from 7 to
26 features per snapshot. End-to-end smoke-test (idle
traffic, 2026-05-11): live IBSR capture → inference
container loads V8 binary + multi-class folded model →
predictions JSONL with per-class probabilities → nr-guard
XDP enforcement consumes JSONL and applies block / redirect
/ pass per verdict. The "V8 NaN-prediction artefact"
characterised at the V10-V14 cycle as a class-prior
collapse under partial feature surface (multi-class argmax
= V13, wrong) materially resolves under the full v7
surface (argmax = benign, correct; `host.cpu_mean` =
13.2%, `host.rss_delta` = +5.9 MB, `resp.count` = 4,
`resp.duration_ns_mean` = 221,528 ns). The framework's
production-deployment claim is no longer "trained models
can exist offline" - it is "trained models run on live
validator traffic with the production extractor at
full-feature-surface parity to the offline-trainer."
Three-step proof: (1) IBSR-side numerical-equivalence to
offline extractor on Phase 1 close-gate features (MC-8,
2026-05-06); (2) IBSR-side schema parity for V10-V14
manifest features (MC-20 Phase A + B landing, 2026-05-11);
(3) production inference container running multi-class
folded model on live IBSR output, predicting idle as
benign + attacks as their class (this evidence,
2026-05-11/12). Substrate-paper material under principle
4: §production-deployment section's empirical anchor;
expands the framework's value proposition from "schema +
trainer" to "schema + trainer + production extractor +
production inference, all at feature-surface parity".

**MC-21: Iterative leak-surface peeling at the
binary-detector layer (V15 → V16 worked example,
2026-05-12 / 2026-05-13).** This paper's canonical
"iterative leak-surface peeling" pattern (§5 methodology
centerpiece) extends to the binary-detector layer with
the V15 → V16 cycle pair. V15 (gossip-abuse binary detector,
trained 2026-05-12 on 10 cycle2 bundles vs 200 TCP RPC
benigns) cleared per-primitive recall at A-grade per
pre-registered triggers but carried an explicit Section H
caveat: *"the model may trivially learn `UDP at port 9001`
as the discriminator - which fires correctly on the attack
mechanism but is a protocol-shape signal, not the
attack-shape signal we want."* The substrate framework's
pre-registration discipline is doing the load-bearing work
here: the caveat names the falsifiable risk in advance.
2026-05-13 early, the first ground-truth UDP gossip benign
(`SOL_BG01_validator_repair_catchup`, real
validator-to-validator repair traffic from a two-validator
lab cluster) landed; scoring V15 against the expanded
corpus produced **35/35 gossip-abuse attacks fired at
1.000 AND SOL_BG01 also fired at 1.000**. Caveat #2
empirically confirmed: V15 learned protocol shape, not
attack shape; as trained, V15 is NOT production-deployable.
The same day, V16 (pre-registered Section J of
`V15-DESIGN-V1.md` with four falsifiable hypotheses) was
trained with `SOL_BG01` in the negative training set, no
manifest change, A-grade-caveat-closed outcome: `SOL_BG01`
in-sample score 1.0000 → **0.0053**; all 35 gossip-abuse
attacks fire at ≥0.9998; 200 sampled holdout benigns
0/200 fire (max 0.0004); H1 confirmed; H2 falsified.
Honest caveats banked: `SOL_BG01` is in-sample at n=1 so
no LOPO is possible; corpus expansion to n≥10 UDP gossip
benigns across postures is the next-cycle path. Multi-class
folded v2 (`MULTICLASS-FOLDED-V2-DESIGN.md`, same day)
absorbs V16 as a 9th softmax column without disturbing
existing classes: per-class recall 0.997-1.000 across the
8 prior classes, V16 recall 1.000 at precision 0.972,
overall OOF 0.9992 (within fold-variance of the 2026-05-11
baseline 0.9996); H1 (regression test) confirmed; H2
(V16 new class fit) confirmed in-sample. The substrate
paper's iterative-leak-surface-peeling worked example
extends from the training-cycle layer (V1 → V7-narrow arc,
§5.4) to the binary-detector layer (V15 → V16) and the
multi-class-folded layer (folded v2 absorbs V16
additively). Substrate-paper material under principle 4:
the pattern is layered, not flat - each cycle's outcome
surfaces the next layer's gap honestly and the methodology
discipline produces detectors whose limitations are
characterised honestly and closed iteratively when corpus
enables it.

**MC-22: Bundle-level vs IBSR-level scoring divergence
(V1 mixed-traffic cycle, 2026-05-14).** Structural
methodology finding load-bearing for this paper's
§methodology section. Bundle aggregation contracts
(attacker-filtered `responses.parquet` - the F10 reproducer's
`record_response()` writes only attacker-originated RPCs)
are *training-time fidelity*; IBSR window-aggregate
contracts (BPF/XDP packet-layer wire view; sees all traffic
on the wire regardless of origin) are *production fidelity*.
The two views **do not converge under mixed traffic**.
Empirical evidence: scoring 10 F10 mixed-traffic bundles at
three dilution ratios (1× / 10× / 100×) via the offline
bundle-level path produced identical V8 scores (0.9977)
across all three ratios - the bundle-level view filters
dilution out of the feature surface by construction. The
IBSR-snapshot view (production-inference path) showed the
real dilution gradient: V8 binary mean 0.9977 → 0.9666 →
0.7993 across 1× / 10× / 100×; V8 binary fired ≥0.5 in
18/18 snapshots at all three ratios. Generalisable form:
any deployment claim that quotes bundle-level scoring
numbers as production-fidelity evidence is a methodology
error. The bundle-level path is for training and offline
methodology evaluation; the IBSR window-aggregate path
is the inference-time analogue. Substrate-paper material
under principle 4: structural cleavage between training-
fidelity and production-fidelity evaluation contracts;
this paper's §methodology section gains the bundle-vs-IBSR
divergence as a load-bearing distinction.

**MC-23: V11-class garbage-attractor under OOD
mixed-traffic inputs (V1 cycle, 2026-05-14).** Structural
decision-boundary property of the multi-class folded
softmax under out-of-distribution mixed-traffic inputs. At
the IBSR-view (production-fidelity path), F10 mixed-traffic
captures at 100× background dilution route to V11
(rate_limiter_bypass) at 100% argmax instead of V8
(response_amp), even though the V8 binary detector still
fires; F14 mixed-traffic captures at 10× and 100× similarly
route to V11 instead of V14 at 100% argmax. The V11-class
manifold absorbs OOD mixed-traffic inputs whose features
are pulled toward the high-`resp.count` + low-`amp_ratio` +
short-`duration_ns` region by background traffic - a
coherent structural property of the trained model's
decision boundary, not random softmax noise. **The
substrate paper's canonical example of "multi-class
identity is harder than binary detection" under mixed
traffic.** Distinct from standard open-set classification
framings because the garbage class is structurally
*absorptive*, not residual. Generalisable form: any
multi-class softmax trained on single-attacker-no-benign-
concurrent-traffic exemplars develops at least one class
manifold that absorbs OOD inputs along the
"mixed-traffic-shifted feature region" axis; the substrate
paper's V11 manifold is the worked example, not the
general claim. Substrate-paper material under principle 4:
§discussion section's load-bearing structural finding;
remediation paths pre-registered (Path 2: mixed-traffic-
positive retrain; Path 3: per-source-IP IBSR aggregation).

**MC-24: Binary-vs-multi-class deployment-policy asymmetry
(V1 cycle, 2026-05-14).** Concrete operational
recommendation derived from MC-22 + MC-23. Under mixed
traffic at production-fidelity (IBSR-view): binary
attack-or-benign verdicts are **dilution-robust** (V8
binary fired ≥0.5 across all dilution ratios in all
mixed-traffic Phase 1 + Phase 2 captures); per-class
identity is **mixed-traffic-fragile** (V11-class
garbage-attractor at higher dilutions). The
production-deployment policy that follows: *trust the
binary verdict; treat per-class identity as advisory under
mixed traffic*. This is the framework's first explicit
deployment-policy claim with empirical backing at a
defined dilution range; remediation paths (Path 2 mixed-
traffic-positive retrain at multiple dilution ratios; Path
3 per-source-IP IBSR v8 schema extension scoring the
attacker's stream in isolation) are pre-registered
remediation cycles when corpus + infra unblock them.
Generalisable form: cross-domain ML deployment policy
under noisy/diluted production inputs should not assume
binary-detection and multi-class-identification share
robustness profiles; the paired-class fragility surfaces
under empirical mixed-traffic verification, and the
remediation paths are corpus-side (mixed-traffic-positive
retrain) or extractor-side (per-source-IP aggregation),
not architectural. Substrate-paper material under
principle 4: §deployment-policy section's empirical
anchor + the framework's first concrete
operator-actionable claim.

**Transferability**: the twenty-four contributions generalise
beyond this project's cipher-agnostic-manifest evaluation.
MC-1 and MC-5 apply to any pre-registration that anchors
thresholds on baseline-behaviour assumptions or prior-cycle
measurements. MC-2 applies to any cycle that consumes a
cross-chain finding by removing one of multiple
candidate-mechanism features. MC-3 applies to any
feature-subset family with structural single-feature-
dominance recurrence. MC-4 applies to any cross-domain or
cross-chain ML evaluation that selects features via
per-primitive effect size alone. MC-6 and MC-7 apply to any
production-extractor empirical-fidelity claim where lossy
event channels and observation-window-coverage asymmetries
bound the criterion-applicable range as a band rather than a
point. MC-8 applies to any composition of low-level
verifier (extractor / preprocessor / pipeline stage) +
downstream high-level deployment claim (model verdict /
decision) where the two diverge under verification
configurations that miss the model's training distribution.
MC-9 applies to any model + pipeline compose where
downstream verdict contradicts upstream verification - the
three checks are domain-independent. MC-10 (footnote-grade)
applies to any cardinality-feature gate that interacts with
L7 connection-pooling semantics. MC-11 applies to any
compositional close-gate that verifies multiple regime-scope
conditions jointly, where some conditions are
gating-from-features, others gating-via-runtime-monitoring,
and detector-specific dispatch keeps each condition
appropriately scoped. MC-12 applies to any
layered-detection deployment where multiple specialised
detectors share a common substrate (kernel-eBPF observation
+ feature aggregation + ML scoring); the V9 case shows the
framework generalises to a different attack class without
architectural change, and the three-iteration history of V9
makes train/inference distribution discipline concrete.
MC-13 applies to any binary-vs-rest detector stack where
attack classes share signal regions; the paired-class
cross-fire rate is the load-bearing diagnostic for how
shared the regions are. MC-14 applies to any binary-vs-rest
stack hitting cross-fire ceilings (MC-13) - multi-class
softmax with the same features and same corpus is an
*additive* architectural option that recovers per-pair
distinctions; binary-as-headline + multi-class-as-cross-fire
-resolution is the production canon. MC-15 applies to any
binary-vs-rest detector trained below the corpus-scale floor
(~50 bundles per primitive, ~250 across a family); below
the floor, binary-vs-rest hits its data-side lower bound
and multi-class becomes the only viable path. MC-16 applies
to any framework shipping per-primitive attack reproducers
with primitive-specific parameter knobs - a data-config +
generic-launcher sweep harness avoids the combinatorial
growth of per-primitive bash scripts and the duplication of
per-primitive Python launchers. MC-17a applies to any ML
detector framework with a manifest composed purely of
traffic-shape features - chain-agnostic generalisation is
inherited by construction, no retraining needed. MC-17b
applies to any ML detector framework where some manifests
include host-runtime features - those features are
chain-specific by design, the train-on-A/eval-on-B
evaluation reveals which manifests transfer cross-chain,
and the per-class manifest composition encodes the
transferability story as a testable hypothesis. MC-18
applies to any cross-chain ML detection compose where
per-class transferability varies: the three-mode taxonomy
(single-category clean / multi-category causal-conjunctive
/ chain-specific-feature poisoning) is characterisable
empirically per-class via three complementary diagnostics
(train-on-A/eval-on-B from MC-17b, SHAP attribution,
feature ablation). Joint training resolves all three modes
operationally (folded-mode recovers chain-specific
manifests to 100% per-chain recall) - same architectural
pattern as MC-14's resolution of cross-class cross-fire
(one operational pattern at two boundaries).
Ablation-as-diagnostic generalises beyond cross-chain
transfer to any cross-domain ML compose where transfer
necessity diverges from intra-distribution feature
contribution. MC-19 applies to any cross-chain ML detection
framework with an attack-family taxonomy - the abstraction
holds empirically when families are anchored on
architectural-weakness equivalence rather than protocol-
mechanism similarity, and the three-pair mechanism-
similarity spectrum (same / structurally-different /
completely-different mechanisms within one family) is the
diagnostic for whether a candidate taxonomy is
mechanism-abstraction-class or implementation-class.
MC-20 applies to any ML detection framework where
production-extractor feature-surface parity to the
offline-trainer extractor is the load-bearing precondition
for live-deployment claims; the three-step proof
(numerical-equivalence on subset features →
schema-parity on full manifest → end-to-end inference on
live extractor output) is the methodology pattern. MC-21
applies to any detector cycle where pre-registration
discipline names a load-bearing falsifiable caveat in
advance, corpus expansion enables empirical testing of the
caveat, and corpus-augmented retrain closes the caveat
iteratively - the paper's iterative-leak-surface-peeling
pattern extends layered (training-cycle layer → binary-
detector layer → multi-class absorption layer). MC-22
applies to any ML deployment compose where the
training-time evaluation contract (e.g., attacker-filtered
bundle aggregation) and the production-fidelity evaluation
contract (e.g., wire-layer extractor aggregation) diverge
under operational inputs (e.g., mixed traffic); quoting
training-time numbers as production-fidelity evidence is a
methodology error. MC-23 applies to any multi-class
softmax trained without out-of-distribution exemplars in
its training distribution; expect one class manifold to
become *structurally absorptive* for OOD inputs along the
operational-shift axis, not residual. MC-24 applies to any
ML deployment under noisy / diluted production inputs:
binary-detection and multi-class-identification do not
share robustness profiles, and the right deployment policy
treats them as separable decisions with separable
trust calibration. We document
each contribution as cycle-specific evidence; reviewers may
find the incident-driven contribution pattern useful as
documented case studies parallel to §8.6's agent-discipline
contributions. The MC-10 "footnote-grade" designation
indicates a corpus-design observation worth preserving but
not load-bearing for any current substrate-paper claim;
unlike MC-1 through MC-9 and MC-11 through MC-24, it does
not generate a pre-registration discipline of its own.

# §9 Conclusion

This paper presents **iterative leak-surface peeling**: a
falsifiability-anchored methodology for ML detection of
blockchain validator infrastructure attacks. The methodology
contributes the multi-layer falsifiability framework
(numerical thresholds + structural predictions + outcome-band
composition + auditor-protocol gate, §5.2), the LOPO regime
with per-chain holdout direction load-bearing for cross-chain
claims (§5.3), and the iteration discipline whereby each
cycle's audit findings drive the next cycle's design (§5.4).
Two pillars substantiate the methodology: **Bundle v1**, an
open multi-modal capture format (§3) with a controlled-
vocabulary manifest, three landed schema-additive extensions
(D-007 → D-009 → D-020), and one adjacent decision under
deliberation (D-015); and the **chain-agnostic family
taxonomy** (§4) whose generative-not-bounding behaviour the
post-cycle IA01/IA02/IA02b classification (§4.3) and nine-chain
public-CVE scale-up (§4.6) substantiate empirically.

The technical centerpiece is the V7-narrow multi-mechanism
finding (§6): cross-chain mechanism non-transfer in this
domain is **feature-localised, not whole-feature-space**.
Three disambiguated mechanisms - lab-fidelity-mediated false
transfer (~83% of V6 Run D Sui ROC deficit), chain-asymmetric
mechanism localised to `resp.status_*_frac` +
`resp.amp_ratio_max`, and symmetric cross-chain transfer in
`resp.amp_ratio_median` - are evidence supporting the
structural finding rather than three competing hypotheses
each. The subsequent Step-11 V8 retrain scopes the §SE3
reframe to the cipher-agnostic byte-count manifest layer
(§7.2; §8.7 MC-2). The methodology produces feature-level
mechanism boundaries; the structural claim is materially
stronger than the single ROC retention number a
non-disambiguated V6 close would have produced.

V7-narrow's headline outcome is Joint C (rate-invariant
manifest layer; cross-chain mechanism claim falsified at lab
fidelity); Step-11 V1+V8 delivers Joint A at the
cipher-agnostic byte-count manifest layer (§7.2). The two
verdicts coexist coherently. §8.1 carries the
methodology-as-finding thesis canonically - the empirical
substantiation runs across the V1 → V7-narrow Step-8
leak-surface arc plus the Step-11 V1+V8 cipher-agnostic
retrain cycle, with eight closed leak surfaces (§8.5) plus
twenty-four Step-11 + Phase-1 + V10-V14 + multi-class +
cross-chain-corpus + cross-chain-LOPO + joint-training
multi-class + family-taxonomy-abstraction +
production-deployment-anchor + V15→V16-worked-example +
mixed-traffic-verification cycle methodology contributions
(§8.7), plus a footnote-grade companion observation paired
with MC-7.

The cipher-agnostic feature subset framework (§7.1) and the
Step-11 V1+V8 empirical Joint A (§7.2) ship in v1. v2 trigger
becomes V9-or-later cycles along orthogonal extension axes
- cipher-suite variation (TLS 1.2 / ECDHE-PSK / ChaCha20),
mTLS / client-cert deployments, additional-chain extension
beyond the Sui+Solana corpus, or a closure hypothesis on
the cipher-agnostic-manifest single-feature-dominance
brittleness pattern (§7.3; §8.7 MC-3). The v1/v2 split
remains a methodology demonstration: framework +
pre-registration + empirical Joint A land publicly first;
next-cycle evidence along orthogonal axes lands second;
falsification conditions for the next-cycle numbers are
public before the numbers exist.

The paper's three contributions each carry concrete
falsification clauses, stated at §1 ¶5 and substantiated in
§3.5 (format), §4.5 (taxonomy), and §5.5 (methodology). At v1
none had triggered; two of the three still have not, but the
**taxonomy clause has since fired and is recorded honestly**
(§4.5): the nine-chain scale-up classified dozens of
cross-chain primitives without extension while also adding one
new network family and a six-family economic layer - documented
family-extension events, forward-tracked under the clause
rather than elided. This is the falsifiability framing working
as designed: we document the methodology against its
conditions, and report a triggered condition as triggered, not
against asserted properties.

Open call: adopt `nr-bundle-spec` v0.1.0
([github.com/NullRabbitLabs/nr-bundle-spec][nrbundle],
MIT-licensed; published 2026-05-13) on your own data;
report when leak-surface peeling surfaces something new. The methodology-as-finding
framing means a field-tested instance - the discipline
working on a different chain's validator infrastructure,
surfacing its own failure modes, producing methodology
contributions independent of headline retention - is itself
substrate-paper-grade material. The closed-leak set grows
monotonically; the methodology's evidence is the closures.

Since v1, the field-tested instance that open call above
anticipated has begun to land: the methodology has run on a
nine-chain public-CVE corpus (§4.6), surfacing its own failure
modes - a triggered taxonomy clause - and producing methodology
contributions independent of any headline number: a
provenance-class publishability discipline and the automated
guarded pipeline (§5.6), now shipped as published models behind
a publish-guard rather than promised artefacts. The cross-chain
family-transfer question those cycles were meant to settle is,
honestly, still open (§8.2) - but it is now an open problem
stated precisely across nine chains rather than a two-chain
caveat.

[nrbundle]: https://github.com/NullRabbitLabs/nr-bundle-spec


# Appendix A - V7-narrow detailed numerical evidence

This appendix carries the per-fold ROC tables, cohen_d
landscape evolution, and SE3 per-feature single-feature ROC
table that §6 references. All numbers cite
`STEP-8-AUDIT-FINDINGS-V2.md §v6 (actual)` + `§v7-narrow
(actual)` (commit-pinned).

## A.0 - Corpus composition

The lab-fidelity corpus across V1 → V7-narrow comprises
**2,103 bundles**: 1,498 Sui (corpus_v1.0 1,092 + v1.1 240
+ v1.2 166) plus 605 Solana (solana_corpus_v1.0). The
decomposition is identical across V5, V6, and V7-narrow
(`STEP-10-DESIGN-V5.md`, `STEP-10-DESIGN-V6.md`,
`STEP-10-DESIGN-V7.md` Section A); V7-narrow's
disambiguation sub-experiments SE1/SE2/SE3 (§6.3) operate
trainer-and-feature-level on the same corpus, no cycle
delta.

| chain | versions | attack | benign | total |
|---|---|---:|---:|---:|
| sui | v1.0 + v1.1 + v1.2 | 1,031 | 467 | 1,498 |
| solana | v1.0 | 5 | 600 | 605 |
| **combined** | | **1,036** | **1,067** | **2,103** |

Sui attack bundles split across two fidelity classes: 876
at `lab` fidelity (in scope for `headline_lab_only` slice
evaluation per Step-8 design pre-registration) plus 155 at
non-lab fidelity (50 `proxy` + 105 `stub`):

| primitive | family | fidelity | bundles |
|---|---|---|---:|
| `sui_H02_state_sync_flood` | gossip_abuse | proxy | 50 |
| `sui_H03_passkey_multisig_auth` | auth_bypass | stub | 105 |
| **non-lab Sui attack subtotal** | | | **155** |

The V6 Run D headline (Table A.1) cites the
`headline_lab_only` slice with `fidelity_filter=['lab']`
(pre-registered at `STEP-8-DESIGN.md` §"Primary headline";
canonical convention carried through V5/V6/V7-narrow audit
docs). Under this slice, V6 Run D evaluates **1,948
bundles** = 1,343 Sui (876 attack + 467 benign) + 605
Solana (5 attack + 600 benign); the 155 non-lab Sui attack
bundles are excluded by fidelity-filter (not by post-hoc
quarantine, not by stratified-benign-holdout residual).

The complementary `inclusive` slice
(`fidelity_filter=['lab', 'production-captured',
'production-derived', 'proxy', 'stub']`) evaluates the full
2,103 - n_test=1,498 Sui in the hold-out-Sui direction;
results in the V6 audit doc's `inclusive` report at the
run-tag-pinned `inclusive/report.json`. The headline numbers
in this paper cite the `headline_lab_only` slice; readers
wanting the inclusive counterpart consult that report at the
pinned run-tag.

The 2,103 / 1,948 / 155 arithmetic resolves transparently:
2,103 (total corpus) = 1,498 Sui + 605 Solana = 1,948
(V6 Run D headline) + 155 (non-lab Sui attack: H02 proxy 50
+ H03 stub 105). §1's "2,103-bundle Sui + Solana corpus"
references the total project corpus; §6.1's "n_test=1343
Sui + n_test=605 Solana" references the V6 Run D
`headline_lab_only` per-chain holdout fold composition.

## Table A.1 - V6 Run A/B/C/D headline + per-chain ROC

V6 retrain four-run matrix; outcome banding per
`STEP-10-DESIGN-V6.md §C` thresholds (Sui ≥ 0.80 / Solana ≥
0.60 Joint A; Sui [0.65, 0.80) / Solana [0.50, 0.60)
Joint B; below = Joint C).

| run | direction | features | Sui ROC | Solana ROC | primary fals % |
|---|---|---:|---:|---:|---:|
| A | per-primitive (V6 baseline) | 92 (full) | 1.0000 (n=17) | 1.0000 (n=3) | 47.5 |
| B | per-primitive (RATE_INVARIANT_V2) | 13 | 1.0000 (n=17) | 1.0000 (n=3) | 0.0 |
| C | **per-chain** (full) | 92 | 0.7559 (n_test=1343) | 0.9037 (n_test=605) | 47.5 |
| **D** | **per-chain** (RATE_INVARIANT_V2) | 13 | **0.3399** (n_test=1343) | **0.5000** (n_test=605) | 0.0 |

Run D row produces the V6 Joint-C verdict: Sui-side per-chain
holdout ROC 0.3399 < 0.65 trips dimension-1 Joint C alone.
Solana-side 0.5000 sits at the B/C boundary informationally.
The headline saturation at ROC = 1.0000 in Runs A + B
(per-primitive direction) vs collapse at 0.3399 / 0.5000 in
Run D (per-chain direction) on the same 13-feature manifest
(B → D) is the load-bearing evidence for the per-chain holdout
direction methodology contribution (§5.3).

## Table A.2 - V7-narrow SE1/SE2/SE3 results

Three pre-registered disambiguation sub-experiments per
D-019. Run-tag pinning per `§v7-narrow (actual)`.

| sub-experiment | run-tag | hold-out-Sui ROC | trigger band | hypothesis verdict |
|---|---|---:|---|---|
| SE1 (`pcap.mean_packet_size` excluded; 12 features) | `step10_v7_se1_run_20260502T214310Z_seed42` | **0.6298** | [0.55, 0.65) → partial recovery | (iii) lab-fidelity-mediation **partially supported** |
| SE2 (Solana training upsampled 605 → 1343 via bootstrap; 13 features) | `step10_v7_se2_run_20260502T220513Z_seed42` | **0.3207** | < 0.55 → persist | (ii) undertraining **FALSIFIED** |
| SE3 (per-feature single-feature ROC sweep; 13 features × 2 fold directions) | `step10_v7_se3_run_20260502T222723Z_seed42` | per-feature pattern (Table A.3) | mixed: 4 anti-transfer features + most-symmetric reference | (i) chain-asymmetric mechanism **CONFIRMED at specific feature subset** |

The hypothesis verdicts compose into the multi-mechanism
finding (§6.4): hypothesis (ii) ruled out cleanly; hypothesis
(iii) partially supports lab-fidelity mediation (~83% of V6
Run D Sui ROC deficit); hypothesis (i) confirmed at feature
granularity via SE3 per-feature evidence (Table A.3).

## Table A.3 - SE3 per-feature single-feature ROC (anti-transfer evidence)

13-feature manifest under per-chain holdout; single-feature
classifier per fold direction. Anti-transfer = ROC < 0.45
on **both** fold directions, indicating systematic
label-feature relationship inversion cross-chain.

| feature | min ROC (across folds) | max ROC (across folds) | classification |
|---|---:|---:|---|
| `resp.amp_ratio_max` | 0.1834 | 0.3808 | **anti-transfer** (both folds < 0.45) |
| `resp.status_2xx_frac` | 0.2508 | 0.3333 | **anti-transfer** (both folds < 0.45) |
| `resp.status_4xx_frac` | 0.2508 | 0.3333 | **anti-transfer** (both folds < 0.45) |
| `resp.status_5xx_frac` | 0.2508 | 0.3333 | **anti-transfer** (both folds < 0.45) |
| `resp.amp_ratio_median` | 0.5820 | 0.6227 | most-symmetric (modest both directions) |
| (other 8 features) | per `§v7-narrow (actual)` Table | per same | mixed individual outcomes |

Direction-agnostic min/max framing: the SE3 TrainReport's
`sanity_floor` block emits `min_roc_auc` / `max_roc_auc` per
single-feature variant; per-fold-direction (hold-out-Sui vs
hold-out-Solana) attribution is not present in the canonical
report. The "anti-transfer" classification holds regardless of
direction - both folds below 0.45 means systematic
label-feature relationship inversion cross-chain whichever
direction is which.

The four anti-transfer features cluster: three HTTP status
fractions (`resp.status_2xx_frac` / `resp.status_4xx_frac` /
`resp.status_5xx_frac`) plus `resp.amp_ratio_max`. The HTTP
status triple shares a feature-class - output-side response-
class fractions, derived from the response status code per
RPC call - consistent with the "Sui attacks and Solana attacks
produce systematically different HTTP-status distributions"
mechanism narrative. `resp.amp_ratio_max` is byte-count-
derived (max of response/request byte ratios per RPC call);
its anti-transfer is a separate mechanism-class observation.
`resp.amp_ratio_median` (most-symmetric) provides a reference:
the most-stable rate-invariant signal cross-chain at modest
strength, neither anti-transferring nor saturating.

The cipher-agnostic boundary (§7.1) removes the three HTTP
status fractions by the body-parse-required exclusion
principle; `resp.amp_ratio_max` is byte-count-derivable and
retained in `CIPHER_AGNOSTIC_V1`. Step-11 Component 1's
empirical retention measurement tests whether the
chain-asymmetric mechanism persists in the cipher-agnostic
regime via `resp.amp_ratio_max`'s Layer-2 prediction (§7.2):
if `resp.amp_ratio_max` continues to anti-transfer cross-
chain on TLS-fronted captures, the chain-asymmetric mechanism
finding generalises to the production-fidelity tier.

## Table A.4 - cohen_d landscape evolution (V4 → V5 → V6 → V7-narrow → Step-11 V1)

Per-feature cohen_d (effect size) evolution across the
manifest progression. The Step-11 V1 column reflects the
CIPHER_AGNOSTIC_V1 8-feature subset derived after V7-narrow
from RATE_INVARIANT_V2 by the body-parse-required exclusion
principle (§7.1); CIPHER_AGNOSTIC_V1 is not V7-narrow's own
manifest. Numbers cited from `STEP-8-AUDIT-FINDINGS-V2.md`
§v4 / §v5 / §v6 / §v7-narrow audit-doc tables and
`STEP-11-AUDIT-FINDINGS.md` for the Step-11 V1 column.

| feature | V4 (Sui-fold-only, single-chain) | V5 (combined-corpus, RATE_INVARIANT_V1) | V6 (combined, RATE_INVARIANT_V2) | Step-11 V1 (CIPHER_AGNOSTIC_V1) |
|---|---:|---:|---:|---:|
| `pcap.mean_packet_size` | 1.0 (lab-fidelity-bound; KDE-overlap ~0.05) | landed in V1 | landed in V2 | retained (Layer-2 prediction §7.2) |
| `pcap.top_dst_port_fraction` | mid Sui-only | **1.000** (chain-deterministic; V5 Joint-C trigger) | dropped (V6 Section B revision) | excluded |
| `resp.status_*_frac` (3 features) | n/a (mid Sui) | retained | retained (in V2) | excluded (cipher-agnostic; SE3 anti-transfer) |
| `resp.amp_ratio_max` | mid Sui-only | retained | retained | retained (Layer-2 prediction §7.2 - anti-transfer prediction) |
| `resp.amp_ratio_median` | low Sui-only | retained | retained | retained (most-symmetric reference) |

The V4 → V5 transition surfaced the chain-deterministic port
leak (`pcap.top_dst_port_fraction`); V5 → V6 dropped 4 port
features (D-018 dec 1) producing RATE_INVARIANT_V2; V6 →
V7-narrow added per-chain holdout direction (D-018 dec 2)
producing the multi-mechanism finding; V7-narrow → CIPHER_AGNOSTIC_V1
removed 5 body-parse-required features (D-020 dec 2)
producing the 8-feature cipher-agnostic manifest. Each
transition closed a leak surface or pre-registered a
falsification dimension; the cohen_d landscape evolves
correspondingly.

## A.5 - Reproducibility commitment

Re-fetching the corpus version + re-running the trainer with
the pinned run-tag produces numerically-equivalent ROC
tables. The run-tag format `step10_v7_se{N}_run_<UTC-
timestamp>_seed{42}` carries seed + timestamp; the trainer
commits to seed-stable RNG initialisation per `lopo_v2.py`
machinery. Discrepancies reproducing the tables indicate
either (a) corpus version mismatch - re-fetch from the
canonical archive at `nr-bundles-public` (gated on Step-12
publication per D-012) or `nr-substrate` commit-pinned -
or (b) trainer-machinery non-determinism (seed-instability
bug); report at the canonical issue tracker per
`AUDITOR-PROTOCOL` cycle-close discipline.


# Appendix B - Decisions log summary (load-bearing decisions, D-001 → D-051)

This appendix summarises this paper's load-bearing
decisions in table form. Full content for each decision is
canonical at `nr-substrate/docs/DECISIONS.md` (commit-pinned
per §8.4 reproducibility); this appendix is a navigation aid
for readers tracing specific paper claims to canonical
provenance. The table is selective and non-contiguous: it lists
the decisions this paper's claims rest on (through D-051), with
the post-v1 additions D-035 (taxonomy extension) and
D-049/D-050/D-051 (held-out ladder, network-detector manifest,
guarded pipeline) folded in; intervening IDs live only in the
canonical log.

| ID | Title | Date | Status | Section |
|---|---|---|---|---|
| D-001 | 10-family taxonomy: 9 attack + 1 benign | 2026-04-23 | Active (extended by D-006) | §4.1 |
| D-002 | Chain-agnostic `family_id` + chain-specific `primitive_id` | 2026-04-23 | Active | §4.2 |
| D-003 | CaptureSession API contract | 2026-04-23 | Active | §3.1 |
| D-004 | (b)/(c) sweep-spec calibration policy | 2026-04-24 | Active (validated by Step 6 Day-1 gate) | (operational) |
| D-005 | Sweep spec template structure | 2026-04-24 | Active | (operational) |
| D-006 | Reconnaissance family scaffolded but unpopulated (10th attack family) | 2026-04-24 | Active | §4.1 |
| D-007 | `fidelity_class` enum structure (initial) | 2026-04-25 | Active (potential extension under D-015) | §3.2, §3.3 |
| D-008 | `target_authorisation` enum structure | 2026-04-25 | Active | §3.2 |
| D-009 | `vectors.parquet` 6th modality slot | 2026-04-25 | Active (slot reserved, unpopulated) | §3.1, §3.3 |
| D-010 | Step 6 option (B) prompt-budget prune (~1,090 bundles) | 2026-04-25 | Active | (operational) |
| D-011 | corpus_v1.0 archived in versioned Spaces (no object-lock) | 2026-04-26 | Active | §3.4, §8.4 |
| D-012 | Open-format / closed-corpus publication strategy | 2026-04-23 | Active (deferred to Step 12) | §3.4 |
| D-013 | Step 7 mainnet capture deferred indefinitely | 2026-04-26 | Active | §8.2 |
| D-014 | Lab reconnaissance pulled forward to parallel Step 8 | 2026-04-26 | Active | §4.1 |
| D-015 | Decomposed-provenance schema (`substrate` / `traffic_origin`) | 2026-04-26 (proposed) | **Pending review** - decision not yet taken | §3.3 (adjacent, under deliberation) |
| D-016 | Cross-chain validation deferred to Step 10, scope pre-defined | 2026-04-27 | Active | §5.4 (V4 → V5) |
| D-017 | Phase-6 V5 cross-chain LOPO design pre-registration | 2026-05-02 | Active | §5.4 (V4 → V5) |
| D-018 | Phase-8 V6 manifest revision + per-chain holdout direction (RATE_INVARIANT_V2; load-bearing for cross-chain) | 2026-05-02 | Active | §5.3, §5.4 (V5 → V6), §6.1 |
| D-019 | Phase-10 V7-narrow disambiguation sub-experiments (SE1/SE2/SE3 pre-registration) | 2026-05-02 | Closed (V7-narrow sub-experiments complete; multi-mechanism finding hardened; V7-broader does NOT fire) | §6.2, §6.3 |
| D-020 | Step-11 TLS-fidelity Component 1 pre-registration (CIPHER_AGNOSTIC_V1 boundary; lab-tls-fronted FidelityClass extension; Layer-2 structural predictions) | 2026-05-03 | Active (Step-11 V1 + V8 retrain closed; cipher-agnostic Joint A empirically validated) | §3.2 (FidelityClass extension), §7.1, §7.2 |
| D-021 | Corpus-design wiring-gap rule (principle 5) - pre-registered primitives that fail to capture due to capture-pipeline wiring (not the underlying mechanism) are corpus-design failures and must be closed at corpus level before the cycle proceeds | 2026-05-03 | Active | §5.1.1 (principle 5), §8.7 (composes with V8 cycle's MC inventory) |
| D-022 | Step-11 V8 manifest trim pre-registration (CIPHER_AGNOSTIC_V2 = CIPHER_AGNOSTIC_V1 minus `pcap.mean_packet_size`; sanity-floor extension for `resp.amp_ratio_max` per-fold decomposition) | 2026-05-04 | Active (Step-11 V8 retrain closed; Joint A by wide margin; V9 does NOT fire) | §7.2, §8.7 |
| D-023 | Step-11 V8 close + cipher-agnostic Joint A (V7-narrow §SE3 reframe scoped; cipher-agnostic-manifest single-feature-dominance brittleness as substrate-paper material per principle 4; Layer-2 §C.3-bis pre-registration miscalibration contribution) | 2026-05-04 | Closed (Step-11 V8 closes; substrate-paper drafting unblocked) | §6.4, §7.2, §8.7 |
| D-024 | Production-architecture vantage rescope: post-TLS-termination loopback (principle-1 misspecification correction; pre-engineering-posture criterion reformulation distinguished from D-021 post-engineering threshold-relaxation prohibition) | 2026-05-05 | Active (auditor verdict 2026-05-05 APPROVED WITH REFINEMENTS) | §8.3 (production deployment) |
| D-025 | Close-gate semantic-coverage rule: production-extractor close-gates verifying a low-level property (extractor numerical equivalence) must pre-register the deployment-claim-load-bearing higher-level property (model prediction-class equivalence) when the two diverge; three regime-scope conditions become mandatory pre-registration items (cardinality envelope + saturation envelope + training-distribution-coverage) | 2026-05-07 | Adopted (Phase-1 close-gate augmented; MC-8 + MC-9 + MC-10 banked) | §8.3, §8.7 (MC-8, MC-9, MC-10) |
| D-035 | Taxonomy extended with a protocol/economic (DeFi) layer: six additional families (schema-additive, `BUNDLE_VERSION` 2→3), firing the pre-registered taxonomy-generativity clause | 2026-06-18 | Active (economic families populated; the network-DoS spine is unchanged) | §1, §4.5 |
| D-049 | Held-out evaluation harness: pre-register the L0→L1→L2 real-data ladder before building it | 2026-06-26 | Active (economic-detector promotion regime, distinct from the network detector's held-out signal) | §4.6 |
| D-050 | Network detector trains on the full `network-v1` feature set (not the 7-feature amplification ablation); adds a per-fit robust-column guard to the production trainer | 2026-06-29 | Active | §4.6 |
| D-051 | Config-driven training pipeline with a standing quality + held-out-ROC gate | 2026-06-29 | Active | §5.6 |

**Decision IDs never re-number.** Superseded decisions stay
in the log with a `Status: Superseded by D-NNN` line; the
new entry gets the next free ID. Revisions of this paper
referencing decisions cite by D-NNN ID with file-path
canonical (per the agent-system-prompt §"On citing project
decisions" discipline that landed 2026-05-02 in response to
the Phase-6a confabulation incident; §8.6).

The three-pillar contribution maps onto specific decisions:

- **Methodology pillar** (§5, §6, §7, §8.3, §8.7)
  load-bearing decisions: D-002 (chain-agnostic family_id),
  D-016 (cross-chain validation deferred to Step 10), D-017
  (V5 design pre-registration), D-018 (V6 manifest revision
  + per-chain holdout direction), D-019 (V7-narrow
  disambiguation), D-021 (corpus-design wiring-gap rule;
  principle 5), D-022 (Step-11 V8 manifest trim
  pre-registration), D-023 (Step-11 V8 close +
  cipher-agnostic Joint A empirically validated), D-024
  (production-architecture vantage rescope: post-TLS-
  termination loopback), D-025 (close-gate semantic-coverage
  rule).
- **Format pillar** (§3) load-bearing decisions: D-003
  (CaptureSession API contract), D-007 (FidelityClass enum),
  D-008 (TargetAuthorisation), D-009 (vectors.parquet sixth
  modality slot), D-011 (corpus_v1.0 archival), D-012
  (publication strategy), D-020 (lab-tls-fronted FidelityClass
  extension).
- **Taxonomy pillar** (§4) load-bearing decisions: D-001
  (10-family taxonomy initial), D-006 (reconnaissance family
  scaffolded), D-014 (lab reconnaissance pulled forward).

D-015 is **adjacent under deliberation**, not load-bearing
for any current claim of this paper. The format-stability
claim (§3, §3.5) cites three landed extensions
(D-007 → D-009 → D-020); D-015 is documented as the
next-test-case for the additive-vs-breaking falsification
condition. Whichever path D-015 resolves to, the resolution
substantiates or challenges the format-stability claim
(Path A single enum value addition: substantiates additively;
Path C decomposed substrate + traffic_origin fields:
substantiates additively; Path B free-form notes: would have
challenged but was rejected on Step-5.7 strict-tightening
grounds).

Reproducibility note: this appendix's table is a navigation
aid; canonical decision content is at
`nr-substrate/docs/DECISIONS.md` with full Alternatives
considered + Decision + Rationale + Consequences + References
sections per decision. We commit the table + citation
pattern as the surface; readers tracing a specific claim
follow the D-NNN ID to canonical text.

