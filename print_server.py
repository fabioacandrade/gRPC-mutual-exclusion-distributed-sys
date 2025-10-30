"""
"Dumb" Print Server - Receives and processes print requests without participating
in mutual exclusion. Only prints messages and returns confirmations.
"""

import grpc
from concurrent import futures
import time
import random
from datetime import datetime

import distributed_printing_pb2
import distributed_printing_pb2_grpc
from lamport_clock import LamportClock


class PrintingServiceImpl(distributed_printing_pb2_grpc.PrintingServiceServicer):
    """
    Implementation of the "dumb" printing service.
    Does NOT participate in mutual exclusion - just prints and confirms.
    """
    
    def __init__(self):
        """Initialize the print server."""
        self.clock = LamportClock()
        self.print_count = 0
    
    def SendToPrinter(self, request, context):
        """
        Handle print request from a client.
        
        Args:
            request: PrintRequest with client info and message
            context: gRPC context
            
        Returns:
            PrintResponse with confirmation
        """
        # Update Lamport clock with received timestamp
        self.clock.update(request.lamport_timestamp)
        
        # Simulate printing delay (2-3 seconds)
        delay = random.uniform(2.0, 3.0)
        
        # Print the message
        self.print_count += 1
        timestamp_str = datetime.now().strftime("%H:%M:%S")
        print(f"\n{'='*60}")
        print(f"[TS: {request.lamport_timestamp}] [Local Time: {timestamp_str}]")
        print(f"CLIENTE {request.client_id} (Request #{request.request_number}):")
        print(f"  {request.message_content}")
        print(f"{'='*60}")
        print(f"Printing... (simulating {delay:.2f}s delay)")
        
        # Simulate print time
        time.sleep(delay)
        
        # Increment clock before sending response
        response_timestamp = self.clock.increment()
        
        print(f"✓ Print completed! Total prints: {self.print_count}\n")
        
        # Return confirmation
        return distributed_printing_pb2.PrintResponse(
            success=True,
            confirmation_message=f"Print completed for client {request.client_id}",
            lamport_timestamp=response_timestamp
        )


def serve(port=50051):
    """
    Start the print server.
    
    Args:
        port: Port to listen on (default: 50051)
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    distributed_printing_pb2_grpc.add_PrintingServiceServicer_to_server(
        PrintingServiceImpl(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    print("="*60)
    print("PRINT SERVER (DUMB) - STARTED")
    print("="*60)
    print(f"Listening on port: {port}")
    print("Waiting for print requests...")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n\nShutting down print server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
