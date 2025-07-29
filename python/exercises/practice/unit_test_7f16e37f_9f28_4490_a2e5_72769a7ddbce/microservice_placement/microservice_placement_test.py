import unittest
from microservice_placement import find_optimal_placement

# Dummy implementations to support the test cases
class Machine:
    def __init__(self, machine_id, cpu_capacity, memory_capacity, network_capacity):
        self.machine_id = machine_id
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.network_capacity = network_capacity

class Microservice:
    def __init__(self, service_id, cpu_requirement, memory_requirement, network_requirement, latency_dependencies):
        self.service_id = service_id
        self.cpu_requirement = cpu_requirement
        self.memory_requirement = memory_requirement
        self.network_requirement = network_requirement
        self.latency_dependencies = latency_dependencies

class TestMicroservicePlacement(unittest.TestCase):

    def test_all_services_on_one_machine_optimal(self):
        # Test where all services can and should be deployed on one machine to minimize cost.
        machines = [
            Machine(machine_id="m1", cpu_capacity=200, memory_capacity=200, network_capacity=200),
            Machine(machine_id="m2", cpu_capacity=200, memory_capacity=200, network_capacity=200)
        ]
        microservices = [
            Microservice(service_id="s1", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={}),
            Microservice(service_id="s2", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={"s1": 60}),
            Microservice(service_id="s3", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={"s2": 70})
        ]
        latency = 50

        placement = find_optimal_placement(machines, microservices, latency)
        # Expect all microservices in one machine (either m1 or m2)
        self.assertTrue(len(set(placement.values())) == 1)
        # Verify every service is allocated
        self.assertCountEqual(list(placement.keys()), ["s1", "s2", "s3"])

    def test_capacity_constraint_failure(self):
        # Test where capacity constraints force an infeasible placement.
        # Here, one machine has too little capacity and the other cannot satisfy latency requirements if separated.
        machines = [
            Machine(machine_id="m1", cpu_capacity=100, memory_capacity=100, network_capacity=100),
            Machine(machine_id="m2", cpu_capacity=100, memory_capacity=100, network_capacity=100)
        ]
        # Three services each requiring 50. All three cannot fit on one machine (total 150 > 100)
        # And if split, a dependency with tight latency constraint cannot be satisfied.
        microservices = [
            Microservice(service_id="s1", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={"s2": 60}),
            Microservice(service_id="s2", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={"s1": 60, "s3": 40}),
            Microservice(service_id="s3", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={"s2": 40})
        ]
        latency = 80  # Latency when services are placed on different machines

        placement = find_optimal_placement(machines, microservices, latency)
        # No valid placement exists because s2-s3 dependency requires latency <=40
        self.assertEqual(placement, {})

    def test_multi_machine_optimal_placement(self):
        # Test where resource limitations force the optimal solution to span two machines.
        machines = [
            Machine(machine_id="m1", cpu_capacity=100, memory_capacity=100, network_capacity=100),
            Machine(machine_id="m2", cpu_capacity=100, memory_capacity=100, network_capacity=100)
        ]
        # Two services can fit on one machine, the third must be on the other.
        # Latency dependencies allow services on different machines as long as latency <= 60.
        microservices = [
            Microservice(service_id="s1", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={"s2": 60}),
            Microservice(service_id="s2", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={"s1": 60, "s3": 60}),
            Microservice(service_id="s3", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={"s2": 60})
        ]
        latency = 50  # acceptable latency

        placement = find_optimal_placement(machines, microservices, latency)
        # We expect two machines to be used
        self.assertTrue(len(set(placement.values())) == 2)
        self.assertCountEqual(list(placement.keys()), ["s1", "s2", "s3"])
        # Check that s2 and s3 might be on same machine; if not then latency constraint is still satisfied.
        if placement["s2"] != placement["s3"]:
            self.assertTrue(latency <= 60)

    def test_no_valid_placement_due_to_latency(self):
        # Test where latency requirements force an impossible placement even if capacity is sufficient.
        machines = [
            Machine(machine_id="m1", cpu_capacity=300, memory_capacity=300, network_capacity=300),
            Machine(machine_id="m2", cpu_capacity=300, memory_capacity=300, network_capacity=300)
        ]
        # Services with very restrictive latency dependency forcing them to be on the same machine,
        # but capacity allows placing them on separate machines.
        microservices = [
            Microservice(service_id="s1", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={"s2": 30}),
            Microservice(service_id="s2", cpu_requirement=50, memory_requirement=50, network_requirement=50, latency_dependencies={"s1": 30})
        ]
        latency = 50 # Higher than allowed latency dependency threshold
        
        placement = find_optimal_placement(machines, microservices, latency)
        # The only valid placement would have both services on the same machine
        if placement:
            self.assertEqual(placement["s1"], placement["s2"])
        else:
            # If algorithm cannot satisfy this due to design, it should return empty dict.
            self.assertEqual(placement, {})

    def test_complex_scenario(self):
        # A more complex scenario with more microservices and dependencies
        machines = [
            Machine(machine_id="m1", cpu_capacity=400, memory_capacity=400, network_capacity=400),
            Machine(machine_id="m2", cpu_capacity=300, memory_capacity=300, network_capacity=300),
            Machine(machine_id="m3", cpu_capacity=300, memory_capacity=300, network_capacity=300)
        ]
        microservices = [
            Microservice(service_id="s1", cpu_requirement=100, memory_requirement=100, network_requirement=100, latency_dependencies={"s2": 50, "s3": 70}),
            Microservice(service_id="s2", cpu_requirement=100, memory_requirement=100, network_requirement=100, latency_dependencies={"s1": 50, "s4": 60}),
            Microservice(service_id="s3", cpu_requirement=100, memory_requirement=100, network_requirement=100, latency_dependencies={"s1": 70}),
            Microservice(service_id="s4", cpu_requirement=100, memory_requirement=100, network_requirement=100, latency_dependencies={"s2": 60, "s5": 80}),
            Microservice(service_id="s5", cpu_requirement=100, memory_requirement=100, network_requirement=100, latency_dependencies={"s4": 80})
        ]
        latency = 40  # stringent latency, forcing services with dependencies to be collocated when possible

        placement = find_optimal_placement(machines, microservices, latency)
        # Verify that a valid placement is returned if one exists
        if placement:
            # Check all services are allocated
            self.assertCountEqual(list(placement.keys()), ["s1", "s2", "s3", "s4", "s5"])
            # For every dependency, if on different machines then latency must be <= threshold.
            for ms in microservices:
                for dep, max_latency in ms.latency_dependencies.items():
                    if placement[ms.service_id] != placement.get(dep, None):
                        self.assertTrue(latency <= max_latency)
        else:
            # If no valid placement, then placement must be empty dict.
            self.assertEqual(placement, {})

if __name__ == '__main__':
    unittest.main()