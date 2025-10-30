"""
Server representation for load balancing simulation.
Each server has a capacity and current load.
"""


class Server:
    """Represents a server in the network."""
    
    def __init__(self, server_id: int, capacity: float = 100.0):
        """
        Initialize a server.
        
        Args:
            server_id: Unique identifier for the server
            capacity: Maximum capacity of the server (default: 100.0)
        """
        self.id = server_id
        self.capacity = capacity
        self.current_load = 0.0
        self.requests_handled = 0
    
    def get_load_percentage(self) -> float:
        """Get current load as a percentage of capacity."""
        if self.capacity == 0:
            return 100.0
        return (self.current_load / self.capacity) * 100.0
    
    def add_load(self, load: float) -> bool:
        """
        Add load to the server.
        
        Args:
            load: Amount of load to add
            
        Returns:
            True if load was added successfully, False if it would exceed capacity
        """
        if self.current_load + load <= self.capacity:
            self.current_load += load
            self.requests_handled += 1
            return True
        return False
    
    def remove_load(self, load: float):
        """Remove load from the server."""
        self.current_load = max(0, self.current_load - load)
    
    def get_available_capacity(self) -> float:
        """Get remaining available capacity."""
        return self.capacity - self.current_load
    
    def reset(self):
        """Reset server load and request count."""
        self.current_load = 0.0
        self.requests_handled = 0
    
    def __str__(self) -> str:
        return f"Server {self.id}: {self.current_load:.2f}/{self.capacity:.2f} ({self.get_load_percentage():.1f}%)"
    
    def __repr__(self) -> str:
        return self.__str__()
