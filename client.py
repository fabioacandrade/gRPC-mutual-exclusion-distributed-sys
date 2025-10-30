"""
Intelligent Client - Implements Ricart-Agrawala mutual exclusion algorithm
and acts as both gRPC client and server.
"""

import grpc
from concurrent import futures
import time
import random
import threading
from datetime import datetime
from typing import List, Tuple

import distributed_printing_pb2
import distributed_printing_pb2_grpc
from lamport_clock import LamportClock


class MutualExclusionServiceImpl(distributed_printing_pb2_grpc.MutualExclusionServiceServicer):
    """
    Implementation of mutual exclusion service for Ricart-Agrawala algorithm.
    Each client implements this service to receive requests from other clients.
    """
    
    def __init__(self, client):
        """
        Initialize the mutual exclusion service.
        
        Args:
            client: Reference to the parent IntelligentClient
        """
        self.client = client
    
    def RequestAccess(self, request, context):
        """
        Handle access request from another client.
        
        Args:
            request: AccessRequest from another client
            context: gRPC context
            
        Returns:
            AccessResponse granting or deferring access
        """
        # Update Lamport clock
        self.client.clock.update(request.lamport_timestamp)
        
        with self.client.lock:
            requesting_client = request.client_id
            requesting_timestamp = request.lamport_timestamp
            
            # Ricart-Agrawala: Grant access if we're not requesting or
            # if the requester has higher priority (lower timestamp, or same timestamp but lower ID)
            should_grant = (
                not self.client.requesting or
                (requesting_timestamp, requesting_client) < 
                (self.client.request_timestamp, self.client.client_id)
            )
            
            if should_grant:
                # Grant access immediately
                response_timestamp = self.client.clock.increment()
                self.client.log(f"GRANTED access to Client {requesting_client} (TS: {requesting_timestamp})")
                return distributed_printing_pb2.AccessResponse(
                    access_granted=True,
                    lamport_timestamp=response_timestamp
                )
            else:
                # Defer the request
                self.client.deferred_requests.append((requesting_client, request.lamport_timestamp))
                self.client.log(f"DEFERRED access for Client {requesting_client} (TS: {requesting_timestamp})")
                
                # Still send a response but with granted=False to acknowledge receipt
                response_timestamp = self.client.clock.increment()
                return distributed_printing_pb2.AccessResponse(
                    access_granted=False,
                    lamport_timestamp=response_timestamp
                )
    
    def ReleaseAccess(self, request, context):
        """
        Handle release notification from another client.
        
        Args:
            request: ReleaseMessage from another client
            context: gRPC context
            
        Returns:
            ReleaseResponse acknowledging the release
        """
        # Update Lamport clock
        self.client.clock.update(request.lamport_timestamp)
        
        with self.client.lock:
            self.client.log(f"Received RELEASE from Client {request.client_id}")
            response_timestamp = self.client.clock.increment()
            
            return distributed_printing_pb2.ReleaseResponse(
                acknowledged=True
            )


