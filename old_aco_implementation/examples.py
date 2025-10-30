"""
Example usage scenarios for the ACO Load Balancer.
This file demonstrates different ways to use the load balancer.
"""

import random
from load_balancer import LoadBalancer
from request import Request
from server import Server
from ant_colony import AntColonyOptimizer


def example_basic_usage():
    """Basic usage example."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60)
    
    # Create a load balancer with 3 servers
    lb = LoadBalancer(
        num_servers=3,
        server_capacity=100.0,
        num_ants=10,
        num_iterations=50
    )
    
    # Create some requests
    requests = [
        Request(0, load=10.0),
        Request(1, load=15.0),
        Request(2, load=20.0),
        Request(3, load=12.0),
        Request(4, load=18.0),
    ]
    
    # Balance the load
    stats = lb.balance_load(requests)
    
    # Display results
    lb.print_status()
    print(f"Load Standard Deviation: {stats['load_std_dev']:.2f}%\n")


def example_heavy_load():
    """Example with heavy load scenario."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Heavy Load Scenario")
    print("="*60)
    
    # Create a load balancer
    lb = LoadBalancer(
        num_servers=4,
        server_capacity=150.0,
        num_ants=15,
        num_iterations=75
    )
    
    # Generate many requests with varying loads
    random.seed(100)
    requests = [Request(i, random.uniform(5, 20)) for i in range(30)]
    
    total_load = sum(r.load for r in requests)
    print(f"Total load to distribute: {total_load:.2f}")
    print(f"Total capacity: {4 * 150.0:.2f}\n")
    
    # Balance the load
    stats = lb.balance_load(requests)
    
    # Display results
    lb.print_status()
    print(f"Load Standard Deviation: {stats['load_std_dev']:.2f}%")
    print(f"Max Load: {stats['max_load_percentage']:.2f}%\n")


def example_parameter_tuning():
    """Example showing parameter tuning effects."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Parameter Tuning")
    print("="*60)
    
    # Generate test requests
    random.seed(42)
    test_requests = [Request(i, random.uniform(2, 8)) for i in range(25)]
    
    scenarios = [
        ("Few iterations (25)", {"num_iterations": 25}),
        ("Many iterations (150)", {"num_iterations": 150}),
        ("High pheromone (α=2)", {"alpha": 2.0, "beta": 1.0}),
        ("High heuristic (β=3)", {"alpha": 1.0, "beta": 3.0}),
    ]
    
    print("Comparing different parameter configurations:\n")
    
    for name, params in scenarios:
        lb = LoadBalancer(
            num_servers=4,
            server_capacity=80.0,
            num_ants=15,
            **params
        )
        
        # Make a copy of requests for each test
        requests_copy = [Request(r.id, r.load) for r in test_requests]
        stats = lb.balance_load(requests_copy)
        
        print(f"{name}:")
        print(f"  Load Std Dev: {stats['load_std_dev']:.2f}%")
        print(f"  Max Load: {stats['max_load_percentage']:.2f}%")
        print(f"  Cost: {stats['cost']:.4f}\n")


def example_custom_servers():
    """Example with servers of different capacities."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Servers with Different Capacities")
    print("="*60)
    
    # Create servers with different capacities
    servers = [
        Server(0, capacity=50.0),   # Small server
        Server(1, capacity=100.0),  # Medium server
        Server(2, capacity=150.0),  # Large server
    ]
    
    # Create custom load balancer
    aco = AntColonyOptimizer(
        servers=servers,
        num_ants=15,
        num_iterations=75,
        alpha=1.0,
        beta=2.0
    )
    
    # Generate requests
    random.seed(50)
    requests = [Request(i, random.uniform(3, 10)) for i in range(20)]
    
    # Optimize
    best_assignment, best_cost = aco.optimize(requests)
    
    # Apply assignment
    for request_id, server_id in best_assignment:
        request = requests[request_id]
        server = next((s for s in servers if s.id == server_id), None)
        if server:
            server.add_load(request.load)
    
    # Display results
    print("\nServer Status:")
    for server in servers:
        bar_length = 30
        filled = int(bar_length * server.get_load_percentage() / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  {server} [{bar}]")
    
    print(f"\nSolution Cost: {best_cost:.4f}\n")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_heavy_load()
    example_parameter_tuning()
    example_custom_servers()
    
    print("="*60)
    print("All examples completed!")
    print("="*60 + "\n")
