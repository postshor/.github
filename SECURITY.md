# Security policy

This policy applies to every repository in the [PostShor organization](https://github.com/postshor) unless a repository has its own `SECURITY.md`.

## Reporting a vulnerability

Please **do not** open a public issue. Use GitHub's private vulnerability reporting: open the affected repository, go to the **Security** tab and choose **Report a vulnerability**.

We aim to acknowledge reports within 3 business days and to publish a fix or mitigation within 30 days for high-severity issues. We credit reporters unless they prefer otherwise.

## Scope

- Vulnerabilities in PostShor code, the GitHub Action, or the research tooling (for example code execution through crafted input, unsafe parsing, injection into generated reports or workflow commands).
- Incorrect security guidance: a rule, remediation or published finding that would lead users to a *less* secure configuration.

Missed detections, false positives and data questions are ordinary issues; please open a normal issue in the relevant repository.
