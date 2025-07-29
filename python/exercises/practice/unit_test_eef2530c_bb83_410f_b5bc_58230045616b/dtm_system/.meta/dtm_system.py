class Service:
    def __init__(self, name):
        self.name = name
        self.data = {}
        self.available = True
        self.validate_update = None

_NO_VALUE = object()

class DTM:
    def __init__(self):
        self._services = {}
        self._transactions = {}  # transaction_id -> {"status": status, "updates": {service_name: {key: (old_value, new_value)}}}
        self._next_txn_id = 1

    def register_service(self, service_name):
        if service_name in self._services:
            raise ValueError(f"Service '{service_name}' is already registered.")
        self._services[service_name] = Service(service_name)

    def begin_transaction(self):
        txn_id = self._next_txn_id
        self._next_txn_id += 1
        self._transactions[txn_id] = {"status": "pending", "updates": {}}
        return txn_id

    def prepare_transaction(self, transaction_id, operations):
        if transaction_id not in self._transactions:
            raise ValueError("Transaction ID not found.")
        txn_record = self._transactions[transaction_id]

        # Validate that each service in operations is registered.
        for service_name in operations:
            if service_name not in self._services:
                raise ValueError(f"Service '{service_name}' is not registered.")

        # First pass: Validate updates without applying them.
        for service_name, op in operations.items():
            service = self._services[service_name]
            if not service.available:
                txn_record["status"] = "rolledback"
                return False
            for key, new_value in op.items():
                if service.validate_update is None or not service.validate_update(key, new_value):
                    txn_record["status"] = "rolledback"
                    return False

        # Second pass: Record the original values and apply the new updates.
        for service_name, op in operations.items():
            service = self._services[service_name]
            txn_record["updates"].setdefault(service_name, {})
            for key, new_value in op.items():
                if key in service.data:
                    old_value = service.data[key]
                else:
                    old_value = _NO_VALUE
                txn_record["updates"][service_name][key] = (old_value, new_value)
                service.data[key] = new_value

        txn_record["status"] = "prepared"
        return True

    def commit_transaction(self, transaction_id):
        if transaction_id not in self._transactions:
            raise ValueError("Transaction ID not found.")
        txn_record = self._transactions[transaction_id]
        if txn_record["status"] == "prepared":
            txn_record["status"] = "committed"
        # If already committed or rolledback, no action is taken.

    def rollback_transaction(self, transaction_id):
        if transaction_id not in self._transactions:
            raise ValueError("Transaction ID not found.")
        txn_record = self._transactions[transaction_id]
        if txn_record["status"] != "prepared":
            # If transaction is not in a prepared state, rollback is not applicable.
            return

        # For each service involved, restore the original value.
        for service_name, updates in txn_record["updates"].items():
            service = self._services[service_name]
            for key, (old_value, new_value) in updates.items():
                if old_value is _NO_VALUE:
                    if key in service.data:
                        del service.data[key]
                else:
                    service.data[key] = old_value
        txn_record["status"] = "rolledback"

    def get_service_data(self, service_name):
        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' is not registered.")
        return self._services[service_name].data.copy()