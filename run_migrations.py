#!/usr/bin/env python3
"""
Script to run database migrations and initialize the database.
This script is called before starting the main application.
"""
import os
import sys
import time
import logging
from config.database import create_tables, check_connection
from config.logging_config import setup_logging

def wait_for_database(max_retries=30, delay=2):
    """Wait for database to be ready."""
    logger = logging.getLogger(__name__)

    for attempt in range(max_retries):
        logger.info(f"Attempting database connection (attempt {attempt + 1}/{max_retries})...")

        if check_connection():
            logger.info("✅ Database connection successful!")
            return True

        if attempt < max_retries - 1:
            logger.warning(f"Database not ready, waiting {delay} seconds...")
            time.sleep(delay)

    logger.error("❌ Failed to connect to database after all retries")
    return False

def main():
    """Main function to initialize database."""
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Starting database initialization...")

    # Wait for database to be ready
    if not wait_for_database():
        logger.error("❌ Cannot proceed without database connection")
        sys.exit(1)

    # Create tables
    try:
        create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        sys.exit(1)

    logger.info("✅ Database initialization complete")

if __name__ == "__main__":
    main()
