from frameml import Frame
import pytest


@pytest.mark.parametrize(
    "markup, expected",
    [
        ("> Give me a funny joke!\n! if 'Knock Knock' in {{1}}\n> Who's there?\n! elif 'Dog' in {{1}}\n> That was a really funny joke!\n! else\n> Great job!\n! endif", True),
        ("> Some text\n# This is a comment\n\n> Another line\n! if True in {{1}}\n> Inside if block\n! elif 'Condition' in {{1}}\n> Inside elif block\n! else\n> Inside else block\n! endif", True),
        ("> Invalid line\n! if 'Condition' in {{1}}\n> Inside if block\n> Missing endif", False),
        ("> First line\n> Second line\n# Comment\n> Third line\n! if 'Condition' in {{1}}\n> Inside if block\n! endif\n> Fourth line", False),
        ("> Single line\n", True),
        ("", False),
        ("> Prompt\n\n> Response\n\n# Comment\n\n> Another response\n! if 'Condition' in {{1}}\n> Inside if block\n! endif", True),
        ("> Invalid prompt!\n! if 'Condition' in {{1}}\n> Inside if block\n! endif", False),
    ]
)
def test_valid(markup, expected):
    assert Frame(markup).is_valid() == expected
