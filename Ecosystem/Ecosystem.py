import json
import networkx as nx
import math
import matplotlib.pyplot as plt


def load_species_data(filename="/Users/zarasrose/Documents/School/Summer2025/cs-projects/McKinsey/Ecosystem/species_data.json"):
    """Load species data from a local JSON file using absolute path."""
    with open(filename, 'r') as f:
        return json.load(f)

def build_food_chain_graph(species_list):
    """
    Build a directed graph of the food chain.
    Each edge A -> B means A eats B.
    """
    G = nx.DiGraph()

    # Add nodes with attributes
    for species in species_list:
        G.add_node(
            species["name"],
            #food_source=species["food_source"],
            calories_needed=species["calories_needed"],
            calories_provided=species["calories_provided"],
            type=species["type"]
        )

    for species in species_list:
        prey = species["name"]
        for predator in species.get("eaten_by", []):
            if predator in G.nodes:
                G.add_edge(predator, prey)

    return G

def scale_node_sizes(graph, min_size=1000, max_size=6000):
    cal_vals = [data["calories_provided"] for _, data in graph.nodes(data=True)]
    min_cal = min(cal_vals)
    max_cal = max(cal_vals)

    sizes = []
    for _, data in graph.nodes(data=True):
        cal = data["calories_provided"]
        # Normalize to range [min_size, max_size]
        if max_cal != min_cal:
            normalized = (cal - min_cal) / (max_cal - min_cal)
        else:
            normalized = 0.5  # fallback if all values are equal
        size = min_size + normalized * (max_size - min_size)
        sizes.append(size)
    return sizes
def get_species_layer(graph, node):
    """
    Returns the trophic layer (1–4) for a given node:
    1 = eats only producers
    2 = eats at least one producer (but not only producers)
    3 = eats only consumers
    4 = apex predator (no one eats it)
    """
    if node not in graph.nodes:
        raise ValueError(f"Node '{node}' not found in graph.")

    data = graph.nodes[node]
    if data["type"] == "producer":
        return 0

    prey = list(graph.successors(node))
    predators = list(graph.predecessors(node))
    producers = {n for n, d in graph.nodes(data=True) if d["type"] == "producer"}

    if not predators:
        return 4  # Apex predator

    if all(p in producers for p in prey if p in graph.nodes) and prey:
        return 1  # Eats only producers

    if any(p in producers for p in prey if p in graph.nodes):
        return 2  # Eats at least one producer (but not only)

    return 3  # Eats only consumers

def assign_node_colors(graph):
    colors = []

    for node, data in graph.nodes(data=True):
        if data["type"] == "producer":
            colors.append("lightgreen")
        else:
            layer = get_species_layer(graph, node)
            if layer == 1:
                colors.append("salmon")
            elif layer == 2:
                colors.append("skyblue")
            elif layer == 3:
                colors.append("steelblue")
            elif layer == 4:
                colors.append("red")
            else:
                colors.append("gray")  # fallback

    return colors
def layer_by_type_layout(graph, layer_gap=2.5, node_gap=3.0):
    """
    Visually layer nodes based on type. This ignores cycles.
    Producers at the bottom, apex predators at the top.
    """
    import collections

    # Categorize by type (can add more nuance here)
    levels = collections.defaultdict(list)

    for node, data in graph.nodes(data=True):
        if data["type"] == "producer":
            levels[0].append(node)
        else:
            layer = get_species_layer(graph, node)
            if layer == 1:
                levels[1].append(node)
            elif layer == 2:
                levels[2].append(node)
            elif layer == 3:
                levels[3].append(node)
            else:
                levels[4].append(node)


    # Assign coordinates
    pos = {}
    for lvl, nodes in sorted(levels.items()):
        nodes.sort()
        x_spacing = node_gap * (len(nodes) - 1)
        for i, node in enumerate(nodes):
            x = i * node_gap - x_spacing / 2
            y = -lvl * layer_gap  # downward pyramid
            pos[node] = (x, y)

    return pos

def visualize_food_chain(graph, pause_time=0.5):
    """Draw the food chain graph with real-time interactive update support."""
    plt.clf()  # Clear previous plot
    pos = layer_by_type_layout(graph)

    node_colors = assign_node_colors(graph)
    node_sizes = scale_node_sizes(graph)

    predators = sorted(
        [n for n, d in graph.nodes(data=True) if d["type"] != "producer"],
        key=lambda n: graph.nodes[n]["calories_provided"],
        reverse=True
    )
    eating_order = {name: i+1 for i, name in enumerate(predators)}

    node_labels = {}
    for node, data in graph.nodes(data=True):
        if data["type"] == "producer":
            label = f"{node}\n(provided: {data['calories_provided']} \nneeded: {data['calories_needed']})"
        else:
            order = eating_order[node]
            label = f"{order}. {node}\n(provided: {data['calories_provided']} \nneeded: {data['calories_needed']})"
        node_labels[node] = label

    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=node_sizes, alpha=0.7)
    nx.draw_networkx_edges(
        graph, pos,
        arrowstyle="->",
        arrowsize=20,
        connectionstyle="arc3,rad=0.2",
        edge_color="black",
        alpha=0.6
    )
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=5)
    plt.title("Ecosystem Food Chain\n(+Calories Provided / -Calories Needed)", fontsize=12)
    plt.axis("off")
    plt.pause(pause_time)

def simulate_feeding(graph, predator_name):
    """
    Simulates a single feeding event for the given predator.
    - The predator eats the prey with the highest available calories.
    - Calories consumed = predator's calories_needed.
    - Prey with same highest calories are shared proportionally.
    Updates:
    - predator's calories_needed
    - prey's calories_provided
    """
    if predator_name not in graph.nodes:
        print(f"❌ '{predator_name}' not found in graph.")
        return

    predator = graph.nodes[predator_name]
    needed = predator["calories_needed"]

    if predator["type"] == "producer":
        print(f"🌱 '{predator_name}' is a producer and does not eat.")
        return

    prey_list = list(graph.successors(predator_name))
    if not prey_list:
        print(f"⚠️ '{predator_name}' has no prey.")
        return

    # Find highest calories provided among prey
    max_cal = max(graph.nodes[p]["calories_provided"] for p in prey_list)
    best_prey = [p for p in prey_list if graph.nodes[p]["calories_provided"] == max_cal]

    total_available = sum(graph.nodes[p]["calories_provided"] for p in best_prey)
    if total_available < needed:
        print(f"⚠️ Not enough total calories among prey. Predator remains hungry.")
        return

    # Divide calories among tied prey
    portion = needed / len(best_prey)
    for prey in best_prey:
        graph.nodes[prey]["calories_provided"] -= portion

    # Predator is now satisfied
    graph.nodes[predator_name]["calories_needed"] = 0

    print(f"🦈 {predator_name} ate {', '.join(best_prey)} (each gave {portion:.1f} cal)")


# Load data and build the graph
species_data = load_species_data()
food_chain_graph = build_food_chain_graph(species_data)

plt.ion()
visualize_food_chain(food_chain_graph)

while True:
    user_input = input("\nEnter an animal to simulate feeding (or type 'exit'): ").strip()
    if user_input.lower() == "exit":
        print("Exiting simulation.")
        plt.ioff()
        plt.close()
        break

    simulate_feeding(food_chain_graph, user_input)
    visualize_food_chain(food_chain_graph)

