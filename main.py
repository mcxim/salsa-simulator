import networkx as nx
from randomizer import BiasedRandomChoice
from dub import create_instruction_audio, correct_times, get_instruction_collector_callback
from random_walk import walk_graph, describe
from salsa_graph import make_graph


def main():
    graph = nx.MultiDiGraph()
    make_graph(graph)

    randomizer = BiasedRandomChoice(graph.nodes, bias_factor=0.0, recovery_rate=0.03)
    instructions = []

    walk_graph(
        graph,
        "Suelta position",
        100,
        randomizer,
        callbacks=[get_instruction_collector_callback(instructions), describe],
    )

    instructions = correct_times(instructions)

    print(instructions)

    create_instruction_audio(instructions, 150)


if __name__ == "__main__":
    main()
