import re
import logging as log
from typing import Callable, List, Dict

# log.basicConfig(level=log.INFO)


class Frame:
    ### REGEXES FOR PARSING
    PAT_COMMENTS = r"(?:#.*|^$)"
    PAT_PROMPT = r"^>\s*(.+)$"
    PAT_VARIABLES = r"(?<!\\){{([\w_]+)}}"
    PAT_BANG = r"^!.*"
    PAT_IF = f"^! if '(.*)' in {PAT_VARIABLES}"
    PAT_ELIF = f"^! elif '(.*)' in {PAT_VARIABLES}"
    PAT_ELSE = r"^! else"
    PAT_ENDIF = r"^! endif"
    ### REGEX_END

    def __init__(self, script: str) -> None:
        """
        A wrapper class for compiling Frame scripts

        Parameters:
        - script (str): A string that has FrameML syntax
        """
        self.script = script
        self.tests = list()

    def add_tests(self, tests: List[str]):
        """
        Used for adding tests

        Parameters:
        - tests (List[str], optional): A list of tests to run on this prompt. Not necessary for compilation
        """
        self.tests = tests

    @staticmethod
    def replace_values(script: str, json):
        """
        Simply replaces the values in script with their variable names

        Parameters:
        - script (str): A string that has FrameML syntax
        - json (Dict): A dictionary that contains replacement values.

        Examples:
        - script = "> Hey {{name}}!"
        - json = {"name": "Robert"}
        returns "> Hey Robert!"
        """
        matches = re.findall(Frame.PAT_VARIABLES, script)
        for match in matches:
            if match not in json:
                raise ValueError(
                    f"Variable '{match}' has no value in the 'values' dictionary."
                )
            script = re.sub("{{" + f"{match}" + "}}", json[match], script)
        return script

    def is_valid(self) -> bool:
        """
        Returns true if this object's script is in valid FrameML syntax
        """
        if not self.script:
            return False

        PAT_COMMENTS = r"(?:#.*|^$)"
        PAT_PROMPT = r"^>\s*(.+)$"
        PAT_VARIABLES = r"(?<!\\){{([\w_]+)}}"
        PAT_BANG = r"^!.*"
        PAT_IF = f"^! if '(.*)' in {PAT_VARIABLES}"
        PAT_ELIF = f"^! elif '(.*)' in {PAT_VARIABLES}"
        PAT_ELSE = r"^! else$"
        PAT_ENDIF = r"^! endif$"

        pattern = rf"^(?:{PAT_COMMENTS}|{PAT_PROMPT}|{PAT_BANG}|{PAT_IF}|{PAT_ELIF}|{PAT_ELSE}|{PAT_ENDIF})$"
        matches = re.findall(pattern, self.script, re.MULTILINE)

        stack = []
        for match in matches:
            if match[0].startswith("! if"):
                stack.append("if")
            elif match[0].startswith("! elif"):
                if not stack or stack[-1] not in ["if", "elif"]:
                    return False
                stack.append("elif")
            elif match[0] == "! else":
                if not stack or stack[-1] not in ["if", "elif"]:
                    return False
                stack[-1] = "else"
            elif match[0] == "! endif":
                if not stack or stack[-1] not in ["if", "elif", "else"]:
                    return False
                stack.pop()

        return len(stack) == 0

    def compile(self, model_call: Callable[[str], str], **kwargs) -> str:
        """
        Compiles this self.script, replacing variables and sends data to the model

        Parameters:
        - model_call (Callable[[str], str]): A function that queries your model with a string and returns a string
        - kwargs: Named replacement values!
        """
        if not self.is_valid():
            raise ValueError(f"This script is invalid!: {self.script}")
        script = re.sub(Frame.PAT_COMMENTS, "", self.script)
        lines = script.strip().splitlines()
        output = ""
        response_count = 1
        values = kwargs

        def _llm_call(arg: str):
            # Yes I know this is kind of cringe but it 'just werks'
            nonlocal response_count
            nonlocal values
            nonlocal output
            nonlocal self

            log.info(f"Sending: '{arg}'")

            if model_call == None:
                raise ValueError("No model call function was supplied!")
            resp = model_call(arg)
            values[f"{response_count}"] = resp
            output += f">{arg}\n>>{resp}\n"
            response_count += 1

            log.info(f"Received: '{resp}'")

            return resp

        def _filter(pattern, list: List, ptr: int):
            """
            Used for skipping the if tree
            """
            ptr += 1
            while ptr < len(list):
                if not re.match(pattern, list[ptr]):
                    ptr += 1
                else:
                    break
            return ptr

        ### END HELPER FUNCS

        ptr = 0
        condition = False
        while ptr < len(lines):
            line = lines[ptr]
            match_prompt = re.match(Frame.PAT_PROMPT, line)
            match_if = re.match(Frame.PAT_IF, line)
            match_elif = re.match(Frame.PAT_ELIF, line)
            match_else = re.match(Frame.PAT_ELSE, line)

            if match_prompt:
                _ = _llm_call(
                    Frame.replace_values(match_prompt.group(1), json=values)
                )  # do nothing with response for now
                ptr += 1
            elif match_if:
                string, var = match_if.groups()
                if re.search(string, values[var]):
                    condition = True
                    ptr += 1
                    res = re.match(Frame.PAT_PROMPT, lines[ptr])
                    while res:
                        _ = _llm_call(Frame.replace_values(res.group(1), json=values))
                        ptr += 1
                        res = re.match(Frame.PAT_PROMPT, lines[ptr])
                    while not res and ptr < len(lines):
                        res = re.match(Frame.PAT_ENDIF, lines[ptr])
                        ptr += 1
                else:
                    ptr = _filter(Frame.PAT_BANG, lines, ptr)
            elif match_elif:
                string, var = match_elif.groups()
                if not condition and re.search(string, values[var]):
                    condition = True
                    ptr += 1
                    res = re.match(Frame.PAT_PROMPT, lines[ptr])
                    while res:
                        _ = _llm_call(Frame.replace_values(res.group(1), json=values))
                        ptr += 1
                        res = re.match(Frame.PAT_PROMPT, lines[ptr])
                    while not res and ptr < len(lines):
                        res = re.match(Frame.PAT_ENDIF, lines[ptr])
                        ptr += 1
                else:
                    ptr = _filter(Frame.PAT_BANG, lines, ptr)
            elif match_else:
                if not condition:
                    ptr += 1
                    res = re.match(Frame.PAT_PROMPT, lines[ptr])
                    while res:
                        _ = _llm_call(Frame.replace_values(res.group(1), json=values))
                        ptr += 1
                        res = re.match(Frame.PAT_PROMPT, lines[ptr])
                    while not res and ptr < len(lines):
                        res = re.match(Frame.PAT_ENDIF, lines[ptr])
                        ptr += 1
                else:
                    ptr = _filter(Frame.PAT_BANG, lines, ptr)
            else:
                ptr += 1

        return output

    def to_json(self) -> Dict:
        d = dict()
        d["script"] = self.script
        d["tests"] = self.tests
        return d

    @staticmethod
    def from_json(json: Dict) -> "Frame":
        l = Frame(json["script"])
        l.add_tests(json["tests"])
        return l

    def __str__(self) -> str:
        return f"{self.to_json()}"


def main():
    script = """
# You can write comments like this! All blank lines are ignored.
> Create a fictional title for the {{MOVIE_ADJECTIVE}} movie ever! This should not be a real movie; only supply me with the title.

# here we refer to the output of the first prompt!
> Write a comprehensive anlaysis of {{1}}, discussing the following details: {{ANALYSIS_DETAILS}}. Make sure to sound as pedantic as possible.

# likewise, we refer to the output of the 2nd prompt here
! if 'masterpiece' in {{2}}
> Someone approaches you and says {{1}} is the worst movie ever made. How do you respond?
! elif 'worst' in {{2}}  # regex supported here!
> Some subhuman piece of garbage online actually thinks that {{1}} is the best movie made. How do you respond?
! else
> Someone feels passionately about {{1}}. They are frustrated with your apathy. What do you respond with?
! endif
 # there must always be an endif
    """

    def llm_call(arg: str) -> str:
        return f"{arg.split()[0]}"

    values = {
        "MOVIE_ADJECTIVE": "worst",
        "ANALYSIS_DETAILS": "sound design, themes, and cinematography",
    }

    temp = Frame(script)
    output = temp.compile(llm_call, **values)
    print(output)


if __name__ == "__main__":
    main()
