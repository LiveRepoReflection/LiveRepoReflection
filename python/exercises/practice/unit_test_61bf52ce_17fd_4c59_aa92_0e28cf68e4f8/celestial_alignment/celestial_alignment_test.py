import unittest
from celestial_alignment import optimize_observations

class CelestialAlignmentTest(unittest.TestCase):
    def test_basic_case(self):
        observatories = ["obs1", "obs2"]
        objects = ["star1", "star2"]
        time_slots = 2
        observatory_capacities = {
            "obs1": 1,
            "obs2": 2
        }
        visibility_scores = {
            ("obs1", "star1", 0): 0.8,
            ("obs1", "star2", 0): 0.6,
            ("obs2", "star1", 0): 0.7,
            ("obs2", "star2", 0): 0.9,
            ("obs1", "star1", 1): 0.6,
            ("obs1", "star2", 1): 0.7,
            ("obs2", "star1", 1): 0.8,
            ("obs2", "star2", 1): 0.5
        }
        object_dependencies = {
            ("star1", 0): {("star2", 1): 0.2}
        }
        
        result = optimize_observations(
            observatories,
            objects,
            time_slots,
            observatory_capacities,
            visibility_scores,
            object_dependencies
        )
        
        self.assertIsInstance(result, dict)
        self.assertTrue(all(isinstance(k, tuple) and len(k) == 3 for k in result.keys()))
        self.assertTrue(all(isinstance(v, bool) for v in result.values()))
        
        # Check capacity constraints
        used_slots = {}
        for (obs, _, slot) in result:
            used_slots[obs] = used_slots.get(obs, 0) + 1
        for obs, count in used_slots.items():
            self.assertLessEqual(count, observatory_capacities[obs])

    def test_empty_case(self):
        result = optimize_observations([], [], 0, {}, {}, {})
        self.assertEqual(result, {})

    def test_single_observatory(self):
        observatories = ["obs1"]
        objects = ["star1"]
        time_slots = 1
        observatory_capacities = {"obs1": 1}
        visibility_scores = {("obs1", "star1", 0): 1.0}
        object_dependencies = {}
        
        result = optimize_observations(
            observatories,
            objects,
            time_slots,
            observatory_capacities,
            visibility_scores,
            object_dependencies
        )
        
        self.assertEqual(len(result), 1)
        self.assertTrue(("obs1", "star1", 0) in result)

    def test_negative_scores(self):
        observatories = ["obs1"]
        objects = ["star1"]
        time_slots = 1
        observatory_capacities = {"obs1": 1}
        visibility_scores = {("obs1", "star1", 0): -1.0}
        object_dependencies = {}
        
        result = optimize_observations(
            observatories,
            objects,
            time_slots,
            observatory_capacities,
            visibility_scores,
            object_dependencies
        )
        
        self.assertEqual(result, {})

    def test_complex_dependencies(self):
        observatories = ["obs1", "obs2"]
        objects = ["star1", "star2", "star3"]
        time_slots = 3
        observatory_capacities = {"obs1": 2, "obs2": 2}
        visibility_scores = {
            ("obs1", "star1", 0): 0.8,
            ("obs1", "star2", 1): 0.9,
            ("obs2", "star3", 2): 0.7
        }
        object_dependencies = {
            ("star1", 0): {("star2", 1): 0.3},
            ("star2", 1): {("star3", 2): 0.2}
        }
        
        result = optimize_observations(
            observatories,
            objects,
            time_slots,
            observatory_capacities,
            visibility_scores,
            object_dependencies
        )
        
        # Check that dependencies are respected
        if ("obs1", "star1", 0) in result and result[("obs1", "star1", 0)]:
            self.assertTrue(
                ("obs1", "star2", 1) in result or ("obs2", "star2", 1) in result
            )

    def test_capacity_limits(self):
        observatories = ["obs1"]
        objects = ["star1", "star2", "star3"]
        time_slots = 3
        observatory_capacities = {"obs1": 1}  # Can only use 1 time slot
        visibility_scores = {
            ("obs1", "star1", 0): 0.8,
            ("obs1", "star2", 1): 0.9,
            ("obs1", "star3", 2): 0.7
        }
        object_dependencies = {}
        
        result = optimize_observations(
            observatories,
            objects,
            time_slots,
            observatory_capacities,
            visibility_scores,
            object_dependencies
        )
        
        # Check that capacity constraint is respected
        obs1_slots = sum(1 for (obs, _, _) in result.keys() if obs == "obs1")
        self.assertLessEqual(obs1_slots, observatory_capacities["obs1"])

    def test_overlapping_constraints(self):
        observatories = ["obs1"]
        objects = ["star1", "star2"]
        time_slots = 1
        observatory_capacities = {"obs1": 1}
        visibility_scores = {
            ("obs1", "star1", 0): 0.8,
            ("obs1", "star2", 0): 0.9
        }
        object_dependencies = {}
        
        result = optimize_observations(
            observatories,
            objects,
            time_slots,
            observatory_capacities,
            visibility_scores,
            object_dependencies
        )
        
        # Check that observatory doesn't observe multiple objects in same time slot
        time_slot_counts = {}
        for (obs, _, slot) in result:
            time_slot_counts[(obs, slot)] = time_slot_counts.get((obs, slot), 0) + 1
            self.assertEqual(time_slot_counts[(obs, slot)], 1)

    def test_large_scale(self):
        # Generate large test case
        observatories = [f"obs{i}" for i in range(20)]
        objects = [f"star{i}" for i in range(20)]
        time_slots = 20
        observatory_capacities = {obs: 10 for obs in observatories}
        
        visibility_scores = {}
        for obs in observatories:
            for obj in objects:
                for slot in range(time_slots):
                    if (obs, obj, slot) not in visibility_scores:
                        visibility_scores[(obs, obj, slot)] = 0.5
        
        object_dependencies = {}
        for obj1 in objects[:5]:
            for slot1 in range(time_slots-1):
                for obj2 in objects[:5]:
                    object_dependencies[(obj1, slot1)] = {(obj2, slot1+1): 0.1}
        
        result = optimize_observations(
            observatories,
            objects,
            time_slots,
            observatory_capacities,
            visibility_scores,
            object_dependencies
        )
        
        # Basic validation of large-scale result
        self.assertIsInstance(result, dict)
        for obs in observatories:
            slots_used = sum(1 for (o, _, _) in result if o == obs)
            self.assertLessEqual(slots_used, observatory_capacities[obs])

if __name__ == '__main__':
    unittest.main()