"""
Network Load Balancer using Ant Colony Optimization.
Main class that coordinates the load balancing process.
"""

from typing import List, Dict
from server import Server
from request import Request
from ant_colony import AntColonyOptimizer


class LoadBalancer:
    """
    Load Balancer that uses Ant Colony Optimization to distribute requests.
    """
    
    def __init__(
        self,
        num_servers: int = 5,
        server_capacity: float = 100.0,
        num_ants: int = 10,
        num_iterations: int = 50,
        alpha: float = 1.0,
        beta: float = 2.0,
        evaporation_rate: float = 0.5
    ):
        """
        Initialize the load balancer.
        
        Args:
            num_servers: Number of servers in the network
            server_capacity: Capacity of each server
            num_ants: Number of ants for ACO
            num_iterations: Number of ACO iterations
            alpha: Pheromone importance in ACO
            beta: Heuristic importance in ACO
            evaporation_rate: Pheromone evaporation rate in ACO
        """
        # Create servers
        self.servers = [Server(i, server_capacity) for i in range(num_servers)]
        
        # Initialize ACO optimizer
        self.aco = AntColonyOptimizer(
            servers=self.servers,
            num_ants=num_ants,
            num_iterations=num_iterations,
            alpha=alpha,
            beta=beta,
            evaporation_rate=evaporation_rate
        )
        
        self.assignments = []
    
    def balance_load(self, requests: List[Request]) -> Dict:
        """
        Balance load across servers using ACO.
        
        Args:
            requests: List of requests to be distributed
            
        Returns:
            Dictionary with assignment results and statistics
        """
        # Reset all servers
        for server in self.servers:
            server.reset()
        
        # Run ACO optimization
        best_assignment, best_cost = self.aco.optimize(requests)
        
        # Apply the best assignment
        self.assignments = best_assignment
        for request_id, server_id in best_assignment:
            # Find the request and server
            request = requests[request_id]
            server = next(s for s in self.servers if s.id == server_id)
            
            # Assign request to server
            server.add_load(request.load)
            request.assign_to_server(server_id)
        
        # Calculate statistics
        stats = self._calculate_statistics()
        stats['cost'] = best_cost
        stats['num_requests'] = len(requests)
        
        return stats
    
    def _calculate_statistics(self) -> Dict:
        """Calculate load distribution statistics."""
        loads = [s.current_load for s in self.servers]
        load_percentages = [s.get_load_percentage() for s in self.servers]
        
        return {
            'total_load': sum(loads),
            'avg_load': sum(loads) / len(self.servers),
            'min_load': min(loads),
            'max_load': max(loads),
            'avg_load_percentage': sum(load_percentages) / len(self.servers),
            'min_load_percentage': min(load_percentages),
            'max_load_percentage': max(load_percentages),
            'load_std_dev': self._std_dev(load_percentages)
        }
    
    def _std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def get_server_status(self) -> List[Dict]:
        """Get status of all servers."""
        return [
            {
                'id': server.id,
                'load': server.current_load,
                'capacity': server.capacity,
                'load_percentage': server.get_load_percentage(),
                'requests_handled': server.requests_handled
            }
            for server in self.servers
        ]
    
    def print_status(self):
        """Print current status of all servers."""
        print("\n" + "="*60)
        print("LOAD BALANCER STATUS")
        print("="*60)
        for server in self.servers:
            bar_length = 40
            filled = int(bar_length * server.get_load_percentage() / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"{server} [{bar}] {server.requests_handled} requests")
        print("="*60 + "\n")
