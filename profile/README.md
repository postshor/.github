<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/postshor/.github/main/brand/logo/postshor-lockup-on-dark.svg">
    <img src="https://raw.githubusercontent.com/postshor/.github/main/brand/logo/postshor-lockup-on-light.svg" alt="PostShor" width="340">
  </picture>
</p>

<p align="center"><b>Open tools and standards for the move to post-quantum cryptography.</b></p>

---

Quantum computers running Shor's algorithm will break RSA and elliptic-curve cryptography. The replacements are already standardized: ML-KEM, ML-DSA and SLH-DSA (FIPS 203/204/205). Governments have set the deadlines: deprecate by 2030, disallow by 2035. What most organisations lack is the first step: **knowing where their quantum-vulnerable cryptography is, and what to fix first.**

PostShor builds that step in the open.

### Projects

| | |
|---|---|
| [**postshor**](https://github.com/postshor/postshor) | Scanner for quantum-vulnerable cryptography in source code (10 languages), dependencies, certificates, keys, server configs, infrastructure-as-code and live TLS endpoints. Produces a migration plan, a CycloneDX CBOM, SARIF and a Quantum Readiness Score. |
| [**Quantum Readiness Score (QRS)**](https://github.com/postshor/postshor/blob/main/docs/spec/qrs-v1.md) | An open, vendor-neutral specification for measuring post-quantum readiness, licensed CC BY 4.0. Draft for public comment. |

### Try it

```
pip install postshor
postshor scan .
postshor tls example.com
```

### Get involved

- Feedback on the QRS specification is welcome in [Discussions](https://github.com/postshor/postshor/discussions).
- New detection rules are the most valuable contribution; see the [contributing guide](https://github.com/postshor/postshor/blob/main/CONTRIBUTING.md).
- Report vulnerabilities privately through [GitHub security advisories](https://github.com/postshor/postshor/security/advisories/new).

<sub>PostShor is an independent open-source project, not affiliated with Peter Shor. · [Brand guidelines](https://github.com/postshor/.github/tree/main/brand)</sub>
