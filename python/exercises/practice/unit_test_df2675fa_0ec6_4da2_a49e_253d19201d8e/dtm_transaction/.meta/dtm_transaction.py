import asyncio
import aiohttp
import logging
import json
from typing import List, Dict, Any
from urllib.parse import urlparse
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DTM:
    def __init__(self, services: List[str], timeout: int = 5, max_retries: int = 3):
        """
        Initialize the Distributed Transaction Manager.
        
        Args:
            services: List of service URLs
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed operations
        """
        self._validate_services(services)
        self.services = services
        self.timeout = timeout
        self.max_retries = max_retries
        self.processed_transactions = set()
        
    def _validate_services(self, services: List[str]) -> None:
        """Validate service URLs."""
        for service in services:
            parsed = urlparse(service)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError(f"Invalid service URL: {service}")

    async def execute_transaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a distributed transaction across all services.
        
        Args:
            payload: Transaction payload containing transaction_id and service-specific data
            
        Returns:
            Dict containing transaction result and status
        """
        if 'transaction_id' not in payload:
            raise ValueError("Payload must contain transaction_id")

        transaction_id = payload['transaction_id']
        
        # Check for idempotency
        if transaction_id in self.processed_transactions:
            logger.info(f"Transaction {transaction_id} already processed")
            return {
                'success': True,
                'transaction_id': transaction_id,
                'message': 'Transaction already processed'
            }

        try:
            # Phase 1: Prepare
            prepare_results = await self._execute_prepare_phase(payload)
            
            # If prepare phase successful, proceed to commit
            if all(result['success'] for result in prepare_results):
                commit_result = await self._execute_commit_phase(payload)
                if commit_result['success']:
                    self.processed_transactions.add(transaction_id)
                    return {
                        'success': True,
                        'transaction_id': transaction_id,
                        'message': 'Transaction completed successfully'
                    }
                else:
                    return {
                        'success': False,
                        'transaction_id': transaction_id,
                        'error': commit_result['error']
                    }
            
            # If prepare phase failed, execute rollback
            else:
                failed_services = [
                    result['service'] 
                    for result in prepare_results 
                    if not result['success']
                ]
                await self._execute_rollback_phase(payload)
                return {
                    'success': False,
                    'transaction_id': transaction_id,
                    'error': f"Prepare phase failed for services: {', '.join(failed_services)}"
                }
                
        except Exception as e:
            logger.error(f"Transaction {transaction_id} failed: {str(e)}")
            await self._execute_rollback_phase(payload)
            return {
                'success': False,
                'transaction_id': transaction_id,
                'error': str(e)
            }

    async def _execute_prepare_phase(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute prepare phase across all services."""
        tasks = []
        for service in self.services:
            tasks.append(self._send_prepare_request(service, payload))
        return await asyncio.gather(*tasks)

    async def _execute_commit_phase(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute commit phase across all services with retry mechanism."""
        for retry in range(self.max_retries):
            try:
                tasks = []
                for service in self.services:
                    tasks.append(self._send_commit_request(service, payload))
                results = await asyncio.gather(*tasks)
                
                if all(result['success'] for result in results):
                    return {'success': True}
                
                if retry < self.max_retries - 1:
                    wait_time = (2 ** retry) * 1  # Exponential backoff
                    logger.info(f"Commit retry {retry + 1}/{self.max_retries} in {wait_time}s")
                    await asyncio.sleep(wait_time)
                
            except Exception as e:
                if retry == self.max_retries - 1:
                    return {'success': False, 'error': f"Commit failed after {self.max_retries} retries: {str(e)}"}
                await asyncio.sleep(2 ** retry)
        
        return {'success': False, 'error': 'Commit phase failed after all retries'}

    async def _execute_rollback_phase(self, payload: Dict[str, Any]) -> None:
        """Execute rollback phase across all services."""
        tasks = []
        for service in self.services:
            tasks.append(self._send_rollback_request(service, payload))
        await asyncio.gather(*tasks)

    async def _send_prepare_request(self, service: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send prepare request to a service."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{service}/prepare",
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    if response.status == 200:
                        return {'success': True, 'service': service}
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'service': service,
                            'error': error_data.get('error', 'Unknown error')
                        }
        except asyncio.TimeoutError:
            return {
                'success': False,
                'service': service,
                'error': 'Request timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'service': service,
                'error': str(e)
            }

    async def _send_commit_request(self, service: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send commit request to a service."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{service}/commit",
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    return {'success': response.status == 200, 'service': service}
        except Exception as e:
            return {'success': False, 'service': service, 'error': str(e)}

    async def _send_rollback_request(self, service: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send rollback request to a service."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{service}/rollback",
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    return {'success': response.status == 200, 'service': service}
        except Exception as e:
            logger.error(f"Rollback failed for service {service}: {str(e)}")
            return {'success': False, 'service': service, 'error': str(e)}