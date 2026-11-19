---
marp: true
theme: default
paginate: true
---

<!-- _class: lead -->

# M1.0 · Introduction to AI Models

From model capability to AI applications

**Tredence · Nano Bank**

By the end of this module, you can:

- Explain why the largest AI opportunity is in applications
- Call a proprietary model and explain where an open-weight model runs
- Put a model behind a small, logged application boundary
- Say where a model call will live once your organisation owns it

<!--
This module is the bridge from M0 Python to the rest of AI engineering. The
through-line is a synthetic Nano Bank statement assistant. It uses the FastAPI
application and SQLite data learners set up yesterday.

The module has one shape: argue that the application is the opportunity
(M1.1), then build toward one — call a model (M1.2), show local inference (M1.3),
choose between them (M1.4), assemble the assistant (M1.5), extend it in the
lab, and only then show where this runs in an enterprise (M1.6).

**Instructor only:** Plan for 35 minutes. Spend 6 on M1.1 and M1.A, 8 on model
access and selection (M1.2–M1.4), 8 on the assistant walkthrough (M1.5), 10 on
the lab, and 3 on the cloud boundary and close (M1.6–M1.7).

For 30 minutes, give M1.A one quick example, skip the optional local and cloud
code walkthroughs, and score the lab result together. For 40 minutes, give
pairs five extra minutes to compare two Claude tiers on the same prompt.

Before class, run `uv run python nano-bank.py` from
`nano-sandbox-bank-snippets/` if yesterday’s server is stopped. Open
http://127.0.0.1:8000/docs and Anthropic Console. The lab has a printed fixture
and a scored example for a no-credentials walkthrough.
-->

---

# M1.1.1 · AI models can work with many kinds of information

**Language** — write, summarise, extract, translate, classify, reason, code

**Vision** — read images, charts, screenshots, and documents

**Audio** — transcribe speech and generate speech

**Generation** — create images, video, and audio

**Action** — select tools and trigger workflow steps

```text
A model can generate an answer.
An AI application must make that answer
useful, safe, and affordable.
```

<!--
Capability is real, but it is not the end of the engineering problem. A useful
application needs permitted context, a workflow, evaluation, safety, cost
control, and operations.

**Instructor only:** ask which capability we need to turn a statement’s JSON
fields into a short explanation. The statement gives us the evidence for the
exercise later.
-->

---

# M1.1.2 · AI becomes useful where work already happens

| Standalone chat | AI inside the work |
|---|---|
| Ask a generic question | Explain a Nano Bank customer's monthly statement |
| Paste documents manually | Read permitted policy or product documents |
| Copy a result elsewhere | Draft a review inside the workflow where work happens |

Examples such as a statement assistant or a document-grounded notebook
show the same transition: capability becomes useful when it meets real work.

<!--
The example does not endorse a particular product. It shows the interaction
shift: context is supplied safely and automatically, and the result appears
where the user already makes decisions.
-->

---

# M1.1.3 · Model families and the capability landscape

| Category | Examples to know | General lesson |
|---|---|---|
| Proprietary frontier models | Gemini, GPT, Claude | Fastest route to broad capability |
| Open-weight generalists | Qwen, Llama, DeepSeek, Mistral | More portability and deployment control |
| Specialists | Speech-to-text, image, embeddings, reranking | Smaller, faster, cheaper, often better at one job |

Model names change quickly. The engineering skill is recognising the category
and choosing it for the task.

<!--
These are dated examples, not a leaderboard. Explain that open weights do not
automatically mean open training data or an unrestricted licence.

The specialist row matters more than it looks: transcription wants a speech
model, semantic search wants an embedding model, and neither wants a frontier
chat model. We meet embeddings and reranking again in the retrieval module.

**Instructor only:** if time allows, one speech-to-text and one text-to-image
demonstration lands this row. They are demonstrations, not learner setup —
hosted availability, quotas, and authentication change frequently.
-->

---

# M1.1.4 · A model is not a product

| Manual model use | Product feature |
|---|---|
| A person pastes data into chat | The application receives permitted workflow data |
| A person writes the prompt | Code supplies instructions consistently |
| A person decides whether to trust it | The application evaluates and shows limits |
| A person copies the result elsewhere | The result appears in the workflow itself |

A model does not know your customers, your policies, your systems, which data
it may use, or what a correct answer means here.

> A product is model + data + workflow + safety + evaluation + operations.

<!--
Use Nano Bank to illustrate the application boundary. SQLite holds the
transactions, Python computes the totals, and Claude explains selected facts.

