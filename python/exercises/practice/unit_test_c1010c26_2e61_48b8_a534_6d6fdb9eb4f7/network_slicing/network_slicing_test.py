import unittest
from network_slicing import optimal_network_slicing

class NetworkSlicingTest(unittest.TestCase):
    
    def test_basic_allocation(self):
        """Test a basic allocation scenario with simple constraints."""
        total_bandwidth = 100
        total_compute = 50
        slices = [
            {
                "slice_id": "eMBB_1",
                "service_type": "eMBB",
                "bandwidth_demand": 20,
                "compute_demand": 10,
                "revenue_per_instance": 10.0,
                "qos_requirements": {"max_latency_ms": 50}
            },
            {
                "slice_id": "URLLC_1",
                "service_type": "URLLC",
                "bandwidth_demand": 10,
                "compute_demand": 5,
                "revenue_per_instance": 20.0,
                "qos_requirements": {"max_latency_ms": 1}
            },
            {
                "slice_id": "mMTC_1",
                "service_type": "mMTC",
                "bandwidth_demand": 5,
                "compute_demand": 2,
                "revenue_per_instance": 5.0,
                "qos_requirements": {"max_latency_ms": 100}
            }
        ]
        
        result = optimal_network_slicing(total_bandwidth, total_compute, slices)
        
        # Check return structure
        self.assertIn('allocation', result)
        self.assertIn('total_revenue', result)
        self.assertIn('unallocated_slices', result)
        self.assertIn('resource_utilization', result)
        
        # Check resource constraints
        used_bandwidth = sum(slices[i]["bandwidth_demand"] * count 
                           for i, (slice_id, count) in enumerate(result["allocation"].items()))
        used_compute = sum(slices[i]["compute_demand"] * count 
                          for i, (slice_id, count) in enumerate(result["allocation"].items()))
        
        self.assertLessEqual(used_bandwidth, total_bandwidth)
        self.assertLessEqual(used_compute, total_compute)
        
        # Check all slices are accounted for
        all_slices = {slice_info["slice_id"] for slice_info in slices}
        allocated_slices = set(result["allocation"].keys())
        unallocated_slices = set(result["unallocated_slices"])
        
        self.assertEqual(all_slices, allocated_slices.union(unallocated_slices))
        
        # Check total revenue
        expected_revenue = sum(slices[i]["revenue_per_instance"] * count 
                             for i, (slice_id, count) in enumerate(result["allocation"].items()))
        self.assertAlmostEqual(expected_revenue, result["total_revenue"])
        
        # Check resource utilization
        expected_bandwidth_utilization = (used_bandwidth / total_bandwidth) * 100
        expected_compute_utilization = (used_compute / total_compute) * 100
        
        self.assertAlmostEqual(expected_bandwidth_utilization, result["resource_utilization"]["bandwidth"])
        self.assertAlmostEqual(expected_compute_utilization, result["resource_utilization"]["compute"])

    def test_no_feasible_allocation(self):
        """Test when no allocation is possible due to resource constraints."""
        total_bandwidth = 10
        total_compute = 5
        slices = [
            {
                "slice_id": "eMBB_1",
                "service_type": "eMBB",
                "bandwidth_demand": 20,  # Exceeds total bandwidth
                "compute_demand": 10,    # Exceeds total compute
                "revenue_per_instance": 10.0,
                "qos_requirements": {"max_latency_ms": 50}
            }
        ]
        
        result = optimal_network_slicing(total_bandwidth, total_compute, slices)
        
        self.assertEqual(result["allocation"], {"eMBB_1": 0})
        self.assertEqual(result["total_revenue"], 0.0)
        self.assertEqual(set(result["unallocated_slices"]), {"eMBB_1"})
        self.assertEqual(result["resource_utilization"]["bandwidth"], 0.0)
        self.assertEqual(result["resource_utilization"]["compute"], 0.0)

    def test_multiple_instances(self):
        """Test allocation of multiple instances of the same slice type."""
        total_bandwidth = 100
        total_compute = 50
        slices = [
            {
                "slice_id": "mMTC_1",
                "service_type": "mMTC",
                "bandwidth_demand": 5,
                "compute_demand": 2,
                "revenue_per_instance": 5.0,
                "qos_requirements": {"max_latency_ms": 100}
            }
        ]
        
        result = optimal_network_slicing(total_bandwidth, total_compute, slices)
        
        # At most 20 instances of mMTC_1 can be allocated (bandwidth constraint)
        # At most 25 instances of mMTC_1 can be allocated (compute constraint)
        # Thus, we expect 20 instances to be allocated
        self.assertLessEqual(result["allocation"]["mMTC_1"], 20)
        self.assertGreaterEqual(result["allocation"]["mMTC_1"], 1)  # At least one instance should be allocated
        
        # Check total revenue
        expected_revenue = slices[0]["revenue_per_instance"] * result["allocation"]["mMTC_1"]
        self.assertEqual(expected_revenue, result["total_revenue"])

    def test_qos_requirements(self):
        """Test allocation with QoS requirements."""
        total_bandwidth = 100
        total_compute = 50
        slices = [
            {
                "slice_id": "URLLC_1",
                "service_type": "URLLC",
                "bandwidth_demand": 10,
                "compute_demand": 5,
                "revenue_per_instance": 20.0,
                "qos_requirements": {"max_latency_ms": 1}
            },
            {
                "slice_id": "URLLC_2",
                "service_type": "URLLC",
                "bandwidth_demand": 10,
                "compute_demand": 5,
                "revenue_per_instance": 15.0,
                "qos_requirements": {"max_latency_ms": 0.5}  # More stringent QoS
            }
        ]
        
        result = optimal_network_slicing(total_bandwidth, total_compute, slices)
        
        # The allocation should prioritize higher revenue slices subject to QoS constraints
        self.assertGreaterEqual(result["allocation"]["URLLC_1"] * 20.0, 
                               result["allocation"]["URLLC_2"] * 15.0)

    def test_complex_scenario(self):
        """Test a complex allocation scenario with multiple slice types and resource constraints."""
        total_bandwidth = 200
        total_compute = 100
        slices = [
            {
                "slice_id": "eMBB_1",
                "service_type": "eMBB",
                "bandwidth_demand": 40,
                "compute_demand": 20,
                "revenue_per_instance": 30.0,
                "qos_requirements": {"max_latency_ms": 50}
            },
            {
                "slice_id": "URLLC_1",
                "service_type": "URLLC",
                "bandwidth_demand": 20,
                "compute_demand": 10,
                "revenue_per_instance": 40.0,
                "qos_requirements": {"max_latency_ms": 1}
            },
            {
                "slice_id": "mMTC_1",
                "service_type": "mMTC",
                "bandwidth_demand": 10,
                "compute_demand": 5,
                "revenue_per_instance": 15.0,
                "qos_requirements": {"max_latency_ms": 100}
            },
            {
                "slice_id": "eMBB_2",
                "service_type": "eMBB",
                "bandwidth_demand": 50,
                "compute_demand": 25,
                "revenue_per_instance": 35.0,
                "qos_requirements": {"max_latency_ms": 40}
            }
        ]
        
        result = optimal_network_slicing(total_bandwidth, total_compute, slices)
        
        # Check resource constraints
        used_bandwidth = 0
        used_compute = 0
        for i, slice_info in enumerate(slices):
            slice_id = slice_info["slice_id"]
            if slice_id in result["allocation"]:
                used_bandwidth += slice_info["bandwidth_demand"] * result["allocation"][slice_id]
                used_compute += slice_info["compute_demand"] * result["allocation"][slice_id]
        
        self.assertLessEqual(used_bandwidth, total_bandwidth)
        self.assertLessEqual(used_compute, total_compute)
        
        # Check all slices are accounted for
        all_slices = {slice_info["slice_id"] for slice_info in slices}
        allocated_slices = set(result["allocation"].keys())
        unallocated_slices = set(result["unallocated_slices"])
        
        self.assertEqual(all_slices, allocated_slices.union(unallocated_slices))
        
        # Check that all unallocated slices have 0 instances
        for slice_id in result["unallocated_slices"]:
            self.assertEqual(result["allocation"].get(slice_id, 0), 0)

    def test_empty_slices(self):
        """Test allocation with empty slices."""
        total_bandwidth = 100
        total_compute = 50
        slices = []
        
        result = optimal_network_slicing(total_bandwidth, total_compute, slices)
        
        self.assertEqual(result["allocation"], {})
        self.assertEqual(result["total_revenue"], 0.0)
        self.assertEqual(result["unallocated_slices"], [])
        self.assertEqual(result["resource_utilization"]["bandwidth"], 0.0)
        self.assertEqual(result["resource_utilization"]["compute"], 0.0)

    def test_zero_resources(self):
        """Test allocation with zero resources."""
        total_bandwidth = 0
        total_compute = 0
        slices = [
            {
                "slice_id": "eMBB_1",
                "service_type": "eMBB",
                "bandwidth_demand": 20,
                "compute_demand": 10,
                "revenue_per_instance": 10.0,
                "qos_requirements": {"max_latency_ms": 50}
            }
        ]
        
        result = optimal_network_slicing(total_bandwidth, total_compute, slices)
        
        self.assertEqual(result["allocation"], {"eMBB_1": 0})
        self.assertEqual(result["total_revenue"], 0.0)
        self.assertEqual(set(result["unallocated_slices"]), {"eMBB_1"})
        self.assertEqual(result["resource_utilization"]["bandwidth"], 0.0)
        self.assertEqual(result["resource_utilization"]["compute"], 0.0)

    def test_optimal_allocation(self):
        """Test that the allocation maximizes total revenue."""
        total_bandwidth = 100
        total_compute = 50
        slices = [
            {
                "slice_id": "eMBB_1",
                "service_type": "eMBB",
                "bandwidth_demand": 20,
                "compute_demand": 10,
                "revenue_per_instance": 10.0,
                "qos_requirements": {"max_latency_ms": 50}
            },
            {
                "slice_id": "URLLC_1",
                "service_type": "URLLC",
                "bandwidth_demand": 10,
                "compute_demand": 5,
                "revenue_per_instance": 20.0,
                "qos_requirements": {"max_latency_ms": 1}
            },
            {
                "slice_id": "mMTC_1",
                "service_type": "mMTC",
                "bandwidth_demand": 5,
                "compute_demand": 2,
                "revenue_per_instance": 5.0,
                "qos_requirements": {"max_latency_ms": 100}
            }
        ]
        
        result = optimal_network_slicing(total_bandwidth, total_compute, slices)
        
        # Verify that the allocation maximizes total revenue
        # For this specific example:
        # Maximum eMBB_1 instances: 100/20 = 5 (bandwidth constraint), 50/10 = 5 (compute constraint)
        # Maximum URLLC_1 instances: 100/10 = 10 (bandwidth), 50/5 = 10 (compute)
        # Maximum mMTC_1 instances: 100/5 = 20 (bandwidth), 50/2 = 25 (compute)
        # 
        # Optimal solution would prioritize higher revenue per resource usage:
        # URLLC_1: 20/10 = 2 revenue per bandwidth, 20/5 = 4 revenue per compute
        # eMBB_1: 10/20 = 0.5 revenue per bandwidth, 10/10 = 1 revenue per compute
        # mMTC_1: 5/5 = 1 revenue per bandwidth, 5/2 = 2.5 revenue per compute
        #
        # Expected optimal allocation:
        # - Maximize URLLC_1 first: 10 instances (uses 100 bandwidth, 50 compute)
        # - Total revenue: 10 * 20.0 = 200.0
        
        total_revenue = sum(slices[i]["revenue_per_instance"] * count 
                           for i, (slice_id, count) in enumerate(result["allocation"].items())
                           if slice_id in result["allocation"])
                           
        self.assertGreaterEqual(total_revenue, 200.0) # Should be at least the expected optimal solution

if __name__ == '__main__':
    unittest.main()