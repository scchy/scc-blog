---
title: 14 Robot Skills in 5 Days on a Single GPU: Queued RL Training for a Bipedal Robot Duck
excerpt: Training a 14-skill policy library for MicroDuck, a bipedal robot duck (15× XL330 servos, 50Hz), with mjlab (MuJoCo Warp) + PPO on a single GPU: serial training queues, OOM downgrade-and-retry, NaN-safe patches, and a different reward-design philosophy per skill. All skill rollout GIFs included.
publishDate: 2026-09-14
isFeatured: false
tags:
  - reinforcement learning
  - robotics
  - ppo
  - mujoco
seo:
  title: 14 Robot Skills in 5 Days on a Single GPU: Queued RL Training for a Bipedal Robot Duck
  description: A full retrospective on training 14 skills for the MicroDuck bipedal robot duck with mjlab + PPO on one GPU — training queues, OOM/NaN failure handling, reward design patterns, and rollout GIFs of every skill.
  pageType: article
---

## Project Overview

[MicroDuck](https://github.com/pollen-robotics/microduck_rl) is a bipedal robot duck: 15 XL330 servos, a Radxa ZERO 3W compute board, and a 50Hz control loop. The goal: train a full multi-skill policy library — walking, skating, standing up, rolling, kicking, picking up objects, sitting/standing — ending with **14/14 skills trained** and exported as ONNX policies for deployment.

The stack:

- **Simulation**: [mjlab](https://github.com/mujocoab/mjlab) (MuJoCo with the Warp GPU-parallel backend)
- **Algorithm**: PPO (rsl_rl), 4096 envs on flat terrain, reduced to 2048 on rough terrain
- **Hardware**: a single GPU, serial task queue, ~5 days total wall clock

## Skill Matrix and Results

| Skill | Flat | Rough | Iterations |
|------|------|-------|-----------|
| Velocity (walking) | ✅ | ✅ | 25k |
| Velocity-Rollers (skating) | ✅ | — | 25k |
| Velocity-Swizzle | ✅ | — | 25k |
| VelStand (walk + recovery) | ✅ | ✅ | 10k |
| StandUp | ✅ | ✅ | 7.5k |
| GroundPick | ✅ | ✅ | 10k |
| BallKick | ✅ | — | 5k |
| Roulade (rolling) | ✅ | — | 7.5k |
| SitStand | ✅ | ✅ | 7.5k |

All skills in one animated grid:

![MicroDuck 12-skill grid](/scc-blog/gifs/microduck/MicroDuck_All12_Grid_small.gif)

## Success Evaluation: Rollout GIFs of Every Skill

A good loss curve does not mean a good gait — **rollout GIFs are the best acceptance test**. Below are single-env rollouts of all 14 skills (300 frames each, converted with ffmpeg palettegen/paletteuse).

### Locomotion family

Velocity-Flat (standard walking):

![Velocity Flat](/scc-blog/gifs/microduck/Mjlab-Velocity-Flat-MicroDuck.gif)

Velocity-Rough (rough-terrain walking; passed after OOM downgrade to 2048 envs):

![Velocity Rough](/scc-blog/gifs/microduck/Mjlab-Velocity-Rough-MicroDuck.gif)

Velocity-Rollers (skating with wheels on the feet):

![Velocity Rollers](/scc-blog/gifs/microduck/Mjlab-Velocity-Flat-MicroDuck-Rollers.gif)

Velocity-Swizzle:

![Velocity Swizzle](/scc-blog/gifs/microduck/Mjlab-Velocity-Swizzle-MicroDuck.gif)

### Recovery family

VelStand-Flat (walking + fall recovery, one policy):

![VelStand Flat](/scc-blog/gifs/microduck/Mjlab-VelStand-Flat-MicroDuck.gif)

VelStand-Rough:

![VelStand Rough](/scc-blog/gifs/microduck/Mjlab-VelStand-Rough-MicroDuck.gif)

StandUp-Flat (stands up on the first attempt):

![StandUp Flat](/scc-blog/gifs/microduck/Mjlab-StandUp-Flat-MicroDuck.gif)

StandUp-Rough:

![StandUp Rough](/scc-blog/gifs/microduck/Mjlab-StandUp-Rough-MicroDuck.gif)

### Trick family

Roulade (rolling; the "textbook" run-2 reward rewrite):

![Roulade Flat](/scc-blog/gifs/microduck/Mjlab-Roulade-Flat-MicroDuck.gif)

SitStand-Flat (sit↔stand switching with posture-conditioned moving targets):

![SitStand Flat](/scc-blog/gifs/microduck/Mjlab-SitStand-Flat-MicroDuck.gif)

SitStand-Rough (passed after the NaN-safe patch):

![SitStand Rough](/scc-blog/gifs/microduck/Mjlab-SitStand-Rough-MicroDuck.gif)

### Task family

BallKick-Flat (blind kick — the actor can't see the ball, the critic can):

![BallKick Flat](/scc-blog/gifs/microduck/Mjlab-BallKick-Flat-MicroDuck.gif)

GroundPick-Flat (picking up objects via task-space definition instead of pose engineering):

![GroundPick Flat](/scc-blog/gifs/microduck/Mjlab-GroundPick-Flat-MicroDuck.gif)

## Engineering: Three Tricks for Long Single-GPU Training Runs

### 1. Serial queue + .done markers

Task lists defined in bash associative arrays, executed strictly serially to avoid GPU contention. Completed tasks get a `.done` marker file; failures (rc≠0) get **no marker** and flow into the retry queue. The simplest reliable scheme for unattended single-GPU training.

### 2. OOM downgrade-and-retry

The first round of rough-terrain tasks died en masse within seconds — 4096 envs with rough terrain blew up VRAM. The fix was blunt: drop all rough tasks to **2048 envs** and rerun. All passed.

Lesson: **rougher terrain → more observation/physics state per env → budget your env count**. Rule of thumb: ~70% envs for rough terrain.

### 3. OOM and NaN are two different failure classes

- **OOM**: dies within tens of seconds with rc=1; read the tail of the log
- **NaN**: dies after minutes-to-hours with `ValueError: The observation group 'critic' contains NaN values`; you need the wandb curves to locate the divergence source

The general NaN fix is a NaN-safe patch: NaN guards on reward/advantage + a `nan_state` termination flag (monitored as `Episode_Termination/nan_state` in wandb). Both SitStand-Rough and GroundPick-Rough passed with it.

## Reward Design: An Economics Problem Per Skill

The most interesting part of the project — nine completely different reward-design philosophies behind 14 skills.

### General principles

- **Task reward magnitude ≈ 10**, so shared regularization terms act with the same relative strength across skills
- **DR/noise/regularization recipes are inherited from the velocity baseline**; each skill only adds its task layer — port proven recipes, don't reinvent
- **Goal terms give gradient; regularizers only collect tax**: in large-motion skills, motion-damping terms (body_ang_vel, impact penalties) are crushed to near zero during exploration and introduced later via curriculum — taxing attempts kills discovery outright
- **Potential-based progress rewards**: pay only for increments past "furthest progress so far"; standing still earns nothing — inherently farming-proof

### A few favorite cases

**Velocity: deliberately harsh upright.** At weight 1.0, a 4° forward lean costs only ~0.05 per step — effectively free — and the converged gait leaned 2–4° forward, with 2/3 of pushes tipping it forward. Tightened to weight 2.0 while leaving margin for transient leans. Also, spin-in-place commands got their own sampling bucket: 15% of envs get lin=0 + |ang|∈[0.4,1.0] (under independent uniform sampling, spin-on-the-spot is only ~2% of data — unlearnable).

**StandUp: escape-basin design.** Three-layer height reward: dense (broad gradient) + sharp (a 0.36→1.0 jump in the last centimeter) + L1 (breaks the static basin: sitting still is net negative). The real unlock was mid-roll spawn reverse curriculum — starting episodes mid-flip splits an unlearnable whole into a proven-learnable half.

**Roulade: run-1 learned violent breakdance.** Rewarding "accumulate 2π as fast as possible" with no contact constraint — the policy was genuinely optimal under that reward. Run-2: support gating (only ground-contact rotation counts) + landing reward gated on roll frontier ≥260° + progress pay rate capped at 3 rad/s + overspeed penalties. Style is the scarce resource.

**BallKick: asymmetric actor-critic.** No ball perception on the real robot (the operator aims), so the actor is ball-blind with robustness from ±2cm ball-placement domain randomization; but the critic sees the ball — value front-runs the kick payoff and helps the actor learn.

**GroundPick: don't define the DOWN pose.** Instead, three balanced forces — mouth-near-ground attraction + strong contact prohibition + vertical orientation — yield a mouth hovering at ground level. Task-space definition over pose engineering.

**VelStand: three audit iterations.** Recovery layer gated on "actually fell" (contributes exactly zero during clean walking); a unified, reachable "recovered" definition (tilt<25° and z>0.09); potential-based Δz progress for the last mile. Every round was a fight with reward-economics loopholes.

## PPO Parameter Cheat Sheet

| Parameter | Value |
|------|------|
| Network | MLP 512-256-128, ELU (symmetric actor/critic) |
| learning_rate | 1e-3, **adaptive** (anchored on desired_kl=0.01) |
| gamma / lam | 0.99 / 0.95 |
| clip_param | 0.2 |
| num_steps_per_env | 24 |
| epochs / mini_batches | 5 / 4 |
| envs | Flat 4096 / Rough 2048 |
| max_iterations | 5k–25k per task |

The core stabilizer is **adaptive LR + desired_kl=0.01**. No RNN, no CNN — plain MLP with obs normalization, entirely sufficient for 50Hz servo control.

## Key Lessons

1. **Queue + .done markers + downgrade-retry** is the simplest reliable scheme for unattended single-GPU training
2. **OOM and NaN are different failure classes**: OOM dies fast, check the log tail; NaN dies young, trace the divergence in wandb curves
3. **Rollout GIFs are the best acceptance test** — a pretty loss curve is not a pretty gait
4. VRAM budgeting: ~70% envs for rough-terrain tasks is the empirical starting point
5. Reward design is economics: for every term, ask "will this tax kill the exploration you're trying to encourage?"

---

Training code is based on pollen-robotics/microduck_rl, simulation via mjlab (MuJoCo Warp), training framework rsl_rl. Happy to chat 🐾
