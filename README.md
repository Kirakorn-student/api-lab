# API Lab — pytest and requests

**Course:** ITDS362 — Software Quality Assurance and Testing  
**Lab:** API Testing with pytest and requests  
**Target API:** [QuickPizza](https://quickpizza.grafana.com)  
**Python:** 3.10 or newer

This repository contains the API-testing exercise from the W10 lab. The tests send real HTTP requests to QuickPizza. They are integration tests: they exercise the API server, request handling, authentication and stored data together.

## 1. Requirements

Install or prepare:

- Python 3.10+
- Git
- curl
- Visual Studio Code or another editor with a terminal
- A GitHub repository named `api-lab` (Public, as required by the lab)

The repository should be cloned to a normal local folder, not inside OneDrive, iCloud Drive or Google Drive.

## 2. Set up the project

### Windows PowerShell

Open PowerShell in the repository folder:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
curl.exe --version
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate the environment again.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
curl --version
```

## 3. Run the tests

Run the complete test suite:

```bash
pytest -v
```

The lab's expected final result is **32 passed, 1 xfailed**. The xfailed test records the known defect in the "exclude all tools" case. Because this suite calls a shared public demo API, the actual result can change if the service changes or is temporarily unavailable.

Run one test by itself:

```bash
pytest -v test_ratings.py::test_delete_rating
```

Generate the required self-contained HTML report after completing the live run:

```bash
pytest -v --html=report.html --self-contained-html
```

Open `report.html` in a browser and check the results before committing it. The report included in this repository was generated from the final full run on **10 November 2026** with Python 3.12.10, pytest 9.2.0 and pytest-html 4.2.0. It contains **32 passed, 1 xfailed and 0 errors**. If the tests change, regenerate the report before submission.

## 4. Files

| File | Purpose |
|---|---|
| `conftest.py` | Shared QuickPizza session and fixtures for users, pizzas and ratings |
| `test_names.py` | Read the pizza-name list |
| `test_tools.py` | Read the available tools using the lab's public practice token |
| `test_pizza.py` | Vegetarian pizza response and missing-token refusal |
| `test_users.py` | Create/log in a new user and check the empty ratings list |
| `test_ratings.py` | Create, read, update and delete a rating |
| `test_refused.py` | Duplicate username, wrong password and empty username |
| `test_excluded_tools.py` | Input partitioning for excluded tools and the known defect |
| `test_create_rating.py` | Base choice coverage for `POST /api/ratings` |
| `test_update_rating.py` | Boundary values for `PUT /api/ratings/{id}` |
| `test_rating_owner.py` | Check that a different user cannot read, change or delete a rating |
| `auth.txt` | Public practice header used by the curl steps |
| `veg.json` | Vegetarian pizza request body for curl |
| `madeup.txt` | Made-up token for the read-only check in Part B |
| `RESULTS.md` | Live observations, defect report and reflection answers |
| `report.html` | Self-contained pytest-html report from the final full test run |

## 5. Important test-design decisions

### Independent test data

Each test that works with ratings receives a fresh user through the `auth` fixture. The user name is generated with `uuid`, then the test logs in and uses the token returned by QuickPizza.

The `api` fixture creates one `requests.Session` for the whole pytest run. It keeps the `AWSALB` cookie, which helps the load balancer route requests to the same backend server. This avoids the flaky create-user / login sequence described in Step 0.12.

The `pizza_id` fixture creates a pizza for the current test user. The `rating` fixture creates a 3-star rating and deletes it after the test, including when the test fails. Tests that create a rating directly also delete that rating after checking the response.

### Input domain model — `POST /api/ratings`

The table below follows Step A1 of the lab. Base choice uses the common valid input for each characteristic.

| Characteristic | Blocks | Test values | Test coverage |
|---|---|---|---|
| C1 — Value of stars | below 1 / 1 to 5 (base) / above 5 | 0 / 3 / 6 | `test_stars_out_of_range`, `test_base_choice_is_saved` |
| C2 — Type of stars | whole number (base) / decimal / text / missing | 3 / 3.5 / `"3"` / no field | `test_base_choice_is_saved`, `test_stars_must_be_a_whole_number` |
| C3 — Pizza | exists (base) / does not exist | a newly created pizza / `999999999` | `test_base_choice_is_saved`, `test_rating_with_unknown_pizza_is_refused` |
| C4 — Token | user's own (base) / none / wrong token | `auth` / no header / `token short` | `test_base_choice_is_saved`, `test_rating_without_token_is_refused`, `test_rating_with_short_token_is_refused` |

**Base choice test count:** 1 base test + 2 other C1 blocks + 3 other C2 blocks + 1 other C3 block + 2 other C4 blocks = **9 tests**.

**All combinations:** 3 × 4 × 2 × 3 = **72 combinations**.

### Boundary values — update rating

`test_update_rating.py` checks 0, 1, 5 and 6. The accepted values 1 and 5 must be saved with status 200. The rejected values 0 and 6 must return 400 and must not change the original rating.

### Ownership

`test_rating_owner.py` creates a rating as one user and attempts to read, update and delete it as another user. Each attempt must be refused with a 4xx status. The test then reads the rating as its owner to verify that it remains unchanged. The observed status codes are recorded in `RESULTS.md`.

## 6. QuickPizza safety rules

QuickPizza is shared by students:

- Create, change and delete only data created by your own tests.
- Never use the public token `abcdef0123456789` to create or change ratings.
- The public token in `auth.txt` is used only for the introductory practice requests in the lab; rating tests use a token obtained by logging in as a newly created test user.
- Use made-up usernames and passwords only. The fixture uses names such as `lab-<random-hex>` and the practice password `Pizza-2026`.
- `madeup.txt` is for the Part B read-only request only. Do not create, update or delete anything with that token.
- A full test run sends many requests. Run it when needed, not in a loop.

## 7. Manual observations

The live observations, exact validation messages, ownership status codes, made-up-token result and defect report are recorded in `RESULTS.md`. Step 0.12 is optional and was not performed for the recorded run. The vegetarian pizza name is random and may differ on another run.

## 8. Git workflow

After each meaningful step, commit and push:

```bash
git add .
git commit -m "Complete API lab tests"
git push
```

If Git has no identity configured yet:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Do not put real passwords, private API keys or group credentials in the repository.
