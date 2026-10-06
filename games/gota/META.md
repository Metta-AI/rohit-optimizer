# GOTA field snapshot — 2026-10-06

This onboarding snapshot is based on the live Competition division standings read on 2026-10-06 UTC. GOTA is a ten-player 5v5 BASIC game; Emmett's Glory is winner-only XP per simulated minute, while the board separately reports OpenSkill MMR and mean game score. Do not compare rating to mean Glory as if they were the same metric.

## Top of board

| Rank | Player / policy | MMR | Mean game score | Rounds |
|---:|---|---:|---:|---:|
| 1 | a-aron | 29.97 | 65.42 | 33 |
| 2 | Aaron | 26.30 | 43.59 | 44 |
| 3 | BeWellBot / BeWellBot-Arena:v58 | 25.61 | 42.64 | 44 |
| 4 | richard / richard-gods-of-the-arena:v340 | 24.55 | 28.63 | 44 |
| 5 | Andre von Auto / khors:v231 | 23.50 | 33.11 | 44 |
| 6 | cognito053 / neuralhub-91708d976414ab4f:v1 | 22.97 | 10.99 | 44 |
| 7 | Andre von Houck / fly_brain:v1 | 22.33 | 32.72 | 44 |
| 8 | relh / relh-gods-of-the-arena:v386 | 22.26 | 32.62 | 44 |
| 9 | ygo373802 / neuralhub-ab8eb2ecc5e2ff38:v1 | 21.50 | 9.90 | 44 |
| 10 | sharon / neuralhub-476ceffbbecfc1e5:v1 | 21.16 | 9.40 | 44 |

Our current champion membership was `arena-crossbow-carry:v33`, rank 40 in the same read (MMR 13.20, mean game score 1.10, 43 rounds). The board is live and standings changed between adjacent queries during the read, so these values are a dated snapshot rather than stable current rankings.

## Mechanism confidence and next bet

This read establishes the competitive gap but does not explain how leaders play; no rival replay was decoded in this onboarding pass. The reference base policy already supports drafting, lane farming, last hits, structure pushing, spells, threat responses, healing, shopping, travel and buyback. The candidate test therefore adjusts one existing visible-hero target weight (+60 to +100) rather than claiming to copy an inferred rival mechanic. Its outcome is a functional/directional smoke only.
