# FrameML

This is meant to be a markup language for interacting with machine learning models. This is written from the ground up with simplicity, minimalism, and power usage in mind.

Core features currently include:
* Variables!
    * These can be from a user supplied dictionary or special variables like: `{{1}}`, previous inputs
* Control flow!
    * Extremely basic if statementst are provided
    * Check [TODO](#TODO) for more info


Included in this repo is a python library for compiling this script and using it with your own programs. Here is a simple example script:

```
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
```
> You can check [init.py](./frameml/__init__.py) for an example of how to use it!

Here's how you would use the python module:

```py
from frameml import Frame

def llm(arg: str) -> str:
    # Simply returns the first word
    return f"{arg.split()[0]}"

test1 = Frame(script="> Create a fictional title for the {{adjective}} movie ever! This should not be a real movie; only supply me with the title.")
test1.compile(llm, adjective="most epic")
```

* `Frame` is our class that wraps this script
    * `script` refers to your actual text. It contains your hopefully valid frameml file.
* `Frame.compile` is a function for actually querying the api
    * `llm` is a function for querying the actual language model. It simply takes a string and returns one.
        * You can create a wrapper around the openai library for example
    * Any other arguments are `kwargs`.
        * These are essentially just named parameters. Check [here](https://www.freecodecamp.org/news/args-and-kwargs-in-python/) to learn more


For more examples, check the [examples folder](./examples)

# Setup

```bash
pip install frameml
```
> It should be ready to use in your project now!


# TODO:

* [ ] Implement other cooler control flow
    * Again, may or may not be necessary but it might be cool
* [ ] Allow user to implement their own functions in the script
    * This may be out of the scope for the project
