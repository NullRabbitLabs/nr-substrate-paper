# Iterative leak-surface peeling

*A falsifiability-anchored methodology for ML detection of
blockchain validator infrastructure attacks.*

**Author**: Simon Morley, NullRabbit

**Status**: working draft (2026-05-06). Updates land directly in
`paper.md`; the v1 preprint ships when arXiv submission lands.

---

## Abstract

Public-internet-reachable blockchain validator infrastructure is an
inviting target for asymmetric resource-consumption attacks;
validator-DoS findings have accumulated steadily across Sui, Solana,
Ethereum, Aptos, and Cosmos-family chains through 2024–2026
coordinated-disclosure pipelines. Detection that survives the
cleartext / TLS-fronted boundary, the cross-chain transfer, and the
lab / mainnet fidelity tier is non-optional for operators standing up
monitoring on this threat surface. Yet ML-based detection of these
attacks routinely ships with median ROC-AUC at or near 1.000 across
cross-validation folds, which on audit prove artefactual rather than
reflecting underlying network behaviour
[sommer2010outside, arp2022dosdonts]. Our V1 trainer's first
TrainReport against an initial 1,092-bundle Sui validator-DoS corpus
is a fresh data point in this pattern: ROC = 1.000 across all 17
leave-one-primitive-out folds, driven by random-Gaussian-feature
ROC = 1.000 (LOPO benign-holdout contamination) and `resp.count`
ROC = 1.000 (capture-pipeline co-linearity).

This paper presents **iterative leak-surface peeling**: a methodology
that pre-registers numerical thresholds, structural predictions, and
outcome-band composition rules before headline numbers land, then
surfaces and closes its own failure modes through multi-layer
falsifiability discriminators and audit-driven iteration. Across
V1 → V7-narrow on a 2,103-bundle Sui+Solana corpus, the methodology
has surfaced and closed eight distinct leak surfaces in sequence. Two
open pillars substantiate the methodology: **Bundle v1**, a
multi-modal capture format with controlled-vocabulary provenance
fields, demonstrated through three landed schema-additive extensions;
and a **chain-agnostic family taxonomy** of ten attack families plus
benign that classifies post-cycle attacks without extension.

The technical centerpiece is the V7-narrow multi-mechanism finding:
cross-chain mechanism non-transfer in this domain is
**feature-localised, not whole-feature-space**. The headline outcome
at the V7-narrow evaluation gate is Joint C (cross-chain mechanism
claim at the rate-invariant 13-feature manifest layer falsified at
lab fidelity). Subsequent Step-11 V1 + V8 retrain cycles deliver
Joint A on the cipher-agnostic claim: 100% retention vs the
pre-registered Step-11 V1 cleartext baseline across both chains in
both LOPO regimes (Step-11 V1 retrain), and 124–191% retention
post-trim (Step-11 V8 retrain) once the V7-narrow §SE3-affected
`pcap.mean_packet_size` distribution-mismatch source is removed from
the manifest. The encryption boundary itself does not introduce
additional accuracy degradation. The methodology contributions
persist independently of any single evaluation-gate outcome; the v2
trigger becomes V9-or-later cycles along orthogonal axes
(cipher-suite variation, mTLS, additional chains).

## Repo layout

- `paper.md` - the working preprint, canonical source. Updates land
  here.
- `bibliography.bib` - references (BibTeX).
- `scripts/check_consistency.py` - automated consistency checker
  (see below).
- `LICENSE-TEXT.md` - CC-BY-4.0 (paper text + figures + tables).
- `LICENSE-CODE.md` - MIT (any scripts / build tooling).

## Consistency checking

Run the consistency checker before each commit:

```sh
python3 scripts/check_consistency.py
```

It encodes the recurring inconsistency patterns surfaced in manual
review cycles - em-dashes (paper convention is hyphen), self-
references (`the substrate paper` → `this paper`), stale state
phrases (`Joint Outcome`, `in flight`), forbidden absolute paths,
MC-N coverage (definitions ↔ references), D-NNN coverage (in-text
↔ Appendix B table), Appendix B title range, bibliography
citation/definition cross-check, count-phrase consistency (e.g.,
"eleven contributions" matching the actual MC count), §5.1.1
principle count, §8.6 upgrade-incident count, mutually-exclusive
state claims (e.g., `nr-bundle-spec` "private until X" vs
"published Y"), and §-cross-reference resolution.

Exit code 0 if all checks pass, 1 if any FAIL, 2 on usage error.
Stdlib only; no external dependencies.

## Companion artefacts

- **`nr-bundle-spec` v0.1.0** - open format specification of
  Bundle v1 (`github.com/NullRabbitLabs/nr-bundle-spec`,
  MIT-licensed; private repo until 2026-06-05 pending
  coordinated-disclosure window closure on Sui F10/F14 + Solana F10,
  public after). JSON Schema + Python and Rust reference parsers + 5
  example bundles + CI for schema regen and cross-language
  consistency.
- **`nr-bundles-public`** (forthcoming, HuggingFace) - curated
  20–50 sample bundles spanning multiple primitives + chains.

## Sister paper

[**Earned Autonomy**](https://doi.org/10.5281/zenodo.18406828)
(Zenodo DOI `10.5281/zenodo.18406828`) - architectural-layer
companion for production deployment. This paper is the data-layer
companion; standalone-readable, cross-references where load-bearing.

## Citing

A formal arXiv preprint identifier lands at v1 ship. Until then, cite
this working draft as:

```bibtex
@misc{morley2026leaksurfacepeeling,
  author = {Morley, Simon},
  title  = {Iterative leak-surface peeling: a falsifiability-anchored
            methodology for {ML} detection of blockchain validator
            infrastructure attacks},
  year   = {2026},
  note   = {Working draft, 2026-05-06.
            \url{https://github.com/NullRabbitLabs/nr-substrate-paper}}
}
```

## License

Dual-licensed:

- **Paper text + figures + tables**: CC-BY-4.0
  ([`LICENSE-TEXT.md`](LICENSE-TEXT.md)).
- **Code, scripts, build tooling**: MIT
  ([`LICENSE-CODE.md`](LICENSE-CODE.md)).
