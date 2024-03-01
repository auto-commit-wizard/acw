import os
import unittest.mock
from unittest import TestCase
from unittest.mock import mock_open, patch

from acw import ACW


class ACWTest(TestCase):
    def tearDown(self):
        os.remove(self.get_mock_file_path())

    def parse_config_file_to_dict(self, file_string):
        result = {}
        for line in file_string.splitlines():
            k, v = line.split("=")
            result[k] = v
        return result

    def get_mock_home_directory(self):
        return "."

    def get_mock_file_path(self):
        return self.get_mock_home_directory() + "/.acw"

    def test_should_input_open_ai_api_key_when_config(self):
        home_directory = self.get_mock_home_directory()
        acw = ACW(check_subcommands=False, home_directory=home_directory)
        open_ai_api_key = "open_ai_api_key"
        dummy_open_ai_api_key = "dummy_open_ai_api_key"
        with patch("builtins.input", return_value=dummy_open_ai_api_key):
            acw.config()

        with open(self.get_mock_file_path(), "r") as f:
            config_map = self.parse_config_file_to_dict(f.read())

        self.assertEqual(dummy_open_ai_api_key, config_map[open_ai_api_key])
