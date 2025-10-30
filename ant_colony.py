"""
Ant Colony Optimization algorithm for load balancing.
This module implements the ACO algorithm where ants explore different server
assignments and deposit pheromones on successful paths.
"""

import random
import math
from typing import List, Tuple
from server import Server
from request import Request


class Ant:
    """Represents an ant that explores server assignments."""
    
    def __init__(self, ant_id: int):
        """Initialize an ant."""
        self.id = ant_id
        self.path = []  # List of (request_id, server_id) tuples
        self.total_cost = 0.0
    
    def reset(self):
        """Reset the ant's path and cost."""
        self.path = []
        self.total_cost = 0.0


class AntColonyOptimizer:
    """
    Ant Colony Optimization algorithm for load balancing.
    
    The algorithm uses artificial ants to find optimal server assignments
    for incoming requests, inspired by the foraging behavior of real ants.
    """
    
    def __init__(
        self,
        servers: List[Server],
        num_ants: int = 10,
        num_iterations: int = 50,
        alpha: float = 1.0,
        beta: float = 2.0,
        evaporation_rate: float = 0.5,
        pheromone_constant: float = 100.0,
        initial_pheromone: float = 1.0
    ):
        """
        Initialize the ACO optimizer.
        
        Args:
            servers: List of available servers
            num_ants: Number of ants to use in the colony
            num_iterations: Number of iterations to run the algorithm
            alpha: Pheromone importance factor
            beta: Heuristic importance factor (server load)
            evaporation_rate: Rate at which pheromones evaporate (0-1)
            pheromone_constant: Constant used in pheromone deposit calculation
            initial_pheromone: Initial pheromone level on all paths
        """
        self.servers = servers
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.pheromone_constant = pheromone_constant
        
        # Initialize pheromone matrix: pheromones[request_idx][server_id]
        self.pheromones = {}
        self.initial_pheromone = initial_pheromone
        
        # Best solution tracking
        self.best_solution = None
        self.best_cost = float('inf')
    
    def _initialize_pheromones(self, num_requests: int):
        """Initialize pheromone levels for all request-server combinations."""
        self.pheromones = {}
        for req_idx in range(num_requests):
            self.pheromones[req_idx] = {
                server.id: self.initial_pheromone 
                for server in self.servers
            }
    
    def _calculate_heuristic(self, server: Server, request: Request) -> float:
        """
        Calculate heuristic value for assigning a request to a server.
        Higher value means better choice (lower load is better).
        
        Args:
            server: Target server
            request: Request to be assigned
            
        Returns:
            Heuristic value (desirability of this assignment)
        """
        # Check if server can handle the request
        if server.current_load + request.load > server.capacity:
            return 0.0001  # Very small value for infeasible assignments
        
        # Prefer servers with lower load percentage
        load_percentage = server.get_load_percentage()
        
        # Heuristic: inverse of load percentage (prefer less loaded servers)
        # Add 1 to avoid division by zero
        heuristic = 1.0 / (load_percentage + 1.0)
        
        return heuristic
    
    def _select_server(self, request: Request, request_idx: int, servers_copy: List[Server]) -> Server:
        """
        Select a server for a request using ACO probability calculation.
        
        Args:
            request: Request to be assigned
            request_idx: Index of the request
            servers_copy: Copy of servers with current load state
            
        Returns:
            Selected server
        """
        # Calculate probabilities for each server
        probabilities = []
        total = 0.0
        
        for server in servers_copy:
            pheromone = self.pheromones[request_idx][server.id]
            heuristic = self._calculate_heuristic(server, request)
            
            # ACO formula: probability proportional to (pheromone^alpha) * (heuristic^beta)
            value = (pheromone ** self.alpha) * (heuristic ** self.beta)
            probabilities.append(value)
            total += value
        
        # Normalize probabilities
        if total > 0:
            probabilities = [p / total for p in probabilities]
        else:
            # If all probabilities are 0, use uniform distribution
            probabilities = [1.0 / len(servers_copy)] * len(servers_copy)
        
        # Select server using roulette wheel selection
        r = random.random()
        cumulative = 0.0
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if r <= cumulative:
                return servers_copy[i]
        
        # Fallback: return last server
        return servers_copy[-1]
    
    def _calculate_solution_cost(self, servers_copy: List[Server]) -> float:
        """
        Calculate the cost of a solution.
        Lower cost is better. Cost is based on load imbalance.
        
        Args:
            servers_copy: List of servers with assigned loads
            
        Returns:
            Cost value (lower is better)
        """
        # Calculate standard deviation of load percentages
        # Lower standard deviation means better balance
        load_percentages = [s.get_load_percentage() for s in servers_copy]
        
        if not load_percentages:
            return 0.0
        
        mean_load = sum(load_percentages) / len(load_percentages)
        variance = sum((x - mean_load) ** 2 for x in load_percentages) / len(load_percentages)
        std_dev = math.sqrt(variance)
        
        # Also consider maximum load (to avoid overloading any single server)
        max_load = max(load_percentages)
        
        # Combined cost: standard deviation + penalty for high max load
        cost = std_dev + (max_load / 10.0)
        
        return cost
    
    def _construct_solution(self, ant: Ant, requests: List[Request]) -> List[Server]:
        """
        Construct a solution (server assignments) for an ant.
        
        Args:
            ant: The ant constructing the solution
            requests: List of requests to be assigned
            
        Returns:
            List of servers with loads assigned according to the ant's path
        """
        # Create a copy of servers to track load during construction
        servers_copy = [Server(s.id, s.capacity) for s in self.servers]
        servers_copy_dict = {s.id: s for s in servers_copy}
        
        ant.reset()
        
        for req_idx, request in enumerate(requests):
            # Select a server for this request
            selected_server = self._select_server(request, req_idx, servers_copy)
            
            # Assign the request to the server
            selected_server.add_load(request.load)
            
            # Record the ant's path
            ant.path.append((request.id, selected_server.id))
        
        # Calculate the cost of this solution
        ant.total_cost = self._calculate_solution_cost(servers_copy)
        
        return servers_copy
    
    def _update_pheromones(self, ants: List[Ant]):
        """
        Update pheromone levels based on ant solutions.
        
        Args:
            ants: List of ants with their solutions
        """
        # Evaporation
        for req_idx in self.pheromones:
            for server_id in self.pheromones[req_idx]:
                self.pheromones[req_idx][server_id] *= (1 - self.evaporation_rate)
        
        # Deposit pheromones from each ant
        for ant in ants:
            # Better solutions (lower cost) deposit more pheromone
            if ant.total_cost > 0:
                pheromone_deposit = self.pheromone_constant / ant.total_cost
            else:
                pheromone_deposit = self.pheromone_constant
            
            for request_id, server_id in ant.path:
                # Find request index
                request_idx = request_id
                self.pheromones[request_idx][server_id] += pheromone_deposit
    
    def optimize(self, requests: List[Request]) -> Tuple[List[Tuple[int, int]], float]:
        """
        Run the ACO algorithm to find optimal server assignments.
        
        Args:
            requests: List of requests to be assigned to servers
            
        Returns:
            Tuple of (best_assignment, best_cost) where best_assignment is a list
            of (request_id, server_id) tuples
        """
        # Initialize pheromones
        self._initialize_pheromones(len(requests))
        
        # Create ant colony
        ants = [Ant(i) for i in range(self.num_ants)]
        
        # Run iterations
        for iteration in range(self.num_iterations):
            # Each ant constructs a solution
            for ant in ants:
                servers_copy = self._construct_solution(ant, requests)
                
                # Track best solution
                if ant.total_cost < self.best_cost:
                    self.best_cost = ant.total_cost
                    self.best_solution = ant.path.copy()
            
            # Update pheromones
            self._update_pheromones(ants)
        
        return self.best_solution, self.best_cost
