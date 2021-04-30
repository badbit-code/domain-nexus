from .context import src


def test_SedoCollector_gather():
    sedo_collector = src.SedoCollector()
    sedo_collector.gather()
