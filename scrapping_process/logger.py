from sentry_sdk.integrations.logging    import LoggingIntegration
from dotenv                             import load_dotenv
import sentry_sdk
import logging
import os

def logger_setup():
    load_dotenv()
    sentry_logger=LoggingIntegration(
        level=logging.INFO, 
        event_level=logging.INFO
    )

    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[sentry_logger]
    )

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'
    )

if __name__=='__main__':
    logger_setup()
    logging.critical('testando')