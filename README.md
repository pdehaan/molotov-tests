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

# Run this000 scenario 1% of time (vs `scenario_two()`).
@scenario(weight=1)
async def scenario_one(session):
    # print("Test scenario_one")
    async with session.get(_API + "/sample.json") as resp:
        res = await resp.json()
        # WARNING: THIS WILL FAIL
        assert res["result"] == "OKs"
        assert resp.status == 200

# Run this scenario 99% of the time (vs `scenario_one()`).
@scenario(weight=99)
async def scenario_two(session):
    # print("Test scenario_two")
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

# By default scenarios will run for 86,400 seconds (24 hours).
# If you want to change the load test duration, you can set one of the following flags:
# `--single-run`: Run each scenario once.
# `--max-runs`: Maximum runs per worker.
# `--duration`: Duration in seconds.

# Run all load test scenarios in my-load-tests.py file for a maximum of 10 seconds.
molotov my-load-tests.py --duration 10

# If you want to stop the load tests on the first scenario failure, you can specify the `--exception` (`-x`) flag.
molotov --exception --duration 600
```

You can use the `--delay` flag to add a pause between each test execution. For example, if you specify a test run duration of 5 seconds (`--duration 5`), and a delay between each test of 1 second (`--delay 1`), then your test run will only run about 5 tests.

```sh
time molotov --duration 5 --delay 1

Preparing 1 worker...
OK
SUCCESSES: 6 | FAILURES: 0 | WORKERS: 1
```

Whereas, without the `--delay` flag, the tests will run as quickly as possible for the specified duration and you might see ~1425 test runs (depending on test complexity and network latency, etc).

```sh
time molotov --duration 5

Preparing 1 worker...
OK
SUCCESSES: 1425 | FAILURES: 0 | WORKERS: 1
```

There is no good way of predicting results from a load test run. You can run the same tests multiple times and get different results. For example, adding a second worker (a coroutine that will run the scenario concurrently) won't necessarily double the requests per second.

If we run our simple loadtest from above with a short 30s duration, we can see that adding additional workers doesn't scale the results like you might expect. This could be due to limitations of the host computer (CPU, RAM, networking, etc).

```sh
time molotov --duration 30

SUCCESSES:  8754 | FAILURES: 0 | WORKERS: 1 # BASELINE
SUCCESSES:  9208 | FAILURES: 0 | WORKERS: 2 # (+5.19% vs baseline)
SUCCESSES:  9493 | FAILURES: 0 | WORKERS: 3 # (+8.44% vs baseline)
SUCCESSES: 10214 | FAILURES: 0 | WORKERS: 4 # (+16.68% vs baseline)
SUCCESSES: 11591 | FAILURES: 0 | WORKERS: 5 # (+32.41% vs baseline)
```

So whether we use use 1 worker (default) or use 5 workers, we only see a 32% increase in requests per second.

## USING A MOLOTOV CONFIG FILE

At some point, managing all your configurations using command line flags gets too tedious and difficult to manage. You can create a test configuration file and specify the config file via the command line.

For example, if we have a file named "molotov.json" with the following contents:

```json
{
  "molotov": {
    "tests": {
      "big": {
        "duration": 30,
        "scenario": "loadtest.py",
        "workers": 100
      },
      "small": {
        "duration": 10,
        "scenario": "loadtest.py",
        "workers": 3
      },
      "smoke": {
        "duration": 1,
        "single_run": true,
        "scenario": "loadtest.py"
      }
    }
  }
}
```

We could run the "smoke" tests using the following command:

```sh
molotov --config molotov.json smoke
```

**NOTE:** Unlike the moloslave example at [Run from GitHub](https://molotov.readthedocs.io/en/stable/slave/), setting the `requirements` or `env` global options don't seem to be supported when executing load tests locally via the `--config` flag.

## TROUBLESHOOTING

1. `ModuleNotFoundError("No module named 'loadtest'")`

You'll encounter this error if you don't specify a scenario file and Molotov is unable to find the default "loadtest.py" file:

```sh
molotov --single-run
**** Molotov v2.1. Happy breaking! ****

Cannot import 'loadtest.py'
ModuleNotFoundError("No module named 'loadtest'")
  File "/Volumes/Dev/github/pdehaan/molotov-tests/venv/lib/python3.8/site-packages/molotov/run.py", line 275, in run
    import_module(args.scenario)
  File "/usr/local/Cellar/python@3.8/3.8.5/Frameworks/Python.framework/Versions/3.8/lib/python3.8/importlib/__init__.py", line 127, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 1014, in _gcd_import
  File "<frozen importlib._bootstrap>", line 991, in _find_and_load
  File "<frozen importlib._bootstrap>", line 961, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 219, in _call_with_frames_removed
  File "<frozen importlib._bootstrap>", line 1014, in _gcd_import
  File "<frozen importlib._bootstrap>", line 991, in _find_and_load
  File "<frozen importlib._bootstrap>", line 973, in _find_and_load_unlocked
```

To fix this, you'll need to do one of the following:
- rename your scenario file to loadtest.py.
- specify a scenario file on the command line. For example, <kbd>molotov --single-run my-loadtests.py</kbd>.

1. `argument -s/--single-mode: expected one argument`

Most likely, you tried running <kbd>molotov -s</kbd> without specifying a single scenario name.

1. Installing molotov latest from GitHub
TODO.
