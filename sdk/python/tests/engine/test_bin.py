import sys

import pytest
from pytest_subprocess.fake_process import FakeProcess

import dagger
from dagger.engine import bin


def test_getting_port(fp: FakeProcess):
    fp.register(["dagger-engine-session"], stdout=["50004", ""])

    with bin.Engine(dagger.Config(host="bin://")) as engine:
        assert engine.cfg.host.geturl() == "http://localhost:50004"


@pytest.mark.parametrize("config_args", [{"log_output": sys.stderr}, {}])
def test_buildkit_not_running(config_args: dict, fp: FakeProcess):
    """
    When buildkit isn't running ensure that the `ValueError` is wrapped
    in a `ProvisionError` and a more helpful error message is printed.
    """

    fp.register(
        ["dagger-engine-session"],
        stderr=["Error: buildkit failed to respond", ""],
        returncode=1,
    )

    engine = bin.Engine(dagger.Config(host="bin://", **config_args))
    with pytest.raises(bin.ProvisionError) as exc_info:
        engine.start_sync()

    assert "Dagger engine failed to start" in str(exc_info.value)