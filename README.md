# CRUSHMYCODE

Don't have time to read all that new code?

Let CRUSHMYCODE read it for you instead and give you the gist.

 - Get a cool visual representation of your codebase
 - Quickly get a lay-of-the land in new codebases

CRUSHMYCODE generates graphs like the following over arbitrary codebases:

## [Maps of code constructs](https://blacktuskdata.com/code-intelligence-node-graph.html)
[<img src="./images/code-nodes.png" />](https://blacktuskdata.com/code-intelligence-node-graph.html)

## [Maps of higher-level concepts](https://blacktuskdata.com/code-intelligence-viz1.html)
[<img src="./images/code-subsystems.png" />](https://blacktuskdata.com/code-intelligence-viz1.html)


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

# Random

 - Progress towards building the knowledge graph is heavily cached - you can assess the progress by looking at which steps and which files have been persisted under the cache directory (default `./kgcache_<project_name>`)
 - Sometimes if there are too many API errors with OpenAI, the worker processes can die and progress will slow to a crawl.  In this case, there is no harm at all in killing the process and restarting.
 - If for whatever reason you want to execute without multiprocessing enabled, execute the script with the environment variable `DEBUG` set to a non-zero value.
