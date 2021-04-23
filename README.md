# molotov-tests

## INSTALLATION

```sh
# Setting up Python3 virtual environment.
python3 -m venv ./venv
source ./venv/bin/activate

# Install molotov locally.
echo "molotov" > requirements.txt
pip install -r requirements.txt
```

```sh
# Confirm molotov is installed locally.
molotov --version # 2.1
```

## LOCAL SERVER (OPTIONAL)

```sh
# Start local webserver (if needed; run this command in a separate Terminal since it's blocking).
# If you're testing against a remote server you can skip this step.
python3 -m http.server 8080
```

## LOAD TEST SCENARIOS

```python
""" loadtest.py """
from molotov import scenario

_API = "http://localhost:8080"

# Run this scenario 1% of time (vs `scenario_two()`).
@scenario(weight=1)
async def scenario_one(session):
    print("Test scenario_one")
    async with session.get(_API + "/sample.json") as resp:
        res = await resp.json()
        # WARNING: THIS WILL FAIL
        assert res["result"] == "OKs"
        assert resp.status == 200

# Run this scenario 99% of the time (vs `scenario_one()`).
@scenario(weight=99)
async def scenario_two(session):
    print("Test scenario_two")
    async with session.get(_API + "/sample.html") as resp:
        assert resp.status == 200
```

## RUNNING LOAD TESTS

```sh
# Run your tests. The `--single-run` flag runs each scenario once only.
molotov --single-run

# NOTE: Using `--single-run` is different than `--max-runs 1`
# `--single-run` runs EACH scenario once.
# `--max-runs 1` runs one scenario.

# Verbose mode (log requests and responses).
molotov --single-run -vv

# By default, molotov will look for a load test file named `loadtest.py`. If you have multiple files with
# load test scenarios, you can specify a custom scenario file (or folder) using the scenario positional argument.
molotov --single-run my-load-tests.py

# If you want to run a specific scenario, you can use the `--single-mode` (`-s`) flag.
molotov --single-mode scenario_one --max-runs 2

# By default scenarios will run for 86, 400 seconds (24 hours).
# If you want to change the load test duration, you can set one of the following flags:
# `--single-run`: Run once every existing scenario.
# `--max-runs`: Maximum runs per worker.
# `--duration`: Duration in seconds.

# Run all load test scenarios in my-load-tests.py file for a maximum of 10 seconds.
molotov my-load-tests.py --duration 10

# If you want to stop the load tests on the first scenario failure, you can specify the `--exception` (`-x`) flag.
molotov --exception --duration 600
```
