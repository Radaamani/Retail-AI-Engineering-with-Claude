---
marp: true
theme: default
paginate: true
---

<!-- _class: lead -->

# M0 · Python with Nano Bank

**Tredence · Claude Application Development**

Revisit yesterday’s setup by tracing one request from Python to the database and back.

<!--
Plan for 35 minutes. Spend 3 on why Python, 7 on uv and libraries, 17 running the app and tracing the statement through the source, and 8 on the lab and handoff. For 30 minutes, use yesterday’s setup and demo one rejected request as a group. For 40 minutes, let pairs run all three checks and explain their results.
-->

---

# Why Python is useful for AI applications

- **Reads close to English.** Use the code to explain the rule.
- **Deep ecosystem.** `httpx` sends requests, FastAPI exposes the API, and SQLModel works with SQLite.
- **One language for the workflow.** Load data, apply rules, call a model, validate the result, and log what happened.

Today, trace one Nano Bank request end to end. All examples use `nano-sandbox-bank-snippets/`.

<!--
An AI engineer ships and operates a feature. An AI researcher improves models. Today we are building around an existing model. Python’s advantages here are library depth and fast feedback. If asked about Java, TypeScript or C, compare the same bank rule in a language the room knows. The rule is portable, and the ecosystem determines how much glue the team writes.
-->

---

# Install uv and Python 3.13

Check uv in a terminal. If it is missing, follow the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) for your operating system, then reopen the terminal.

```bash
uv --version
uv python install 3.13
```

`uv` manages the project’s Python interpreter, virtual environment, and libraries.

<!--
Most learners did this yesterday. Spend one or two minutes here. Homebrew users can run `brew install uv`. On Windows, use PowerShell and `winget install --id=astral-sh.uv -e` if WinGet is available. The install guide has standalone options for each platform. Reopen the terminal if a newly installed uv is missing from PATH. The sandbox’s WINDOWS_UV_TROUBLESHOOTING.md uses 3.12 in examples. Substitute the classroom pin, 3.13.
-->

---

# Set up the Nano Bank environment

From the repository root:

```bash
cd nano-sandbox-bank-snippets
uv sync
uv run python --version
uv run python hello-world.py
```

Expect Python **3.13.x** and `Simple Python Program running with UV`.

`uv sync` creates or updates `.venv` and installs the project’s libraries. `uv run` uses that environment directly.

<!--
Open the three project files. `pyproject.toml` declares dependencies such as FastAPI, Uvicorn, SQLModel, Faker, Loguru, and httpx. `uv.lock` records the resolved versions. `.python-version` selects Python 3.13 for the classroom project. A working `uv run` uses the project interpreter without manual activation. First-time setup may need access to the package registry.
Reference: https://docs.astral.sh/uv/guides/projects/
-->

---

# Install a library in a new project

In a separate scratch folder, outside the Nano Bank project:

```bash
uv init nano-bank-practice --python 3.13
cd nano-bank-practice
uv add httpx
uv run python -c "import httpx; print(httpx.__version__)"
```

- `uv init` creates project files.
- `uv add httpx` declares and installs a new dependency and updates `uv.lock`.
- Use `uv sync` when joining an existing project like Nano Bank.

<!--
Ask why `import httpx` works after `uv add`. Then show where the existing Nano Bank project declares httpx for its client. Learners who already have Nano Bank running can watch the scratch-project demo. Use a fresh folder name for a repeat demo.
Reference: https://docs.astral.sh/uv/guides/projects/#managing-dependencies
-->

---

# Follow the request

```text
httpx client → FastAPI route → Python rules → SQLite
             ← JSON response ← computed fields
```

| Where | Classroom file |
|---|---|
| Client that sends GET and POST | `nano-bank-client.py` |
| Routes, models, and business rules | `nano-bank.py` |
| Local data that survives a restart | `nano_bank_simple.db` |

<!--
Show the two Python files side by side. Uvicorn runs the app. FastAPI routes and validates HTTP requests. SQLModel connects Python models to SQLite. Faker supplies synthetic merchant names and Loguru records the write operations. As learners trace the request, point out the variables, functions, classes, storage, server, and logs.
-->

---

# Start the app and read a statement

From `nano-sandbox-bank-snippets/`, in terminal 1:

```bash
uv run python nano-bank.py
```

