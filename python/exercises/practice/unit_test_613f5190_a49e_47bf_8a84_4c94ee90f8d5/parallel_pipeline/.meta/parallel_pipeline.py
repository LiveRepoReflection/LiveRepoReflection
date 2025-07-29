import concurrent.futures
import traceback

def run_pipeline(data_objects, processing_steps, dependencies):
    """
    Process each data object concurrently using a pipeline that respects dependency constraints.
    
    :param data_objects: List[int] - list of data object IDs.
    :param processing_steps: Dict[str, function] - mapping from step names to functions.
    :param dependencies: Dict[str, List[str]] - mapping from step names to list of step names they depend on.
    :return: Dict[int, Dict[str, Any]] - mapping from data object ID to a dictionary of results per processing step.
    """
    results = {}

    # We use ThreadPoolExecutor at the outer level to process multiple data objects concurrently.
    with concurrent.futures.ThreadPoolExecutor() as outer_executor:
        # Submit tasks to process individual data objects concurrently.
        future_to_data = {
            outer_executor.submit(process_data, data_id, processing_steps, dependencies): data_id
            for data_id in data_objects
        }
        for future in concurrent.futures.as_completed(future_to_data):
            data_id = future_to_data[future]
            try:
                results[data_id] = future.result()
            except Exception as ex:
                # In case processing the entire data object fails, record the error under a special key.
                results[data_id] = {"error": str(ex)}
    return results

def process_data(data_id, processing_steps, dependencies):
    """
    Process a single data object, running processing steps with dependency resolution in parallel.
    
    :param data_id: int - identifier for the data object.
    :param processing_steps: Dict[str, function] - mapping from step names to functions.
    :param dependencies: Dict[str, List[str]] - mapping from step names to list of step names they depend on.
    :return: Dict[str, Any] - results of each processing step for the data object.
    """
    # Use a local executor for steps concurrency for this data_id.
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(processing_steps)) as local_executor:
        step_futures = {}

        def get_future(step_name):
            if step_name in step_futures:
                return step_futures[step_name]
            
            # Gather futures for all dependencies first.
            dep_names = dependencies.get(step_name, [])
            dep_futures = [get_future(dep) for dep in dep_names]

            # Function to execute after waiting for dependencies.
            def execute_step():
                # Wait for dependencies to complete.
                for dep_future in dep_futures:
                    try:
                        dep_future.result()
                    except Exception:
                        # Even if dependency failed, we consider it as "completed"
                        pass
                try:
                    # Call the processing function for the current step.
                    return processing_steps[step_name](data_id)
                except Exception as e:
                    # Return the error message if an exception is raised.
                    return str(e)
            
            # Submit the task to the local executor.
            future = local_executor.submit(execute_step)
            step_futures[step_name] = future
            return future

        # Schedule all steps.
        for step in processing_steps.keys():
            get_future(step)

        # Wait for all tasks to complete and collect results.
        results = {}
        for step, future in step_futures.items():
            try:
                value = future.result()
                results[step] = value
            except Exception as e:
                # Though exceptions are caught inside execute_step, this is a fallback.
                results[step] = str(e)
        return results