This is also the course map. Every later module adds one term to that
equation: prompt design, data preparation, retrieval, tools and oversight,
evaluation, and production operations.
-->

---

# M1.1.5 · Every platform creates an application wave

```text
Computers created software companies.
The internet created web applications.
Cloud created SaaS applications.

AI creates a new application layer.
```

Every repeated **question, decision, document, review, search, and hand-off**
is a candidate: a bank assistant for a statement review, a support assistant
for triaging an exception, a policy assistant for extracting constraints.

> The model may be shared by everyone. The application is what you build.

<!--
As infrastructure becomes available, builders create applications that solve
previously uneconomic or impossible problems.

The point is possibility, not that every workflow should be automated. The
next question is practical, and the rest of the module answers it: how do we
reach a model from an application?
-->

---

# M1.A · Find an AI application opportunity

Choose one repeated question, decision, document task, review, search, or
workflow hand-off. Describe:

```text
User:
Current manual workflow:
AI capability needed:
Data required:
What makes a good answer:
```

Keep it as a candidate. Later we can decide whether it needs a prompt, RAG,
fine-tuning, an agent, or a conventional software rule.

<!--
Take one or two minutes. Invite the room to suggest one recurring question
for Nano Bank. Capture the fields the app would need and one check for a good
answer. Use the monthly statement for the rest of the walkthrough.
-->

---

# M1.2.1 · Three ways to reach a model

| Path | Example | What changes |
|---|---|---|
| Proprietary, direct | Gemini, GPT, Claude API | Fastest path from Python to a model |
| Open weights, local | SmolLM2 with weights already downloaded | No key or network for inference |
| *Through your cloud* | *Vertex, Bedrock, Azure* | *Project, identity, billing, governance* |

Ask the same questions every time: **task, quality, cost, data boundary,
ownership, and serving effort.**

<!--
Say the third row out loud and then set it aside. The organisation chooses
the approved deployment boundary. For now we use Claude directly so the
mechanics are visible. Return to identity and governance in M1.6.

Expect the objection early — "we are not allowed to put an API key in a
script." Agree with it, point at M1.6, and move on.

Use "open weights" precisely: weights may be available while training data,
training pipeline, and licence terms remain different.
-->

---

# M1.2.2 · Three proprietary SDKs, one identical shape

```python
def call_gemini(prompt, api_key, model_id):
    client = genai.Client(api_key=api_key)
    reply = client.models.generate_content(
        model=model_id, contents=prompt)
    return reply.text

def call_openai(prompt, api_key, model_id):
    client = OpenAI(api_key=api_key)
    reply = client.responses.create(
        model=model_id, input=prompt)
    return reply.output_text

def call_claude(prompt, api_key, model_id):
    client = anthropic.Anthropic(api_key=api_key)
    reply = client.messages.create(
        model=model_id, max_tokens=512,
        messages=[{"role": "user", "content": prompt}])
    return "\n".join(b.text for b in reply.content if b.type == "text")
```

Live Claude smoke test: `claude_101.py`

<!--
Read down the left edge, not across: client, call, return. Three vendors, one
shape. The differences are naming — `contents` / `input` / `messages` — and
one real design difference worth pausing on.

Claude returns a list of content blocks rather than a string, because a
response may contain thinking blocks before the text. `reply.content[0].text`
is the bug everyone writes first; picking the text block is the fix. That is
the first hint of something M2 makes central: a model call is structured, not
a string in and a string out.

These are comparison excerpts. Each uses its own SDK imports, API key, and
configured model ID. Teach the Claude block live. If API access is ready, run
the existing smoke test from the repository root:

    uv run --no-project --with anthropic --with python-dotenv python claude_101.py

The smoke test reads CLAUDE_API_KEY from the environment or .env. Its only
input is a connectivity check. Use Anthropic Console if the batch is already
set up there.

SDK references:
- Claude: https://platform.claude.com/docs/en/api/python/messages/create
- OpenAI: https://developers.openai.com/api/docs/guides/text?lang=python
- Gemini: https://github.com/googleapis/python-genai#generate-content
-->

---

# M1.2.3 · A proprietary model has more than chat

The same model family may support:

- text generation and structured extraction
- image, document, and chart understanding
- tool or function calling
- audio and grounded responses, where supported

In the code-along, change one variable at a time. Ask for the same Nano Bank
statement as one sentence, three bullets, then a small JSON-shaped answer.

<!--
This is not a second snippet. It is guided exploration of the first one.
Availability varies by model and provider, so verify a feature before building
a dependency on it.
-->

