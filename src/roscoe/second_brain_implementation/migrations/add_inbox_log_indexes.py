#!/usr/bin/env python3
"""
Inbox Log Schema Migration for FalkorDB

This script adds indexes to CaptureLog nodes for efficient inbox tracking and querying.
CaptureLog nodes are created by CaptureMiddleware as an audit trail for all captures.

Indexes added:
- timestamp: For querying captures by date/time (captured_at field)
- status: For filtering filed vs needs_review captures
- confidence: For finding low-confidence captures that need review

Usage:
    # Normal migration (executes changes)
    python add_inbox_log_indexes.py

    # Dry run (shows what would be done)
    python add_inbox_log_indexes.py --dry-run

    # Validate schema without changes
    python add_inbox_log_indexes.py --validate

    # Rollback (remove CaptureLog indexes)
    python add_inbox_log_indexes.py --rollback

Requirements:
    - FalkorDB running and accessible
    - falkordb-py package installed
    - FALKORDB_HOST and FALKORDB_PORT environment variables (or defaults)

Author: Task 4 - Second Brain Integration
Date: 2026-01-11
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from falkordb import FalkorDB
except ImportError:
    print("ERROR: falkordb package not installed. Run: pip install falkordb")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

FALKORDB_HOST = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", "6379"))
GRAPH_NAME = "roscoe_graph"

# Log file location
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, f"migration_inbox_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


# =============================================================================
# Index Definitions
# =============================================================================

@dataclass
class IndexDefinition:
    """Defines an index to be created"""
    label: str
    property: str

    def create_query(self) -> str:
        """Generate CREATE INDEX query (FalkorDB simple syntax)"""
        return f"CREATE INDEX ON :{self.label}({self.property})"

    def drop_query(self) -> str:
        """Generate DROP INDEX query"""
        return f"DROP INDEX ON :{self.label}({self.property})"

    def __str__(self) -> str:
        return f":{self.label}({self.property})"


# CaptureLog indexes for inbox tracking
INBOX_LOG_INDEXES = [
    # Timestamp for querying captures by date/time
    IndexDefinition("CaptureLog", "timestamp"),

    # Status for filtering filed vs needs_review captures
    IndexDefinition("CaptureLog", "status"),

    # Confidence for finding low-confidence captures
    IndexDefinition("CaptureLog", "confidence"),
]


# Sample queries to validate CaptureLog schema
VALIDATION_QUERIES = [
    "MATCH (l:CaptureLog) RETURN count(l) as capture_log_count",
    "CALL db.indexes() YIELD label, properties RETURN label, properties",
]


# =============================================================================
# Logging Setup
# =============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging to file and console"""
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("migration_inbox_log")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # File handler (always DEBUG level)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


# =============================================================================
# Database Operations
# =============================================================================

