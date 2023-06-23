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

# blank lines and comments are all deleted
> Write a comprehensive anlaysis of {{1}}, discussing the following details: {{ANALYSIS_DETAILS}}. Make sure to sound as pedantic as possible.

! if 'masterpiece' in {{2}}
> Someone approaches you and says {{1}} is the worst movie ever made. How do you respond?
! elif 'worst' in {{2}}  # regex supported here!
> Some subhuman piece of garbage online actually thinks that {{1}} is the best movie made. How do you respond?
! else
> Someone feels passionately about {{1}}. They are frustrated with your apathy. What do you respond with?
! endif
```

The script could be called like so:

* `FrameML` is our class that wraps this functionality
* `model_call` is a `Callable` that takes a string and returns a string from your model
* `FrameML.compile()` takes a `**kwargs`, named parameters


# TODO:

* [ ] Implement other cooler control flow
    * Again, may or may not be necessary but it might be cool
* [ ] Allow user to implement their own functions in the script
    * This may be out of the scope for the project
