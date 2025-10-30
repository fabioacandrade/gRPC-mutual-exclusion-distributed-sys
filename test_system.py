"""
Test script to demonstrate the distributed printing system.
Runs all components and shows them working together.
"""

import subprocess
import time
import signal
import sys

def run_test():
    """Run a test of the distributed printing system."""
    print("="*70)
    print("DISTRIBUTED PRINTING SYSTEM - TEST")
    print("="*70)
    print("\nStarting print server...")
    
    processes = []
    
    try:
        # Start print server
        server_proc = subprocess.Popen(
            ['python3', 'print_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        processes.append(('Server', server_proc))
        time.sleep(2)
        
        print("✓ Print server started")
        print("\nStarting clients...")
        
        # Start clients
        for client_id in [1, 2, 3]:
            client_proc = subprocess.Popen(
                ['python3', 'client.py', str(client_id)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            processes.append((f'Client {client_id}', client_proc))
            time.sleep(1)
        
        print("✓ All clients started")
        print("\n" + "="*70)
        print("System is running! Observing for 45 seconds...")
        print("The clients will automatically coordinate and print documents.")
        print("="*70 + "\n")
        
        # Let it run for 45 seconds
        for i in range(45):
            time.sleep(1)
            # Check if any process died
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠ {name} terminated unexpectedly!")
        
        print("\n" + "="*70)
        print("Test period completed. Shutting down...")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    
    finally:
        # Terminate all processes
        print("\nStopping all processes...")
        for name, proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=3)
                print(f"✓ {name} stopped")
            except Exception as e:
                print(f"⚠ Error stopping {name}: {e}")
                try:
                    proc.kill()
                except:
                    pass
        
        print("\n" + "="*70)
        print("Test completed!")
        print("="*70)


if __name__ == '__main__':
    run_test()
