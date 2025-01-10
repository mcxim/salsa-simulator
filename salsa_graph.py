"""
Trying to represent cuban salsa as a state machine.
"""

from typing import Self
from dub import create_instruction_audio
from contextvars import ContextVar
from networkx.classes.graph import Graph

graph_var: ContextVar[Graph] = ContextVar("graph_var")


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
    vacilala = MoveNode("Vacilala", 4)
    vacilala_con_la_mano = MoveNode("Vacilala Con La Mano", 4)
    vuelta = MoveNode("Vuelta", 8)
    ocho = MoveNode("Ocho", 4)
    enchufala = MoveNode("Enchufala", 4)
    doble_of_enchufala = MoveNode("Doble", 4)
    complicado_of_enchufala = MoveNode("Complicado", 4)
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
    guapea.add_signal(1, "Take left hand with right, turn through left shoulder", 0, el_camino).resolves_to(
        guapea
    )
    guapea.add_signal(1, "Make way", 0, dile_que_si).resolves_to(closed)

    closed.add_signal(1, "Step forward", 0, dile_que_no_start)
    dile_que_no_start.add_signal("Turn partner to the left and raise hand", 0, vamos_abajo).resolves_to(
        closed
    )
    dile_que_no_start.add_signal("Make way", 5, guapea)
    closed.add_signal(5, "Lower left hand, then go forward", 4, tarro_de_mentira).resolves_to(closed)
    closed.add_signal(7, "Turn upper body of partner", 2, exhibala).resolves_to(closed)

    suelta.add_signal(7, "Hand on back", 2, dile_que_no_start)
    suelta.add_signal(7, "No hand on back", 2, suelta)
