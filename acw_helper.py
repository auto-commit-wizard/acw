import subprocess

from git_command import GitCommand


class ACW_Helper(object):
    @staticmethod
    def get_file_list_from_git_command(git_command: GitCommand):
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

    @staticmethod
    def read_file_diff(selected_files, is_diff):
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
