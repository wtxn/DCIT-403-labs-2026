# Lab 2: Architectures: A ReAct Agent From Scratch: Concept Check

Answer in your own words before the Wednesday session (independent work). Your answers feed Section 2 of your lab report (Concept and classical root).

## Q1. Classify a thermostat, a chess engine and a ReAct agent as reactive, deliberative or hybrid, with one reason each.

**Thermostat → Reactive.**
A thermostat maps the current temperature percept directly to an on/off action using a fixed condition-action rule ("if temperature < threshold, switch on"). It holds no internal world model, keeps no history, and makes no plan — it only reacts to what it senses right now.

**Chess engine → Deliberative.**
A chess engine builds an internal model of the board, searches a tree of possible future moves (using minimax or Monte Carlo Tree Search), and selects the action whose projected long-term outcome best maximises its performance measure. It plans ahead before acting rather than reacting immediately to the current percept.

**ReAct agent → Hybrid.**
A ReAct agent combines both layers. The Thought step is deliberative — the model reasons about what to do next and can plan across multiple steps. The Action step is reactive — it immediately responds to the latest Observation returned by the tool. Neither layer alone describes it; it needs both.

---

## Q2. In the trace above, which lines are percepts, and which are actions?

**Percepts (inputs received by the agent from the environment):**
- `Observation: 1025` — the result returned by the calculator after the first tool call. This is a new piece of information fed back into the agent.
- `Observation: 175` — the result returned after the second calculator call.

**Actions (outputs produced by the agent that affect the environment):**
- `Action: calculator` / `Action Input: 4*185 + 3*95` — the agent invokes the calculator tool.
- `Action: calculator` / `Action Input: 1200 - 1025` — the agent invokes the calculator a second time.
- `Action: finish` / `Action Input: You will have GHS 175 left.` — the agent delivers its final answer.

**Note:** The `Thought:` lines are internal deliberation — they are neither percepts nor actions. They are reasoning the agent writes for itself before choosing an action.

---

## Q3. Why do we pass `stop=["Observation:"]` when calling the model?

If we do not set a stop token, the model will keep generating text past its `Action Input:` line and invent its own `Observation:` line, effectively hallucinating the tool result without ever calling the real tool. By passing `stop=["Observation:"]`, we instruct the model to pause the moment it would write that word and hand control back to our Python code. Our code then actually runs the named tool and appends the real result as the next `Observation:` message. This guarantees that every observation in the conversation comes from a genuine tool call, not from the model's imagination.

---

## Q4. Map the trace above to the BDI terms belief, desire and intention.

| BDI Term | In the Budget Trace |
|---|---|
| **Belief** | The full conversation history at any point in time — the original question ("I have GHS 1,200…"), and every Observation received so far (`1025`, then `175`). Beliefs are what the agent currently holds to be true about the world. |
| **Desire** | To correctly answer the user's budget question. This is the top-level goal that motivates the entire interaction and does not change during the run. |
| **Intention** | The committed sub-plan stated in each Thought. In Step 1 the intention is "I need the total cost first — compute 4 × 185 + 3 × 95." After receiving `Observation: 1025`, the agent re-plans and commits to a new intention: "Now subtract the cost from the budget — compute 1200 − 1025." Each intention drives exactly one tool call before the agent re-evaluates. |
