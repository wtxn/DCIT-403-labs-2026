"""Lab 2: a ReAct agent from scratch (no framework). Model calls go through LiteLLM."""
import os
import re
import sys

from tools import TOOLS

MODEL = os.getenv("LLM_MODEL", "groq/llama-3.3-70b-versatile")
# gpt-oss-20b tries to use native tool calling with the ReAct prompt; use a
# llama model instead, which follows the text-based Thought/Action protocol.
if "gpt-oss-20b" in MODEL:
    MODEL = "groq/llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful assistant for a trader at Makola Market.
You solve problems by alternating Thought, Action and Action Input.

Tools:
- calculator: evaluates arithmetic (+ - * / and brackets). Input: an expression, e.g. 4*185 + 3*95
- wiki_lookup: returns a short Wikipedia summary. Input: a page title, e.g. Bono East Region
- finish: gives the final answer to the user. Input: the final answer text.

You MUST reply in EXACTLY this format on every step, and nothing else:

Thought: <your reasoning>
Action: calculator | wiki_lookup | finish
Action Input: <input for the tool, or the final answer if finish>

Rules:
- Never do arithmetic in your head: use the calculator.
- Never write an Observation yourself. Stop after Action Input and wait.
- If a tool returns an error or finds nothing, say so honestly; do not invent facts.
- If no tool is needed, use finish straight away.
"""

# Tolerant of extra spaces, any case, and a missing newline before Action Input.
ACTION_RE = re.compile(
    r"Action\s*:\s*(\w+)\s*\n\s*Action Input\s*:\s*(.*)", re.DOTALL | re.IGNORECASE
)


def parse(text):
    """Return (action, action_input), or (None, None) if the reply is malformed."""
    m = ACTION_RE.search(text or "")
    if not m:
        return None, None
    return m.group(1).strip().lower(), m.group(2).strip()


def call_model(messages):
    """One model call. stop=['Observation:'] stops the model inventing observations."""
    from litellm import completion  # imported here so tools/parser can be tested offline

    resp = completion(model=MODEL, messages=messages, stop=["Observation:"],
                      temperature=0, max_tokens=512,
                      extra_body={"tool_choice": "none"})
    return resp.choices[0].message.content or ""


def run_agent(question, max_steps=6, llm=call_model, verbose=True):
    """Run the Thought -> Action -> Observation loop. Returns (answer, trace_text)."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}]
    trace = [f"Question: {question}"]

    def log(line):
        trace.append(line)
        if verbose:
            print(line)

    if verbose:
        print(trace[0])

    for step in range(1, max_steps + 1):
        try:
            reply = llm(messages).strip()
        except Exception as e:  # rate limit, network, bad key...
            log(f"[Model error at step {step}: {e}]")
            return f"Stopped: model call failed ({e})", "\n".join(trace)

        log(f"\n--- Step {step} ---\n{reply}")
        messages.append({"role": "assistant", "content": reply})
        action, arg = parse(reply)

        # Failure 1: unparseable reply -> corrective Observation
        if action is None:
            obs = ("Observation: Could not parse your reply. Reply in exactly this format:\n"
                   "Thought: ...\nAction: calculator | wiki_lookup | finish\nAction Input: ...")
        elif action == "finish":
            log(f"\nFINAL ANSWER: {arg}")
            return arg, "\n".join(trace)
        # Failure 2: unknown tool -> tell the model which tools exist
        elif action not in TOOLS:
            obs = (f"Observation: Unknown action '{action}'. "
                   f"Valid actions: {', '.join(TOOLS)}, finish.")
        else:
            obs = f"Observation: {TOOLS[action](arg)}"

        log(obs)
        messages.append({"role": "user", "content": obs})

    # Failure 3: runaway loop
    msg = f"Stopped: reached max_steps={max_steps} without a final answer."
    log(f"\n{msg}")
    return msg, "\n".join(trace)


def save_trace(trace, n):
    os.makedirs("evidence", exist_ok=True)
    path = f"evidence/trace_{n}.txt"
    with open(path, "w") as f:
        f.write(trace + "\n")
    print(f"[saved {path}]")


QUESTIONS = [
    "I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil at GHS 95 each. How much will I have left?",
    "Look up the Bono East Region and tell me how many people live there, then work out 15% of that number.",
    "What is the capital of the Bono East Region, and if a trader there sells 12 yams at GHS 40 each, what is her income?",
    "Tell me about the Wikipedia page 'Zorblax Market Spirit of Kumasi 1999'.",
    "Say hello and tell me what you can help with.",
    "rice 4 bag 185 and also oil?? total left from 1200 how",
]

if __name__ == "__main__":
    # python react_agent.py          -> run the budget question only (trace_1)
    # python react_agent.py all      -> run all questions (trace_1 ... trace_6)
    # python react_agent.py "text"   -> run your own question
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg == "all":
        for i, q in enumerate(QUESTIONS, 1):
            _, tr = run_agent(q)
            save_trace(tr, i)
            print("\n" + "=" * 70 + "\n")
    elif arg:
        _, tr = run_agent(arg)
        save_trace(tr, "custom")
    else:
        _, tr = run_agent(QUESTIONS[0])
        save_trace(tr, 1)