---

# M1.3.1 · Local open weights keep inference on this machine

```python
import os
from transformers import pipeline

os.environ.setdefault("HF_HUB_OFFLINE", "1")

generate = pipeline(
    "text-generation",
    model=os.environ["LOCAL_MODEL_DIR"],
)
reply = generate(
    "January deposits: 5000 USD. Summarise this in one sentence.",
    max_new_tokens=30,
)
print(reply[0]["generated_text"])
```

No key. No network. No per-call bill.

<!--
Optional instructor demo. It requires transformers, a compatible backend such
as PyTorch, and a model already downloaded to LOCAL_MODEL_DIR. SmolLM2 135M
Instruct is one example. HF_HUB_OFFLINE makes a missing file fail without a
network download. Present the excerpt as a walkthrough if weights are absent.

The code-along then opens the model folder: config, tokenizer, shards,
prompt format, generation, decoding.
-->

---

# M1.3.2 · What a local model costs you

| You gain | You give up |
|---|---|
| No key, no network, no per-call bill | Capability — this model is 135M parameters |
| Data never leaves the machine | Someone must serve and update it |
| Stable, versioned behaviour | Hardware becomes your problem at scale |

If it’s configured, run it and read the answer. A narrow task with a clear
check makes it easy to judge whether the smaller model is sufficient.

<!--
A deliberately small model demonstrates the local boundary. Check the output
against the supplied deposit amount. Capability is one factor alongside
latency, cost, privacy, and the team's ability to run the service.
-->

---

# M1.4.1 · Proprietary and open-weight models are different trade-offs

| | Proprietary model | Open-weight model |
|---|---|---|
| Fastest first feature | Usually lower setup | Depends on hosting and setup |
| Capability | Often broad frontier capability | Strong and rapidly evolving |
| Cost | Usage pricing | Hosting or infrastructure cost |
| Data boundary | Provider or cloud agreement | Can run in a controlled boundary |
| Control | Provider roadmap | More model and deployment control |

> Neither is better. The feature, data boundary, cost, and operating model decide.

<!--
Refer back to the direct Claude call and the local inference example. Ask
which factors change when inference moves from the provider to this laptop.

This is not an ideological closed-versus-open debate. A team may use both in
one application: a high-capability hosted model for uncertain work and an
owned local model for a narrow, high-volume task. The assistant in M1.5 accepts
the model call as a parameter, which makes that choice a caller decision.
-->

---

# M1.4.2 · Choose the smallest sufficient model and deployment

| Ask first | Why it matters |
|---|---|
| What is the task and modality? | Chat, speech, image, embeddings, classification |
| How good and fast must it be? | A draft and a compliance decision differ |
| What can it cost? | Calls, tokens, GPUs, and engineering effort |
| Where may data go? | Vendor, cloud account, provider, or local machine |
| What must the organisation control? | Weights, licence, deployment, behaviour |

> Start with the simplest option that is good enough for the real task.

<!--
Use scenarios instead of a list of fashionable model names: transcription
needs a speech specialist; semantic search needs embeddings; local-sensitive
work may favour a small local model. This is a decision framework, not a
benchmark debate.

Point back to the M1.A candidates here and ask two or three learners which row
decides their case.

For a Claude-only choice, use Haiku, Sonnet, or Opus where available. Compare
the same input on correctness, latency and token usage. A recorded usage count
and the configured model’s input/output rates give an estimated request cost.
Reference: https://platform.claude.com/docs/en/models/overview
-->

---

# M1.5.1 · Build the assistant: facts in, logged answer out

```python
def build_prompt(question, facts):
    given = "\n".join(f"{k}: {v}" for k, v in facts.items())
    return (
        f"{SYSTEM}\n\nFacts:\n{given}"
        f"\n\nQuestion: {question}"
    )

def answer(question, facts, call_model):
    prompt = build_prompt(question, facts)
    log.info("prompt_chars=%d", len(prompt))
    reply = call_model(prompt)
    log.info("reply_chars=%d", len(reply))
    return reply
```

Facts: `GET /accounts/ACC101/statement/2025/1` in Nano Bank’s `/docs`.

<!--
This is the module's payoff and the first thing all day that is an
application rather than a call. Three moves: assemble instruction plus
grounding facts plus question, measure both sides of the boundary, and take
the model as a parameter so the caller decides which one.

`call_model` being injected is not style. It is what makes the boundary
testable without a key, and it is the same seam the lab and every later module
use.

