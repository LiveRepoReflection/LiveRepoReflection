import logging
from threading import Lock
from .services import InventoryError, PaymentError, OrderError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SagaOrchestrator:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SagaOrchestrator, cls).__new__(cls)
        return cls._instance

    def orchestrate_order(self, order_details, inventory_service, payment_service, 
                         order_service, notification_service):
        try:
            logger.info("Starting order processing for user %s", order_details['user_id'])
            
            # Step 1: Reserve inventory
            logger.info("Reserving inventory...")
            inventory_service.reserve_inventory(order_details)
            
            try:
                # Step 2: Process payment
                logger.info("Processing payment...")
                payment_service.process_payment(order_details)
                
                try:
                    # Step 3: Create order
                    logger.info("Creating order...")
                    order_service.create_order(order_details)
                    
                    try:
                        # Step 4: Send notification
                        logger.info("Sending notification...")
                        notification_service.send_confirmation(order_details)
                        logger.info("Order processed successfully")
                        return True
                        
                    except Exception as e:
                        logger.warning("Notification failed: %s. Continuing as this is non-critical.", str(e))
                        return True
                        
                except OrderError as e:
                    logger.error("Order creation failed: %s. Initiating compensation...", str(e))
                    # Compensate: Refund payment and release inventory
                    payment_service.refund_payment(order_details)
                    inventory_service.release_inventory(order_details)
                    return False
                    
            except PaymentError as e:
                logger.error("Payment processing failed: %s. Initiating compensation...", str(e))
                # Compensate: Release inventory
                inventory_service.release_inventory(order_details)
                return False
                
        except InventoryError as e:
            logger.error("Inventory reservation failed: %s. Aborting transaction.", str(e))
            return False

def orchestrate_order(order_details, inventory_service, payment_service, 
                     order_service, notification_service):
    orchestrator = SagaOrchestrator()
    return orchestrator.orchestrate_order(
        order_details, 
        inventory_service, 
        payment_service, 
        order_service, 
        notification_service
    )