from key_value_store import DistributedKeyValueStore

def main():
    # Initialize the store with default node count
    n_nodes = 100
    store = DistributedKeyValueStore(n_nodes)
    
    # Number of operations to process
    try:
        num_operations = int(input())
    except ValueError:
        num_operations = 0
    
    # Process each operation
    for _ in range(num_operations):
        try:
            command = input().strip()
            parts = command.split()
            
            if parts[0] == "PUT":
                key = parts[1]
                value = int(parts[2])
                replication_factor = int(parts[3])
                store.put(key, value, replication_factor)
            
            elif parts[0] == "GET":
                key = parts[1]
                print(store.get(key))
            
            elif parts[0] == "DELETE":
                key = parts[1]
                store.delete(key)
            
            else:
                print(f"Unknown operation: {parts[0]}")
        
        except Exception as e:
            print(f"Error processing command: {e}")

if __name__ == "__main__":
    main()