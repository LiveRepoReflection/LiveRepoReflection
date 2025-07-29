import logging

def configure_logging():
    """
    Configure logging for the consistency checker.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('dfs_consistency.log')
        ]
    )