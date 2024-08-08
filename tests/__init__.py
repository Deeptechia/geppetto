import logging
import unittest


class TestBase(unittest.TestCase):
    def setUp(self):
        logging.getLogger().setLevel(logging.CRITICAL)


def OF(**kw):
    class OF:
        pass

    instance = OF()
    for k, v in kw.items():
        setattr(instance, k, v)
    return instance
