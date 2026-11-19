---
marp: true
theme: default
paginate: true
---

<!-- _class: lead -->

# M2.0 · AI Application Patterns

Build a chatbot from the M1 Claude call. Then choose the simplest application pattern that meets the next requirement.

- Build a browser chat with **Gradio**.
- Give the chatbot **Nano Bank statement facts**.
- Compare **direct calls, structured output, RAG, fine-tuning, and agents**.

<!--
Plan for 38 minutes: 7 Claude and Gradio, 7 Nano Bank mini lab, 2 request boundaries, 10 five patterns and selection, 10 pattern lab, and 2 close. For a 30-minute session, demo the Nano Bank wiring as a group and give each team one case in Lab 2. For 40 minutes, let teams compare cases and defend a rejected alternative. Preinstall the Gradio demo dependencies and confirm Nano Bank is running before class.

The source deck’s model selection material is available in the appendix. Keep the core session focused on choosing and testing application patterns.
-->

---

# M2.1 · Start with the M1 Claude call

In `claude_101_old.py`, the client sends a single message and prints a reply.

```python
response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=32,
    messages=[{"role": "user", "content": "Reply with only: API key works!"}],
)
```

The new chatbot uses the same Messages API call. The browser supplies the current message and the earlier turns.

<!--
Open the old file and point at load_dotenv, Anthropic, and messages.create. The original smoke test used CLAUDE_API_KEY. The new demo uses the same key and accepts an optional CLAUDE_MODEL environment variable for a different model ID available to the account.
Reference: https://platform.claude.com/docs/en/api/python/messages/create
-->

---

# M2.1 · Put a browser interface around the call

```python
chat = gr.ChatInterface(reply, title="Claude chatbot")
chat.launch(server_name="127.0.0.1", share=False)
```

From the repository root, with `CLAUDE_API_KEY` configured:

```bash
uv run --python 3.13 claude_101_gradio.py
```

Open the local URL printed in the terminal.

<!--
Show the dependency header in claude_101_gradio.py. uv reads it and installs the script's dependencies. Gradio calls reply(message, history) every time the user sends a message. The Claude client and model are configured once at the top of the file, as in the M1 script. If learners see KeyError for CLAUDE_API_KEY, check the .env file or terminal environment. Use the instructor's UI if pairs are waiting on setup.
Reference: https://gradio.app/docs/gradio/chatinterface
-->

---

# M2.1 · Turn history into a model request

```python
def reply(message, history):
    messages = []
    for earlier_message in history:
        role = earlier_message["role"]
        content = earlier_message["content"]
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model=model, max_tokens=512, messages=messages,
    )
    text = []
    for block in response.content:
        if block.type == "text":
            text.append(block.text)
    return "\n".join(text) or "Claude returned no text."
```

**Try two turns:** “Call me Sam.” Then “What name did I give you?”

<!--
Each item in history is a dictionary. In the loop, earlier_message is the dictionary for one previous message. Copy its role and content, then add the new user message after the loop. Send the resulting list to Claude and collect the text for Gradio to display. Gradio can also include display fields, so the loop selects the two fields Claude needs. Start a new chat to show what an empty history does.
Reference: https://gradio.app/guides/gradio-6-migration-guide
-->

---

# M2.L1 · Mini lab: build a Nano Bank chatbot

Keep the Gradio UI. Make its callback read a Nano Bank statement before calling Claude.

1. Copy `claude_101_gradio.py` to `nano_bank_chatbot.py`. Run `uv add --script nano_bank_chatbot.py httpx`.
2. In `nano-sandbox-bank-snippets/`, run `uv run python nano-bank.py`.
3. Wire the statement into the callback, then run `uv run --python 3.13 nano_bank_chatbot.py` from the root.

**Done when** the chat explains January’s **4,820 USD** net inflow and says the January closing balance is unavailable.

<!--
Timebox to seven minutes. Use a local copy of claude_101_gradio.py for the lab. If your Nano Bank instance prints a different port, use that port. Open /docs on the same base URL, then inspect the statement response. The exercise uses synthetic account ACC101 and only the statement GET. current_balance is deliberately excluded because the exercise asks about the January closing balance. The live endpoint does not return that historical value. Ask “What was January’s net flow?” and “What was the closing balance?” in the browser.
-->

---

# M2.L1 · Wire the statement into the callback

Add `import httpx` and a second function that prepares the bank question.