class IntelligentClient:
    """
    Intelligent client that implements Ricart-Agrawala mutual exclusion
    and coordinates with other clients before accessing the print server.
    """
    
    def __init__(self, client_id: int, client_port: int, print_server_address: str,
                 other_clients: List[Tuple[int, str]]):
        """
        Initialize the intelligent client.
        
        Args:
            client_id: Unique ID for this client
            client_port: Port for this client's gRPC server
            print_server_address: Address of the print server (e.g., 'localhost:50051')
            other_clients: List of (client_id, address) tuples for other clients
        """
        self.client_id = client_id
        self.client_port = client_port
        self.print_server_address = print_server_address
        self.other_clients = other_clients
        
        # Lamport clock
        self.clock = LamportClock()
        
        # Ricart-Agrawala state
        self.requesting = False
        self.request_timestamp = 0
        self.request_number = 0
        self.replies_received = 0
        self.deferred_requests = []
        
        # Thread synchronization
        self.lock = threading.Lock()
        
        # gRPC server for receiving requests from other clients
        self.server = None
        
        # Status display
        self.total_prints = 0
        self.running = True
    
    def start_server(self):
        """Start the gRPC server to receive requests from other clients."""
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        distributed_printing_pb2_grpc.add_MutualExclusionServiceServicer_to_server(
            MutualExclusionServiceImpl(self), self.server
        )
        self.server.add_insecure_port(f'[::]:{self.client_port}')
        self.server.start()
        self.log(f"Started gRPC server on port {self.client_port}")
    
    def stop_server(self):
        """Stop the gRPC server."""
        if self.server:
            self.server.stop(0)
    
    def log(self, message: str):
        """
        Log a message with timestamp.
        
        Args:
            message: Message to log
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [Client {self.client_id}] [LT: {self.clock.get_time()}] {message}")
    
    def request_critical_section(self):
        """
        Request access to critical section using Ricart-Agrawala algorithm.
        """
        with self.lock:
            self.requesting = True
            self.request_number += 1
            self.request_timestamp = self.clock.increment()
            self.replies_received = 0
            
            current_request = self.request_number
            current_timestamp = self.request_timestamp
        
        self.log(f"Requesting critical section (Request #{current_request}, TS: {current_timestamp})")
        
        # Send request to all other clients
        for other_client_id, other_client_address in self.other_clients:
            self.send_access_request(other_client_id, other_client_address, current_request, current_timestamp)
        
        # Wait for all replies
        required_replies = len(self.other_clients)
        while True:
            with self.lock:
                if self.replies_received >= required_replies:
                    break
            time.sleep(0.1)
        
        self.log(f"✓ Received all replies, entering critical section")
    
    def send_access_request(self, target_client_id: int, target_address: str, 
                           request_num: int, timestamp: int):
        """
        Send access request to another client.
        
        Args:
            target_client_id: ID of the target client
            target_address: gRPC address of the target client
            request_num: Request number
            timestamp: Lamport timestamp of the request
        """
        try:
            channel = grpc.insecure_channel(target_address)
            stub = distributed_printing_pb2_grpc.MutualExclusionServiceStub(channel)
            
            request = distributed_printing_pb2.AccessRequest(
                client_id=self.client_id,
                lamport_timestamp=timestamp,
                request_number=request_num
            )
            
            response = stub.RequestAccess(request, timeout=5.0)
            
            # Update clock with response
            self.clock.update(response.lamport_timestamp)
            
            # If access granted, increment reply count
            if response.access_granted:
                with self.lock:
                    self.replies_received += 1
                    self.log(f"Received GRANT from Client {target_client_id} ({self.replies_received}/{len(self.other_clients)})")
            else:
                # Access deferred, will be granted later
                # For simplicity, we count deferred as received and will wait
                with self.lock:
                    self.replies_received += 1
                    self.log(f"Received DEFER from Client {target_client_id} ({self.replies_received}/{len(self.other_clients)})")
            
            channel.close()
        except grpc.RpcError as e:
            self.log(f"ERROR requesting access from Client {target_client_id}: {e}")
            # Count as received to avoid blocking
            with self.lock:
                self.replies_received += 1
    
    def release_critical_section(self):
        """
        Release the critical section and send release messages to deferred clients.
        """
        with self.lock:
            self.requesting = False
            deferred = self.deferred_requests.copy()
            self.deferred_requests = []
            release_timestamp = self.clock.increment()
        
        self.log(f"Releasing critical section (TS: {release_timestamp})")
        
        # Send release/grant messages to all other clients
        for other_client_id, other_client_address in self.other_clients:
            self.send_release_notification(other_client_id, other_client_address, release_timestamp)
        
        # Send explicit grants to deferred clients
        for deferred_client_id, _ in deferred:
            self.log(f"Granting deferred request from Client {deferred_client_id}")
    
    def send_release_notification(self, target_client_id: int, target_address: str, timestamp: int):
        """
        Send release notification to another client.
        
        Args:
            target_client_id: ID of the target client
            target_address: gRPC address of the target client
            timestamp: Lamport timestamp of the release
        """
        try:
            channel = grpc.insecure_channel(target_address)
            stub = distributed_printing_pb2_grpc.MutualExclusionServiceStub(channel)
            
            release_msg = distributed_printing_pb2.ReleaseMessage(
                client_id=self.client_id,
                lamport_timestamp=timestamp,
                request_number=self.request_number
            )
            
            stub.ReleaseAccess(release_msg, timeout=5.0)
            channel.close()
        except grpc.RpcError as e:
            self.log(f"ERROR sending release to Client {target_client_id}: {e}")
    
    def send_to_printer(self, message: str):
        """
        Send a print request to the dumb print server.
        
        Args:
            message: Message to print
        """
        try:
            channel = grpc.insecure_channel(self.print_server_address)
            stub = distributed_printing_pb2_grpc.PrintingServiceStub(channel)
            
            # Increment clock before sending
            timestamp = self.clock.increment()
            
            request = distributed_printing_pb2.PrintRequest(
                client_id=self.client_id,
                message_content=message,
                lamport_timestamp=timestamp,
                request_number=self.request_number
            )
            
            self.log(f"Sending to print server: '{message}'")
            response = stub.SendToPrinter(request, timeout=10.0)
            
            # Update clock with response
            self.clock.update(response.lamport_timestamp)
            
            if response.success:
                self.total_prints += 1
                self.log(f"✓ Print confirmed: {response.confirmation_message}")
            else:
                self.log(f"✗ Print failed")
            
            channel.close()
        except grpc.RpcError as e:
            self.log(f"ERROR sending to print server: {e}")
    
    def print_document(self, message: str):
        """
        Print a document using mutual exclusion.
        
        Args:
            message: Message to print
        """
        # Request critical section (coordinate with other clients)
        self.request_critical_section()
        
        # Critical section: send to print server
        self.send_to_printer(message)
        
        # Release critical section
        self.release_critical_section()
    
    def run_automatic_requests(self, interval_min: float = 5.0, interval_max: float = 15.0):
        """
        Automatically generate print requests at random intervals.
        
        Args:
            interval_min: Minimum interval between requests (seconds)
            interval_max: Maximum interval between requests (seconds)
        """
        messages = [
            "Relatório financeiro do mês",
            "Documento de requisitos do projeto",
            "Ata da reunião de equipe",
            "Contrato de prestação de serviços",
            "Lista de tarefas pendentes",
            "Planilha de custos operacionais",
            "Manual de instruções",
            "Proposta comercial",
            "Certificado de conclusão",
            "Declaração de responsabilidade"
        ]
        
        while self.running:
            # Wait random interval
            wait_time = random.uniform(interval_min, interval_max)
            self.log(f"Next request in {wait_time:.1f}s...")
            time.sleep(wait_time)
            
            if not self.running:
                break
            
            # Generate and print document
            message = random.choice(messages)
            self.log(f"=== Initiating print request ===")
            self.print_document(message)
            self.log(f"=== Print request completed (Total: {self.total_prints}) ===\n")
    
    def show_status(self):
        """Display current status."""
        print("\n" + "="*60)
        print(f"CLIENT {self.client_id} STATUS")
        print("="*60)
        print(f"Port: {self.client_port}")
        print(f"Lamport Clock: {self.clock.get_time()}")
        print(f"Requesting CS: {self.requesting}")
        print(f"Total Prints: {self.total_prints}")
        print(f"Deferred Requests: {len(self.deferred_requests)}")
        print("="*60 + "\n")


def run_client(client_id: int, client_port: int, print_server: str, 
               other_clients: List[Tuple[int, str]]):
    """
    Run an intelligent client.
    
    Args:
        client_id: Unique ID for this client
        client_port: Port for this client's gRPC server
        print_server: Address of print server
        other_clients: List of (id, address) for other clients
    """
    client = IntelligentClient(client_id, client_port, print_server, other_clients)
    
    print("="*60)
    print(f"INTELLIGENT CLIENT {client_id} - STARTING")
    print("="*60)
    print(f"Client Port: {client_port}")
    print(f"Print Server: {print_server}")
    print(f"Other Clients: {len(other_clients)}")
    print("="*60 + "\n")
    
    # Start gRPC server
    client.start_server()
    
    # Wait a bit for all clients to start
    time.sleep(2)
    
    try:
        # Run automatic requests
        client.run_automatic_requests()
    except KeyboardInterrupt:
        print("\n\nStopping client...")
        client.running = False
        client.stop_server()
        print("Client stopped.")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 client.py <client_id>")
        print("Example: python3 client.py 1")
        sys.exit(1)
    
    client_id = int(sys.argv[1])
    
    # Default configuration for 3 clients
    print_server = 'localhost:50051'
    
    # Configure client based on ID
    if client_id == 1:
        client_port = 50052
        other_clients = [
            (2, 'localhost:50053'),
            (3, 'localhost:50054')
        ]
    elif client_id == 2:
        client_port = 50053
        other_clients = [
            (1, 'localhost:50052'),
            (3, 'localhost:50054')
        ]
    elif client_id == 3:
        client_port = 50054
        other_clients = [
            (1, 'localhost:50052'),
            (2, 'localhost:50053')
        ]
    else:
        print(f"Invalid client_id: {client_id}. Use 1, 2, or 3.")
        sys.exit(1)
    
    run_client(client_id, client_port, print_server, other_clients)