Take the five fields shown on the lab slide from the statement rather than
sending every field. Python computes the totals before Claude sees them. The
assistant has read access to the selected fields. Deposit and withdrawal remain
separate API actions.

For the walkthrough, use the lab’s instruction as SYSTEM. Set up log with
logging.getLogger(__name__). Pass call_claude from M1.2.2 with its key and
model ID bound with functools.partial, or pass a fake model callable to show
the prompt without network access. Learners can run the same prompt in Console
without copying the Python wrapper. nano-bank.py supplies the statement API
and has chatbot, rag, and agent stubs for later exercises.
-->

---

# M1.5.2 · Carry M0 practice into AI code

- configuration outside business logic — keys from `.env`, never source
- log the outcome, the model id, duration, and usage where available
- handle missing or empty output safely
- accept the model as a parameter, so tests never call a live provider

> First call proves access. This boundary makes access maintainable.

<!--
Every one of these is ordinary software engineering, which is the point:
almost nothing about an AI feature is new engineering. What is new is that the
dependency is non-deterministic, remote, metered, and occasionally wrong — so
the ordinary practices matter more, not less.

The empty-output case is the lab's job, and it is not hypothetical: a
truncated response, a safety refusal, and a quota error all reach your code as
"no usable text".
-->

---

<!-- _class: lead -->

# M1.L · Lab: explain a Nano Bank statement

**Mini lab** — one controlled instruction, one concise response.

```text
month: 2025-01               total_deposits: 5000 USD
total_withdrawals: 180 USD    net_flow: 4820 USD
current_balance: 157840 USD (as of the statement request)
```

**Instruction:** Use only the supplied facts. Say when a requested value is missing.

**Ask:** Summarise January’s activity in two sentences. What was the January closing balance?

Check the three monthly figures and how the reply handles the missing balance.

<!--
Ten minutes: 2 to inspect the statement, 4 to run the prompt in Console or
through the M1.5 wrapper, 2 to score the reply, and 2 to share a failure or a
revision. Use the printed fixture in Console for the model comparison. The
database balance may differ after yesterday’s deposits or withdrawals.

Expected: 5,000 USD deposited, 180 USD withdrawn, 4,820 USD net inflow, and
the January closing balance is unavailable. Give one point per correct check
and flag extra invented claims. If API access is unavailable, score the
worked example on the final slide together.

For a longer lab, keep the original application extension: add a terminal
reply(message, history) around the wrapper, handle a model response with no
usable text, and prove both behaviours with two tests using a fake model.
If you have five extra minutes in class, compare two available Claude tiers
with the same facts and instruction, then choose a default.
-->

---

# M1.6.1 · Cloud platforms provide a governed model boundary

| Cloud platform | What it adds |
|---|---|
| Google Cloud / Vertex AI | Gemini access, project, IAM, billing |
| AWS / Bedrock | Model catalogue, AWS identity, governance controls |
| Azure AI | Model catalogue, Azure identity, enterprise controls |

The organisation’s approved deployment path determines the identity, access,
and billing configuration.

<!--
Cloud catalogues change. A platform introduces a project or account,
identity and access management, billing, regional controls, and organisational
governance.

The next slide is optional. Read the changes to configuration aloud, then
ask how the team would restrict which statement fields leave the application.
-->

---

# M1.6.2 · The same Gemini capability through Vertex AI

```python
client = genai.Client(
    vertexai=True,
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location="global",
)
reply = client.models.generate_content(
    model=os.environ["GEMINI_MODEL_ID"],
    contents=prompt,
)
```

Gemini through Vertex AI changes the **identity and governance boundary**.
The same statement question can go through either configured client.

<!--
Compare this to M1.2.2 line by line. The request shape is still client, call,
and response, and the business question stays the same. The caller now uses
an approved project and an IAM-authenticated identity the organisation grants
and can revoke. Choose a model and region configured for that project. This is
a read-through example. No cloud credentials or setup are needed for the lab.
Reference: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-rag-generate-content?hl=en
-->

---

# M1.7.1 · Access is only the first engineering problem

Consider this plausible answer to the Nano Bank lab:

```text
January deposits were $5,000 and withdrawals were $180,
for a net inflow of $4,820. January closed at $157,840.
```

The numbers match the input. The last sentence uses the **current balance** as the **January closing balance**.

> Next: write the prompt and define the checks that catch this error.

<!--
This is a worked example. The first sentence earns three points. The last
sentence fails the missing-information check. A correct reply would say that
January’s closing balance is unavailable. The app could retrieve a historical
balance if a suitable source were available. Use the failed check as the first
example for M2 prompt engineering.
-->
