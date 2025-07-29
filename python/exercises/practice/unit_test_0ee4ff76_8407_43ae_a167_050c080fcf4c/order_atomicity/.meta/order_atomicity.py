class InventoryService:
    @staticmethod
    def reserve_stock(item_id, quantity):
        # Simulated implementation for reserving stock
        return True

    @staticmethod
    def release_stock(item_id, quantity):
        # Simulated implementation for releasing stock
        return True


class PaymentService:
    @staticmethod
    def charge(user_id, amount):
        # Simulated implementation for charging a user
        return "txn_default"

    @staticmethod
    def refund(transaction_id):
        # Simulated implementation for refunding a transaction
        return True


class ShippingService:
    @staticmethod
    def schedule_shipment(user_id, item_id, quantity, address):
        # Simulated implementation for scheduling a shipment
        return "ship_default"

    @staticmethod
    def cancel_shipment(shipment_id):
        # Simulated implementation for canceling a shipment
        return True


class NotificationService:
    @staticmethod
    def send_notification(user_id, message):
        # Simulated implementation for sending notification
        return True


class OrderOrchestrator:
    def place_order(self, user_id, item_id, quantity, address):
        steps = []
        # Step 1: Reserve stock
        if not InventoryService.reserve_stock(item_id, quantity):
            return "Order failed: Insufficient stock."
        steps.append({"step": "inventory", "data": (item_id, quantity)})

        # Step 2: Charge the user
        # For demonstration, amount is derived as quantity * 10
        transaction_id = PaymentService.charge(user_id, amount=quantity * 10)
        if not transaction_id:
            self.compensate(steps)
            return "Order failed: Payment failed."
        steps.append({"step": "payment", "data": transaction_id})

        # Step 3: Schedule shipment
        shipment_id = ShippingService.schedule_shipment(user_id, item_id, quantity, address)
        if not shipment_id:
            self.compensate(steps)
            return "Order failed: Shipping could not be scheduled."
        steps.append({"step": "shipping", "data": shipment_id})

        # Step 4: Send notification (non-critical)
        notification_sent = NotificationService.send_notification(user_id, "Your order has been placed.")
        if not notification_sent:
            # Log notification failure, but do not rollback the transaction.
            pass

        order_data = {
            "order_id": f"order_{user_id}_{item_id}",
            "transaction_id": transaction_id,
            "shipment_id": shipment_id
        }
        return order_data

    def compensate(self, steps):
        # Rollback all steps in reverse order.
        for step in reversed(steps):
            if step["step"] == "shipping":
                ShippingService.cancel_shipment(step["data"])
            elif step["step"] == "payment":
                PaymentService.refund(step["data"])
            elif step["step"] == "inventory":
                item_id, quantity = step["data"]
                InventoryService.release_stock(item_id, quantity)