```python
def bank_reply(message, history):
    url = "http://127.0.0.1:8002/accounts/ACC101/statement/2025/1"
    response = httpx.get(url, timeout=5)
    response.raise_for_status()
    statement = response.json()
    keys = ("month", "total_deposits", "total_withdrawals", "net_flow")
    facts = {key: statement[key] for key in keys}

    prompt = f"Use only these USD statement facts: {facts}\n"
    prompt += "Say when a requested value is missing.\n"
    prompt += f"Question: {message}"
    return reply(prompt, history)
```

Launch `gr.ChatInterface(bank_reply)` in the lab copy.

<!--
In the lab copy, import httpx. Put bank_reply below reply and above the launch code. Change gr.ChatInterface(reply, ...) to gr.ChatInterface(bank_reply, ...). Here is the full callback with a message for a stopped bank server.

    def bank_reply(message, history):
        url = "http://127.0.0.1:8002/accounts/ACC101/statement/2025/1"
        try:
            response = httpx.get(url, timeout=5)
            response.raise_for_status()
        except httpx.HTTPError:
            return "The January statement is unavailable. Check the Nano Bank server."
        statement = response.json()
        keys = ("month", "total_deposits", "total_withdrawals", "net_flow")
        facts = {key: statement[key] for key in keys}
        prompt = (
            "Explain the supplied January statement in USD. Use only these facts. "
            "Say when a requested value is missing.\n"
            f"Statement: {facts}\nQuestion: {message}"
        )
        return reply(prompt, history)

If the API is down, test the callback against the M1 fixture: month 2025-01, deposits 5000 USD, withdrawals 180 USD, net flow 4820 USD. Keep the selected fields identical so the comparison is useful.
-->

---

# M2.2 · Keep four things separate

| Thing | Question it answers | Owned by |
| --- | --- | --- |
| Model | What language capability is available? | provider / deployment |
| Instruction | How should it behave? | application |
| Context | What facts are available now? | application / data boundary |
| Prompt | What assembled request is sent? | application |

Confusing these makes failures hard to diagnose.

---

# M2.2 · Assemble the request visibly

```python
def assemble_prompt(instruction, context, question):
    return f"INSTRUCTION: {instruction}\nCONTEXT: {context}\nQUESTION: {question}"
```

If tone is wrong, inspect the instruction. If a fact is wrong or missing,
inspect the context. If the call is malformed, inspect assembly.

In the chatbot, the statement fields are context and the user turn is the question.

<!--
This boundary helps students stop saying “the prompt failed.” Ask which input
actually owns the observed failure. If the net flow is wrong in Nano Bank’s JSON, inspect the calculation in Python.
-->

---

# M2.3 · The five-pattern ladder

| Pattern | Adds | Use when |
| --- | --- | --- |
| Direct call | general language capability | drafting, rewriting, translation |
| Prompted application | instruction, format, constraints | extraction or controlled shape |
| RAG | retrieved evidence and citations | answers from a document collection |
| Fine-tuning | learned repeated behaviour | stable high-volume task or style |
| Agentic workflow | dynamic tools and steps | steps genuinely vary |

Each pattern introduces its own tests. One application can combine several patterns.

---

# M2.3 · Pattern 1 — Direct call

```python
messages = [
    {"role": "user", "content": "Rewrite: Your January statement is ready."}
]
response = client.messages.create(
    model=model, max_tokens=128, messages=messages,
)
```

Use it for a self-contained language task such as rewriting a supplied note, support reply, or internal update.

<!--
The Gradio demo starts here. The user supplies the complete input. An observable check is that the rewrite preserves the meaning and adds no figures or promises.
-->

---

# M2.3 · Pattern 2 — Prompted application with structured output

```python
class SupportHandoff(BaseModel):
    category: Literal["statement", "access", "other"]
    summary: str = Field(min_length=1)
```

The app supplies an instruction and requests a response matching this schema. The receiving code can use `category` and `summary`.

<!--
The Nano Bank mini lab is a prompted application with a controlled scope and text output. This example adds a downstream schema because another system will consume the result. Pydantic validates the typed response. Instructor plus Pydantic is one way to request and validate it. Show the schema here and leave the provider integration for a later lab.
-->

---

# M2.3 · Schema validation and business validation

```python
def can_explain_statement(account_id):
    return account_id == "ACC101"
```

- **Schema:** Are the fields and types correct?
- **Business rules:** May the requester access this account or perform the action?
- **Evidence:** Does the answer match the data?

Python policy, permissions, and approval controls remain application-owned.

<!--
ACC101 is a fixed synthetic classroom account. Real access checks would use authenticated identity and account permissions. The first test here verifies that application code rejects an unknown account before model or data access.
-->

---

# M2.3 · Pattern 3 — RAG

