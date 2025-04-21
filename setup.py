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
        "btdcore",
        "expert_llm",
        "minikg",
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
    package_data={
        "": ["*.yaml"],
    },
    scripts=["./bin/crushmycode"],
)
