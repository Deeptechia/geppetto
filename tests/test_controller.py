import unittest
from geppetto.llm_api_handler import LLMHandler
from geppetto.llm_controller import LLMController
import xmlrunner

ClientMock = {}


class HandlerMockA(LLMHandler):

    def __init__(self):
        super().__init__(
            "First LLM",
            "LLM1",
            ClientMock
        )

    def llm_generate_content(self, **args):
        pass

    def get_prompt_from_thread(self, **args):
        pass


class HandlerMockB(LLMHandler):

    def __init__(self, some_arg):
        self.some_arg = some_arg
        super().__init__(
            "Second LLM",
            "LLM2",
            ClientMock
        )

    def llm_generate_content(self, **args):
        pass

    def get_prompt_from_thread(self, **args):
        pass


class HandlerMockC(LLMHandler):

    def __init__(self, some_arg):
        self.some_arg = some_arg
        super().__init__(
            "Third LLM",
            "LLM3",
            ClientMock
        )

    def llm_generate_content(self, **args):
        pass

    def get_prompt_from_thread(self, **args):
        pass


sample_llms_cfg = [
    {
        "name": "First LLM",
        "handler": HandlerMockA,
        "handler_args": {}
    },
    {
        "name": "Second LLM",
        "handler": HandlerMockB,
        "handler_args": {"some_arg": "SecondGPT"}
    }
]


class TestController(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.llm_controller = LLMController(
            sample_llms_cfg
        )

    @classmethod
    def tearDown(cls):
        cls.llm_controller = None

    def test_controller_set_up(self):
        self.assertEqual(len(self.llm_controller.llm_cfgs), 2)
        self.assertEqual(len(self.llm_controller.handlers), 0)

    def test_initialize_controller(self):
        self.llm_controller.init_controller()
        self.assertEqual(len(self.llm_controller.llm_cfgs), 2)
        self.assertEqual(len(self.llm_controller.handlers),2)

    def test_get_llm_cfg(self):
        cfg = self.llm_controller.get_llm_cfg("Second LLM")
        self.assertEqual(cfg["handler_args"]["some_arg"], "SecondGPT")

    def test_attempt_get_nonexistent_llm_cfg(self):
        self.assertRaises(
            ValueError,
            self.llm_controller.get_llm_cfg,
            "Wrong LLM"
        )

    def test_list_llms(self):
        list = self.llm_controller.list_llms()
        self.assertEqual(list, ["First LLM", "Second LLM"])

    def test_get_handler(self):
        handler = self.llm_controller.get_handler("Second LLM")
        self.assertIsInstance(handler, HandlerMockB)

    def test_controller_handler_usage(self):
        self.llm_controller.init_controller()
        info1 = self.llm_controller.handlers["First LLM"].get_info()
        self.assertEqual(info1, "Name: First LLM - Model: LLM1")
        self.assertEqual(self.llm_controller.handlers["Second LLM"].some_arg, "SecondGPT")


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='./test_results'))
