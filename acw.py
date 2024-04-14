import os
import signal
import subprocess
import sys
from enum import Enum, auto

import inquirer
from openai import OpenAI
from rich import print

import ollama


class Constants(Enum):
    LANGUAGE_MODEL = "LANGUAGE_MODEL"
    COMMIT_MESSAGE_LANGUAGE = "COMMIT_MESSAGE_LANGUAGE"
    OPEN_AI_API_KEY = "OPEN_AI_API_KEY"
    OPEN_AI_PROMPT_MESSAGE = "OPEN_AI_PROMPT_MESSAGE"
    OPEN_AI_MODEL = "OPEN_AI_MODEL"
    OPEN_AI_TEMPERATURE = "OPEN_AI_TEMPERATURE"
    OPEN_AI_TOP_P = "OPEN_AI_TOP_P"
    OPEN_AI_MAX_TOKENS = "OPEN_AI_MAX_TOKENS"
    OPEN_AI_FREQUENCY_PENALTY = "OPEN_AI_FREQUENCY_PENALTY"
    OPEN_AI_PRESENCE_PENALTY = "OPEN_AI_PRESENCE_PENALTY"


class GitCommand(Enum):
    UNSTAGED_FILES = ["git", "ls-files", "--others", "--exclude-standard"]
    MODIFIED_FILES = ["git", "diff", "--name-only"]


class LanguageModel(Enum):
    OPENAI = "openai"
    OLLAMA_LLAMA2 = "ollama.llama2"