Add retrieved facts and citations when the answer depends on current, private,
or document-bound knowledge.

- **Question:** “How do I dispute a statement error?”
- **Retrieve:** Find relevant passages in the approved policy guide.
- **Generate:** Answer using those passages and cite the policy section.

<!--
Keep the original retrieve → prompt → answer architecture. The Mini Lab makes one known GET request for a particular statement. RAG applies when the app must find evidence across documents, such as several versions of the bank’s guide. Ask which section supports the answer and what to do when none is found.
-->

---

# M2.3 · Pattern 4 — Fine-tuning

Add learned repeated behaviour only when a prompt/RAG baseline has evidence of
a persistent gap on a stable, high-volume task.

- Needs representative labelled examples
- Adds training, versioning, serving, and regression risk
- Does not replace current/private facts

**Example:** Improve consistent routing labels after a tested prompt baseline still misses a stable, repetitive classification task.

---

# M2.3 · Pattern 5 — Agentic workflow

Add dynamic tool selection and multi-step control only when the steps genuinely
vary at runtime.

- Example tools include finding a statement, retrieving a policy, and drafting a hand-off.
- The request determines which tools are needed and in what order.
- The application enforces permissions, records actions, and stops at approval boundaries.

---

# M2.4 · Choose the simplest pattern that works

```text
Complete input + general language task → Direct call
Stable output shape or business rules  → Prompted application
Evidence across documents              → RAG
Persistent gap in a stable behaviour   → Fine-tuning candidate
Tools or steps vary at runtime         → Agentic workflow
```

Start with the smallest pattern that meets the requirement, then earn each extra layer with observed failure evidence.

<!--
Use ordinary Python for exact calculations and fixed sequences. A deterministic test can verify that an unsupported account never reaches the statement API. A review test can verify that a reply preserves the meaning of a customer's note. Fine-tuning and retrieval solve different problems and can be combined when both are justified.
-->

---

# M2.L2 · Pattern lab: choose and defend

| Build request | What to decide |
|---|---|
| Rewrite a supplied statement email in plain English | What input is already available? |
| Route a customer issue as `category` and `summary` | What contract does the receiving system need? |
| Answer from versioned internal dispute policies | Where should the evidence come from? |
| Improve a repetitive routing task after a measured prompt failure | What evidence justifies a training run? |
| Triage exceptions that need different tools depending on the case | Which actions and approvals does the app own? |

<!--
Assign cases to pairs. At 38 minutes, each pair takes one case and compares its reasoning with a pair on a different case. At 40 minutes, cover all five collectively. Expected starting patterns in order: direct call, prompted application with structured output, RAG, fine-tuning candidate, agentic workflow. For the final case, ask for a concrete reason fixed orchestration would fall short. Accept a simpler design if it satisfies the actual requirement.
-->

---

# M2.L2 · Produce a decision card and one check

```text
candidate | data needed | likely failure | simplest pattern
model/deployment boundary | limit of a simpler option | first test
```

Build one tiny example where time allows. Try a direct rewrite in the Gradio app or validate a `SupportHandoff` with Pydantic.

**Done when** another pair can explain your pattern choice and run or observe your first check.

<!--
Timebox to ten minutes. Spend five choosing and writing, three trying a direct or prompted example, and two exchanging cards. For a direct rewrite, paste “Your January statement is ready.” into the starter chatbot and ask it to rewrite the message in plain English. Check for an invented date. For a support handoff, use the class from Pattern 2 with Literal from typing and BaseModel and Field from pydantic. Try SupportHandoff(category="statement", summary="Customer needs a January copy") and then change "statement" to "wire_transfer" to see the validation error. RAG, fine-tuning, and agent rows are design exercises. Ask for an observable check specific to each, such as a policy citation, a holdout improvement, or a blocked write.
-->

---

<!-- _class: lead -->

# M2.5 · The application owns the checks

Use models through an explicit boundary.
Choose a model boundary for the task.
Choose the simplest application pattern that works.
Test deterministic rules outside the model.

<!--
Name one example from the room. Restate its evidence source, pattern and first test, then ask what would make the team change its design.
-->

---

<!-- _class: lead -->

# M2.A · Model selection reference

Use these slides when a pattern decision also needs a model or a deployment choice.

---

# M2.A · Model selection is an operating decision

```text
task → quality → cost → latency → data boundary
     → ownership → serving effort
```

The best benchmark score is not automatically the best product choice.

Choose the smallest capable model and the simplest operating boundary that meet
the workflow's constraints.

<!--
M1 introduced ways to access models. Here, turn that inventory into an
engineering decision. Do not begin with a provider or a favourite model name.
Begin with the task and the constraints under which it must operate.

