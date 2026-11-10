# API lab results

Live observations below were collected from QuickPizza on 10 November 2026. Values that can change on the shared demo service are recorded as observations from that run.

## Part 0

- Step 0.1, number of pizza names: **18** (GET /api/names returned HTTP 200).
- Step 0.3, status code of the request without a token: **401** (body: `{"error":"authentication failed"}`).
- Step 0.4, name of the vegetarian pizza: **An Empty Calzone** (observed in this run; QuickPizza selects the pizza randomly).
- Step 0.12, results of the three runs without a session (optional): **Not performed.** This experiment is optional in the lab.
- Step 0.16, blocks of "how many of the three tools are excluded":
  - 0 tools excluded: `[]`
  - 1 tool excluded: `["Knife"]` or `["Scissors"]`
  - 2 tools excluded: `["Knife", "Scissors"]`
  - 3 tools excluded: `["Knife", "Pizza cutter", "Scissors"]`
  - The 0-, 1- and 2-tool blocks returned HTTP 200 and did not use an excluded tool. The 3-tool block is the known defect described below.

## Defect report

- **Title:** Excluding all available pizza-cutting tools returns HTTP 500 with an empty response body.
- **Request:**
  - Method: `POST`
  - Path: `/api/pizza`
  - Header: Authorization token belonging to a test user created by the test fixture
  - JSON body:
    ```json
    {
      "excludedTools": ["Knife", "Pizza cutter", "Scissors"]
    }
    ```
- **Expected result:** HTTP 400 with a JSON error message explaining that no pizza can satisfy the request.
- **Actual result:** HTTP 500 with an empty response body. The dedicated regression test is retained as xfailed, as instructed by Step 0.16.
- **Severity:** **Medium.** A validly formed request with impossible constraints is a client-side input problem. Returning an empty HTTP 500 makes the failure look like an unexpected server crash and gives the calling application no useful error to display.

## Part A

### Step A2 — observed error messages

The following messages were observed by running the invalid-input tests against QuickPizza:

- C2 decimal stars: `json: cannot unmarshal number 3.5 into Go struct field Rating.stars of type int`
- C2 text stars: `json: cannot unmarshal string into Go struct field Rating.stars of type int`
- C2 missing stars field: `number of stars must be between 1 and 5 (inclusive)`
- C3 unknown pizza: `pizza ID 999999999 not found`
- C4 no Authorization header: `authentication failed`
- C4 short / invalid token: `authentication failed`

### Step A4 — status codes when another user reads, changes and deletes

- Read: **404**
- Update: **400**
- Delete: **400**

Each operation was refused with a 4xx status. The owner could still read the rating afterwards, and the rating remained unchanged.

## Part B

### 1. What can API tests find that unit tests with stubs cannot? Why write unit tests too?

API tests can find integration failures such as a route or HTTP method being wired incorrectly, and authentication or cookies not being handled correctly by the real server. They also exercise the real request handling and stored data together. Unit tests with stubs replace neighbouring components, so they cannot prove that the real server and persistence layer work together. Unit tests are still valuable because they run quickly, isolate one function and make the source of a failure easier to locate.

### 2. Why create a new user for each test instead of using the public token? How does this apply to Project 2?

Each test creates its own user so that the data belongs to that test and cannot interfere with another student's work. The public token is shared by everyone, so using it to create or change ratings could affect other students' data. In Project 2, the group should use its own shop or hotel account, create test records belonging to that group, and clean up only records that its own tests created. Group passwords and API keys must be read from environment variables, not committed to GitHub.

### 3. Why send every request through one session? What happened in the optional experiment?

A `requests.Session` keeps cookies between requests. QuickPizza sets an `AWSALB` cookie that helps the load balancer send requests to the same backend server. Keeping the cookie helps ensure that a user created on one server is logged in on that same server. Step 0.12 was optional and was not performed for this run.

### 4. Which excluded-tools block revealed the defect? Why is HTTP 500 with an empty body worse than HTTP 400 with a message? Why keep the test as xfail?

The block that excludes all three available tools revealed the defect. The API should return HTTP 400 and a JSON error because no pizza can satisfy the request. HTTP 500 with an empty body suggests an unexpected server failure and gives the calling application no useful explanation. The test remains marked xfail so the known defect stays visible without making the rest of the suite fail. With `strict=True`, the test will alert us if the API is fixed and it unexpectedly passes; the xfail marker should then be removed.

### 5. How many tests does base choice coverage need, and how many would all-combinations coverage need?

Base choice coverage needs **9 tests**:

- 1 base test
- 2 other blocks for C1
- 3 other blocks for C2
- 1 other block for C3
- 2 other blocks for C4

Total: `1 + 2 + 3 + 1 + 2 = 9`.

All-combinations coverage needs `3 × 4 × 2 × 3 = 72` tests because C1 has 3 blocks, C2 has 4, C3 has 2 and C4 has 3.

### 6. In Step A4, which status codes did the other user receive? Which codes would you expect? Is a difference a defect?

The other user received **404** when reading, **400** when updating and **400** when deleting. I would expect all three operations to be refused consistently, commonly with 403 Forbidden or with 404 Not Found if the API intentionally hides the existence of another user's rating. All three observed responses are in the required 4xx range, and the owner could still read the unchanged rating afterwards, so the tests found no successful unauthorized read, update or delete. The different status codes are an API-consistency concern; whether they are a defect depends on the API's documented error contract.

### 7. What comes back when using the made-up token to read ratings? Is it a defect, and what could a stranger do with it on a real system?

The read-only request using `Authorization: token 0000000000000000` returned **HTTP 200** and a JSON `ratings` list. This is an authentication defect because a made-up token was accepted for a protected read operation. On a real system, a stranger could potentially read rating records that should not be public. Only a GET request was made with this token; no data was created, changed or deleted with it.

### 8. What does an API test check better than a web-page test, and what can only a web-page test check?

An API test checks HTTP status codes, response headers and JSON fields directly and precisely. A web-page test can check what a person actually sees and uses, such as page layout, visible text, buttons, forms, navigation and whether an error message is displayed in the right place.

## Final report

- Full test command: `pytest -v --html=report.html --self-contained-html`
- Final result: **32 passed, 1 xfailed, 0 errors** (33 tests collected; Python 3.12.10, pytest 9.2.0; 10 November 2026).
- HTML report: **Generated as a self-contained pytest-html report.** The generated file was checked for report content. Open `report.html` in a browser before submitting to review its test details.
