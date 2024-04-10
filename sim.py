import networkx as nx
import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as ep
import random
from collections import Counter
G = nx.erdos_renyi_graph(n=100, p=0.05)
node_weights = {i: random.uniform(0.1, 0.5) for i in G.nodes()}
def calculate_node_impact_scores(G, node_weights):
    impact_scores = {}
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        neighbor_weight_sum = sum(node_weights[n] for n in neighbors)
        impact_scores[node] = neighbor_weight_sum * len(neighbors)  # Simplistic impact score
    return impact_scores

def simulate_recovery_with_aid(G, aid_level, base_recovery_chance=0.05, max_iterations=100):
    model = ep.ThresholdModel(G)
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.1)
    impact_scores = calculate_node_impact_scores(G, node_weights)
    nodes_sorted_by_impact = sorted(impact_scores, key=impact_scores.get, reverse=True)
    for node in nodes_sorted_by_impact:
        total_neighbor_weight = sum(node_weights[n] for n in G.neighbors(node))
        base_threshold = (2 / 3) * total_neighbor_weight
        adjusted_threshold = max(base_threshold - aid_level, 0)
        config.add_node_configuration("threshold", node, adjusted_threshold)
    model.set_initial_status(config)
    enhanced_recovery_chance = base_recovery_chance + aid_level
    for iteration in range(max_iterations):
        model.iteration()
        for node in [n for n, status in model.status.items() if status == 1]:
            if random.random() <= enhanced_recovery_chance:
                model.status[node] = 0    
    final_status = model.status
    recovered_nodes = sum(status == 0 for status in final_status.values())
    return recovered_nodes, iteration + 1

def find_optimal_aid(G, aid_levels, target_recovery_rate, base_recovery_chance=0.05, max_iterations=100):
    """
    Find the minimal level of financial aid that achieves the target recovery rate within the least amount of time,
    applying 'DiscountFrac' inspired optimization.
    """
    optimal_aid = None
    optimal_time = max_iterations
    total_nodes = len(G.nodes())
    
    for aid_level in aid_levels:
        recovered, time_taken = simulate_recovery_with_aid(G, aid_level, base_recovery_chance, max_iterations)
        recovery_rate = recovered / total_nodes
        
        if recovery_rate >= target_recovery_rate and time_taken < optimal_time:
            optimal_aid = aid_level
            optimal_time = time_taken
    return optimal_aid, optimal_time

model = ep.ThresholdModel(G)
initial_iterations = model.iteration_bunch(100)
initial_status_distribution = Counter(model.status.values())
print("Initial Status Distribution:", initial_status_distribution)
aid_levels = [i * 0.01 for i in range(21)] 
target_recovery_rate = 0.8
optimal_aid, optimal_time = find_optimal_aid(G, aid_levels, target_recovery_rate)
print(f"Optimal Aid Level: {optimal_aid}, Achieved in {optimal_time} iterations")
