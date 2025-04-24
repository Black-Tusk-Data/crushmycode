import logging
from pathlib import Path
from typing import NamedTuple

from expert_llm.api import LlmApi
from expert_llm.remote.openai_shaped_client_implementations import OpenAIApiClient

from minikg.build_output import BuildStepOutput_Package
from minikg.logic.communities import get_all_descendant_node_ids


class CriticalComponents(NamedTuple):
    content: str
    code_node_ids: list[str]
    pass


class CodeReportBuilder:
    def __init__(
        self,
        *,
        code_base_path: str,
        pkg: BuildStepOutput_Package,
        num_critical_components: int = 5,
    ) -> None:
        self.code_base_path = Path(code_base_path)
        self.pkg = pkg
        self.num_critical_components = num_critical_components
        self.llm_api = LlmApi(OpenAIApiClient("gpt-4o"))
        return

    def build_report(self) -> str:
        executive_summary_content = self._get_executive_summary()
        critical_components = self._get_critical_components()
        skillset_requirements = self._get_skillset_requirements(critical_components)
        report_parts: list[str] = []
        report_parts.append("# Executive Summary")
        report_parts.append(executive_summary_content.strip())
        report_parts.append("\n\n")
        report_parts.append("# Major Modules and Components")
        report_parts.append(critical_components.content.strip())
        report_parts.append("\n\n")
        report_parts.append("# Suggested Developer Skillset")
        report_parts.append(skillset_requirements.strip())
        return "\n".join(report_parts)

    def _format_community_for_context(self, community_id: str) -> str:
        summaries = self.pkg.summaries_by_id[community_id]
        name = summaries.get("name")
        purpose = summaries.get("purpose")
        if not name:
            logging.error("community %s summary missing 'name'", community_id)
            pass
        if not purpose:
            logging.error("community %s summary missing 'purpose'", community_id)
            pass
        return "\n".join(
            [
                f"Component {community_id} - '{name}'",
                f" - {purpose}",
            ]
        )

    def _get_executive_summary(self) -> str:
        """
        - use the highest-level community summaries as context
        - delegate the summary mostly to the LLM
        """
        top_level_community_ids = self.pkg.community_hierarchy[0]
        context = "\n".join(
            [
                self._format_community_for_context(community_id)
                for community_id in top_level_community_ids
            ]
        )
        system_prompt = "\n".join(
            [
                "You are an expert Chief Technology Officer.",
                "You are particularly adept at delivering concise summaries of technical behavior to product stakeholders.",
                "Given a description of the key parts of a software system, your task is to prepare a brief report for product stakeholders on the functionality of that system.",
                "Instructions for the Executive Report:",
                " - No implementation details should be mentioned",
                " - Focus on high-level functionality of the system",
                " - Describe the combined behaviour of all the pieces of the system combined: There is no need to re-summarize each individual component of the system",
                " - The report should have a neutral, impartial tone.  There is no need to speak positively about the code.",
            ]
        )
        schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the complete system",
                },
                "functionality_summary": {
                    "type": "string",
                    "description": "Summary of the high-level functionality of the system.",
                },
            },
        }
        summary_res = self.llm_api.completion(
            output_schema=schema,
            req_name="executive-summary",
            system=system_prompt,
            user=context,
        )
        assert summary_res.structured_output
        data = summary_res.structured_output
        return "\n".join(
            [
                f"## {data['title']}",
                data["functionality_summary"],
            ]
        )

    def _get_most_important_constructs(self, community_id: str) -> CriticalComponents:
        descendant_node_ids = get_all_descendant_node_ids(
            self.pkg.communities,
            community_id,
        )

        node_context_lines: list[str] = []
        for i, node_id in enumerate(descendant_node_ids):
            node_info = self.pkg.G.nodes[node_id]
            node_context_lines.append(f'{i + 1}. {node_info["entity_type"]} {node_id}')
            node_context_lines.append(f' - {node_info["description"]}')
            node_context_lines.append("\n")
            pass
        schema = {
            "type": "object",
            "properties": {
                "most_important_code_construct_ids": {
                    "description": "The 3 most important code constructs IDs, in descending order of importance",
                    "items": {
                        "description": "Index of important code construct",
                        "type": "number",
                    },
                    "type": "array",
                }
            },
        }
        r = self.llm_api.completion(
            output_schema=schema,
            req_name="identify-important-code-components",
            system="\n".join(
                [
                    "You are an expert software architect.",
                    "Given a description of code constructs that comprise one subsystem of a software application, respond with the indexes of the 3 most important code constructs.",
                    "'Importance' can be defined as playing a major role in the ultimate functionality of the system.",
                ]
            ),
            user="\n".join(node_context_lines),
        )
        assert r.structured_output
        chosen_node_ids = [
            descendant_node_ids[i - 1]
            for i in r.structured_output["most_important_code_construct_ids"]
            if 1 <= i <= len(descendant_node_ids)
        ]

        content_lines: list[str] = []
        for node_id in chosen_node_ids:
            node_info = self.pkg.G.nodes[node_id]
            content_lines.append(f"*_{node_info['entity_type']}_ {node_id}*")
            content_lines.append("\n")
            content_lines.append(f" - {node_info['description']}")
            content_lines.append("\n")
            pass
        return CriticalComponents(
            code_node_ids=descendant_node_ids,
            content="\n".join(content_lines),
        )

    def _get_critical_components(self) -> CriticalComponents:
        """
        1. identify most important top-level communities
        2. for each important community, identify the 3 most important software constructs
        """
        top_level_community_ids: list[str] = []
        for i in range(len(self.pkg.community_hierarchy)):
            if self.num_critical_components <= len(self.pkg.community_hierarchy[i]):
                top_level_community_ids = self.pkg.community_hierarchy[i]
                break
            pass
        else:
            top_level_community_ids = [
                community_id
                for level in self.pkg.community_hierarchy
                for community_id in level
            ]
            pass
        important_communities_schema = {
            "type": "object",
            "properties": {
                "most_important_subsystems": {
                    "description": f"The {self.num_critical_components + 2} most important sub-system IDs, in descending order of importance",
                    "items": {
                        "description": "Subsystem ID",
                        "enum": top_level_community_ids,
                        "type": "string",
                    },
                    "type": "array",
                }
            },
        }
        important_communities_context = "\n".join(
            [
                self._format_community_for_context(community_id)
                for community_id in top_level_community_ids
            ]
        )
        important_communities_res = self.llm_api.completion(
            output_schema=important_communities_schema,
            req_name="identify-important-communities",
            system="\n".join(
                [
                    "You are an expert software architect.",
                    f"Given a description of various sub-systems that comprise a single software application, respond with the IDs of the {self.num_critical_components + 2} most important sub-systems.",
                    "'Importance' can be defined as playing a major role in the ultimate functionality of the system.",
                ]
            ),
            user=important_communities_context,
        )
        assert important_communities_res.structured_output
        most_important_community_ids = important_communities_res.structured_output[
            "most_important_subsystems"
        ][: self.num_critical_components]
        most_important_constructs_by_community = {
            community_id: self._get_most_important_constructs(community_id)
            for community_id in most_important_community_ids
        }

        # combine...
        content_lines: list[str] = []
        for community_id in most_important_community_ids:
            community_summaries = self.pkg.summaries_by_id[community_id]
            community_name = community_summaries.get("name", "")
            content_lines.append(f"## {community_name}")
            content_lines.append("\n")
            content_lines.append(
                most_important_constructs_by_community[community_id].content
            )
            content_lines.append("\n")
            pass

        return CriticalComponents(
            code_node_ids=list(
                set(
                    node_id
                    for critical_components in most_important_constructs_by_community.values()
                    for node_id in critical_components.code_node_ids
                )
            ),
            content="\n".join(content_lines),
        )

    def _get_skillset_requirements(self, critical_components: CriticalComponents):
        node_data: list[dict] = [
            dict(self.pkg.G.nodes[node_id])
            for node_id in critical_components.code_node_ids
        ]

        fragments = {
            dat["defining_fragment"]["fragment_id"]: dat["defining_fragment"]
            for dat in node_data
        }
        context_lines: list[str] = []
        for fragment in fragments.values():
            context_lines.append(fragment["fragment_id"])
            with open(self.code_base_path / fragment["source_path"], "r") as f:
                content = f.read()
                context_lines.append(
                    content[fragment["start_line_incl"] : fragment["end_line_excl"]]
                )
                pass
            context_lines.append("")
            pass

        system_prompt = "\n".join(
            [
                "You are an expert software engineer and manager.",
                "You are particularly adept at assembling technical teams.",
                "Given some important code snippets from a code base, identify the technologies and skillsets that would be most advantageous for working on that code base.",
            ]
        )
        schema = {
            "type": "object",
            "properties": {
                "relevant_frameworks": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "A software framework that is used in the codebase",
                    },
                },
                "relevant_programming_languages": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "A specific programming language that is used in the codebase",
                    },
                },
                "relevant_technologies": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "A specific technology that is used in the codebase",
                    },
                },
                "requisite_skillsets": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "A specific software engineering skillset necessary for working on the codebase",
                    },
                },
            },
        }
        res = self.llm_api.completion(
            output_schema=schema,
            req_name="identify-relevant-skillsets",
            system=system_prompt,
            user="\n".join(context_lines),
        )
        assert res.structured_output
        data = res.structured_output

        content_lines: list[str] = []
        for key, entries in data.items():
            title = key.title().replace("_", " ")
            content_lines.append(f"## {title}")
            for entry in entries:
                content_lines.append(f" - {entry}")
                pass
            content_lines.append("")
            pass
        return "\n".join(content_lines)

    pass
