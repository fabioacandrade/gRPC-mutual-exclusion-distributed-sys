"""
Lamport Logical Clock implementation for distributed systems.
"""


class LamportClock:
    """
    Implementation of Lamport's logical clock for ordering events in distributed systems.
    """
    
    def __init__(self, initial_time: int = 0):
        """
        Initialize the Lamport clock.
        
        Args:
            initial_time: Initial timestamp value (default: 0)
        """
        self.time = initial_time
    
    def increment(self) -> int:
        """
        Increment the local clock (on local event or message send).
        
        Returns:
            The new timestamp after increment
        """
        self.time += 1
        return self.time
    
    def update(self, received_time: int) -> int:
        """
        Update the clock when receiving a message.
        Takes max of local time and received time, then increments.
        
        Args:
            received_time: Timestamp from received message
            
        Returns:
            The new timestamp after update
        """
        self.time = max(self.time, received_time) + 1
        return self.time
    
    def get_time(self) -> int:
        """
        Get current timestamp without modifying it.
        
        Returns:
            Current timestamp
        """
        return self.time
    
    def __str__(self) -> str:
        return f"LamportClock(time={self.time})"
    
    def __repr__(self) -> str:
        return self.__str__()
