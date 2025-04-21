# CRUSHMYCODE

Don't have time to read all that new code?

Let CRUSHMYCODE read it for you instead and give you the gist.

 - Get a cool visual representation of your codebase
 - Quickly get a lay-of-the land in new codebases

CRUSHMYCODE generates graphs like the following over arbitrary codebases:

 - [maps of code constructs](https://blacktuskdata.com/code-intelligence-node-graph.html)

 - [maps of higher-level concepts](https://blacktuskdata.com/code-intelligence-viz1.html)



# Installation

From PyPi:
```sh
python -m pip install crushmycode
```

or from the git repository root:

```sh
python -m pip install .
```


# Usage

 - First, must `export OPENAI_API_KEY=<your API key>`

On a large (~300 file) repository:

```sh
crushmycode  https://github.com/google/adk-python --input-files "*.py" --ignore-files "tests/*"
```

Other options:

# Details

This is a CLI tool for the [minikg](https://github.com/Black-Tusk-Data/minikg) library.

We explain the knowledge-graph creation process in detail [in this article](https://blacktuskdata.com/code_intelligence.html).
