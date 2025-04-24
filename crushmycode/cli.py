from abc import abstractmethod
import argparse
import enum
from textwrap import dedent
from typing import Any

from pydantic import BaseModel, Field


class CMCArgs(BaseModel):
    @staticmethod
    @abstractmethod
    def get_command_name() -> str:
        pass

    pass


class CMCArgsBuild(CMCArgs):
    @staticmethod
    def get_command_name() -> str:
        return "build"

    repo_url: str = Field(
        cli_kwargs={
            "type": str,
            "help": dedent(
                """
            Local folder path or github URL.
            """
            ),
        },
    )
    input_files: list[str] = Field(
        cli_kwargs={
            "name": "--input-files",
            "nargs": "*",
            "help": dedent(
                """
            List of glob expressions that specify which source files should be considered.
            """
            ),
        },
        default_factory=lambda: ["*"],
    )
    ignore_files: list[str] = Field(
        cli_kwargs={
            "name": "--ignore-files",
            "nargs": "*",
            "help": dedent(
                """
            List of glob expressions that specify which source files should be ignored.
            These are applied only after some 'input_files' expression has matched.
            """
            ),
        },
        default_factory=list,
    )
    pass


class CMCArgsShowGraph(CMCArgs):
    @staticmethod
    def get_command_name() -> str:
        return "show-graph"

    cache_path: str = Field(
        cli_kwargs={
            "type": str,
            "help": """
            Path to the directory created during the 'build' step.
            """,
        },
    )

    show_nodes: bool = Field(
        cli_kwargs={
            "name": "--show-nodes",
            "action": "store_true",
            "help": """
            Whether or not to include code nodes themselves in the output graph.
            In big repositories this can be very noisy.
            """,
        },
        default=False,
    )
    pass


sub_commands = {
    args.get_command_name(): args
    for args in [
        CMCArgsBuild,
        CMCArgsShowGraph,
    ]
}


def parse_cli_args() -> CMCArgs:
    parser = argparse.ArgumentParser(
        prog="Crush My Code",
        description="Knowledge graph tools for codebases",
    )
    subparsers = parser.add_subparsers(
        dest="command",
    )

    for cmd, cmd_args_class in sub_commands.items():
        subparser = subparsers.add_parser(cmd)
        for field, field_info in cmd_args_class.model_fields.items():
            cli_kwargs: dict[str, Any] = field_info.json_schema_extra["cli_kwargs"]
            subparser.add_argument(cli_kwargs.pop("name", field), **cli_kwargs)
            pass
        pass

    args = {k: v for k, v in vars(parser.parse_args()).items() if v is not None}
    cmd = args.pop("command")
    if cmd not in sub_commands:
        raise Exception(f"unknown command '{cmd}'")
    args_class = sub_commands[cmd]
    return args_class.model_validate(args)
