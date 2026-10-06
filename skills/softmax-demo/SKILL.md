---
name: softmax-demo
description: Run or resume the IDE-driven GOTA policy-development demo with separate research and policy repositories.
---

# IDE-driven GOTA demo

## Setup and resume

1. Resolve the research and policy directories as described in SOUL.md. Verify their Git origins and revisions.
2. Read research AGENTS.md, WORKING_CONTEXT.md, and policy provenance.json. Record gaps rather than inventing game bindings.
3. Use the seed's documented lifecycle checklist until native hooks have been verified. Rotate lessons on a genuinely new research session, not every chat message or reconnect.
4. Verify the supported Softmax client identity and GitHub repository access without displaying credentials. Read current command help and the live API schema before constructing requests.
5. Resolve the current GOTA league, its game manifest, accepted policy format, and evaluation contract. Do not assume the imported baseline matches the hosted game revision.

## First complete loop

1. Record the input source commit, game version, target league, objective, and bounded experiment size in the research repository.
2. Build/package the policy according to the live manifest. Game-hosted file policies use the supported file upload path; they do not require a policy Docker image.
3. Upload an inert policy version. Immediately record the returned policy/version IDs and artifact checksum in the policy VERSION_LOG.md and research record.
4. Run the smallest valid smoke experience request through the supported client/API. Record the returned request ID before waiting. Respect server-enforced budgets; never refill credits or alter limits automatically.
5. Wait for terminal status, inspect episode errors, download a replay and available policy artifacts, and record what the replay actually shows. A download alone is not inspection.
6. Read the current leaderboard and record timestamp, league, policy identities, and the relevant comparison. A successful smoke test is not evidence of leaderboard strength.
7. Commit policy code plus version provenance to a dedicated branch in rohit-gota-policy and push it. Commit the experiment report separately in rohit-optimizer.
8. Report links, source revision, upload ID, experience-request ID, episode/replay evidence, leaderboard observation, and remaining gaps in IDE chat.

## Improvements and concurrency

A winning version requires a measured comparison under the seed's evaluation discipline. Preserve failed and inconclusive experiments.
The present goal authorizes a functional demo, not indefinite spending. Do not schedule unbounded research.
If a background researcher is added, give it its own branch/checkout and one recorded experiment at a time.
The director reads its records and communicates through the IDE; never let both agents edit one checkout concurrently.
League submission remains separate from an experiment and requires explicit authorization.

## Completion evidence

Store one report linking the source commit, build checksum, upload version, experience request, completed episode,
downloaded replay checksum and inspection findings, leaderboard read, and pushed Git commit.
If any step fails, report the exact failed boundary. Do not claim end-to-end success from partial setup.
