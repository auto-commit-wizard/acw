from enum import Enum, auto


class GitCommand(Enum):
    UNSTAGED_FILES = ["git", "ls-files", "--others", "--exclude-standard"]
    MODIFIED_FILES = ["git", "diff", "--name-only"]
