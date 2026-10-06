# Working context

## Current objective

Complete one bounded, local-only GOTA policy iteration using the official fixture under /opt/data/local-gota, source Metta-AI/polyworld commit 150119c89b3535eb353af75c5bf5bc22b36e31f2. Use the provisioned policy checkout /opt/data/workspaces/policy and research checkout /opt/data/workspaces/research; local player ply_762bc195-556b-4f65-aed3-c17cc4afe660. Initialize from the supplied baseline, make one hypothesized policy change, run baseline then candidate with the same seed and nine baseline opponents on ten seats, inspect results/logs/replay metadata, record exact config and hashes, then commit and push both repositories on dedicated branches. At most two local matches. No hosted actions, uploads, league/credit changes, or credential reads.

## Active games

GOTA local iteration only. Policy repository: https://github.com/djbhindi/softmax-policy-762bc195-556b-4f65-aed3-c17cc4afe660. Official fixture provenance: Metta-AI/polyworld commit 150119c89b3535eb353af75c5bf5bc22b36e31f2.

## Open threads

Finish the authorized baseline/candidate local comparison and publish the policy and research report on their dedicated agent branches. Stop after this one iteration; local evidence is functional/behavioral only, not a hosted strength or champion claim.

## Identity

Softmax/local player: ply_762bc195-556b-4f65-aed3-c17cc4afe660. Runtime objective overrides prior player and instance identifiers.

## Harness wiring

Not installed yet. Follow harness/README.md and harness/other/README.md.
Use native Hermes hooks where supported; record verified wiring rather than assuming hooks run.
The seed's documented checklist fallback is available if no compatible hook exists.

## Policy ownership

Policy source and VERSION_LOG.md belong to the separate policy repository.
Research records belong here and cite immutable policy commit IDs.
Multiple agents will use independent checkouts and branches. Only one agent is in scope now.
