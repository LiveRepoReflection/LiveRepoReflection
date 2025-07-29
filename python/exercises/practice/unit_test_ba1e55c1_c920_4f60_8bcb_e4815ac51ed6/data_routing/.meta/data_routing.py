class RoutingSystem:
    def __init__(self):
        # Internal mapping from sensor_id to the set of processing center IDs.
        self.sensor_to_centers = {}

    def update_routing_rules(self, routing_rules):
        # Override previous rules by resetting the internal mapping.
        self.sensor_to_centers = {}
        # Update the mapping for each provided routing rule.
        for sensor_id_set, processing_center_id_set in routing_rules:
            for sensor in sensor_id_set:
                if sensor in self.sensor_to_centers:
                    self.sensor_to_centers[sensor].update(processing_center_id_set)
                else:
                    self.sensor_to_centers[sensor] = set(processing_center_id_set)

    def route_data(self, sensor_id):
        # Return the set of processing center IDs for the given sensor_id.
        # If the sensor has no associated centers, return an empty set.
        return self.sensor_to_centers.get(sensor_id, set())