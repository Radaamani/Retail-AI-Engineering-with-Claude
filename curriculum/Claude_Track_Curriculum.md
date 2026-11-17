# Claude Track AI Application Development Curriculum

12 modules across six AIDLC phases · 20 hours

Claude by Anthropic is a frontier AI assistant and API. This curriculum covers the full AIDLC — from problem framing and prompt design (P1) to building production Claude-powered applications (P3/P5) and responsible governance (P6).  
Special Note: Pricing & Optimisation

THROUGH-LINE (M1–M11): UC-DE Retail Orders pipeline — daily CSV/JSON order files → ingest → quality → transform → gold KPI table → data contract. CAPSTONE (M12 only): new generic business persona — not opened in M1.

Source workbook: [Claude Track spreadsheet](https://docs.google.com/spreadsheets/d/1Ug3aU3V7EsYnBtT4bXcJAYjh8_Kmpszf/edit)

## Module Overview

| Module | Title                                                                                                     | Phase | Hours |
|--------|-----------------------------------------------------------------------------------------------------------|-------|-------|
| M1     | Claude Ecosystem & AIDLC Mindset                                                                          | P1    | 1.5   |
| M2     | Prompt Engineering for Claude                                                                             | P1    | 2     |
| M3     | Use Case Scoping & Feasibility with Claude                                                                | P1    | 1.5   |
| M4     | Document & Data Processing with Claude                                                                    | P2    | 1.5   |
| M5     | Claude Projects & Knowledge Management / Custom Skills & Instructions Studio — skill.md + instructions.md | P2    | 2     |
| M6     | Building Claude-Powered Applications                                                                      | P3    | 1.5   |
| M7     | RAG with Claude API — Retrieval-Augmented Generation                                                      | P3    | 1.5   |
| M8     | Agentic Workflows with Claude                                                                             | P3    | 1.5   |
| M9     | Claude Code for AI-Assisted Development                                                                   | P3    | 1.5   |
| M10    | Evaluation & Testing Claude Outputs                                                                       | P4    | 1.5   |
| M11    | Production Deployment & API Integration                                                                   | P5    | 1.5   |
| M12    | Responsible AI, Governance & Continuous Learning                                                          | P6    | 2.5   |

P1 · Problem Definition & Use Case Selection \| 1.5 hours \| Lecture / Discussion

## M1 Claude Ecosystem & AIDLC Mindset

### Use Case

UC-DE Retail Orders pipeline — daily CSV/JSON order files → ingest → quality → transform → gold KPI table → data contract.

### Key Topics

- AIDLC 6-phase framework — where Claude fits at each phase

- Claude product landscape: Claude.ai, Claude API, Claude Code, Claude in Chrome, Cowork / Projects

- Model tiers: Haiku (speed), Sonnet (balanced), Opus (reasoning) — when to use each

- Claude vs other LLMs: long-context, code, analysis, instruction-following

- Map the Retail Orders pipeline onto AIDLC (ingest → transform → test → deploy); mark Claude assist vs human accountability

- AI scope: what Claude CAN and CANNOT do on this Orders dataset

### Hands On Lab Scenarios

- Sketch Orders: landing files → bronze/silver/gold → data contract. Label AIDLC on each box.

- On each box, mark Claude assist vs human gate (validation, security, IP, UAT-locked gold).

- Draft AI Scope Statement for THIS pipeline: which order columns Claude may see; NEVER_MODIFY list.

- Compare Haiku vs Sonnet vs Opus on one Orders quality prompt; pick a default model and write why.

### Learning Outcomes

- Understand Claude’s ecosystem, model tiers, and AIDLC positioning

- Choose the right Claude model for a given task (cost vs quality)

- Frame the Orders through-line; know capstone is a different generic persona

- Apply responsible AI and data governance before any Claude integration

### Claude Tools and APIs

Claude.ai · Claude API (claude.ai/api) · Anthropic Console · Model comparison matrix · AI Scope Statement template

### UAT and Quality Gate

Gate: AI Scope Statement completed for chosen use case — data sensitivity classified, model tier justified, responsible-AI checklist passed. Lead review required before M2.

P1 · Problem Definition & Use Case Selection \| 2 hours \| Lab

## M2 Prompt Engineering for Claude

### Use Case

Retail Orders pipeline (ingest, quality, contract).

### Key Topics

- Prompt anatomy — purpose of each part: role, context, task, constraints, examples, output contract, evaluation criteria

- Why weak prompts fail: missing constraints, no output contract, no success criteria

- Ablation: remove one part at a time and see what breaks

- Claude structure with rationale: system vs user turn, XML tags (\<context\>, \<task\>, \<constraints\>, \<format\>), few-shot, chain-of-thought — when each helps

- Context-window discipline (200K): what to include, what to leave out, and why

- Eval-Driven Prompting: write pass/fail criteria before writing the prompt

- Independent design from a blank page — not copy-paste of a trainer prompt

- Anti-patterns: vague instructions, over-trusting outputs, hidden assumptions

### Hands On Lab Scenarios

- Dissect a weak “clean the orders file” prompt. Label missing parts (role, context, task, constraints, examples, output contract, success test).

- From a blank page, write a prompt: ingest raw orders CSV → bronze table. Before running, say why each section exists.

- Ablation: five variants of an orders quality prompt (nulls, duplicates, late flag), each missing a different part. Score outputs on a shared rubric.

- XML lab: structure a silver-transform prompt with \<context\>, \<task\>, \<constraints\>, \<format\>. Explain each block, then run.

- Few-shot: add 3 good/bad order-quality examples; note how style and strictness change.

- Independent: new slice of this orders data (e.g. returns rows). No sample prompt given. Write the prompt; peer-critique with the rubric.

- Eval-Driven: write pass/fail criteria first; test your prompt on 10 order rows (not a trainer demo).

### Learning Outcomes

- Name each prompt component and the failure if it is removed

- Write a structured prompt from a blank page for an orders-pipeline task

- Use system prompts and XML as configuration, with a stated reason for each block

- Apply Eval-Driven Prompting — define success before building

### Claude Tools and APIs

Claude.ai · Anthropic Console (prompt editor) · Claude API (messages endpoint) · XML prompt templates · System prompt library

### UAT and Quality Gate

Gate: System prompt for the team use case must pass a 10-question eval suite (accuracy ≥ 80%) before being used in any downstream application build.

P1 · Problem Definition & Use Case Selection \| 1.5 hours \| Workshop

## M3 Use Case Scoping & Feasibility with Claude

### Use Case

Retail Orders pipeline only.

### Key Topics

- Use-case evaluation: value vs complexity vs risk

- Claude strengths vs limits (analysis, code, writing, reasoning vs real-time data, calc errors, hallucination)

- Split a DE pipeline into layers: ingest, quality, transform, data contract, orchestration

- Skill inventory: what is reusable vs one-off for this pipeline (name, trigger, expected output)

- Feasibility: data availability, latency, cost modelling

- Responsible AI: bias, PII on orders, human-in-the-loop before gold overwrite

- Build vs buy: Claude API vs Claude.ai vs Projects vs Claude Code for this job

- Pilot scoping: success metrics, eval criteria, rollback

### Hands On Lab Scenarios

- Score the Orders pipeline on value / complexity / risk. Write why it is in scope for this programme.

- Split Orders into layers: ingest, quality, transform, data contract, orchestration. One box per layer.

- For each layer, fill a skill inventory row: name, when Claude should use it, expected output, what stays human.

- Estimate token cost for one daily Orders run (pricing calculator).

- Responsible AI checklist: email/address on orders; HITL before gold overwrite.

- Build vs buy: which Claude surface for pipeline work vs chat-only.

- Draft a one-page Orders pilot scope: success metrics, eval criteria, data rules, rollback (stop writing gold).

### Learning Outcomes

- Score and justify a DE use case before building

- Decompose a pipeline into layers and reusable skills

- Produce a scoped, responsible pilot with metrics, cost, and rollback

### Claude Tools and APIs

Anthropic Console · Pricing calculator · Use case scoring matrix · Responsible AI checklist · Pilot scope template

### UAT and Quality Gate

Gate: Pilot scope document reviewed and approved by product/tech lead — includes success metrics, eval criteria, data governance plan, and rollback decision point.

P2 · Data Collection & Preparation \| 1.5 hours \| Lab

## M4 Document & Data Processing with Claude

### Use Case

Retail Orders pipeline — daily CSV/JSON files → bronze / quality / silver / gold → data contract

### Key Topics

- Claude for DE work: ingest, cleansing, transform, data-quality checks, data contracts

- Prompt design per layer — write the prompt; do not paste a master prompt

- Schema-bound outputs: JSON mode / tool use for contracts and validation scripts

- Documents only when they serve the pipeline (specs, mapping docs, runbooks)

- Large-context handling (200K): schemas, samples, pipeline code

- Batch patterns for high-volume files

- Reusable vs one-off prompts (parameterise path, schema, grain)

### Hands On Lab Scenarios

- From a blank page, prompt ingest: raw daily orders CSV/JSON → bronze table. Parameterise file path and schema. Run on sample files.

- Prompt data-quality checks: null order_id, duplicate order_id, negative amount, late vs promised date. Run on sample; record failures.

- Prompt silver (grain: order line) and gold KPI table (order count, late %, quality-fail count by region).

- From a messy orders spec or CSV header, extract a JSON data contract; validate required fields.

- If output is wrong: name which prompt part failed (role, constraints, output contract, etc.); fix that part — do not throw the whole prompt away.

- Keep the prompts, scripts, and contract as the artefacts from this session.

### Learning Outcomes

- Use Claude as a DE assistant (not only a PDF summariser)

- Write a layer-specific prompt with a stated reason for each part

- Produce schema-bound, validated output (pipeline + data contract)

### Claude Tools and APIs

Claude API (messages, JSON mode) · Python SDK (anthropic) · Batch API · PDF/text loaders · JSON output validation

### UAT and Quality Gate

Gate: Batch processing pipeline produces structured output with ≥ 95% field extraction accuracy on held-out test set before proceeding to model development (P3).

P2 · Data Collection & Preparation \| 2 hours \| Lab

## M5 Claude Projects & Knowledge Management Custom Skills & Instructions Studio — skill.md + instructions.md

### Use Case

Retail Orders pipeline only. One file pack for this pipeline.

### Key Topics

- Start from the Orders workflow already layered (ingest, quality, transform, contract)

- How to identify skill requirements: reusable vs one-off

- skill.md structure: name, trigger, procedure, constraints, examples, expected output, non-goals

- instructions.md structure: role, guidelines, constraints, trusted context, expected outputs, escalation / HITL

- Claude Projects custom instructions as the runtime of instructions.md; CLAUDE.md as the repo-level twin

- When to use instructions (always-on) vs a skill (task-triggered) vs a turn-level prompt

- Grounding: schema, sample data, certified definitions

- Versioning; what must never sit in a skill (secrets, UAT-locked paths)

- End-to-end wiring: instructions + skill + prompt → one working Orders path

### Hands On Lab Scenarios

- From the Orders layer map, name 2–3 skills. Must include schema-to-pipeline and orders data-quality checks.

- Author skill.md #1 (schema-to-pipeline). Trainer walks each section with rationale: trigger, steps, constraints, example, output, non-goals.

- Author skill.md #2 (orders quality checks) the same way.

- Author instructions.md for an Orders DE copilot: guidelines, constraints (no PII in logs, HITL before gold write), trusted schema/sample, expected outputs.

- Load instructions.md as Claude Project custom instructions and/or CLAUDE.md. Add both skills.

- Blank-page prompt for one layer; explain why each block exists; run using only the files just written (no pasted trainer prompt).

- End-to-end: ingest → quality → contract with those files. Score on the prompt rubric.

- Failure drill: remove one constraint from instructions.md; show the regression; restore it.

### Learning Outcomes

- Identify skills from a DE workflow (not from a blank template dump)

- Author a working skill.md and instructions.md with guidelines, constraints, and output contracts

- Explain how instructions, skills, and a turn-level prompt work together

- Load and test the pack in Claude Projects and/or Claude Code

### Claude Tools and APIs

Claude.ai (Projects) · Knowledge base upload · Custom instructions · Claude in Cowork · Retrieval quality eval

### UAT and Quality Gate

Gate: Claude Project Q&A accuracy ≥ 80% on 20-question test suite before recommending for stakeholder use.

P3 · Model Development \| 1.5 hours \| Lab

## M6 Building Claude-Powered Applications

### Use Case

Retail Orders pipeline assistant (same orders data).

### Key Topics

- Claude API: authentication, messages endpoint, streaming, error handling

- Python Anthropic SDK: request–response cycle

- Conversation management: multi-turn threads, context-window budgeting

- Streaming for real-time UX

- Tool use (function calling): scoped tools on real data

- Minimal app: FastAPI backend + Streamlit frontend

- System prompt from the participant’s instructions.md — not a generic demo bot

### Hands On Lab Scenarios

- Build FastAPI POST /chat with conversation history. System prompt = the participant’s Orders instructions.md.

- Streaming: async Claude response in the UI while asking “show yesterday’s orders quality failures”.

- One tool on the Orders dataset (schema lookup or run the orders quality-check skill). Test 3 tool-call scenarios.

- Streamlit UI: pipeline status / exceptions; show structured output aligned to the data contract.

- Local run: 10 conversation tests on Orders only, including 3 that must call the Orders tool.

### Learning Outcomes

- Build a Claude-powered app with the Anthropic Python SDK

- Implement streaming and multi-turn state

- Extend Claude with tool use against the Orders dataset

- Wire the app to the written instructions/skills, not a pasted generic bot prompt

### Claude Tools and APIs

Anthropic Python SDK · FastAPI · Streamlit · Claude API (messages, streaming, tool use) · dotenv / Secret Manager

### UAT and Quality Gate

Gate: Claude-powered API passes functional test suite (10 conversation scenarios, 3 tool-use scenarios) before moving to RAG or agentic build.

P3 · Model Development \| 1.5 hours \| Lecture / Lab

## M7 RAG with Claude API — Retrieval-Augmented Generation

### Use Case

Retail Orders pipeline.

### Key Topics

- RAG architecture: embed → store → retrieve → inject → generate

- Embedding models: Voyage AI embeddings (Anthropic-recommended), OpenAI ada

- Vector stores: pgvector, FAISS, Pinecone — trade-offs for Claude RAG

- Chunking strategies: fixed, recursive, semantic — impact on retrieval quality

- Context injection patterns: how to format retrieved chunks in Claude's prompt

- RAGAS evaluation: faithfulness ≥ 0.85, answer relevance ≥ 0.80, context recall ≥ 0.75

- Advanced: HyDE, re-ranking with Cohere, multi-query retrieval

### Hands On Lab Scenarios

- Naive RAG: load the Orders pack (data contract, schema, quality rules, gold KPI definitions) → chunk → embed (Voyage AI) → FAISS → Claude generation.

- Evaluate with RAGAS: faithfulness, answer relevance, context recall on an Orders Q&A set (late orders, quality failures, KPI definitions).

- Improve: add multi-query retriever + Cohere re-ranker; measure RAGAS delta.

- Target: Answer Correctness ≥ 80% before treating this RAG as production-ready.

### Learning Outcomes

- Build production RAG pipelines with Claude as the generation layer

- Evaluate RAG quality with RAGAS and iterate until thresholds are met

- Apply advanced retrieval techniques to improve answer quality over naive baseline

### Claude Tools and APIs

Anthropic Python SDK · Voyage AI Embeddings · FAISS / pgvector · LangChain (retrieval) · RAGAS · Cohere Rerank

### UAT and Quality Gate

Gate: RAG system must meet RAGAS thresholds (faithfulness ≥ 0.85, answer relevance ≥ 0.80) on 50-question golden dataset before deployment.

P3 · Model Development \| 1.5 hours \| Agent Lab

## M8 Agentic Workflows with Claude

### Use Case

Retail Orders pipeline.

### Key Topics

- Claude as an agent: reasoning, tool selection, multi-step execution, error recovery

- Tool use patterns: search, code execution, database query, external API calls

- Multi-agent architectures: orchestrator + subagent patterns with Claude

- Human-in-the-loop (HITL) design: when Claude must pause and ask before acting

- Anti-patterns: blind agent approval, unbounded loops, secrets in context, over-trust

- Claude's extended thinking mode for complex multi-step reasoning tasks

### Hands On Lab Scenarios

- Tool-using agent: Claude receives an Orders exception question (late orders, quality failures, KPI drift) → searches the Orders pack / queries the Orders dataset → synthesises an answer with citations.

- Multi-step agent: receive a data request → query Orders → analyse → write an exception report → draft a summary (send is simulated, not live).

- HITL lab: agent must pause and ask before irreversible actions (write to gold, auto-fix quality rules, send the summary).

- Extended thinking lab: enable extended thinking for a complex Orders root-cause task; compare to standard mode.

### Learning Outcomes

- Design and build reliable Claude agents with well-scoped tool sets

- Apply HITL design patterns for responsible agentic AI

- Use extended thinking for complex reasoning tasks that benefit from step-by-step deliberation

### Claude Tools and APIs

Anthropic Python SDK (tool use) · Claude extended thinking · LangGraph (orchestration) · External APIs · HITL approval flow

### UAT and Quality Gate

Gate: Agent eval suite: tool-call accuracy ≥ 90%, routing correctness ≥ 85%, no unintended side effects on 20 test scenarios before deployment.

P3 · Model Development \| 1.5 hours \| Lab

## M9 Claude Code for AI-Assisted Development

### Use Case

Retail Orders pipeline.

### Key Topics

- Claude Code: Anthropic's agentic CLI tool for software development

- Claude Code architecture: reads codebase → plans → edits files → runs commands → iterates

- CLAUDE.md: project context file (parallel to .cursorrules) — what Claude Code knows about your repo

- Slash commands, custom sub-agents, MCP server integration

- Claude Code for complex refactors, feature builds, bug fixes, test generation

- UAT protection in Claude Code: CLAUDE.md NEVER_MODIFY section, /diff before accepting changes

### Hands On Lab Scenarios

- Install Claude Code. Write CLAUDE.md for the Orders pipeline (ingest / quality / transform / gold). NEVER_MODIFY: data contract, gold schema, quality thresholds, secrets.

- Feature build: scaffold one Orders service (e.g. quality-check CLI or exception-report endpoint). Review each change before accepting.

- /diff discipline: inspect every Claude Code change; reject any edit to UAT-locked files.

- Same multi-file Orders task in Claude Code vs Cursor Composer — document strengths.

### Learning Outcomes

- Use Claude Code as a powerful agentic coding assistant for complex development tasks

- Configure CLAUDE.md to encode project context and UAT protection constraints

- Apply /diff review discipline to every Claude Code session — never accept changes blindly

### Claude Tools and APIs

Claude Code CLI · CLAUDE.md · MCP servers · Slash commands · git diff / /diff review · VS Code integration

### UAT and Quality Gate

Gate: CLAUDE.md committed to repo with NEVER_MODIFY section before any Claude Code generation. /diff review mandatory — any modification to locked files rejected before acceptance.

P4 · Training & Evaluation \| 1.5 hours \| Eval / Lab

## M10 Evaluation & Testing Claude Outputs

### Use Case

Retail Orders pipeline.

### Key Topics

- Eval taxonomy: correctness, groundedness, faithfulness, safety, latency, cost

- Anthropic Console: built-in eval runner for prompt and model comparison

- DeepEval: unit tests for LLM outputs — assert correctness, hallucination, toxicity

- PromptFoo: regression testing across prompt versions — block release if score drops

- LLM-as-judge: using Claude Opus to evaluate Claude Sonnet outputs

- Building a golden dataset: 100-question benchmark for your use case

- Local eval gate: a script that blocks release if eval score drops \> 5%

### Hands On Lab Scenarios

- DeepEval suite for the Orders assistant (10 cases: correctness + hallucination on late orders, quality failures, KPI definitions).

- PromptFoo: run the suite across 3 prompt versions of the same Orders task; identify which version regresses.

- Local eval gate: run a DeepEval / PromptFoo script; if faithfulness is below threshold, the release is blocked (trainer sign-off on the fail).

- Golden dataset: 100-question Orders benchmark; measure and document baseline scores.

### Learning Outcomes

- Embed evals into the development lifecycle — test before shipping (EDD at P4)

- Build regression suites that catch Claude quality drops before production

- Operate an automated local eval gate that blocks release if Claude quality drops

### Claude Tools and APIs

Anthropic Console (eval) · DeepEval · PromptFoo · GitHub Actions · LLM-as-judge (Claude Opus) · Golden dataset template

### UAT and Quality Gate

Gate: Eval suite with ≥ 20 test cases must pass before any Claude application is deployed. CI eval gate active in team repo.

P5 · Deployment & Monitoring \| 1.5 hours \| Lab

## M11 Production Deployment & API Integration

### Use Case

Retail Orders pipeline.

### Key Topics

- Production architecture: FastAPI + Claude API + vector store + cache layer

- Semantic caching: reducing API cost by caching semantically similar queries

- Rate limiting and cost management: token budgets, model routing, fallbacks

- Environment management: API key secrets (Secret Manager / AWS Secrets Manager)

- Containerisation: Docker + Docker Compose for Claude-powered services

- Health checks, graceful degradation, and circuit breakers for Claude API calls

- Deployment to Cloud Run, AWS Lambda, or Azure Functions

### Hands On Lab Scenarios

- Package the Orders assistant API into a Docker container; deploy to Cloud Run.

- Semantic caching on Orders queries; measure API cost reduction.

- Rate limiting: token budget per user; test with concurrent requests.

- Health check and graceful degradation: fallback response when the Claude API is unavailable.

### Learning Outcomes

- Deploy Claude-powered applications to production with proper secrets, caching, and rate management

- Reduce API cost with semantic caching and model routing

- Build resilient Claude services with health checks and graceful degradation

### Claude Tools and APIs

Anthropic Python SDK · FastAPI · Docker · Cloud Run / AWS Lambda · Secret Manager · Redis (semantic cache) · Prometheus / Grafana

### UAT and Quality Gate

Gate: Production deployment checklist complete: secrets in Secret Manager, rate limiting active, health check endpoint passing, eval gate green, Docker image scanned.

P6 · Continuous Learning & Optimisation \| 2.5 hours \| Assessment

## M12 Responsible AI, Governance & Continuous Learning

### Use Case

Business Generic case study

### Key Topics

- Anthropic's Responsible AI principles: Constitutional AI, harm avoidance, transparency

- Data privacy: what data leaves the environment; what Claude must not invent or expose

- Prompt injection: detection and mitigation on this system prompt

- Transfer test: unseen generic business persona (not Retail Orders) — layer the job, then write new instructions.md and skill.md from a blank page

- Prompt design with rationale: role, context, constraints, output, success test

- Independent submit: file pack + one prompt with written rationale

### Hands On Lab Scenarios

- Read the brief (10 min). No sample prompts. No ready skill.md.

- Layer reusable vs one-off (10 min).

- Write new instructions.md + new skill.md (40 min).

- Design 2 prompts from a blank page, each with rationale (20 min).

- e2e: files + Excel → Monday briefing; 10 test questions; fail if invented KPIs or jargon (25 min).

- RAI checklist + 5 injection attacks; harden the two that work (10 min).

- Submit: new files + one prompt with rationale.

### Learning Outcomes

- Independently design prompts and custom skills for an unseen business persona

- Operate Claude with a responsible-AI and privacy bar on a live briefing

- Defend the new system prompt against prompt injection

### Claude Tools and APIs

Anthropic Console · Claude API safety filters · Production eval tracking · SKILL.md library · CoP knowledge base · Prompt injection test suite

### UAT and Quality Gate

Gate: Responsible AI audit passed, prompt injection defence verified, production monitoring active, CoP entry submitted. Final capstone reviewed against full AIDLC checklist.

## Appendix Original Module Content

These topics, labs and outcomes come from the original columns in the workbook.

### M1 Claude Ecosystem & AIDLC Mindset

#### Key Topics

- AIDLC 6-phase framework — where Claude fits at each phase

- Claude product landscape: Claude.ai, Claude API, Claude Code, Claude in Chrome, Cowork mode

- Model tiers: Claude Haiku (speed), Sonnet (balanced), Opus (reasoning) — when to use each

- Claude vs other LLMs: strengths in long-context, code, analysis, and instruction-following

- Responsible AI: Anthropic's Constitutional AI approach, safety layers, usage policies

- AI scope definition: what Claude CAN and CANNOT do safely in enterprise context

#### Hands On Labs

- Map Claude product tiers to AIDLC phases for a sample use case

- Compare Claude Haiku vs Sonnet vs Opus on the same complex prompt — cost/quality analysis

- Draft an AI Scope Statement for a Claude-powered feature: what data Claude sees, what it doesn't

- Identify 3 use cases in your organisation where Claude adds the most value

#### Learning Outcomes

- Understand Claude's ecosystem, model tiers, and AIDLC positioning

- Choose the right Claude model for a given task (cost vs quality trade-off)

- Apply responsible AI and data governance principles before any Claude integration

### M2 Prompt Engineering for Claude

#### Key Topics

- Claude's prompt anatomy: system prompt, human turn, assistant turn

- Context window management: Claude's 200K token window — what to include and what to leave out

- Prompting techniques: chain-of-thought, few-shot, role prompting, XML tagging

- System prompts as product configuration: persona, constraints, output format

- Prompt anti-patterns: vague instructions, missing constraints, over-trusting outputs

- Eval-Driven Prompting: write the success criteria before writing the prompt

#### Hands On Labs

- Build a system prompt for a customer support bot — iterate through 3 versions, measure improvement

- Few-shot prompting lab: provide 3 examples; observe Claude's style alignment

- XML tagging lab: structure a complex prompt with \<context\>, \<task\>, \<constraints\>, \<format\> blocks

- Eval-Driven Prompting: define pass/fail criteria for a prompt BEFORE writing it; test against 10 inputs

#### Learning Outcomes

- Write reproducible, well-structured prompts that produce consistent Claude outputs

- Use system prompts to configure Claude as a reliable product component

- Apply Eval-Driven Prompting — define success before building

### M3 Use Case Scoping & Feasibility with Claude

#### Key Topics

- AI use case evaluation framework: value vs complexity vs risk matrix

- Claude capabilities map: what Claude does well (analysis, code, writing, reasoning) vs limitations (real-time data, calculation errors, hallucination risk)

- Feasibility assessment: data availability, latency requirements, cost modelling

- Responsible AI use case checklist: bias risk, data privacy, human-in-the-loop requirements

- Build vs buy decision: when to use Claude API vs Claude.ai vs Claude in Cowork

- Scoping a Claude pilot: success metrics, eval criteria, rollback plan

#### Hands On Labs

- Score 5 proposed use cases on the value/complexity/risk matrix

- Feasibility lab: estimate token cost for a proposed Claude workflow using the Anthropic pricing calculator

- Responsible AI checklist: assess a sample use case for bias risk, PII exposure, HITL needs

- Draft a one-page Claude pilot scope document for your highest-priority use case

#### Learning Outcomes

- Score and prioritise AI use cases rigorously before building

- Assess feasibility across cost, latency, data, and risk dimensions

- Produce a scoped, responsible Claude pilot definition with clear success criteria

### M4 Document & Data Processing with Claude

#### Key Topics

- Claude as a document intelligence engine: summarisation, extraction, classification, comparison

- Processing large documents: 200K context window — PDFs, reports, contracts, code

- Structured data extraction: JSON output mode, function calling for schema-bound outputs

- Multi-document synthesis: research aggregation, competitive analysis, audit trail

- Data cleaning and preparation with Claude: normalising messy inputs before downstream processing

- Batch processing patterns: processing 100s of documents efficiently via API

#### Hands On Labs

- Extract structured data from 10 sample PDFs using Claude with JSON output mode

- Multi-document synthesis: load 5 research reports; ask Claude to produce a structured comparison table

- Batch processing lab: loop through 50 short documents; summarise each; aggregate into master report

- Data cleaning: provide messy CSV data; use Claude to produce normalised, validated output

#### Learning Outcomes

- Use Claude as a production document processing engine (P2 data preparation)

- Extract structured, schema-bound data from unstructured documents reliably

- Design batch processing workflows for high-volume document intelligence tasks

### M5 Claude Projects & Knowledge Management Custom Skills & Instructions Studio — skill.md + instructions.md

#### Key Topics

- Claude Projects: persistent context, uploaded knowledge bases, custom instructions

- Building a team knowledge base in Claude Projects: document corpus upload, retrieval quality

- Custom instructions as system prompt layer: persona, style, constraints per project

- Use cases: technical documentation assistant, policy Q&A bot, onboarding guide chatbot

- Knowledge base curation: what to include, how to chunk, how to test retrieval quality

- Projects vs API-based RAG — trade-offs and when to use each

#### Hands On Labs

- Build a Claude Project for a sample use case: upload 10 documents; write custom instructions; test Q&A quality

- Knowledge base retrieval test: generate 20 questions from the documents; measure answer accuracy

- Custom instructions iteration: improve system prompt until answer accuracy ≥ 80%

- Compare Projects (no-code) vs API RAG (M7) on the same use case — document trade-offs

#### Learning Outcomes

- Build and operate Claude Projects as no-code knowledge management systems

- Curate knowledge bases that improve Claude's answer quality and reduce hallucination

- Know when Projects is sufficient vs when API-based RAG (M7) is needed

### M6 Building Claude-Powered Applications

#### Key Topics

- Claude API fundamentals: authentication, messages endpoint, streaming, error handling

- Python Anthropic SDK: building a complete request-response cycle

- Conversation management: multi-turn threads, context window budgeting

- Streaming responses for real-time UX

- Tool use (function calling): giving Claude access to external tools (search, calculator, database)

- Building a minimal Claude-powered chatbot end-to-end: FastAPI backend + Streamlit frontend

#### Hands On Labs

- Build a Claude-powered REST API with FastAPI: POST /chat endpoint with conversation history

- Streaming lab: implement real-time streaming response with async Claude API call

- Tool use lab: give Claude a weather search tool and a calculator tool; test tool invocation quality

- End-to-end: Claude chatbot with FastAPI backend + Streamlit frontend deployed locally

#### Learning Outcomes

- Build production-quality Claude-powered applications using the Anthropic Python SDK

- Implement streaming for responsive UX; manage multi-turn conversation state

- Extend Claude with tool use — connect it to real-world data and functions

### M7 RAG with Claude API — Retrieval-Augmented Generation

#### Key Topics

- RAG architecture: embed → store → retrieve → inject → generate

- Embedding models: Voyage AI embeddings (Anthropic-recommended), OpenAI ada

- Vector stores: pgvector, FAISS, Pinecone — trade-offs for Claude RAG

- Chunking strategies: fixed, recursive, semantic — impact on retrieval quality

- Context injection patterns: how to format retrieved chunks in Claude's prompt

- RAGAS evaluation: faithfulness ≥ 0.85, answer relevance ≥ 0.80, context recall ≥ 0.75

- Advanced: HyDE, re-ranking with Cohere, multi-query retrieval

#### Hands On Labs

- Build Naive RAG: PDF loader → chunk → embed (Voyage AI) → FAISS → Claude generation

- Evaluate with RAGAS: measure faithfulness, answer relevance, context recall

- Improve: add multi-query retriever + Cohere re-ranker; measure RAGAS delta

- Target: Answer Correctness ≥ 80% before considering RAG production-ready

#### Learning Outcomes

- Build production RAG pipelines with Claude as the generation layer

- Evaluate RAG quality with RAGAS and iterate until thresholds are met

- Apply advanced retrieval techniques to improve answer quality over naive baseline

### M8 Agentic Workflows with Claude

#### Key Topics

- Claude as an agent: reasoning, tool selection, multi-step execution, error recovery

- Tool use patterns: search, code execution, database query, external API calls

- Multi-agent architectures: orchestrator + subagent patterns with Claude

- Human-in-the-loop (HITL) design: when Claude must pause and ask before acting

- Anti-patterns: blind agent approval, unbounded loops, secrets in context, over-trust

- Claude's extended thinking mode for complex multi-step reasoning tasks

#### Hands On Labs

- Build a research agent: Claude receives a question → searches web → synthesises → cites sources

- Multi-step agent: receive a data request → query database → analyse → write report → email summary

- HITL lab: build an agent that pauses and asks for human confirmation before irreversible actions

- Extended thinking lab: enable extended thinking for a complex analytical task; compare to standard mode

#### Learning Outcomes

- Design and build reliable Claude agents with well-scoped tool sets

- Apply HITL design patterns for responsible agentic AI

- Use extended thinking for complex reasoning tasks that benefit from step-by-step deliberation

### M9 Claude Code for AI-Assisted Development

#### Key Topics

- Claude Code: Anthropic's agentic CLI tool for software development

- Claude Code architecture: reads codebase → plans → edits files → runs commands → iterates

- CLAUDE.md: project context file (parallel to .cursorrules) — what Claude Code knows about your repo

- Slash commands, custom sub-agents, MCP server integration

- Claude Code for complex refactors, feature builds, bug fixes, test generation

- UAT protection in Claude Code: CLAUDE.md NEVER_MODIFY section, /diff before accepting changes

#### Hands On Labs

- Install Claude Code; configure CLAUDE.md with project context and NEVER_MODIFY list

- Feature build lab: scaffold a new service using Claude Code; review each change before accepting

- /diff discipline: inspect every Claude Code change; reject any modification to UAT-locked files

- Compare Claude Code vs Cursor Composer on the same multi-file task — document strengths

#### Learning Outcomes

- Use Claude Code as a powerful agentic coding assistant for complex development tasks

- Configure CLAUDE.md to encode project context and UAT protection constraints

- Apply /diff review discipline to every Claude Code session — never accept changes blindly

### M10 Evaluation & Testing Claude Outputs

#### Key Topics

- Eval taxonomy: correctness, groundedness, faithfulness, safety, latency, cost

- Anthropic Console: built-in eval runner for prompt and model comparison

- DeepEval: unit tests for LLM outputs — assert correctness, hallucination, toxicity

- PromptFoo: regression testing across prompt versions — block deployment if score drops

- LLM-as-judge: using Claude Opus to evaluate Claude Sonnet outputs

- Building a golden dataset: 100-question benchmark for your use case

- CI eval gate: GitHub Actions blocking PR if eval score drops \> 5%

#### Hands On Labs

- Build DeepEval test suite for a Claude-powered chatbot (10 test cases covering correctness + hallucination)

- PromptFoo regression lab: run suite across 3 prompt versions; identify which version regresses

- Build GitHub Actions eval gate: PR blocked if faithfulness drops below threshold

- Golden dataset lab: generate 100-question benchmark; measure and document baseline scores

#### Learning Outcomes

- Embed evals into the development lifecycle — test before shipping (EDD at P4)

- Build regression suites that catch Claude quality drops before production

- Operate an automated eval gate in CI/CD for Claude-powered applications

### M11 Production Deployment & API Integration

#### Key Topics

- Production architecture: FastAPI + Claude API + vector store + cache layer

- Semantic caching: reducing API cost by caching semantically similar queries

- Rate limiting and cost management: token budgets, model routing, fallbacks

- Environment management: API key secrets (Secret Manager / AWS Secrets Manager)

- Containerisation: Docker + Docker Compose for Claude-powered services

- Health checks, graceful degradation, and circuit breakers for Claude API calls

- Deployment to Cloud Run, AWS Lambda, or Azure Functions

#### Hands On Labs

- Package a Claude-powered API into Docker container; deploy to Cloud Run

- Semantic caching lab: implement caching layer; measure API cost reduction

- Rate limiting lab: implement token budget per user; test with concurrent requests

- Health check and graceful degradation: build a fallback response when Claude API is unavailable

#### Learning Outcomes

- Deploy Claude-powered applications to production with proper secrets, caching, and rate management

- Reduce API cost with semantic caching and model routing

- Build resilient Claude services with health checks and graceful degradation

### M12 Responsible AI, Governance & Continuous Learning

#### Key Topics

- Anthropic's Responsible AI principles: Constitutional AI, harm avoidance, transparency

- Prompt injection attacks: detection and mitigation patterns for Claude applications

- Data privacy: what data leaves your environment, Anthropic's data handling commitments

- Monitoring Claude in production: output quality, hallucination rate, user feedback, latency

- Eval regression tracking: alert when production eval score drops below threshold

- SKILL.md library for Claude: versioning reusable prompt templates as governed artefacts

- Community of Practice: capturing Claude incidents and sharing learnings cross-team

#### Hands On Labs

- Responsible AI audit: assess your Claude application against Anthropic's usage policies and a responsible AI checklist

- Prompt injection defence lab: test 10 injection attempts against your system prompt; harden and retest

- Production monitoring dashboard: set up eval score tracking and hallucination rate alerts

- CoP Lab: document one real or simulated Claude incident; write root cause + SKILL.md fix; publish to shared library

- Capstone: end-to-end AIDLC workflow — scope → prompt → build → eval → deploy → CoP entry

#### Learning Outcomes

- Operate Claude applications responsibly with governance, monitoring, and privacy controls

- Defend against prompt injection and maintain safe, grounded Claude outputs in production

- Run CoP forum and SKILL.md library for continuous, cross-team Claude improvement