The outcome is a written selection rationale, not a claim that one model wins
all tasks. Use the Nano Bank chatbot to discuss what you would measure first.
-->

---

# M2.A · Open models: family before version

Examples include Qwen, Llama, Mistral, and Gemma families.

- A family has a characteristic capability, license, and operating shape
- A version changes quickly; read the current model card before committing
- Check license, modality, context, hardware, and evaluation evidence

Open weights can improve control and portability; they also make you own more
of serving, upgrades, safety, and evaluation.

<!--
Avoid a leaderboard. The durable habit is to understand a family and inspect a
specific release only when a feature has real requirements. A model card is a
delivery artifact: confirm license terms, supported modalities, context limit,
hardware needs, and known limitations before procurement or implementation.

Open weights do not mean that everything is open. Weights, training data,
licence, and distribution rights can all have different boundaries.
-->

---

# M2.A · Size is one dial

```text
task fit + supplied context + prompting + model size
                 + deployment + evaluation
```

More parameters can improve capability, but size is not an intelligence score.

- A small model can excel at a narrow, supplied-context task
- A larger model may still fail without facts, tests, or permissions
- Mixture-of-experts models make raw parameter counts especially imperfect

<!--
Connect this to the statement chatbot. Bigger models commonly cost more and take longer,
but parameter count alone does not tell learners whether a model will solve the
task. Training data, post-training, model architecture, the supplied context,
and the desired output shape all matter.

The practical question remains: what is the smallest capable choice that passes
the tests for this workflow?
-->

---

# M2.A · What size buys

| Tier | Open-weight size* | Good first use |
| --- | --- | --- |
| Small / local | 0.1B–3B | tagging, extraction, simple rewrite |
| Workhorse | 7B–32B | supplied-context Q&A, summaries, tools |
| Frontier-sized | 70B+ | difficult reasoning, complex coding |

*For mixture-of-experts models, total parameters ≠ active parameters per token.

Start at the lowest tier that can pass a representative test set. Escalate with
evidence—not because a larger model sounds safer.

<!--
The bands are approximate open-weight model sizes, not a benchmark leaderboard.
Exact parameter counts become stale quickly, and parameter count is not
comparable across every architecture. In mixture-of-experts models, total
parameters can be large while only part of the model is active for each token.
The table gives learners a starting hypothesis to test.

A template or small local model may be sufficient for a narrow Nano Bank
notification rewrite. Cross-document reasoning can require stronger evidence
selection and a test of a more capable model.
-->

---

# M2.A · Closed models change the operating model

```text
no download → no GPU → one HTTP call
```

You gain fast access to capability and reduce infrastructure work.

You also send permitted prompt data across a service boundary and pay for
input/output tokens under the provider’s terms.

<!--
This is not an argument against closed services. They are often the fastest
path to a useful feature. The point is that the model no longer runs in the
application's environment: identity, data handling, usage, token bills,
availability, and provider terms become system concerns.

In a regulated workflow, ask which data may cross the boundary and under what
contract before asking which model is strongest.
-->

---

# M2.A · Service boundaries trade different things

| Boundary | You gain | You take on |
| --- | --- | --- |
| Direct provider API | fastest access | API-key/data boundary, token bill |
| Cloud model platform | IAM and governance | account, region, billing setup |
| Hosted open-weight API | model choice | provider evaluation and portability risk |

There is no universally right boundary. Choose one that fits the task, data,
organisation, and delivery constraints.

<!--
Examples change quickly, so do not turn this into a vendor comparison. A direct
provider API is normally fastest to prototype. A cloud platform adds enterprise
identity, audit, billing, and regional controls. Hosted open-weight inference
offers model choice without operating GPUs, but the provider still forms a data
and availability boundary.
-->

---

# M2.A · Match the model to the job

| Model kind | Use it when | Example |
| --- | --- | --- |
| Specialist | one modality or narrow task dominates | embedding search, reranking, speech |
| General-purpose | language work is the core workflow | draft, extract, classify, explain |
| Multimodal | the evidence includes images, audio, or documents | chart, statement, call recording |

Do not pay for broad capability when a specialised model reliably solves the
task. Do not force a specialist to perform a general reasoning workflow.

<!--
This is a second selection axis independent of size. An embedding model may be
small and superb at retrieval but cannot draft a customer reply. A multimodal
model is valuable when a chart or PDF is actual evidence, not merely because it
has more features.

The selection document should name task modality, quality target, context/data
boundary, latency and cost budget, and why this model kind is sufficient.
-->
