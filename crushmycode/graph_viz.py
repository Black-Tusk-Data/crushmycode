from minikg.models import Community, Group


MAX_WORDS_PER_LINE = 10


def _format_title(text: str) -> str:
    words = text.split(" ")
    line_words = [
        words[i : i + MAX_WORDS_PER_LINE]
        for i in range(0, len(words), MAX_WORDS_PER_LINE)
    ]
    return "\n".join([" ".join(words) for words in line_words])


def draw_communities_graph(
    *,
    groups: dict[str, Group],
    communities: dict[str, Community],
    com_summaries: dict[str, dict[str, str]],
    node_details_by_id: dict[str, dict[str, str]],
    outfile_name: str,
    include_nodes: bool = False,
):
    from pyvis.network import Network

    net = Network()

    # NODES
    for group in groups.values():
        net.add_node(
            group.group_id,
            label=group.summary["name"],
            title=_format_title(group.summary["purpose"]),
        )
        pass

    for community in communities.values():
        community_title = _format_title(com_summaries[community.id]["purpose"])
        child_node_blurb = (
            ""
            if not community.child_node_ids
            else "\n".join(
                [
                    "Code components:",
                    *[f" - {node_id}" for node_id in community.child_node_ids],
                ]
            )
        )
        net.add_node(
            community.id,
            label=com_summaries[community.id]["name"],
            title="\n".join(
                [
                    com_summaries[community.id]["name"],
                    community_title,
                    child_node_blurb,
                ]
            ),
        )
        if not include_nodes:
            continue
        for code_node_id in community.child_node_ids:
            node_details = node_details_by_id[code_node_id]
            net.add_node(
                code_node_id,
                title=_format_title(
                    "\n".join(
                        [
                            node_details["entity_type"],
                            node_details["description"],
                        ]
                    )
                ),
            )
            pass
        pass

    # EDGES
    for group in groups.values():
        for child_group_id in group.child_group_ids:
            net.add_edge(
                group.group_id,
                child_group_id,
            )
            pass
        for child_com_id in group.child_community_ids:
            net.add_edge(
                group.group_id,
                child_com_id,
            )
            pass
        pass

    for community in communities.values():
        for child_com_id in community.child_community_ids:
            net.add_edge(
                community.id,
                child_com_id,
            )
            pass
        if not include_nodes:
            continue
        for child_node_id in community.child_node_ids:
            net.add_edge(
                community.id,
                child_node_id,
            )
            pass
        pass

    net.show(outfile_name, notebook=False)
    pass
