"""
Main simulation script for the Ant Colony Optimization Load Balancer.
Demonstrates the load balancing algorithm with sample requests.
"""

import random
from load_balancer import LoadBalancer
from request import Request


def generate_random_requests(num_requests: int, min_load: float = 1.0, max_load: float = 10.0) -> list:
    """
    Generate random requests with varying loads.
    
    Args:
        num_requests: Number of requests to generate
        min_load: Minimum load per request
        max_load: Maximum load per request
        
    Returns:
        List of Request objects
    """
    requests = []
    for i in range(num_requests):
        load = random.uniform(min_load, max_load)
        requests.append(Request(i, load))
    return requests


def run_simulation(
    num_servers: int = 5,
    server_capacity: float = 100.0,
    num_requests: int = 50,
    num_ants: int = 20,
    num_iterations: int = 100
):
    """
    Run a load balancing simulation.
    
    Args:
        num_servers: Number of servers
        server_capacity: Capacity of each server
        num_requests: Number of requests to generate
        num_ants: Number of ants in ACO
        num_iterations: Number of ACO iterations
    """
    print("\n" + "="*60)
    print("ANT COLONY OPTIMIZATION - NETWORK LOAD BALANCER")
    print("="*60)
    print(f"\nSimulation Parameters:")
    print(f"  - Servers: {num_servers}")
    print(f"  - Server Capacity: {server_capacity}")
    print(f"  - Requests: {num_requests}")
    print(f"  - Ants: {num_ants}")
    print(f"  - ACO Iterations: {num_iterations}")
    print()
    
    # Initialize load balancer
    lb = LoadBalancer(
        num_servers=num_servers,
        server_capacity=server_capacity,
        num_ants=num_ants,
        num_iterations=num_iterations,
        alpha=1.0,
        beta=2.0,
        evaporation_rate=0.5
    )
    
    # Generate requests
    print("Generating random requests...")
    requests = generate_random_requests(num_requests, min_load=1.0, max_load=10.0)
    total_load = sum(req.load for req in requests)
    print(f"Total load to distribute: {total_load:.2f}")
    print(f"Total available capacity: {num_servers * server_capacity:.2f}")
    
    # Run load balancing
    print("\nRunning Ant Colony Optimization...")
    stats = lb.balance_load(requests)
    
    # Display results
    print("\n✓ Load balancing complete!")
    print(f"\nOptimization Statistics:")
    print(f"  - Solution Cost: {stats['cost']:.4f}")
    print(f"  - Total Load Distributed: {stats['total_load']:.2f}")
    print(f"  - Average Load per Server: {stats['avg_load']:.2f}")
    print(f"  - Min/Max Load: {stats['min_load']:.2f} / {stats['max_load']:.2f}")
    print(f"  - Average Load %: {stats['avg_load_percentage']:.2f}%")
    print(f"  - Load Std Deviation: {stats['load_std_dev']:.2f}%")
    
    # Display server status
    lb.print_status()
    
    # Show load distribution
    print("Load Distribution Summary:")
    for server_info in lb.get_server_status():
        print(f"  Server {server_info['id']}: "
              f"{server_info['requests_handled']} requests, "
              f"{server_info['load']:.2f}/{server_info['capacity']:.2f} "
              f"({server_info['load_percentage']:.1f}%)")
    
    print("\n" + "="*60)
    print("Simulation completed successfully!")
    print("="*60 + "\n")


def run_comparison():
    """Run a comparison of different load balancing scenarios."""
    print("\n" + "="*60)
    print("COMPARISON: ACO vs Random Assignment")
    print("="*60 + "\n")
    
    # Parameters
    num_servers = 5
    server_capacity = 100.0
    num_requests = 50
    
    # Generate same requests for fair comparison
    requests = generate_random_requests(num_requests, min_load=1.0, max_load=10.0)
    
    # ACO Load Balancing
    print("1. ACO-based Load Balancing:")
    lb_aco = LoadBalancer(
        num_servers=num_servers,
        server_capacity=server_capacity,
        num_ants=20,
        num_iterations=100
    )
    stats_aco = lb_aco.balance_load([Request(r.id, r.load) for r in requests])
    print(f"   Load Std Dev: {stats_aco['load_std_dev']:.2f}%")
    print(f"   Max Load: {stats_aco['max_load_percentage']:.2f}%")
    
    # Random Assignment
    print("\n2. Random Assignment:")
    from server import Server
    servers_random = [Server(i, server_capacity) for i in range(num_servers)]
    for req in requests:
        server = random.choice(servers_random)
        server.add_load(req.load)
    
    load_percentages = [s.get_load_percentage() for s in servers_random]
    mean = sum(load_percentages) / len(load_percentages)
    variance = sum((x - mean) ** 2 for x in load_percentages) / len(load_percentages)
    std_dev_random = variance ** 0.5
    max_load_random = max(load_percentages)
    
    print(f"   Load Std Dev: {std_dev_random:.2f}%")
    print(f"   Max Load: {max_load_random:.2f}%")
    
    # Show improvement
    print("\n3. Improvement with ACO:")
    improvement_std = ((std_dev_random - stats_aco['load_std_dev']) / std_dev_random) * 100
    improvement_max = ((max_load_random - stats_aco['max_load_percentage']) / max_load_random) * 100
    print(f"   Std Dev Reduction: {improvement_std:.1f}%")
    print(f"   Max Load Reduction: {improvement_max:.1f}%")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Run main simulation
    run_simulation(
        num_servers=5,
        server_capacity=100.0,
        num_requests=50,
        num_ants=20,
        num_iterations=100
    )
    
    # Run comparison
    run_comparison()
