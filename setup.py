#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="crushmycode",
    version="v0.1.0",
    description="Codebase knowledge graph tools",
    author="Liam Tengelis",
    author_email="liam.tengelis@blacktuskdata.com",
    packages=find_packages(),
    install_requires=[
        "btdcore@git+https://github.com/Black-Tusk-Data/btdcore.git@v0.1.8",
        "expert_llm@git+https://github.com/Black-Tusk-Data/expert_llm.git@v0.1.9",
        "minikg@git+https://github.com/Black-Tusk-Data/minikg.git@v0.2.0",
        "future",
        "graspologic",
        "networkx",
        "numpy",
        "pandas",
        "pydantic",
        "pyvis",
        "requests",
        "scikit-learn",
        "scipy",
    ],
    scripts=["./bin/crushmycode"],
)
