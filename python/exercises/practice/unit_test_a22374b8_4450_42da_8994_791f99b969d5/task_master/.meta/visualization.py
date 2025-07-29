import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import numpy as np

def visualize_schedule(events, tasks, num_workers, output_file=None):
    """
    Visualize the task schedule on a Gantt chart
    
    Args:
        events: List of events (timestamp, worker_id, event_type, task_id)
        tasks: List of tuples (task_id, priority, dependencies, execution_time)
        num_workers: Number of workers
        output_file: Optional file path to save the visualization
    """
    # Extract task information for easier access
    task_dict = {task[0]: {"id": task[0], 
                          "priority": task[1], 
                          "deps": set(task[2]), 
                          "exec_time": task[3]} for task in tasks}
    
    # Track task execution periods
    executions = []
    task_colors = {}
    
    # Process events to extract execution periods
    for i in range(len(events)):
        timestamp, worker_id, event_type, task_id = events[i]
        
        if event_type == "SCHEDULED":
            # Find the corresponding COMPLETED or FAILED event
            end_time = None
            for j in range(i+1, len(events)):
                t2, w2, e2, tid2 = events[j]
                if w2 == worker_id and tid2 == task_id and (e2 == "COMPLETED" or e2 == "FAILED"):
                    end_time = t2
                    break
            
            if end_time is not None:
                executions.append((worker_id, task_id, timestamp, end_time, event_type))
    
    # Assign colors to tasks
    for task_id in task_dict:
        if task_id not in task_colors:
            # Generate a random color
            task_colors[task_id] = (random.random(), random.random(), random.random())
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Set up the chart
    ax.set_xlabel('Time')
    ax.set_ylabel('Worker')
    ax.set_yticks(range(num_workers))
    ax.set_yticklabels([f'Worker {i}' for i in range(num_workers)])
    
    # Find the maximum end time to set the x-axis limit
    max_time = max([end_time for _, _, _, end_time, _ in executions]) if executions else 0
    ax.set_xlim(0, max_time + 1)
    
    # Plot task executions
    for worker_id, task_id, start_time, end_time, event_type in executions:
        color = task_colors[task_id]
        duration = end_time - start_time
        
        # Add a rectangle for the task execution
        rect = patches.Rectangle((start_time, worker_id - 0.4), duration, 0.8, 
                                linewidth=1, edgecolor='black', facecolor=color, alpha=0.7)
        ax.add_patch(rect)
        
        # Add task label
        ax.text(start_time + duration/2, worker_id, f'Task {task_id}', 
                ha='center', va='center', color='black', fontweight='bold')
        
        # Indicate failed tasks with a pattern
        if event_type == "FAILED":
            ax.add_patch(patches.Rectangle((start_time, worker_id - 0.4), duration, 0.8, 
                                        fill=False, hatch='///', edgecolor='red'))
    
    # Add a legend for the tasks
    legend_elements = [patches.Patch(facecolor=task_colors[task_id], 
                                   edgecolor='black',
                                   label=f'Task {task_id} (Priority: {task_dict[task_id]["priority"]})') 
                      for task_id in sorted(task_dict.keys())]
    
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.15),
              fancybox=True, shadow=True, ncol=min(5, len(task_dict)))
    
    plt.title('Task Execution Schedule')
    plt.grid(True, axis='x')
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
    else:
        plt.show()

def visualize_dependency_graph(tasks, output_file=None):
    """
    Visualize the task dependency graph
    
    Args:
        tasks: List of tuples (task_id, priority, dependencies, execution_time)
        output_file: Optional file path to save the visualization
    """
    try:
        import networkx as nx
    except ImportError:
        print("NetworkX library is required for dependency graph visualization.")
        return
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes (tasks)
    for task_id, priority, _, exec_time in tasks:
        G.add_node(task_id, priority=priority, exec_time=exec_time)
    
    # Add edges (dependencies)
    for task_id, _, dependencies, _ in tasks:
        for dep_id in dependencies:
            G.add_edge(dep_id, task_id)
    
    # Create plot
    plt.figure(figsize=(10, 8))
    
    # Position nodes using spring layout
    pos = nx.spring_layout(G, seed=42)
    
    # Get node colors based on priority (lower priority number = higher priority = darker color)
    priorities = nx.get_node_attributes(G, 'priority')
    max_priority = max(priorities.values()) if priorities else 1
    node_colors = [1 - (priorities.get(n, 0) / max_priority) for n in G.nodes()]
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.Blues, 
                          node_size=500, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=15)
    
    # Draw labels
    labels = {n: f'Task {n}\nP: {priorities.get(n, "N/A")}' for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10)
    
    plt.title('Task Dependency Graph')
    plt.axis('off')
    
    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
    else:
        plt.show()

if __name__ == "__main__":
    # Example usage
    from task_master import schedule_tasks
    
    # Example tasks
    tasks = [
        (1, 1, [], 5),
        (2, 2, [1], 3),
        (3, 1, [], 4),
        (4, 3, [2, 3], 2)
    ]
    
    num_workers = 2
    schedule = schedule_tasks(tasks, num_workers)
    
    visualize_schedule(schedule, tasks, num_workers)
    visualize_dependency_graph(tasks)