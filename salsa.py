"""
Trying to represent cuban salsa as a state machine.
"""

from pprint import pprint
from typing import Protocol, Self
import random
import networkx as nx
from networkx.classes.graph import Graph
from contextvars import ContextVar
from randomizer import BiasedRandomChoice

graph_var: ContextVar[Graph] = ContextVar("graph")


class SalsaNode:
    name: str

    def __init__(self, name, **kwargs):
        self.name = name
        self.graph = graph_var.get()
        self.graph.add_node(name, **kwargs)


class MoveNode(SalsaNode):
    def __init__(self, name: str, duration: int):
        self.duration = duration
        super().__init__(name, duration=self.duration, node_type="move")

    def add_signal(self, signal_description: str, duration: int, other_node: Self) -> Self:
        self.graph.add_edge(self.name, other_node.name, signal=signal_description, duration=duration)
        return other_node

    def resolves_to(self, other_node: SalsaNode, duration=0):
        self.graph.add_edge(self.name, other_node.name, duration=duration)


class PositionNode(SalsaNode):
    def __init__(self, name: str):
        super().__init__(name, node_type="position")

    def add_signal(
        self,
        start_beat: int,
        signal_description: str,
        duration: int,
        other_node=MoveNode,
    ) -> MoveNode:
        self.graph.add_edge(
            self.name,
            other_node.name,
            signal=signal_description,
            duration=duration,
            start_beat=start_beat,
        )
        return other_node


def make_graph(graph):

    graph_var.set(graph)

    guapea = PositionNode("Guapea position")
    closed = PositionNode("Closed position")
    suelta = PositionNode("Suelta position")

    siete = MoveNode("Siete", 8)
    dile_que_si = MoveNode("Dile Que Si", 8)
    el_camino = MoveNode("El Camino", 8)
    prima_con_la_hermana = MoveNode("Prima Con La Hermana", 8)
    el_uno = MoveNode("El Uno", 24)
    kentucky = MoveNode("Kentucky", 16)
    vacilala = MoveNode("Vacilala", 4)  # without la mano (=hand)
    vacilala_con_la_mano = MoveNode("Vacilala Con La Mano", 4)
    vuelta = MoveNode("Vuelta", 8)
    ocho = MoveNode("Ocho", 4)
    enchufala = MoveNode("Enchufala", 4)
    doble_of_enchufala = MoveNode("Doble", 8)
    complicado_of_enchufala = MoveNode("Complicado", 8)
    dile_que_no_start = MoveNode("Dile Que No Start", 3)
    vamos_abajo = MoveNode("Vamos Abajo", 5)
    tarro_de_mentira = MoveNode("Tarro De Mentira", 8)
    exhibala = MoveNode("Exhibala", 8)

    guapea.add_signal(7, "?", 2, siete).resolves_to(guapea)
    guapea.add_signal(7, "Transfer to right hand", 2, el_uno).resolves_to(dile_que_no_start)
    guapea.add_signal(7, "Hold both hands", 2, kentucky).resolves_to(dile_que_no_start)
    guapea.add_signal(7, "Pull hand then release (with spin)", 2, vacilala)
    vacilala.add_signal("Hands not touching", 4, suelta)
    vacilala.add_signal("Right hand on back", 4, dile_que_no_start)
    guapea.add_signal(7, "Pull hand then raise", 2, vacilala_con_la_mano)
    vacilala_con_la_mano.add_signal("Switch places", 4, enchufala)
    vacilala_con_la_mano.add_signal("Right hand on back", 4, dile_que_no_start)
    guapea.add_signal(7, "Foot and hand to the right", 2, ocho).resolves_to(guapea, 4)
    guapea.add_signal(7, "Pull hand", 2, prima_con_la_hermana).resolves_to(enchufala)
    guapea.add_signal(1, "Tension", 0, enchufala)
    enchufala.add_signal("Touch Shuolder with right hand", 0, doble_of_enchufala).resolves_to(enchufala)
    enchufala.add_signal("Take left hand with right", 0, complicado_of_enchufala).resolves_to(enchufala)
    enchufala.add_signal("Complete", 4, closed)
    enchufala.add_signal("Hook turn", 4, closed)
    guapea.add_signal(1, "Raise left hand", 0, vuelta).resolves_to(enchufala)
    guapea.add_signal(1, "Take left hand with right", 0, el_camino).resolves_to(guapea)
    guapea.add_signal(1, "Make way", 0, dile_que_si).resolves_to(closed)

    closed.add_signal(1, "Step forward", 0, dile_que_no_start)
    dile_que_no_start.add_signal("Turn partner to the left and raise hand", 0, vamos_abajo).resolves_to(
        closed
    )
    dile_que_no_start.add_signal("Make way", 5, guapea)
    closed.add_signal(5, "Lower left hand, then go forward", 4, tarro_de_mentira).resolves_to(closed)
    closed.add_signal(7, "Turn upper body of partner", 2, exhibala).resolves_to(closed)

    suelta.add_signal(7, "Hand on back", 2, dile_que_no_start)


