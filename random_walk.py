import random
from dataclasses import dataclass


@dataclass
class WalkCallbackParams:
    signal_description_available: bool
    edge_duration: int
    node_type: str
    current_node: str
    next_node: str
    move_duration: int
    edge_attributes: dict
    waiting: int
    current_beat: int
    is_only_option: bool


def validate_start_node(graph, start_node):
    if start_node not in graph:
        print(f"Start node {start_node} is not in the graph.")
        return False
    return True


def select_next_node(graph, current_node, randomizer):
    neighbors = dict(graph[current_node].items())
    if not neighbors:
        print(f"No more neighbors to walk to from node {current_node}. Stopping walk.")
        return None, None, None
    next_node = (
        randomizer.choose(list(neighbors.keys())) if randomizer else random.choice(list(neighbors.keys()))
    )
    return next_node, neighbors[next_node], len(neighbors) == 1


def process_edge_attributes(edge_attributes, current_beat):
    edge_attributes = edge_attributes[0]
    waiting = 0
    start_beat = None
    if "start_beat" in edge_attributes:
        start_beat = edge_attributes["start_beat"]
        waiting = ((start_beat - 1) - current_beat) % 8
    edge_duration = edge_attributes.get("duration", 0)
    signal_description_available = "signal" in edge_attributes
    return edge_duration, waiting, signal_description_available, edge_attributes


def describe(params: WalkCallbackParams):
    if params.waiting > 0:
        print(f"Wait for beat {params.edge_attributes['start_beat']}, ", end="")

    if params.signal_description_available:
        signal_repr = f"{params.edge_attributes['signal']} into"
    elif params.edge_duration > 0:
        signal_repr = "Naturally continue into"
    elif params.node_type == "move":
        signal_repr = "Perform"
    else:
        signal_repr = "You are now in"

    duration_repr = f"For {params.edge_duration} beats, " if params.edge_duration > 0 else ""
    move_duration_repr = f" ({params.move_duration} beats)" if params.move_duration else ""
    print(f"{duration_repr}{signal_repr} {params.next_node}{move_duration_repr}")


def walk_graph(graph, start_node, max_steps=10, randomizer=None, callbacks=[]):
    if not validate_start_node(graph, start_node):
        return

    current_node = start_node
    current_beat = 0

    for _ in range(max_steps):
        next_node, edge_attributes, is_only_option = select_next_node(graph, current_node, randomizer)
        if not next_node:
            break

        edge_duration, waiting, signal_description_available, edge_attributes = process_edge_attributes(
            edge_attributes, current_beat
        )
        node_attributes = graph.nodes[next_node]
        node_type = node_attributes["node_type"]
        move_duration = node_attributes.get("duration", None)

        for callback in callbacks:
            callback(
                WalkCallbackParams(
                    signal_description_available,
                    edge_duration,
                    node_type,
                    current_node,
                    next_node,
                    move_duration,
                    edge_attributes,
                    waiting,
                    current_beat,
                    is_only_option,
                )
            )

        current_beat += waiting + edge_duration + (move_duration or 0)

        current_node = next_node
