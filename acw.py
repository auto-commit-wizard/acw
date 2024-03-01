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
            "config": self.config,
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

    def check_config(self):
        print("Checking config...")
        return False

    def config(self):
        exist = self.check_config()
        if exist:
            print("Edit config...")
            return
        else:
            print("Configuring...")
            return

    def commit(self):
        exist = self.check_config()
        if not exist:
            self.config()
        print("Commiting...")


if __name__ == "__main__":
    try:
        ACW()
    except:
        pass
