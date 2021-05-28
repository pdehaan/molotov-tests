from molotov import scenario

_API = "http://localhost:8080"

# Run this scenario 1% of time (vs `scenario_two()`).
@scenario(weight=1)
async def scenario_one(session):
    # print("Test scenario_one")
    async with session.get(_API + "/sample.json") as resp:
        res = await resp.json()
        # WARNING: THIS WILL FAIL
        assert res["result"] == "OK"
        assert resp.status == 200

# Run this scenario 99% of the time (vs `scenario_one()`).
@scenario(weight=99)
async def scenario_two(session):
    # print("Test scenario_two")
    async with session.get(_API + "/sample.html") as resp:
        assert resp.status == 200