Open [the interactive API docs](http://127.0.0.1:8000/docs). Execute:

```text
GET /accounts/ACC101/statement/2025/1
```

Expect `200 OK`. Find `total_deposits`, `total_withdrawals`, `net_flow`, and `current_balance` in the JSON.

<!--
This is a read. The January totals are 5,000 deposited, 180 withdrawn, and 4,820 net. Current balance is 157,840 USD on a freshly seeded database and may differ if students used the client yesterday. Leave the server running for the later activities.
-->

---

# Functions and route parameters

From `nano-bank.py`, abridged:

```python
@app.get("/accounts/{account_id}/statement/{year}/{month}")
def statement(account_id: str, year: int = Path(ge=1),
              month: int = Path(ge=1, le=12)):
    account = get_account(account_id)
    period = f"{year:04d}-{month:02d}"
    # Query this account and period, then compute totals.
```

For `ACC101`, `2025`, and `1`, the formatted `period` is `2025-01`. Descriptive names and type hints make the inputs and purpose easy to read. FastAPI checks the month range before the function runs.

<!--
Point out the decorator, typed parameters, the local variable, the called function, and the f-string. Try month 13 from /docs and ask where it was rejected. This excerpt leaves out the query and return so the inputs are easy to see.
-->

---

# Classes and input validation

```python
class Account(SQLModel, table=True):
    id: str = Field(primary_key=True)
    owner: str
    balance: int = 100000

class AmountRequest(BaseModel):
    amount: StrictInt = Field(gt=0)
```

`Account` represents a stored record. `AmountRequest` checks incoming JSON. `{"amount": 500}` passes. A string, fraction, or zero returns `422`.

<!--
Show the Transaction class in the source as well. The opening default is 100,000 before the synthetic 2025 transactions are seeded. StrictInt and Field(gt=0) enforce whole positive USD at the request boundary. Type hints alone are annotations in ordinary Python functions.
-->

---

# SQLite stores the facts. Python computes the totals.

The statement route reads this account’s transactions for the selected month, then sums deposit and withdrawal amounts separately.

| January 2025 for `ACC101` | USD |
|---|---:|
| Deposits | 5,000 |
| Withdrawals | 180 |
| Net flow | 4,820 |

`current_balance` comes from the account record. It can change when a transaction is posted in a different month.

<!--
Show the SQLModel select and the two sum expressions in the source. Discuss the two filters: account ID identifies whose rows, and the date prefix identifies the period. SQLModel keeps values separate from query structure. Ask students why the January cash flow stays the same after a November 2026 deposit. This distinction becomes the fact-check in M1.
-->

---

# Read and write from Python

In terminal 2, from `nano-sandbox-bank-snippets/`:

```bash
uv run python nano-bank-client.py
```

1. Read the January 2025 statement.
2. Deposit **500 USD** and withdraw **100 USD**.
3. Read the November 2026 statement.

Each run adds two transactions and increases the balance by **400 USD**. Check the two requests in the server logs.

<!--
Open nano-bank-client.py and point out httpx.get, httpx.post with json=, and response.json(). New records use the fixed classroom date 2026-11-06. The same method, URL and body work in /docs or Postman. If yesterday’s database already has writes, compare before and after values.
-->

---

# Quick lab · Logging, testing, and debugging

Work in `/docs`. Check `ACC101`’s current balance first.

| Request | Your prediction |
|---|---|
| Withdraw `{"amount": 0}` | Which rule rejects it? |
| Withdraw `{"amount": 999999}` | Which rule rejects it? |
| Read January for `UNKNOWN` | Which lookup fails? |

Run the zero withdrawal as a group. In pairs, try the other requests if time allows. Record the status codes and check the balance after the rejected withdrawals.

<!--
Zero returns 422 because request validation runs before the route. The oversized withdrawal returns 409 on the classroom data because the balance is insufficient. The missing account returns 404 from get_account. Both rejected withdrawals leave the balance unchanged. If the seeded balance has been altered above the example amount, use a whole dollar amount greater than the displayed balance. Compare the HTTP status and JSON error with the Loguru success message produced after a committed withdrawal. Predict, run, look at the result, and change one thing. A notebook or REPL can help explore data and a small calculation. Keep the reusable rule in the .py module, where a teammate can read and test it.
-->

---

# Take one verified result into M1

Keep the January statement open. Be ready to point to:

- **The route** that produced the JSON.
- **The fields** that describe January’s activity.
- **The balance** that describes the account now.

In M1, Claude will explain this statement in plain language. We’ll check its explanation against these same fields.

<!--
The existing chatbot, rag and agent functions are placeholders for later exercises. Leave the server running for the M1 demonstration. The January values are also printed in the M1 deck so the exercise can continue if the server is unavailable.
-->