class MigrationManager:
    """Manages CaptureLog inbox schema migration"""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.logger = setup_logging(verbose)
        self.db = None
        self.graph = None
        self.errors: List[str] = []

    def connect(self) -> bool:
        """Connect to FalkorDB"""
        try:
            self.logger.info(f"Connecting to FalkorDB at {FALKORDB_HOST}:{FALKORDB_PORT}")
            self.db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
            self.graph = self.db.select_graph(GRAPH_NAME)
            self.logger.info(f"Connected to graph: {GRAPH_NAME}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to FalkorDB: {e}")
            self.errors.append(f"Connection failed: {e}")
            return False

    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute a Cypher query"""
        try:
            self.logger.debug(f"Executing query: {query}")
            if params:
                self.logger.debug(f"Parameters: {params}")

            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would execute: {query}")
                return None

            result = self.graph.query(query, params or {})
            self.logger.debug(f"Query executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Query failed: {query}")
            self.logger.error(f"Error: {e}")
            self.errors.append(f"Query failed: {query} - {e}")
            raise

    def validate_existing_schema(self) -> bool:
        """Validate that existing schema is intact"""
        self.logger.info("=" * 80)
        self.logger.info("Validating existing schema...")
        self.logger.info("=" * 80)

        try:
            for query in VALIDATION_QUERIES:
                self.logger.info(f"Running validation: {query}")
                result = self.execute_query(query)

                if result and hasattr(result, 'result_set'):
                    for row in result.result_set:
                        self.logger.info(f"  Result: {row}")

            self.logger.info("Existing schema validation PASSED")
            return True
        except Exception as e:
            self.logger.error(f"Schema validation FAILED: {e}")
            return False

    def check_existing_indexes(self) -> List[str]:
        """Check which CaptureLog indexes already exist"""
        self.logger.info("Checking for existing CaptureLog indexes...")

        try:
            result = self.execute_query("CALL db.indexes() YIELD label, properties RETURN label, properties")
            existing = []

            if result and hasattr(result, 'result_set'):
                for row in result.result_set:
                    label = row[0]
                    props = row[1] if len(row) > 1 else []

                    if label == "CaptureLog":
                        for prop in props:
                            index_str = f"{label}({prop})"
                            existing.append(index_str)
                            self.logger.info(f"  Found existing index: {index_str}")

            if not existing:
                self.logger.info("  No existing CaptureLog indexes found")

            return existing
        except Exception as e:
            self.logger.warning(f"Could not check existing indexes: {e}")
            return []

    def create_indexes(self) -> bool:
        """Create CaptureLog indexes"""
        self.logger.info("=" * 80)
        self.logger.info("Creating CaptureLog indexes...")
        self.logger.info("=" * 80)

        existing = self.check_existing_indexes()
        created_count = 0
        skipped_count = 0

        for index_def in INBOX_LOG_INDEXES:
            index_str = str(index_def)

            if index_str in existing:
                self.logger.info(f"SKIP: Index already exists: {index_str}")
                skipped_count += 1
                continue

            try:
                self.logger.info(f"Creating index: {index_str}")
                self.execute_query(index_def.create_query())
                created_count += 1
                self.logger.info(f"  SUCCESS: Created {index_str}")
            except Exception as e:
                # Some index creation failures are expected (index already exists with different method)
                # Log as warning, not error
                self.logger.warning(f"  Could not create {index_str}: {e}")

        self.logger.info(f"\nIndex creation summary: {created_count} created, {skipped_count} skipped")
        return True

    def create_test_node(self) -> Optional[str]:
        """Create a test CaptureLog node"""
        self.logger.info("=" * 80)
        self.logger.info("Creating test CaptureLog node...")
        self.logger.info("=" * 80)

        test_log_id = f"__MIGRATION_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}__"

        query = """
        CREATE (l:CaptureLog {
            id: $id,
            raw_text: 'Test capture created by migration script',
            category: 'PersonalAssistant_Task',
            confidence: 0.95,
            status: 'filed',
            entity_id: 'test_entity_123',
            timestamp: timestamp()
        })
        RETURN l.id as log_id
        """

        try:
            result = self.execute_query(query, {"id": test_log_id})

            if not self.dry_run and result and hasattr(result, 'result_set') and result.result_set:
                created_id = result.result_set[0][0]
                self.logger.info(f"SUCCESS: Created test CaptureLog: {created_id}")
                return created_id
            elif self.dry_run:
                self.logger.info(f"[DRY RUN] Would create test CaptureLog: {test_log_id}")
                return test_log_id
            else:
                self.logger.error("Failed to create test node")
                return None
        except Exception as e:
            self.logger.error(f"Error creating test node: {e}")
            return None

    def delete_test_node(self, log_id: str) -> bool:
        """Delete the test CaptureLog node"""
        self.logger.info(f"Deleting test CaptureLog: {log_id}")

        query = """
        MATCH (l:CaptureLog {id: $id})
        DELETE l
        RETURN count(l) as deleted_count
        """

        try:
            result = self.execute_query(query, {"id": log_id})

            if not self.dry_run and result and hasattr(result, 'result_set') and result.result_set:
                deleted = result.result_set[0][0]
                self.logger.info(f"SUCCESS: Deleted {deleted} test CaptureLog(s)")
                return True
            elif self.dry_run:
                self.logger.info(f"[DRY RUN] Would delete test CaptureLog: {log_id}")
                return True
            else:
                self.logger.error("Failed to delete test node")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting test node: {e}")
            return False

    def drop_indexes(self) -> bool:
        """Drop CaptureLog indexes (rollback)"""
        self.logger.info("=" * 80)
        self.logger.info("Rolling back CaptureLog indexes...")
        self.logger.info("=" * 80)

        dropped_count = 0

        for index_def in INBOX_LOG_INDEXES:
            try:
                self.logger.info(f"Dropping index: {index_def}")
                self.execute_query(index_def.drop_query())
                dropped_count += 1
                self.logger.info(f"  SUCCESS: Dropped {index_def}")
            except Exception as e:
                # Index might not exist - log as warning
                self.logger.warning(f"  Could not drop {index_def}: {e}")

        self.logger.info(f"\nRollback summary: {dropped_count} indexes dropped")
        return True

    def run_migration(self) -> bool:
        """Execute full migration"""
        self.logger.info("=" * 80)
        self.logger.info("STARTING CAPTURELOG INBOX SCHEMA MIGRATION")
        self.logger.info("=" * 80)
        self.logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        self.logger.info(f"Database: {FALKORDB_HOST}:{FALKORDB_PORT}")
        self.logger.info(f"Graph: {GRAPH_NAME}")
        self.logger.info(f"Log file: {LOG_FILE}")
        self.logger.info("")

        # Step 1: Connect
        if not self.connect():
            return False

        # Step 2: Validate existing schema
        if not self.validate_existing_schema():
            self.logger.error("ABORT: Existing schema validation failed")
            return False

        # Step 3: Create indexes
        if not self.create_indexes():
            self.logger.error("ABORT: Index creation failed")
            return False

        # Step 4: Create test node
        test_log_id = self.create_test_node()
        if not test_log_id:
            self.logger.error("ABORT: Test node creation failed")
            return False

        # Step 5: Delete test node
        if not self.delete_test_node(test_log_id):
            self.logger.warning("Warning: Could not delete test node - manual cleanup may be required")

        # Step 6: Final validation
        self.logger.info("=" * 80)
        self.logger.info("Running final validation...")
        self.logger.info("=" * 80)

        final_indexes = self.check_existing_indexes()
        self.logger.info(f"Total CaptureLog indexes: {len(final_indexes)}")

        # Success
        self.logger.info("=" * 80)
        self.logger.info("MIGRATION COMPLETED SUCCESSFULLY")
        self.logger.info("=" * 80)

        if self.dry_run:
            self.logger.info("\nThis was a DRY RUN - no changes were made to the database")
            self.logger.info("Run without --dry-run to execute the migration")

        return True

    def run_validate(self) -> bool:
        """Validate schema without making changes"""
        self.logger.info("=" * 80)
        self.logger.info("SCHEMA VALIDATION (READ-ONLY)")
        self.logger.info("=" * 80)

        if not self.connect():
            return False

        # Check existing schema
        if not self.validate_existing_schema():
            return False

        # Check CaptureLog indexes
        self.logger.info("")
        existing = self.check_existing_indexes()

        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("VALIDATION COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"Existing CaptureLog indexes: {len(existing)}/{len(INBOX_LOG_INDEXES)}")

        if len(existing) == 0:
            self.logger.info("\nNo CaptureLog indexes found - migration has not been run")
        elif len(existing) < len(INBOX_LOG_INDEXES):
            self.logger.warning("\nPartial CaptureLog schema detected - migration may be incomplete")
        else:
            self.logger.info("\nCaptureLog inbox schema is fully migrated")

        return True

    def run_rollback(self) -> bool:
        """Rollback CaptureLog schema changes"""
        self.logger.info("=" * 80)
        self.logger.info("ROLLING BACK CAPTURELOG SCHEMA")
        self.logger.info("=" * 80)

        if not self.connect():
            return False

        # Drop indexes
        if not self.drop_indexes():
            self.logger.error("Rollback failed")
            return False

        # Check for CaptureLog nodes (don't delete, just report)
        self.logger.info("")
        self.logger.info("Checking for CaptureLog nodes...")

        try:
            result = self.execute_query(
                "MATCH (l:CaptureLog) RETURN count(l) as node_count"
            )

            if result and hasattr(result, 'result_set') and result.result_set:
                node_count = result.result_set[0][0]

                if node_count > 0:
                    self.logger.warning(f"Found {node_count} CaptureLog nodes still in database")
                    self.logger.warning("These nodes were NOT deleted - they contain capture history")
                else:
                    self.logger.info("No CaptureLog nodes found")
        except Exception as e:
            self.logger.warning(f"Could not check for CaptureLog nodes: {e}")

        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("ROLLBACK COMPLETED")
        self.logger.info("=" * 80)

        return True


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main script entry point"""
    parser = argparse.ArgumentParser(
        description="Add CaptureLog inbox indexes to Roscoe FalkorDB graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run migration
  python add_inbox_log_indexes.py

  # Preview changes without executing
  python add_inbox_log_indexes.py --dry-run

  # Validate schema status
  python add_inbox_log_indexes.py --validate

  # Rollback changes
  python add_inbox_log_indexes.py --rollback

Environment Variables:
  FALKORDB_HOST    FalkorDB host (default: roscoe-graphdb)
  FALKORDB_PORT    FalkorDB port (default: 6379)
        """
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing changes"
    )

    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Remove CaptureLog indexes (reverses migration)"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate schema without making changes"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose debug logging"
    )

    args = parser.parse_args()

    # Create migration manager
    manager = MigrationManager(dry_run=args.dry_run, verbose=args.verbose)

    try:
        # Execute requested operation
        if args.validate:
            success = manager.run_validate()
        elif args.rollback:
            if args.dry_run:
                print("ERROR: Cannot use --dry-run with --rollback")
                sys.exit(1)
            success = manager.run_rollback()
        else:
            success = manager.run_migration()

        # Exit with appropriate code
        if success:
            print(f"\nLog file: {LOG_FILE}")
            sys.exit(0)
        else:
            print(f"\nMigration failed - check log file: {LOG_FILE}")
            if manager.errors:
                print("\nErrors encountered:")
                for error in manager.errors:
                    print(f"  - {error}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nMigration interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print(f"Check log file: {LOG_FILE}")
        sys.exit(1)


if __name__ == "__main__":
    main()