class ACW:
    def __init__(self, check_subcommands=True, home_directory=None) -> None:
        """
        Initialize the command_map with the appropriate method references,
        process the subcommands provided as arguments,
        and call the corresponding method based on the input subcommand.
        """
        self.text_color = "light_slate_blue"
        self.home_directory = os.path.expanduser("~")
        if home_directory:
            self.home_directory = home_directory
        self.acw_config_path = self.home_directory + "/.acw"
        self.commit_message_language = "English"
        self.prompt_message = "You will be provided with a piece of code, and your task is to generate a commit message for it in a conventional commit message format. Commit Subject and Body are up to 70 charactors each lines. Commit Subject and Body should be in {0}.".format(
            self.commit_message_language
        )

        if check_subcommands:
            subcommands = sys.argv[1:]

            if len(subcommands) > 1:
                # subcommand 를 2개 이상 입력한 경우
                print("Too many arguments")
                sys.exit(1)
            elif len(subcommands) == 1:
                # subcommand 를 1개만 입력한 경우
                if subcommands[0] == "config":
                    self.config(edit_config=True)
                elif subcommands[0] == "commit":
                    self.commit()
                else:
                    # 모르는 subcommand 는 무시하도록 처리
                    print("Unknown command")
                    sys.exit(1)
            else:
                # 'acw' 만 입력한 경우
                self.config()
                self.commit()

    def config(self, edit_config=False):
        exist = (
            os.path.exists(self.acw_config_path)
            and os.path.isfile(self.acw_config_path)
            and os.access(self.acw_config_path, os.R_OK)
            and os.path.getsize(self.acw_config_path) > 0
        )

        if exist:
            try:
                with open(self.acw_config_path, "r") as file:
                    file_contents = file.read()
                    self.language_model = file_contents.split("\n")[0].split("=")[1]
            except FileNotFoundError:
                print(f"The file {self.acw_config_path} was not found.")

            if edit_config:
                current_config_map = {}
                with open(self.acw_config_path, "rb") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            k, v = line.split(b"=")
                            current_config_map[k.decode("utf-8")] = v.decode("utf-8")
                for k, v in current_config_map.items():
                    print('Current value of "{0}": "{1}"'.format(k, v))
                    new_value = input(
                        "Enter a new value or press Enter to keep the current value: "
                    )
                    if new_value:
                        current_config_map[k] = new_value
                    print()
                with open(self.acw_config_path, "wb") as f:
                    for k, v in current_config_map.items():
                        f.write(k.encode("utf-8"))
                        f.write(b"=")
                        f.write(str(v).encode("utf-8"))
                        f.write(b"\n")
            return
        else:
            # 언어 모델을 선택
            key = "cofirm"
            questions = [
                inquirer.List(
                    key,
                    message="Select the language model you want to use.",
                    choices=[
                        "openai",
                        "ollama.llama2 (Make sure you've installed ollama in advance.)",
                    ],
                )
            ]
            model_name = inquirer.prompt(questions)[key].split(" ")[0]

            self.config_language_model(model_name)

            return

    def config_language_model(self, model_name):

        if (
            model_name != LanguageModel.OPENAI.value
            and model_name != LanguageModel.OLLAMA_LLAMA2.value
        ):
            raise Exception("Unsupported Model.")

        self.language_model = model_name
        config_map = {Constants.LANGUAGE_MODEL.name: model_name}

        if model_name == LanguageModel.OPENAI.value:
            self.open_ai_model = "gpt-3.5-turbo"
            self.open_ai_temperature = 0
            self.open_ai_top_p = 0.95
            self.open_ai_max_tokens = 500
            self.open_ai_frequency_penalty = 0
            self.open_ai_presence_penalty = 0

            open_ai_api_key = input("Enter your OpenAI API key: ")
            config_map = config_map | {
                Constants.OPEN_AI_API_KEY.name: open_ai_api_key,
                Constants.COMMIT_MESSAGE_LANGUAGE.name: self.commit_message_language,
                Constants.OPEN_AI_PROMPT_MESSAGE.name: self.prompt_message,
                Constants.OPEN_AI_MODEL.name: self.open_ai_model,
                Constants.OPEN_AI_TEMPERATURE.name: self.open_ai_temperature,
                Constants.OPEN_AI_TOP_P.name: self.open_ai_top_p,
                Constants.OPEN_AI_MAX_TOKENS.name: self.open_ai_max_tokens,
                Constants.OPEN_AI_FREQUENCY_PENALTY.name: self.open_ai_frequency_penalty,
                Constants.OPEN_AI_PRESENCE_PENALTY.name: self.open_ai_presence_penalty,
            }

        with open(self.acw_config_path, "wb") as f:
            for k, v in config_map.items():
                print(k, v)
                f.write(k.encode("utf-8"))
                f.write(b"=")
                f.write(str(v).encode("utf-8"))
                f.write(b"\n")

        return

    def commit(self):

        if self.language_model == LanguageModel.OPENAI.value:
            try:
                with open(self.acw_config_path, "r") as file:
                    file_contents = file.read()
                    api_key = file_contents.split("\n")[1].split("=")[1]
            except FileNotFoundError:
                print(f"The file {self.acw_config_path} was not found.")
            self.client = OpenAI(api_key=api_key)
        elif self.language_model == LanguageModel.OLLAMA_LLAMA2.value:
            self.client = ollama
        else:
            raise Exception("Unsupported Model.")

        selected_unstaged_file_name_list = self.get_selected_unstaged_file_name_list()
        selected_modified_file_name_list = self.get_selected_modified_file_name_list()

        diff_lines = self.read_file_diff(
            selected_unstaged_file_name_list, False
        ) + self.read_file_diff(selected_modified_file_name_list, True)

        self.validate_diff_lines(diff_lines)

        parsed_diff_line = self.parse_diff_lines_to_single_string(diff_lines)

        generated_commit_message = self.generate_commit_message_using_prompt(
            parsed_diff_line
        )

        final_commit_message = self.confirm_commit_message(
            generated_commit_message, diff_lines
        )

        self.git_add_files(
            selected_unstaged_file_name_list + selected_modified_file_name_list
        )

        self.git_commit(final_commit_message)
        self.git_push_if_needed()

    def get_selected_unstaged_file_name_list(self) -> list:
        unstaged_file_name_list = self.get_file_list_from_git_command(
            git_command=GitCommand.UNSTAGED_FILES
        )

        if unstaged_file_name_list:
            return self.select_checkbox(
                "Select from [Untracked files]", unstaged_file_name_list
            )
        else:
            return []

    def get_selected_modified_file_name_list(self) -> list:
        modified_file_name_list = self.get_file_list_from_git_command(
            git_command=GitCommand.MODIFIED_FILES
        )

        if modified_file_name_list:
            return self.select_checkbox(
                "Select from [Changes not staged for commit]", modified_file_name_list
            )
        else:
            return []

    def get_file_list_from_git_command(self, git_command: GitCommand):
        """
        Executes a Git command based on the GitCommand enum, returning a list of file names or an empty list on error.
        Handles execution errors by printing the error message and returning an empty list.
        """
        try:
            output = subprocess.check_output(
                git_command.value,
                stderr=subprocess.STDOUT,  # Capture stderr in case of errors
                text=True,  # Automatically decode output to string
            ).strip()  # Remove leading/trailing whitespace characters
            if output:  # If there's any output, split it into a list
                return output.split("\n")
            else:
                return []  # Return an empty list if there's no output
        except subprocess.CalledProcessError as e:
            # Handle errors (e.g., not a git repo, git command not found)
            print(f"Error executing git command: {e.output}")
            return []

    def select_checkbox(self, message, file_name_list):
        """
        Prompt the user to select files from a list using a checkbox interface. Returns a list of selected file names.
        """
        if len(file_name_list) == 0:
            return []
        key = "selected_files"
        questions = [
            inquirer.Checkbox(
                key, message=message, choices=file_name_list, carousel=True
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers[key]

    def read_file_diff(self, selected_files, is_diff):
        """
        Reads and returns the contents of selected files or their diffs if specified.
        """
        result = []
        if is_diff:
            for filename in selected_files:
                try:
                    output = subprocess.check_output(
                        ["git", "diff", "--", filename],
                        stderr=subprocess.STDOUT,  # Capture stderr in case of errors
                        text=True,  # Automatically decode output to string
                    ).strip()  # Remove leading/trailing whitespace characters
                    if output:  # If there's any output, split it into a list
                        result += output.split("\n")[:-1]
                    else:
                        continue
                except subprocess.CalledProcessError as e:
                    # Handle errors (e.g., not a git repo, git command not found)
                    print(f"Error executing git command: {e.output}")
                    return
        else:
            for filename in selected_files:
                with open(filename, "r") as file:
                    raw_data = file.read()
                    result += [raw_data]
        return result

    def validate_diff_lines(self, diff_lines):
        try:
            if len(diff_lines) == 0:
                print("[bold red]No files have been changed.[/bold red]")
                raise Exception("diff lines is empty.")
        except Exception:
            sys.exit(0)

    def parse_diff_lines_to_single_string(self, diff_lines):
        return "\n".join(diff_lines)

    def generate_commit_message_using_prompt(self, parsed_diff_line):
        """
        Automatically generate and suggest commit messages through prompt engineering
        """
        if self.language_model == LanguageModel.OPENAI.value:
            completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.prompt_message,
                    },
                    {"role": "user", "content": parsed_diff_line},
                ],
                model=self.open_ai_model,
                frequency_penalty=self.open_ai_frequency_penalty,
                max_tokens=self.open_ai_max_tokens,
                temperature=self.open_ai_temperature,
                top_p=self.open_ai_top_p,
                presence_penalty=self.open_ai_presence_penalty,
                stop=None,
            )
            return completion.choices[0].message.content
        elif self.language_model == LanguageModel.OLLAMA_LLAMA2.value:
            completion = self.client.chat(
                model="llama2",
                messages=[
                    {
                        "role": "system",
                        "content": self.prompt_message,
                    },
                    {"role": "user", "content": parsed_diff_line},
                ],
            )
            return completion["message"]["content"]
        else:
            raise Exception("Unsupported Model.")

    def confirm_commit_message(self, genenrated_commit_message, diff_lines):
        """
        Prompts the user to confirm or modify the generated commit message.
        """
        print(
            "[bold " + self.text_color + "]Generated Commit Message" + "[/"
            "bold " + self.text_color + "] :point_down::point_down:"
        )
        print()
        self.print_msg_box(genenrated_commit_message)
        print()
        key = "cofirm"
        questions = [
            inquirer.List(
                key,
                message="Do you like the generated commit message?",
                choices=[
                    "Yes, please commit with this message.",
                    "No, I want to modify it.",
                ],
            ),
        ]
        answers = inquirer.prompt(questions)
        result = genenrated_commit_message
        if answers[key] == "No, I want to modify it.":
            print("Please enter a commit message.")
            lines = []
            while True:
                line = input()
                if line:
                    lines.append(line)
                else:
                    break
            text = "\n".join(lines)
            result = text
        return result

    def print_msg_box(self, msg, indent=1, width=None, title=None):
        """
        Draw a message box with the given commit message.
        """
        lines = msg.split("\n")
        space = " " * indent
        if not width:
            width = max(map(len, lines))
        box = f'{"═" * (width + indent * 2)}\n'  # upper_border
        if title:
            box += f"║{space}{title:<{width}}{space}║\n"  # title
            box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
        box += "".join([f"{space}{line:<{width}}{space}\n" for line in lines])
        box += f'{"═" * (width + indent * 2)}'  # lower_border
        print(box)

    def git_add_files(self, file_name_list):
        for filename in file_name_list:
            subprocess.run(["git", "add", filename], stdout=subprocess.PIPE)

    def git_commit(self, final_commit_message):
        subprocess.run(
            ["git", "commit", "-m", final_commit_message],
            stdout=subprocess.PIPE,
        )

    def git_push_if_needed(self):
        """
        Prompts the user to decide whether to proceed with pushing the current branch to the remote repository.
        """
        key = "cofirm"
        questions = [
            inquirer.List(
                key,
                message="Shall we continue with the push?",
                choices=["Yes, push it.", "No, Later."],
            ),
        ]

        answers = inquirer.prompt(questions)
        if answers[key] == "Yes, push it.":
            current_branch_name = (
                subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    stdout=subprocess.PIPE,
                )
                .stdout.decode("utf-8")
                .split("\n")[:-1]
            )[0]
            subprocess.run(
                [
                    "git",
                    "push",
                    "--set-upstream",
                    "origin",
                    current_branch_name,
                ],
                stdout=subprocess.PIPE,
            )


if __name__ == "__main__":
    try:
        ACW()
    except:
        pass
