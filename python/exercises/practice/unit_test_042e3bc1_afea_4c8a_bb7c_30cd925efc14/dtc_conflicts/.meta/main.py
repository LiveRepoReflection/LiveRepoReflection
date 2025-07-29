import sys
from .dtc import DistributedTransactionCoordinator

def main():
    """
    Main function to run the DTC from command line.
    
    Usage:
    - Pass commands via stdin, one per line
    - Commands should follow the format described in the problem statement
    - Outputs will be printed to stdout
    """
    dtc = DistributedTransactionCoordinator()
    
    # Set up initial services (user can modify this as needed)
    for i in range(1, 6):
        dtc.add_service(i)
    
    print("DTC initialized with services 1-5. Ready for input.")
    print("Enter commands (BEGIN, READ, WRITE, COMMIT, ROLLBACK):")

    # Process commands from stdin
    for line in sys.stdin:
        line = line.strip()
        
        if not line or line.lower() == "exit":
            break
            
        try:
            output = dtc.process_command(line)
            if output:
                print(output)
        except ValueError as e:
            print(f"Error: {str(e)}")
    
    print("DTC terminating")

if __name__ == "__main__":
    main()