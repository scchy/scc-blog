---
title: "My Personal Knowledge Management Loop: Obsidian + Blog + DeepTutor"
excerpt: "I strung collect, process, output, and review into a sustainable loop: Obsidian for processing, Blog for output, and DeepTutor for review and tutoring. Here's the architecture, implementation details, and pitfalls I hit."
publishDate: 2026-08-06
isFeatured: false
tags:
  - productivity
  - knowledge-management
  - obsidian
  - workflow
  - agent
seo:
  title: "My Personal Knowledge Management Loop: Obsidian + Blog + DeepTutor"
  description: Building a personal knowledge management loop with Obsidian for processing, Blog for output, and DeepTutor for review. Architecture, implementation, and lessons learned.
  pageType: article
---

> The goal of knowledge management isn't "store more," it's "use it well." This post shares how I strung collecting, processing, output, and reviewing into a **sustainable loop**.

---

## Why a loop

As a developer, I've been writing blogs, building projects, and learning new things. But for a long time, my knowledge management was **fragmented**:

- Blog posts were written and never revisited
- Things I learned were scattered everywhere, hard to find when needed
- Output and input were disconnected—writing blogs felt like squeezing toothpaste, not natural flow

The root cause: **my workflow was inverted**.

I spent most of my energy directly on writing (output) while skipping the "collect → process" stages. The result: my blog became a junk drawer where everything got stuffed, instead of a finished-goods warehouse for things I'd actually thought through.

The loop I built with three tools finally solved this.

---

## The loop at a glance

```
Obsidian (local: collect + process)
   │  distill into articles when mature
   ▼
Blog (output: site + community distribution)
   │  one-click sync script
   ▼
DeepTutor (server: RAG Q&A + personal mentor review)
   │  deeper review, new understanding
   ▼
(feed back into Obsidian, loop closes)
```

Each of the three components has a distinct role:

| Component | Role | Core value |
|:---|:---|:---|
| **Obsidian** | Processing workshop | Collect fragments, recombine with links, organize via PARA, build reusable assets |
| **Blog** | Finished-goods warehouse | Publish thought-through content, SEO accumulation, multi-platform distribution |
| **DeepTutor** | Review coach | RAG Q&A grounded in your notes, mentor persona guides deeper understanding |

---

## Ring 1: Obsidian — the processing workshop

Obsidian is the **starting point and foundation** of the whole loop. I use the classic **PARA structure**:

```
KnowledgeBase/
├── 0-Inbox        (fragments land here first)
├── 1-Projects     (ongoing work)
├── 2-Areas        (long-term responsibility areas)
├── 3-Resources    (permanent notes, reusable assets)
├── 4-Archive      (finished content)
└── _templates
```

**The core mechanic is bidirectional links.** For example, one of my Agent retrospective notes links to 4 permanent notes (Agent skeleton, SSE streaming, context compaction, tool safety). In the graph view, knowledge isn't isolated files—it's a **web**.

Key principle: **Obsidian stores "processed" assets, not raw copies.** From a 70KB blog post, I distilled 5 core sentences plus 4 structured notes. That's real sedimentation.

---

## Ring 2: Blog — the finished-goods warehouse

The Blog receives content that's **already been thought through**. My blog is built with Astro (see [this post](first-post)) and uses a **dual-track content strategy**:

- **Main hub**: my site (Astro + GitHub Pages), for SEO and long-term content
- **Distribution channels**: Dev.to, Juejin, for immediate reach

All distributed articles carry a `canonical_url` pointing back to the main site, avoiding duplicate-content penalties and funneling SEO weight to the hub.

**Key shift**: I went from "write whatever comes to mind" to "distill into an article once it's matured in Obsidian." Writing went from squeezing toothpaste to a natural overflow.

---

## Ring 3: DeepTutor — the review coach

This is the ring that actually keeps the loop **spinning**—**review**.

I upload my Obsidian knowledge base to a DeepTutor server via its API and index it with **llamaindex** for RAG retrieval. DeepTutor can then answer questions grounded in my notes instead of speaking in generalities.

More importantly, I configured a **mentor persona** for it, whose prompt specifies:
- Prioritize referencing already-sedimented content in the knowledge base, connecting new questions to existing knowledge
- Socratic guidance, but give direct answers when asked
- Tie back to my real experience (knowing I've read 2000 lines of Agent code and which pitfalls I hit)

So every question I ask in DeepTutor becomes a **deeper review grounded in existing knowledge**, and the new understanding feeds back into Obsidian.

---

## Implementation details

### Sync: Obsidian → DeepTutor

I wrote a sync script with this core logic:

```
Detect local note changes (MD5 hash comparison)
   ├─ no change → skip
   └─ changed → delete old KB → re-upload all → wait for index → save state
```

Now I just write in Obsidian, run the script, and DeepTutor's knowledge base updates.

### DeepTutor integration notes

- **Knowledge base**: upload markdown notes, index with llamaindex (works out of the box, no API key)
- **Persona**: custom "personal mentor" persona that guides based on the knowledge base
- **Flow**: login for token → upload files → poll until index is ready

---

## Pitfalls I hit

1. **Inverted workflow**: the biggest one. I used to write directly, skipping sedimentation, so content never formed a system. Build the Obsidian foundation first, then talk about output.
2. **Opening the wrong vault**: Obsidian defaulted to an empty vault, making me think the knowledge base was empty. Point Obsidian's default path at the real knowledge base directory.
3. **Server can't read local files**: DeepTutor runs on a server and can't see local paths. Solution: upload files via API instead of having the server read local directories directly.

---

## What this loop changed for me

1. **Knowledge went from dead to alive**: notes connect into a web via links, no longer isolated files
2. **Output went from squeezing to natural**: once matured in Obsidian, Blog is just distillation
3. **Review went from occasional to daily**: DeepTutor turns every question into a deepening

The core takeaway: **knowledge management isn't hoarding, it's flow.** Collect, process, output, review—every step makes knowledge more useful.

---

## Next steps

- Wrap the sync script into a one-command shortcut
- Keep iterating on DeepTutor's mentor persona so it understands my knowledge system better
- Keep writing, and let the loop spin on its own

If you're doing personal knowledge management too, I'd love to hear how you've structured your system.
