---
title: "Building a Pi Agent from Scratch (7-Day Retrospective)"
excerpt: "I spent 7 days building a Pi Agent from scratch and understood the universal skeleton behind every agent: loop + tools + context management."
publishDate: 2026-08-06
isFeatured: false
tags:
  - llm
  - agent
  - aiengineering
  - contextmanagement
seo:
  title: "Building a Pi Agent from Scratch (7-Day Retrospective)"
  description: "A module-by-module retrospective of a hand-written Pi Agent, distilling the universal agent skeleton."
  pageType: article
---

> I spent 7 days building a Pi Agent from scratch and understood the universal skeleton behind every agent:
> **loop + tools + context management**.

Full implementation: [mini-PI-Agent](https://github.com/scchy/My_Learn/tree/master/PI_Agent/pi_agent)

---

## Why I Wrote This Post

- **Motivation**: I didn't want to remain just an API caller. I wanted to truly understand the internals of an Agent, so I could do better Agent development and RL-related research.
- **Outcome**: ~2,000 lines of code, 205 unit tests passing.
- **Audience**: Developers who want to understand how Agents work under the hood.
- **Preview**: Each module = one engineering problem + my solution, ending with a distilled universal skeleton.

---

## Big Picture: Agent System Architecture

Think of an Agent as a computer: LLM + Tools = CPU, recent conversation = RAM, compressed summaries = virtual memory, session tree = disk, CLI = operating system. Once these components are wired together into a reusable system, you can run different apps on top — coding, research, data analysis. Swap the app without changing the skeleton: that's the essence of generalizing to any Agent.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐  │
│   │   OS / CLI                                                       │  │
│   │   ── Agent terms: Harness / Agent loop scheduler               │  │
│   │   Scheduling · Config precedence · Interaction/steering          │  │
│   │   Meta-commands (/compact /status)                             │  │
│   └─────────────────────────────┬──────────────────────────────────┘  │
│                                 │ Assemble into a reusable system       │
│                                 ▼                                      │
│   ┌────────────────────────────────────────────────────────────────┐  │
│   │                                                              │  │
│   │   ┌─────────────── Agent Loop (the heart) ────────────────┐ │  │
│   │   │                                                       │ │  │
│   │   │    ┌──────────┐      ┌──────────────┐      ┌────────┐ │ │  │
│   │   │    │ Reason   │─────►│   Act         │─────►│Observe │ │ │  │
│   │   │    │ (LLM)    │      │ (call Tools)  │      │(result)│ │ │  │
│   │   │    └────┬─────┘      └──────┬───────┘      └───┬────┘ │ │  │
│   │   │         │                   │                  │      │ │  │
│   │   │         └───────────────────┴──────────────────┘      │ │  │
│   │   │                     ▲ Loop until done                 │ │  │
│   │   │    (no tool_call / max_turns / user interrupt)        │ │  │
│   │   └───────────────────────────────────────────────────────┘ │  │
│   │                                                              │  │
│   │   ┌────────────────────────┐   ┌──────────────────────────┐  │  │
│   │   │  CPU (compute)         │   │  RAM (working memory)    │  │  │
│   │   │  ── Agent: LLM + Tools │◄─►│  ── Agent: Context      │  │  │
│   │   │  Reasoner + toolset    │   │  Recent msgs + state     │  │  │
│   │   └────────────────────────┘   └────────────┬─────────────┘  │  │
│   │                                             │ Swap out when full│  │
│   │                                             ▼                │  │
│   │   ┌──────────────────────────────────────────────────────┐  │  │
│   │   │  Virtual memory (swap)                             │  │  │
│   │   │  ── Agent: Compaction / retrieval                  │  │  │
│   │   │  Compressed summaries + retrieval (swap in/out)  │  │  │
│   │   └──────────────────────────────┬───────────────────────┘  │  │
│   │                                  │ Persist                  │  │
│   │   ┌──────────────────────────────▼───────────────────────┐  │  │
│   │   │  Device (persistent storage)                         │  │  │
│   │   │  ── Agent: Session / file tracking                   │  │  │
│   │   │  Session tree / JSONL / file tracking                │  │  │
│   │   └─────────────────────────────────────────────────────┘  │  │
│   │                                                              │  │
│   └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐  │
│   │   APP (concrete tasks running on the system)                   │  │
│   │   Coding · Research · Data analysis · File ops ...             │  │
│   │   ── Swap the app, keep the skeleton ──                        │  │
│   └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

**Mapping table**:

| Computer | Agent | Role |
|:---|:---|:---|
| CPU | LLM + Tools | Compute unit |
| RAM | Context | Working memory |
| Virtual memory | Compaction / retrieval | Swap in/out |
| Device | Session / file tracking | Persistent storage |
| OS | Harness / CLI | Scheduling + config + interaction |
| App | Concrete Agent app | Tasks running on the system |

---

## Module 1: LLM Client

### Problem

How do you stably call an OpenAI Chat Completions-style streaming LLM API?

**The hard part**: Streaming doesn't return the full response at once; it pushes chunks as they are generated. Network jitter and rate limits (429) can interrupt at any moment. Stable calling = correct SSE parsing + graceful failure handling.

**Module role**: The LLM client is a **generic layer** — every Agent calls an LLM. Keep only "mechanics" here (how to parse, retry, estimate tokens), not "policy" (when to compress, how much to keep). Policy belongs to the Agent-specific context manager.

### Solution

- [x] SSE streaming parse (`async for`, line by line)
  - `data: <JSON>` + blank-line separators
  - `[DONE]` marks the end of the stream
  - `delta` is incremental, not a full snapshot

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    LLM server (e.g. OpenAI API)                      │
│                                                                     │
│   Generated text: "The weather is nice, let's" → "go to the park"    │
│                                                                     │
│   Server cuts content into chunks and pushes them over SSE:          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP response stream (SSE)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Raw SSE byte stream (network layer)              │
│                                                                     │
│   data: {"choices":[{"delta":{"content":"The"}}]}                    │
│                                                                     │
│   data: {"choices":[{"delta":{"content":" weather"}}]}                │
│                                                                     │
│   data: {"choices":[{"delta":{"content":" is"}}]}                    │
│                                                                     │
│   data: {"choices":[{"delta":{"content":" nice"}}]}                  │
│                                                                     │
│   data: {"choices":[{"delta":{"content":","}}]}                     │
│                                                                     │
│   data: {"choices":[{"delta":{"content":" let's"}}]}                 │
│                                                                     │
│   data: {"choices":[{"delta":{"content":" go"}}]}                   │
│                                                                     │
│   data: {"choices":[{"delta":{"content":" to"}}]}                   │
│                                                                     │
│   data: {"choices":[{"delta":{"content":" the"}}]}                  │
│                                                                     │
│   data: {"choices":[{"delta":{"content":" park"}}]}                  │
│                                                                     │
│   data: [DONE]                                                      │
│                                                                     │
│   (Lines separated by \n\n; data: prefix + JSON body)                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Read line by line (async for)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Client parse (llm.py)                            │
│                                                                     │
│   async for line in response:          # read SSE line by line      │
│       if line.startswith("data:"):     # only handle data: lines    │
│           data = line[5:].strip()      # strip "data:" prefix        │
│           if data == "[DONE]":         # stream end marker           │
│               break                    # stop the loop               │
│           chunk = json.loads(data)     # parse JSON                │
│           text = chunk["choices"][0]["delta"]["content"]             │
│           yield text                   # emit text fragment          │
│                                                                     │
│   Emitted sequence: "The" → " weather" → " is" → ... → " park"     │
│                                                                     │
│   Client concatenates: "The weather is nice, let's go to the park"  │
└─────────────────────────────────────────────────────────────────────┘
```

- [x] Exponential backoff retry (network jitter / 429)
  - Exponential backoff borrows the "backoff" idea from CSMA/CD, but the scenario is different — one avoids collisions before sending, the other waits after failure.
    - Exponential backoff: 1s, 2s, 4s, 8s ... after each failure
    - CSMA/CD (Ethernet): wait $2^n × slot\_time$ after n collisions

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    Client (llm.py)                                  │
│                                                                     │
│   ┌─────────────┐                                                   │
│   │ 1st request │───► fails (network jitter / 429)                  │
│   └─────────────┘        │                                          │
│                          ▼                                          │
│                   wait 1s (2^0 × base)                              │
│                          │                                          │
│   ┌─────────────┐        │                                          │
│   │ 2nd request │◄───────┘                                          │
│   └─────────────┘───► still 429                                     │
│                          │                                          │
│                          ▼                                          │
│                   wait 2s (2^1 × base)                              │
│                          │                                          │
│   ┌─────────────┐        │                                          │
│   │ 3rd request │◄───────┘                                          │
│   └─────────────┘───► still 429                                     │
│                          │                                          │
│                          ▼                                          │
│                   wait 4s (2^2 × base)                              │
│                          │                                          │
│   ┌─────────────┐        │                                          │
│   │ 4th request │◄───────┘                                          │
│   └─────────────┘───► success!                                      │
│                          │                                          │
│                          ▼                                          │
│                   reset backoff counter                             │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  wait = 2^(n-1) × base + random jitter                    │   │
│   │  n = retry count, base = initial delay (e.g. 1s)          │   │
│   │  cap: max_retries (e.g. 5) or max_wait (e.g. 60s)         │   │
│   └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

- [x] **Token estimation**: classify characters — CJK ≈ 1 token, other chars 4 ≈ 1 token, round up, add ~4 tokens metadata overhead per message. Conservative estimate to avoid overflow.
- [x] **LLM self-summarization**: provide prompt templates and wrappers for summaries.
  - Mechanics (how to summarize) + LLM call → `llm.py`, reusable
  - Policy (when to summarize, how much to keep, how to splice back) → `context.py`, Agent-specific

### Pitfalls

**Boundary cases in streaming parse** (everyone who writes SSE parsing will hit these):

- **Truncated JSON**: network jitter may deliver only half a JSON object in one chunk, causing `json.loads` to throw.
  - Fix: catch `json.JSONDecodeError`, skip the chunk, wait for the next chunk to complete it.
- **Broken stream**: server drops mid-stream, `async for` ends early without `[DONE]`.
  - Fix: treat "stream ended early" as an error and retry (with exponential backoff).
- **Empty / comment lines**: SSE may include blank lines or lines starting with `:`.
  - Fix: skip them; don't try to parse them as data.
- **Empty delta**: some chunks have `delta` without `content` (e.g. only `role` or `tool_calls`).
  - Fix: check before accessing, otherwise `KeyError`.
- **`data:` prefix stripping**: `data:` is protocol, not payload. Strip with `line[5:]`.
  - Pitfall: `json.loads(line)` will try to parse `data:` as JSON and fail.

**Reflection**: SSE parsing is easy in the happy path; the hard part is boundary cases. Half JSON, broken streams, empty deltas — you only encounter these in real runs. **Defensive programming** (null checks, exception handling, treating broken streams as errors) is mandatory for streaming parsing.

### Reflection

The LLM client is the foundation of every Agent. Without stable streaming and retries, everything above collapses. Separating mechanism from policy is what makes the client reusable — it doesn't care how the Agent uses context; it only needs to reliably return results.

---

## Module 2: Tool System

### Problem

How do you let an LLM call functions safely?

**The hard part**: An LLM only emits text; it cannot execute code directly. The tool system must do two things — **expose functions to the LLM** (so it knows what tools exist and how to call them) and **protect the system** (prevent the LLM from invoking dangerous operations). The former uses schemas; the latter uses defensive lines.

**Module role**: The tool protocol is the Agent's "limbs and hands". It determines what the Agent can and cannot do. The core design is **declarative** — developers declare tools with an `@tool` decorator, the system auto-generates schemas, and the LLM calls according to the schema.

### Solution

- [x] **Decorator registration (`@tool`)**
  - A developer decorates a normal function with `@tool`; the system registers it automatically.
  - Benefit: **declarative** — adding a tool means adding a function, similar to `@mcp.tool`.

```python
@tool
def get_weather(city: str) -> str:
    """Query the weather for a city"""
    return f"{city} is sunny today, 25°C"
```

- [x] **Auto-generated schema** (JSON Schema from function signature)
  - Read the function signature with `inspect.signature`, convert parameter types, defaults, and docstring into JSON Schema.
  - Benefit: single source of truth — the signature is the only truth; the schema is generated automatically, so you never "update the signature but forget the schema".

- [x] **Dangerous confirmation** (dangerous ops require human approval)
  - Mark a tool `dangerous=True`; a confirmation dialog pops before execution.
  - Benefit: LLMs may misjudge or be tricked (prompt injection); dangerous ops must have human oversight.

```python
@tool(dangerous=True)
def delete_file(path: str) -> str:
    """Delete a file (dangerous, requires confirmation)"""
    os.remove(path)
    return f"Deleted {path}"
```

- [x] **Timeout cutoff** (prevent tools from running forever)
  - Add a timeout (e.g. 30s) to each tool call; force-interrupt if it exceeds, so a stuck tool cannot hang the whole Agent.
  - Benefit: a single tool failure should not crash the loop; the Agent can continue or report the error.

### Pitfalls

**1. Schema generation: all parameters typed as `string` (simplification in current implementation)**

- When the LLM passes parameters according to the schema, it sends ints as strings (e.g. `"30"` instead of `30`).
- Therefore the built-in tools are full of manual conversions like `int(offset)` and `float(timeout_sec)` — the cascading cost of the "schema simplification".

```python
# All parameters are treated as string
prop: dict[str, Any] = {"type": "string", "description": param_name}
```

> Essence of the pitfall: the schema is a contract between LLM and function. An imprecise contract (everything marked string) makes the LLM pass wrong types, so the function must do fallback conversions. Contract precision = amount of fallback code.

**2. What counts as "dangerous"?**

- In the current implementation only `bash` is marked `dangerous=True`; other tools (write, edit, delete) are not. But:
  - write / edit modify files — are they dangerous?
  - bash can execute arbitrary commands, including `rm -rf` — definitely dangerous.

> Essence of the pitfall: danger classification has no absolute standard; it's an engineering judgment. The principle is "better over-mark than under-mark" — mark uncertain tools as dangerous and let the user confirm, rather than under-mark and cause accidental deletion. Marking only bash is conservative; whether write/edit should also be marked is debatable.

**3. Timeout cutoff: cooperation of `asyncio.wait_for` and `to_thread`**

```python
result = await asyncio.wait_for(
    asyncio.to_thread(spec._func, **arguments),
    timeout=spec.timeout
)
```

- The bash tool additionally uses `subprocess.run(timeout=...)` to actually kill the child process.
- But for other tools (e.g. reading a large file), the thread may keep running in the background after timeout.

> Essence of the pitfall: `asyncio.wait_for` only stops waiting; it cannot kill a thread. Real termination requires internal timeout support in the tool itself (e.g. `subprocess.run(timeout=)`). Timeout is cooperative, not forcible.

**4. Output truncation: prevent tool output from blowing up context**

```python
if len(output) > 4000:
    output = output[:3900] + f"\n\n... [truncated, original output {len(output)} chars]"
```

- Tool output (e.g. `ls -R` from bash) can be huge; stuffing it directly into context can blow the token budget. Truncate to 4000 chars and annotate the original length.

> Essence of the pitfall: tool output is an important context source but uncontrolled. Truncation is the first line of defense in context management — limiting output size at the tool layer is cheaper than compressing at the context layer.

### Reflection

The tool system is the Agent's limbs and hands; four lines of defense (`dangerous flag` / `confirmation` / `timeout` / `error wrapping` / `output truncation`) are standard in production. But deeper design philosophies emerge from the code:

- **"Contract" determines everything**: The schema is the contract between LLM and function. An imprecise contract (all strings) makes the LLM pass wrong types, so the function must do fallback conversions. Contract precision = amount of fallback code.
- **Errors are "data", not exceptions**: `ToolResult` wraps errors as return values so the LLM can see the error and adjust. This is unique to Agent scenarios — errors should be handed to the LLM for judgment rather than crashing the loop.
- **Timeout is cooperative**: `asyncio.wait_for` can only stop waiting, not kill threads. Real termination needs internal tool support. Timeout is not a silver bullet; tools must be able to exit gracefully.
- **Security is layered**: dangerous flag (static declaration) + human confirmation (runtime gate) + timeout (anti-hang) + output truncation (anti-bloat). A single layer is not enough; layers must stack.

---

## Module 3: Agent Loop

### Problem

How do you make an LLM act autonomously?

**The hard part**: An LLM is stateless — it generates output based only on the current input and doesn't "do things" by itself. The Agent loop wires "thinking" and "acting" together: LLM thinks one step → executes tools → observes results → thinks again... until the task is done. This "think → act → observe → think again" loop is the heart of the Agent.

**Module role**: The Agent loop is the **skeleton of every Agent**. Whether the upper layer is ReAct, Plan-then-Execute, or Reflexion, the bottom layer is this loop. Its core design decision is the **termination condition** — when to stop.

### Solution

- [x] **ReAct loop (Reason → Act → Observe)**
  - Each turn: LLM streams "thought" (text) + "action" (tool_call) → execute tools → feed results (tool messages) back to LLM → next turn
  - Until the LLM stops calling tools (gives final answer directly), or `max_turns` is reached (default 50)

```python
for turn in range(self.config.max_turns):
    # 1. Check steering (user interjection mid-run)
    steering_msg = await self._drain_steering()
    if steering_msg:
        self.messages.append(Message(role='user', content=f'[User steering]\n{steering_msg}'))

    # 2. Context compression (check token usage every turn)
    self.messages = await self.compressor.compress_if_needed(...)

    # 3. Stream LLM call, collect text + tool_calls
    accumulated = await self._stream_and_collect()

    # 4. No tool_calls → task complete
    if not tool_calls:
        final_text = text
        break

    # 5. Has tool_calls → execute in parallel, inject results
    tool_msgs, tool_outputs = await self._execute_tools(tool_calls)
    self.messages.extend(tool_msgs)
```

- [x] **Parallel tool calls (`asyncio.gather`)**
  - When the LLM emits multiple tool_calls at once, execute them concurrently rather than serially.
  - Key: `return_exceptions=True` — ensures all tools run to completion; one failure doesn't drag down the others.

```python
tasks = [asyncio.create_task(self.tools.execute(name, args)) for ...]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

- [x] **Streaming render**
  - LLM replies are displayed as they generate (typewriter effect), so users don't wait idle.
  - Key: single panel + delayed tool-result printing — avoids nested `Live` conflicts.

```python
with Live("", console=self.console, refresh_per_second=10) as live:
    async for delta in stream:
        if delta.kind == 'text':
            live_text += delta.text
            live.update(Markdown(live_text + "▌"))
```

- [x] **Steering interrupt** (`asyncio.Queue` injects user messages)
  - Users can interject while the Agent is running to change direction.
  - Implementation: `steer()` puts a message into `_steer_queue` and sets `_cancel_event` to interrupt the current LLM stream; next loop `_drain_steering()` extracts and injects it.

```python
async def steer(self, message: str) -> None:
    await self._steer_queue.put(message)
    self._cancel_event.set()  # interrupt current LLM stream
```

### Pitfalls

**1. Termination condition design (most overlooked, most critical decision)**

The Agent loop must be able to stop, otherwise it loops forever and burns money. The code has four layers of termination:

- No `tool_call`: LLM no longer calls tools, gives final answer directly → normal end
- `max_turns`: max turns reached (default 50) → forced end, prevents infinite loops
- User interrupt: `StreamCancelledError` or `_aborted` → immediate end
- LLM error: `LLMError` → log error, end current turn

> Essence of the pitfall: termination is not "one thing" but "multiple layers stacked". Relying only on "no tool_call" is insufficient — the LLM might keep calling tools (e.g. reading the same file repeatedly), so `max_turns` is mandatory. Termination conditions are the most overlooked and most critical decision in loop design.

**2. Result replay order for parallel tools**

`asyncio.gather` executes multiple tools concurrently, but when replaying results into `messages`, the order must match the `tool_call` order. The key practice in the code:

```python
# Use zip to pair task_info with results one-to-one
for (call_id, name, args), result in zip(task_info, results):
    tool_msgs.append(Message(role="tool", content=tr.output, tool_call_id=call_id))
```

> Essence of the pitfall: `asyncio.gather` returns results in submission order (not completion order), so as long as results are replayed by `tool_call_id`, order is preserved. The key is to explicitly maintain the mapping between tool_call and result; don't assume "whoever finishes first gets replayed first".

**3. Tool results must map back to the correct `tool_call_id`**

The OpenAI protocol requires: tool results must carry `tool_call_id`, and every `tool_call` must have a corresponding result. Missing one will cause the LLM to error or behave strangely.

> Essence of the pitfall: tool results are not "just stuffed into messages"; they must map precisely by `tool_call_id`. This is a protocol requirement and a prerequisite for correct LLM reasoning.

**4. Tool errors should be fed back to the LLM, not crash**

The design of `return_exceptions=True + ToolResult(is_error=True)` (the comment says "tool errors are fed back to the LLM with isError semantics rather than crashing"):

```python
if isinstance(result, Exception):
    tr = ToolResult.error(f'{type(result).__name__}: {result}')
```

> Essence of the pitfall: there are two philosophies for tool errors — throw and crash the flow, or return an error flag and let the LLM handle it. The current implementation chooses the latter because in Agent scenarios, errors should be judged by the LLM so it can adjust and retry. The code also has an `all_failed` check — when all tools fail, it notes "the LLM will attempt to recover".

**5. Dangerous tool confirmation (`confirm_dangerous`)**

Before executing dangerous tools (e.g. bash), the code prints a warning, but auto-confirms in non-interactive mode:

```python
if self.confirm_dangerous and name in self.tools.get_dangerous_tools():
    self.console.print(f"[yellow]⚠ Dangerous op: {name}...[/yellow]")
    self.console.print("[dim]Auto-confirming dangerous operation[/dim]")  # non-interactive auto-confirm
```

> Essence of the pitfall: dangerous confirmation should prompt the user in interactive mode, but in non-interactive mode (scripts, CI) there is no one to wait for, so it must auto-confirm or reject. The "confirmation" action itself must be mode-aware.

### Reflection

The Agent loop is the heart of the Agent, and its design philosophy is **"loop + termination + resilience"**:

1. **Loop = repetition of think → act → observe**: the LLM only does one step per turn; the loop strings multi-step tasks together. This is the core of ReAct — breaking complex tasks into multiple simple decisions.
2. **Termination condition is the soul of the loop**: without it, the loop is infinite. Four-layer termination (no `tool_call` / `max_turns` / user interrupt / LLM error) is standard in production — it must end normally, have a forced fallback, and be interruptible by humans.
3. **Resilience means feedback, not crash**: tool errors are wrapped as `ToolResult(is_error=True)` and fed back to the LLM so it can recover. This is unique to Agent scenarios — errors are "data", handed to the LLM for judgment rather than crashing the loop.
4. **Parallelism saves time but is not required**: parallel tool calls are an optimization, not the core. **The core is correct replay — order and `tool_call_id` mapping** — these details determine whether the LLM can reason correctly.
5. **Steering is the key to human-in-the-loop collaboration**: an Agent is not a fully automatic black box; users must be able to interject and change direction. `asyncio.Queue` + `cancel_event` is the implementation of human-in-the-loop — it can inject new instructions and interrupt current actions.

---

## Module 4: Context Management

### Problem

How do you prevent long conversations from "forgetting"?

**The hard part**: LLM context windows are limited (128K or less), while a single coding task can generate thousands of messages — reading files, editing code, running tests, fixing bugs, back and forth for dozens of turns. When the total token count approaches the window limit, you must **swap old content out** to leave space for recent conversation. But swapping out is not simply discarding — the discarded context may contain key decisions, file paths, and error information; lose them and the Agent "forgets".

The difficulty of swapping out lies in three conflicts:
1. **Keep vs discard**: which messages should be swapped out? On what basis?
2. **Summary vs original**: when swapping out, do you discard directly or compress into a summary? How much detail does the summary lose?
3. **First vs repeated**: the first compression into a summary is fine, but long conversations may be compressed 5–10 times — should you fully rewrite the old summary every time, or incrementally update?

**Module role**: Context management is the Agent's "virtual memory" — when RAM (recent conversation) is full, old pages are swapped out to disk (compressed into summaries) and swapped back in when needed (injected as summary messages). It determines the Agent's "memory span" — can it remember decisions from 50 turns ago, or only the last 5?

### Solution

The overall flow: at the start of each Agent loop turn, `compress_if_needed()` is called and does 5 things:

```text
compress_if_needed(messages, context_limit)
  │
  ├── Step 1: Estimate tokens → trigger only above threshold
  │     threshold = context_limit - reserve_tokens
  │     e.g. 128K - 16K = 112K, current 115K → trigger
  │
  ├── Step 2: Split system / non-system messages
  │     system messages (prompts) → always keep, never compress
  │     non_system → proceed
  │
  ├── Step 3: Walk backward to find a valid cut point
  │     Keep the most recent keep_recent_tokens of raw messages
  │     Cut point must be valid (user / tool_call start / non-orphan assistant)
  │     ↓
  │     Determine is_split_turn: does the cut fall in the middle of a Turn?
  │
  ├── Step 4: Generate summary
  │     ├── Normal cut (Turn boundary) → single summary (full / incremental)
  │     └── Split Turn → dual summary (history summary + turn prefix summary)
  │
  └── Step 5: Merge summary + file-operation tracking → rebuild message list
        system + [summary messages] + kept recent messages
```

- [x] **Absolute token budgets (`reserve_tokens` + `keep_recent_tokens`)**
  - Two budgets, separate concerns:
    - `reserve_tokens = 16384`: space reserved for model generation + safety margin. `context_limit - reserve_tokens` is the trigger threshold — compression starts only above this value.
    - `keep_recent_tokens = 20000`: how many of the most recent tokens of raw messages to keep (uncompressed).
  - Key distinction: `reserve_tokens` decides **when to trigger**; `keep_recent_tokens` decides **how much to keep**. They are independent and must not be the same value.

```python
@dataclass
class CompactionConfig:
    reserve_tokens: int = 16384       # trigger threshold = context_limit - reserve_tokens
    keep_recent_tokens: int = 20000   # keep the most recent N tokens of raw messages
    summary_max_tokens: int = 4096    # history summary length cap
    turn_prefix_summary_max_tokens: int = 2048  # split-turn prefix summary length cap
```

- [x] **Cut-point search (walk backward + Turn boundary protection)**
  - Idea: start from the newest message, accumulate token count backward until exceeding `keep_recent_tokens` → find the first valid cut point after that position.
  - Valid cut-point rules (`is_valid_cut_point`):

```text
Role               │ Valid cut?   │ Reason
───────────────────┼──────────────┼─────────────────────────────
user               │ ✅ yes       │ Turn start, natural boundary
assistant + tool_calls │ ✅ yes   │ Tool-call unit start, followed by tool results
assistant (plain)  │ ⚠️ depends   │ Cannot cut if previous is tool (would break tool unit)
tool               │ ❌ no        │ Would create orphan tool result
system             │ ❌ no        │ At the beginning, not involved
```

```python
def is_valid_cut_point(messages, index):
    msg = messages[index]
    if msg.role == "tool":    # tool alone creates orphan
        return False
    if msg.role == "user":    # user is Turn start
        return True
    if msg.tool_calls:        # assistant with tool_calls = unit start
        return True
    # Plain assistant: previous cannot be tool
    if index > 0 and messages[index - 1].role == "tool":
        return False
    return True
```

- After finding the cut point, determine whether it is a **split turn**: find the nearest `user` message before the cut as the Turn start; if cut ≠ Turn start, it's a split turn → dual summary.

```text
Message sequence (old → new):
[user: "read file"] [assistant: tool_call(read)] [tool: file content] [assistant: "file content is..."]
←─── Turn start                               ↑ cut lands here → split turn!
```

- [x] **Dual summaries (`SUMMARIZATION_PROMPT` + `UPDATE_SUMMARIZATION_PROMPT`)**

  Two prompt templates cover two scenarios:

  - **Full summary** (`SUMMARIZATION_PROMPT`): first compression, no old summary. Ask the LLM to produce a structured summary from scratch: Goal → Constraints → Progress (Done / In Progress / Blocked) → Key Decisions → Next Steps → Critical Context.
  - **Incremental summary** (`UPDATE_SUMMARIZATION_PROMPT`): 2nd+ compression, old summary exists. Inject the old summary text via `{previous_summary}` and ask the LLM to append new progress, update status, and preserve key information.

  Key logic at call time — detect whether an old summary exists:

```python
def _extract_previous_summary(messages, cut_index):
    """Scan backward for [Context Summary] marker and extract old summary text."""
    for i in range(cut_index - 1, -1, -1):
        if messages[i].content.startswith("[Context Summary]"):
            summary = messages[i].content.replace("[Context Summary]", "", 1).strip()
            return summary, i   # return old summary text + index
    return None, 0              # no old summary → full mode
```

  With an old summary, only pass **new messages after the summary** to the LLM (`history_start = prev_summary_idx + 1`), rather than re-reading all history:

```python
# Incremental mode: pass only new messages + old summary
previous_summary, prev_idx = _extract_previous_summary(non_system, cut_index)
history_start = prev_idx + 1 if previous_summary else 0
new_messages = non_system[history_start:cut_index]  # only new messages

summary = await generate_summary(
    client, new_messages,
    previous_summary=previous_summary,  # non-None → UPDATE_SUMMARIZATION_PROMPT
)
```

  - **Turn prefix summary** (`TURN_PREFIX_SUMMARIZATION_PROMPT`): unique product of a split turn. When a Turn is cut in half — first half compressed, second half kept — the turn prefix summary carries the "context" of the first half to the second half.

```text
Split Turn diagram:
┌──────────────────────────────────────────────────────┐
│  Compressed part                │  Kept part         │
│                                  │                    │
│  [user: task request]            │  [assistant: plan] │
│  [assistant: tool_call(read)]   │  [assistant: edit] │
│  [tool: file content]           │  ← second half needs│
│                                  │    to know what    │
│  ← generate turn prefix summary ─→│    first half read │
│  "User asked to read file X;    │                    │
│   content shows issue Y..."      │                    │
└──────────────────────────────────────────────────────┘
```

- [x] **File operation tracking (`fileops.py`)**
  - From all `tool_calls` in the compressed messages, extract paths for `read` / `grep` / `find` / `ls` (read类) and `write` / `edit` / `bash` (modify类).
  - Format the file list as a Markdown block appended under the summary, helping the LLM know "which files were read/modified historically".

```python
def extract_file_operations(messages):
    reads, modified = set(), set()
    for msg in messages:
        if msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc["function"]["name"]
                path = json.loads(tc["function"]["arguments"]).get("path", "")
                if name in {"read", "grep", "find", "ls"}:
                    reads.add(path)
                elif name in {"write", "edit", "bash"}:
                    modified.add(path)
    return {"read_files": sorted(reads), "modified_files": sorted(modified)}
```

  Final summary message format:

```markdown
[Context Summary]

## Goal
Fix database connection error in config.py

## Progress
### Done
- [x] Read config.py, found db_host points to localhost:3306
...

## Files Read
- config.py
- db.py

## Files Modified
- config.py
```

- [x] **Turn boundary protection (don't break tool-call pairing)**
  - The validity check (`is_valid_cut_point`) is the "constraint cornerstone" of the compression system — if you cut at the wrong position, the LLM receives isolated `tool` messages (without corresponding `assistant` tool_calls), causing protocol errors.
  - The rule in one sentence: **only cut at "natural conversation boundaries"** — either a Turn start (user) or a tool-call unit start (assistant + tool_calls), never in the middle of a tool-call chain.

### Pitfalls

**1. The "connection" problem of incremental summary — the most important gap to fix**

`UPDATE_SUMMARIZATION_PROMPT` and `generate_summary(previous_summary=...)` were written from the start, but `compress_if_needed()` always passed `None` — causing every compression to fully rewrite the old summary. A conversation compressed 5 times = 5 full rewrites, wasting tokens and possibly losing details.

The fix centers on `_extract_previous_summary()` — scan backward for `[Context Summary]` marker messages, extract the old text, then pass only **new messages after the summary** to the LLM:

```python
# Before fix: always full rewrite
history_summary = await generate_summary(client, history_messages, previous_summary=None)

# After fix: detect old summary, incrementally update
previous_summary, prev_idx = _extract_previous_summary(non_system, cut_index)
history_start = prev_idx + 1 if previous_summary else 0
history_summary = await generate_summary(
    client,
    non_system[history_start:cut_index],  # only new messages
    previous_summary=previous_summary,    # old summary → UPDATE_SUMMARIZATION_PROMPT
)
```

> Essence of the pitfall: the incremental summary "interface" was ready, but the "call" was not wired. This is a classic "code present, logic not connected" — the prompt template and parameter definitions were correct; what was missing was the step to "discover" the old summary from the message list. **Interface correctness ≠ functional completeness**.

**2. The necessity of "forward search" after finding the threshold**

After walking backward and finding position i where token budget is exceeded, you cannot cut directly at i. Because i may be an invalid cut point (e.g. inside a tool message). You must search **forward** from i for the first valid point — this expands the kept range but preserves message integrity.

```python
for i in range(len(messages) - 1, -1, -1):
    accumulated += estimate_message_tokens(messages[i])
    if accumulated >= keep_recent_tokens:
        for j in range(i, len(messages)):    # search forward for valid point
            if is_valid_cut_point(messages, j):
                cut_index = j
                break
        break
```

> Essence of the pitfall: "finding the threshold position" and "finding a valid cut point" are two separate steps. Forward search means keeping slightly more messages than budget — this is an intentional trade-off: **better to spend a few extra tokens preserving complete messages than to cut a tool-call chain for budget precision**.

**3. Dual-summary concatenation logic for split turns**

When the cut lands in the middle of a Turn, two summaries are needed:
- History summary: compression of all complete Turns (history before the Turn start)
- Turn prefix summary: the first half of the current Turn that was cut away

But concatenating these two summaries is not a simple `+` — the merged message must clearly distinguish "historical context" from "the first half of the current Turn", otherwise the LLM gets confused.

```python
def merge_summaries(history_summary, turn_prefix_summary):
    return f"""{history_summary}

---

**Turn Context (split turn):**

{turn_prefix_summary}"""
```

> Essence of the pitfall: split turn is a "boundary case" of compression, but it happens frequently in long conversations. The core of dual summaries is **using formatting to distinguish context layers** — history is "background", turn prefix is "continuation of the current task". Blurring the layers causes the LLM to treat history as the current task.

**4. Identity of compressed summary messages**

Compressed summaries in the message list are special — they are neither from the user nor a normal LLM reply; they are system-injected. The `[Context Summary]` prefix exists precisely for identifiability:
- `_is_compaction_summary()` uses it to identify summary messages
- `_extract_previous_summary()` uses it to find old summaries
- It is also the watershed between incremental and full mode

> Essence of the pitfall: when injecting "meta-messages" (summaries) into the message stream, you must give them an identifiable marker. Otherwise later compression logic cannot tell which messages are summaries and which are raw conversation, and incremental updates become impossible. **Markers carry metadata**.

### Reflection

Context management is **the hardest part of productionizing an Agent** — not because the code is complex (~550 lines total), but because **strategy choices directly affect the quality and cost of long conversations**.

1. **Token budget vs turn budget**: Pi uses absolute token budgets (`reserve_tokens` / `keep_recent_tokens`), not "keep last N turns". Turn budgets fail because turns vary wildly (from 10-token "continue" to 5000-token code reviews); fixed turn counts either waste space or blow the window. **Token budgets match model windows more precisely**.

2. **Forward search after threshold is a trade-off**: finding the threshold then searching forward for a valid point means keeping more messages than budget. This is a deliberate compromise on "message integrity" — **better to spend a few extra tokens preserving tool-call pairing than to save tokens but create orphan messages**.

3. **"Interface + call" two-layer design of incremental summaries**: `UPDATE_SUMMARIZATION_PROMPT` is the interface layer ("how to incrementally update"); `_extract_previous_summary` is the call layer ("when to go incremental"). Correct interface does not mean complete function — **between code present and logic connected lies the step of "discovering the old summary"**. This is the easiest engineering detail to overlook.

4. **Split turn is a compromise on "atomicity"**: ideally compression cuts at Turn boundaries, but a long Turn may have one user request followed by 20 tool-calls — 20 turns that may far exceed `keep_recent_tokens`. Split turn acknowledges "this Turn is too long, must cut in the middle". Dual summaries compensate by distinguishing context layers via formatting.

5. **File tracking is the first building block of "long-term memory"**: `fileops.py` extracts read/modified file lists from historical tool_calls, so the summary contains not only "what was said" but also "which files were touched". This information exists independently of the summary — even if the LLM-generated summary loses file paths (uncontrollable), the file list remains. **Dual encoding (summary + structured list) is more reliable than relying solely on LLM summaries**.

The computer analogy is particularly apt here:
- **Context = RAM**: recent conversation is working memory, fast but limited.
- **Compaction = virtual memory**: old conversation is "swapped out" into summaries and "swapped back in" via summary messages when needed.
- **Incremental summary = incremental checkpoint**: instead of dumping all RAM to disk every time, only write dirty pages.
- **File tracking = page table**: maintains metadata of "which files were touched", independent of content.

The essence of context management is one sentence: **use limited space to remember infinitely long conversations**. Compression strategy (full vs incremental), cut-point choice (Turn boundary vs split turn), and metadata preservation (file tracking) are all concrete implementations of this goal.

---

## Module 5: Session Persistence

### Problem

How do you save and restore conversations?

**The hard part**: An Agent conversation can last hours and span multiple sessions. Code written today should be resumable tomorrow — you cannot start from scratch every time. So the conversation must be **persisted to disk** and **restored** on next launch. But persistence is more than "dump messages to a file" — it involves three deeper issues:

1. **Structural problem**: conversation is not a straight line. A user might `/save` a checkpoint at any time, then branch from that point into different exploration directions. What is saved is not a file but a **conversation tree**.
2. **Performance problem**: if every `save()` fully rewrites the whole file (possibly hundreds of KB), frequent saves are slow. Can we append only new data?
3. **Consistency problem**: if the program crashes mid-write (e.g. power loss), the file may be corrupted. How do we guarantee **atomic writes**?

**Module role**: Session persistence is the Agent's "disk" (Device). It maps to the lowest layer of the computer analogy — whatever is in RAM must eventually land on disk. Without it, the Agent has the memory of a fish — every launch is a fresh start.

### Solution

- [x] **JSONL storage + full in-memory load**
  - Each line is a JSON object (one session node), easy to append and parse line by line.
  - On startup, load everything into `dict[str, SessionNode]` for O(1) lookup.
  - Write back on exit.

```python
class SessionStore:
    def __init__(self, filepath="sessions.jsonl"):
        self._nodes: dict[str, SessionNode] = {}   # in-memory index
        self._loaded = False
        self._dirty = False
        self._new_ids: set[str] = set()             # newly added nodes
        self._modified_ids: set[str] = set()         # modified nodes

    def load(self):
        """Load everything on startup."""
        with open(self.filepath) as f:
            for line in f:
                data = json.loads(line.strip())
                node = SessionNode(id=data["id"], parent_id=data.get("parent_id"),
                                   messages=data["messages"], bookmark=data.get("bookmark"))
                self._nodes[node.id] = node
        self._loaded = True
```

- [x] **Conversation tree (`parent_id` linked list)**
  - Each node points to its parent via `parent_id`, forming a tree.
  - Branching: the same parent can have multiple child nodes → users can explore different directions from a checkpoint.
  - Queries: `get_branch(node_id)` walks from leaf to root; `get_children(parent_id)` lists all branches.

```text
Conversation tree:
                    ┌──────────────┐
                    │  root (abc1) │  ← first conversation
                    │  "Build an API"│
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  node (abc2) │  ← user /save checkpoint1
                    │  "API done"  │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
     ┌────────▼───┐  ┌─────▼──────┐  ┌─▼──────────┐
     │ node (abc3)│  │ node (abc4)│  │ node (abc5) │  ← three branches
     │ Add cache  │  │ Make async │  │ Add tests   │
     └────────────┘  └────────────┘  └────────────┘
```

- [x] **Bookmarks (restore points)**
  - Users can bookmark any node: `store.bookmark_node(node_id, "before-refactor")`
  - Restore by bookmark: `store.get_by_bookmark("before-refactor")`
  - Bookmarks are "human-readable restore points" — much friendlier than memorizing `abc123def456`.

- [x] **Atomic write + append-only optimization**
  - Two write strategies, chosen automatically:
    - **Only new nodes** (`_new_ids` non-empty, `_modified_ids` empty) → **append-only**: append new lines to the end, O(new nodes), zero rewrite cost.
    - **Modified nodes exist** (`_modified_ids` non-empty) → **full atomic rewrite**: write to a temp file → `os.replace(tmp, target)`. `os.replace` is atomic on POSIX: either fully succeeds or leaves the original file untouched.

```python
def save(self):
    if self._modified_ids:
        self._full_rewrite()        # full atomic rewrite
    elif self._new_ids:
        self._append_new()          # fast append

def _full_rewrite(self):
    """Write to temp file → atomic rename, never corrupts original."""
    fd, tmp = tempfile.mkstemp(dir=str(self.filepath.parent), prefix='.sessions_')
    with os.fdopen(fd, 'w') as f:
        for node in self._nodes.values():
            f.write(json.dumps({...}) + '\n')
    os.replace(tmp, str(self.filepath))  # atomic replace
```

- [x] **Message serialization / deserialization**
  - `Message` ↔ `dict` conversion: `_message_to_dict()` / `_dict_to_message()`.
  - Session nodes store `list[dict]` (JSON-compatible), restored to `list[Message]`.

### Pitfalls

**1. Tree vs linear: when do you need branches?**

JSONL one node per line + `parent_id` links = naturally supports trees. But "tree" brings complexity:
- On restore, you restore **one node** (one path), not the whole tree.
- Branch child nodes exist but do not affect the current path — this is both an advantage (isolation) and a potential confusion ("why can't I find my recent edit? Because it's in another branch").

> Essence of the pitfall: tree structure models "exploration" — users can return to checkpoints and try different approaches. But **most conversations do not need branching** — users just progress linearly. Tree is a capability, but linear is the default. **Default linear, branch when needed** is the pragmatic strategy.

**2. State reconstruction on restore (compactor state, token counts)**

The current implementation only restores the `messages` list, but the Agent has runtime state:
- `ContextCompactor._last_stats`: compression statistics
- `Agent._turn_count`: current turn count (resets to 0 after restore)
- `Agent._steer_queue` / `_cancel_event`: runtime control signals

These states are not persisted — the restored Agent is "partially reconstructed". Losing compactor state means the first compression after restore may be less precise (no previous statistics reference).

> Essence of the pitfall: persistence granularity determines restore "completeness". Current is "message-level persistence" (only messages), not "state-level persistence" (all runtime states). Full restore would require serializing all Agent internal state — complexity doubles, but completeness doubles too. **This is a trade-off: simple vs complete**.

**3. Empty-write guard: necessity of `ensure_loaded()`**

If the user calls `save()` without first calling `load()`, it causes an **empty overwrite** — empty `_nodes` overwrites the existing JSONL file. Fix:

```python
def save(self):
    if not self._loaded:
        raise RuntimeError("SessionStore has not loaded data, save() forbidden")
```

> Essence of the pitfall: persistence operations need an **explicit state machine** — "loaded" is a precondition. Writing without checking state is catastrophic. **Defensive programming in I/O is not optional, it is mandatory**.

**4. Append-only "dirty data" risk**

If the same node is appended twice (e.g. `_new_ids` not cleared after `create_node`, then `save()` again), the JSONL file will have duplicate lines. On next `load()`, later lines overwrite earlier ones — result is fine, but the file bloats.

> Essence of the pitfall: append-only is performant but state-dependent — you must precisely track "what has already been written". The cleanup timing of `_new_ids` and `_modified_ids` (at the end of `save()`) is critical. Cleaning too early or too late both cause problems.

### Reflection

Session persistence is the most durable layer of the Agent's "three-tier memory":

1. **Short-term memory = `agent.messages`** (RAM): full message list of current conversation, disappears when the program exits.
2. **Medium-term memory = conversation tree** (Disk): JSONL-persisted conversation history, exists across sessions. Can branch, backtrack, restore.
3. **Long-term memory = file tracking + summaries** (Archive): file operation records extracted by `fileops.py` and compaction summaries — not tied to a specific conversation, can be referenced in entirely different sessions.

Design philosophy:
- **JSONL > SQLite**: for "hundreds of nodes, occasional queries", JSONL + full in-memory load is far simpler than SQLite. No SQL, no ORM, no migration scripts. **Simple scenarios use simple solutions**.
- **Atomic write > direct write**: `tempfile + os.replace` is the classic POSIX atomic-write pattern. The cost is one extra file copy; the benefit is "original file is never corrupted". **I/O safety beats I/O performance**.
- **Append-only optimizes the common path**: most save operations only need to append new nodes (normal conversation → exit → save), not modify existing nodes. Optimize the common path, not the rare one — **the 80/20 rule applies to engineering optimization too**.

---

## Module 6: CLI / Harness

### Problem

How do you turn the Agent into a usable product?

**The hard part**: The first five modules build the Agent kernel — LLM client, tool system, loop, context management, session persistence. But users cannot write Python scripts every time they want to use the Agent. A **"Harness"** is needed to wrap the kernel, providing a command-line entry point, configuration management, and interactive experience.

Harness's core challenge is **"multi-scenario adaptation"**:
1. **One-shot vs continuous conversation**: ask one question and leave, or keep interacting?
2. **Configuration source precedence**: users may provide API Key / model / base_url via CLI args, environment variables, or config files — how to merge them?
3. **Interrupt recovery**: last conversation was interrupted; how to resume quickly?

**Module role**: Harness is the Agent's "operating system" — it starts, configures, and schedules the Agent, providing the user interface. The Agent kernel is the "engine"; the Harness is the "steering wheel + dashboard".

### Solution

- [x] **typer commands (`chat` + `resume`)**
  - `pi-agent chat`: start a new conversation. Can take a `prompt` argument for one-shot Q&A; omit to enter interactive mode.
  - `pi-agent resume <bookmark>`: resume a previous conversation from a saved point.

```python
@app.command()
def chat(
    prompt: Optional[str] = typer.Argument(None),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k"),
    base_url: Optional[str] = typer.Option(None, "--base-url", "-b"),
    max_turns: Optional[int] = typer.Option(None, "--max-turns"),
    no_confirm: bool = typer.Option(False, "--no-confirm"),
):
    ...
```

- [x] **Configuration precedence (CLI > env > config file)**

  Three sources, strict ordering. `resolve_kwargs()` uses an `or` chain for fallback:

```python
def resolve_kwargs(cli_kwargs):
    config = load_config()  # load from config.yaml
    return {
        "api_key":  cli_kwargs["api_key"]
                    or os.environ.get("OPENAI_API_KEY")
                    or config.get("api_key"),
        "base_url": cli_kwargs["base_url"]
                    or os.environ.get("OPENAI_BASE_URL")
                    or config.get("base_url")
                    or "https://api.deepseek.com",
        "model":    cli_kwargs["model"]
                    or config.get("model")
                    or "deepseek-chat",
        ...
    }
```

  Precedence chain:

```text
CLI args  >  environment variables  >  config file (config.yaml)  >  hard-coded defaults
  --model      OPENAI_API_KEY        model: deepseek-chat           "deepseek-chat"
  deepseek-v4  OPENAI_BASE_URL       base_url: https://...          "https://api.deepseek.com"
```

- [x] **Interactive / non-interactive dual mode**
  - **Non-interactive** (`chat "write me a function"`): one sentence in, result out, auto-save, exit. Good for scripts/CI.
  - **Interactive** (`chat` without args): enter REPL loop, continuous conversation, supports meta-commands. Good for development and debugging.

```python
if prompt:
    asyncio.run(_run_non_interactive(agent, store, prompt))
else:
    asyncio.run(_run_interactive(agent, store))
```

- [x] **Meta-command system (`/save` `/exit` `/stats` `/bookmarks` `/help`)**

  In interactive mode, inputs starting with `/` are interpreted as meta-commands rather than sent to the LLM:

```text
/exit        save current session and exit
/save <name> bookmark current node (no new node created)
/bookmarks   list all bookmarks (★ marks current node)
/stats       show context stats (turns, message count, token usage)
/help        show help
```

  Implementation: in `_run_interactive` main loop, first check `user_input.startswith("/")`; if a command matches, `continue` to skip LLM call.

- [x] **Rich terminal rendering**
  - Startup info: `Panel.fit()` shows model, API address, max turns, recent bookmarks.
  - Agent output: `Markdown()` renders code-block highlighting.
  - Tool results: `Panel(body, title=f"tool: {name}")` colored panels distinguish success/failure.
  - Resume hint: displays bookmark name and corresponding node ID.

- [x] **Smart `resume`**
  - First lookup by bookmark name, then by node ID — bookmarks are human-friendly.
  - Restore runtime params (model, max_turns) from node `metadata`, but CLI explicit args override.
  - After restore, enter interactive mode directly without reconfiguration.

### Pitfalls

**1. The `or` chain trap of configuration precedence**

The `or` chain for fallback looks elegant, but has a pitfall — **empty string vs None handling**. If `OPENAI_API_KEY=""` (set but empty), `or` treats it as falsy and skips it. If the user passes `--api-key ""` (typer gives empty string), it is also skipped — the user may think they cleared the key, but fallback is used.

> Essence of the pitfall: the `or` chain cannot distinguish "user didn't pass" from "user passed empty". For fields like API Key that "must have value" this is fine, but for fields "allowed to be empty" (e.g. `base_url`), an empty string may be intentional. Python's `or` is concise but imprecise fallback — **if you need to distinguish "unset" from "set to empty", use `is None`**.

**2. Exception handling in the interactive loop**

`_run_interactive` wraps `agent.run()` in a `try/except`:

```python
try:
    result = await agent.run(user_input)
except Exception as exc:
    console.print(f"[red]✗ Runtime error: {exc}[/red]")
    continue
```

But if `agent.run()` throws an uncaught exception internally (e.g. LLM API down), this `except` catches it — yet the Agent's internal state (`messages`, `_turn_count`) may already be partially modified. The next `run()` starts from a half-modified state.

> Essence of the pitfall: not crashing on exceptions = good interactive UX (user doesn't lose conversation), but state consistency = possibly broken. The current implementation chooses the former — **"resilience over consistency"** — which is reasonable for interactive tools, but production-grade Agents need finer-grained state rollback.

**3. Partial state recovery with `resume`**

Restore only recovers `agent.messages` and partial config, but the following are lost:
- Compactor state (`compressor._last_stats`)
- Turn count (restarts from 0)
- Current `current_node_id` binding (if a new conversation restores an old node)

These losses mean post-restore behavior is not fully consistent with pre-interruption — e.g. compression threshold judgment may be less accurate (last compression stats lost).

> Essence of the pitfall: restore "completeness" is a sliding scale — from "only messages" (simplest) to "full snapshot" (most complete). Current chooses the simplest because full snapshots require serializing all Agent internal state, and snapshots from different Agent versions are incompatible. **"Restore 80% of state" is more practical than "restore 100% but version-incompatible"**.

**4. Config file location and format**

Two locations supported: `./config.yaml` (project-level) and `~/.pi-agent/config.yaml` (user-level). Current implementation merges with `config.update()`, later-loaded overrides earlier-loaded (i.e. user-level overrides project-level). But YAML nested structures can produce unexpected merge results.

```yaml
# config.yaml
api_key: sk-xxx
model: deepseek-chat
base_url: https://api.deepseek.com
max_turns: 50
```

> Essence of the pitfall: simple flat configs work fine, but once nested configs are supported (e.g. `compaction.reserve_tokens: 8192`), `dict.update` shallow merge breaks. **Shallow merge is enough for flat configs; nested configs need deep merge**.

### Reflection

Harness is the "last mile" of the Agent — no matter how well the kernel is written, users won't use it without a good CLI. Several design philosophies:

1. **Dual mode = dual users**: one-shot mode for scripts/CI (composable, automatable), interactive mode for humans (explorable, interruptible). Both modes share the same Agent initialization logic (`_build_agent_and_store`), diverging only at the "input loop". **Share core, fork interface**.

2. **Configuration precedence = user freedom**: CLI overrides the most (can differ per call), config file overrides the least (global defaults). The longer the precedence chain, the more user freedom, but also harder to debug — "which value actually took effect?" is the classic config-precedence problem. Current implementation lacks a `--show-config` command to print the effective config, a UX gap.

3. **Meta-commands vs natural language**: the `/` prefix is a clear "command vs conversation" boundary. Why not natural language (e.g. "please save the session")? Because:
   - Determinism: `/save` 100% triggers save; natural language may be misinterpreted by the LLM.
   - Efficiency: one character `/` distinguishes, no extra LLM round-trip.
   - Privacy: meta-commands do not go through the LLM (no token cost, no conversation leakage).

4. **Harness is a "replaceable shell"**: the same Agent kernel can wear different Harnesses — CLI, Web UI, IDE plugin, API service. Harness decides "how to interact"; Agent decides "what it can do". **Decoupling Harness from Agent is the first step to productization**.

5. **`resume` is key to human-machine trust**: a user spends 30 minutes debugging a bug with the Agent, exits or crashes, and returns seamlessly next time — this builds more trust than any new feature. **Interrupt recovery is not "nice to have", it is "must have"**.

---

## Closing: From Pi Agent to Any Agent

### 1. Universal skeleton

> Loop + Tools + Context Management + Memory + Control

### 2. Swappable parts (the key to generalization)

| Component | Pi's implementation | Other variants |
|:---|:---|:---|
| Decision paradigm | ReAct | Plan-then-Execute / Reflexion |
| Tool protocol | Local functions | MCP |
| Context compression | Dual summaries | 5-stage progressive pipeline / RAG |
| Memory | Conversation tree | Vector store |
| Multi-Agent | Single Agent | Sub-agent delegation / orchestration |

### 3. The computer analogy (the finishing touch)

> Think of an Agent as a computer: LLM + Tools = CPU, Context = RAM,
> Compaction = virtual memory, Session = disk, CLI = operating system.
> Wire these components into a reusable system, and you can run different apps on top — coding, research, data analysis.
> **Swap the app, keep the skeleton — that is the essence of generalizing to any Agent.**

### 4. What's next

- Sub-agent delegation (spawn independent-context child agents)
- Richer meta-command system (`/compact`, `/status`, `/undo` handled by the Agent layer)
- MCP tool protocol support (replacing local function tools)