def validate_start_node(graph, start_node):
    if start_node not in graph:
        print(f"Start node {start_node} is not in the graph.")
        return False
    return True


def select_next_node(graph, current_node, randomizer):
    neighbors = dict(graph[current_node].items())
    if not neighbors:
        print(f"No more neighbors to traverse from node {current_node}. Stopping traversal.")
        return None, None
    next_node = (
        randomizer.choose(list(neighbors.keys())) if randomizer else random.choice(list(neighbors.keys()))
    )
    return next_node, neighbors[next_node]


def process_edge_attributes(edge_attributes, current_beat):
    edge_attributes = edge_attributes[0]
    waiting = 0
    if "start_beat" in edge_attributes:
        start_beat = edge_attributes["start_beat"]
        waiting = ((start_beat - 1) - current_beat) % 8
        if waiting > 0:
            print(f"Wait for beat {start_beat}, ", end="")
    edge_duration = edge_attributes.get("duration", 0)
    signal_description_available = "signal" in edge_attributes
    return edge_duration, waiting, signal_description_available, edge_attributes


def format_traversal_output(
    signal_description_available, edge_duration, node_type, next_node, move_duration, edge_attributes
):
    if signal_description_available:
        signal_repr = f"Lead ({edge_attributes['signal']}) into"
    elif edge_duration > 0:
        signal_repr = "Naturally continue into"
    elif node_type == "move":
        signal_repr = "Perform"
    else:
        signal_repr = "You are now in"

    duration_repr = f"For {edge_duration} beats, " if edge_duration > 0 else ""
    move_duration_repr = f" ({move_duration} beats)" if move_duration else ""
    return f"{duration_repr}{signal_repr} {next_node}{move_duration_repr}"


def traverse_graph(graph, start_node, max_steps=10, randomizer=None):
    if not validate_start_node(graph, start_node):
        return

    current_node = start_node
    current_beat = 0

    for _ in range(max_steps):
        next_node, edge_attributes = select_next_node(graph, current_node, randomizer)
        if not next_node:
            break

        edge_duration, waiting, signal_description_available, edge_attributes = process_edge_attributes(
            edge_attributes, current_beat
        )
        node_attributes = graph.nodes[next_node]
        node_type = node_attributes["node_type"]
        move_duration = node_attributes.get("duration", None)

        current_beat += waiting + edge_duration + (move_duration or 0)
        output = format_traversal_output(
            signal_description_available, edge_duration, node_type, next_node, move_duration, edge_attributes
        )
        print(output)

        current_node = next_node


def main():
    graph = nx.MultiDiGraph()
    make_graph(graph)
    randomizer = BiasedRandomChoice(graph.nodes, bias_factor=0.2)
    # nx.write_graphml(graph, "salsa_graph.gexf")
    traverse_graph(graph, "Closed position", 100, randomizer)


if __name__ == "__main__":
    main()
