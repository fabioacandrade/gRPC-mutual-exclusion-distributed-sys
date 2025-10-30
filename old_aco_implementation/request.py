"""
Request representation for load balancing simulation.
"""


class Request:
    """Represents a network request that needs to be processed."""
    
    def __init__(self, request_id: int, load: float = 1.0):
        """
        Initialize a request.
        
        Args:
            request_id: Unique identifier for the request
            load: Processing load required by this request (default: 1.0)
        """
        self.id = request_id
        self.load = load
        self.assigned_server = None
    
    def assign_to_server(self, server_id: int):
        """Assign this request to a server."""
        self.assigned_server = server_id
    
    def __str__(self) -> str:
        server_info = f"-> Server {self.assigned_server}" if self.assigned_server is not None else "(unassigned)"
        return f"Request {self.id} (load: {self.load}) {server_info}"
    
    def __repr__(self) -> str:
        return self.__str__()
