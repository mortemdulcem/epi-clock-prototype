"""Test suite for epi-clock"""


def test_version():
    from epi_clock import __version__

    assert __version__ == "0.1.0"
