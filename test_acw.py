import os
import unittest.mock
from unittest import TestCase
from unittest.mock import mock_open, patch

from acw import ACW, Constants, Models


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
        # given
        home_directory = self.get_mock_home_directory()
        acw = ACW(check_subcommands=False, home_directory=home_directory)
        open_ai_api_key = "open_ai_api_key"
        dummy_open_ai_api_key = "dummy_open_ai_api_key"

        # when
        with patch("builtins.input", return_value=dummy_open_ai_api_key):
            with patch(
                "inquirer.prompt", return_value={"confirm": Models.GPT_3_5_TURBO.name}
            ):
                acw.config()

        # then
        with open(self.get_mock_file_path(), "r") as f:
            config_map = self.parse_config_file_to_dict(f.read())

        self.assertEqual(
            dummy_open_ai_api_key, config_map[Constants.OPEN_AI_API_KEY.name]
        )

    def test_should_update_config_when_edit_config_is_true(self):
        # given
        home_directory = self.get_mock_home_directory()
        acw = ACW(check_subcommands=False, home_directory=home_directory)
        dummy_open_ai_api_key = "dummy_open_ai_api_key"
        with patch("builtins.input", return_value=dummy_open_ai_api_key):
            with patch(
                "inquirer.prompt", return_value={"confirm": Models.GPT_3_5_TURBO.name}
            ):
                acw.config()

        with open(self.get_mock_file_path(), "r") as f:
            config_map = self.parse_config_file_to_dict(f.read())

        self.assertEqual(
            dummy_open_ai_api_key, config_map[Constants.OPEN_AI_API_KEY.name]
        )
        updated_dummy_open_ai_api_key = "updated_dummy_open_ai_api_key"

        # when
        with patch("builtins.input") as mocked_input:
            mocked_input.side_effect = [
                Models.GPT_3_5_TURBO.name,
                None,
                None,
                updated_dummy_open_ai_api_key,
                None,
                None,
                None,
                None,
                None,
            ]
            acw.config(edit_config=True)

        # then
        with open(self.get_mock_file_path(), "r") as f:
            updated_config_map = self.parse_config_file_to_dict(f.read())
        self.assertEqual(
            updated_dummy_open_ai_api_key,
            updated_config_map[Constants.OPEN_AI_API_KEY.name],
        )
        config_map.pop(Constants.OPEN_AI_API_KEY.name)
        updated_config_map.pop(Constants.OPEN_AI_API_KEY.name)
        self.assertEqual(config_map, updated_config_map)
