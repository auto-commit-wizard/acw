import os
import signal
import sys


class ACW:
    def __init__(self) -> None:
        """
        Initialize the command_map with the appropriate method references,
        process the subcommands provided as arguments,
        and call the corresponding method based on the input subcommand.
        """

        self.commit_message_language = "English"
        self.open_ai_prompt_message = "You will be provided with a piece of code, and your task is to generate a commit message for it in a conventional commit message format. Commit Subject and Body are up to 70 charactors each lines. Commit Subject and Body should be in {0}.".format(
            self.commit_message_language
        )
        self.open_ai_model = "gpt-3.5-turbo"
        self.open_ai_temperature = 0
        self.open_ai_top_p = 0.95
        self.open_ai_max_tokens = 500
        self.open_ai_frequency_penalty = 0
        self.open_ai_presence_penalty = 0

        command_map = {
            "config": self.config(edit_config=True),
            "commit": self.commit,
        }
        subcommands = sys.argv[1:]
        if len(subcommands) > 1:
            # subcommand 를 2개 이상 입력한 경우
            print("Too many arguments")
            sys.exit(1)
        elif len(subcommands) == 1:
            # subcommand 를 1개만 입력한 경우
            if subcommands[0] not in command_map:
                # 모르는 subcommand 는 무시하도록 처리
                print("Unknown command")
                sys.exit(1)
            command_map[subcommands[0]]()
        else:
            # 'acw' 만 입력한 경우
            self.commit()

    def config(self, edit_config=False):
        home_directory = os.path.expanduser("~")
        acw_config_path = home_directory + "/.acw"
        exist = (
            os.path.exists(acw_config_path)
            and os.path.isfile(acw_config_path)
            and os.access(acw_config_path, os.R_OK)
        )
        if exist:
            if edit_config:
                current_config_map = {}
                with open(acw_config_path, "rb") as f:
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
                with open(acw_config_path, "wb") as f:
                    for k, v in current_config_map.items():
                        f.write(k.encode("utf-8"))
                        f.write(b"=")
                        f.write(str(v).encode("utf-8"))
                        f.write(b"\n")
            return
        else:
            open_ai_api_key = input("Enter your OpenAI API key: ")
            config_map = {
                "open_ai_api_key": open_ai_api_key,
                "commit_message_language": self.commit_message_language,
                "open_ai_prompt_message": self.open_ai_prompt_message,
                "open_ai_model": self.open_ai_model,
                "open_ai_temperature": self.open_ai_temperature,
                "open_ai_top_p": self.open_ai_top_p,
                "open_ai_max_tokens": self.open_ai_max_tokens,
                "open_ai_frequency_penalty": self.open_ai_frequency_penalty,
                "open_ai_presence_penalty": self.open_ai_presence_penalty,
            }
            with open(acw_config_path, "wb") as f:
                for k, v in config_map.items():
                    f.write(k.encode("utf-8"))
                    f.write(b"=")
                    f.write(str(v).encode("utf-8"))
                    f.write(b"\n")

    def commit(self):
        self.config()
        print("Commiting...")


if __name__ == "__main__":
    try:
        ACW()
    except:
        pass
