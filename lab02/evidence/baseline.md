# Baseline: the model on its own (no tools)

This records what the raw LLM answered before any tools were connected.
The correct answer to the budget question is **GHS 175**.

---

## Budget Question (run 3 times)

**Question:** I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil at GHS 95 each. How much will I have left?

| Run | Model's answer | Correct? |
|---|---|---|
| 1 | "4 bags of rice cost 4 × GHS 185 = GHS 740. 3 gallons of oil cost 3 × GHS 95 = GHS 285. Total spent = GHS 1,025. Amount left = GHS 1,200 − GHS 1,025 = **GHS 175**." | ✅ Yes |
| 2 | "Rice: 4 × 185 = GHS 740. Oil: 3 × 95 = GHS 285. Total = GHS 1,025. You will have GHS 1,200 − GHS 1,025 = **GHS 175** left." | ✅ Yes |
| 3 | "Rice costs 4 × 185 = GHS 720. Oil costs 3 × 95 = GHS 275. Total = GHS 995. You will have GHS 1,200 − GHS 995 = **GHS 205 left**." | ❌ No — arithmetic errors (720 instead of 740; 275 instead of 285) |

**Observation:** At lower temperature the model happened to get the arithmetic right twice, but on the third attempt (higher temperature) it made multiplication errors — computing 4 × 185 as 720 and 3 × 95 as 275. The model never uses a calculator; it generates plausible-sounding numbers, which are not always correct.

---

## Factual Questions

| Question | Model's answer | Confident tone? | Correct? |
|---|---|---|---|
| What is the capital of the Bono East Region? (Techiman) | "The capital of the Bono East Region of Ghana is **Techiman**." | Yes — no hedging or uncertainty expressed | ✅ Yes |
| In what year was the University of Ghana founded? | "The University of Ghana was founded in **1948**." | Yes — stated as a plain fact with no qualification | ✅ Yes |

---

## Summary

The raw model answered the arithmetic question correctly 2 out of 3 times, but the third run shows that at higher temperature it makes arithmetic errors confidently — it cannot actually compute. For factual questions it sounded equally confident whether it was right or guessing. This confirms why the ReAct agent delegates all arithmetic to `calculator` and factual look-ups to `wiki_lookup` rather than relying on the model's memory.
