#!/usr/bin/env python3
"""
MemoryBox and ConversationTrace Schema Migration for FalkorDB

This script adds indexes for MemoryBox and ConversationTrace nodes to enable
topic continuity tracking in conversations (Membox pattern from research).

Indexes added:
- MemoryBox: box_id (NEW), thread_id (existing), started_at (existing)
  Note: thread_id and started_at were created in add_personal_assistant_schema.py
- ConversationTrace: trace_id (NEW), started_at (NEW), last_activity (NEW)

Usage:
    # Normal migration (executes changes)
    python add_memorybox_schema.py

    # Dry run (shows what would be done)
    python add_memorybox_schema.py --dry-run

    # Validate schema without changes
    python add_memorybox_schema.py --validate

    # Rollback (remove ConversationTrace indexes)
    python add_memorybox_schema.py --rollback

Requirements:
    - FalkorDB running and accessible
    - falkordb-py package installed
    - FALKORDB_HOST and FALKORDB_PORT environment variables (or defaults)

Author: Task 7 - Second Brain Integration (Membox Schema)
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
LOG_FILE = os.path.join(LOG_DIR, f"migration_memorybox_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


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


# MemoryBox indexes (most already created in add_personal_assistant_schema.py)
# ConversationTrace indexes (NEW - not yet created)
MEMORYBOX_INDEXES = [
    # MemoryBox indexes (already exist from prior migration)
    IndexDefinition("PersonalAssistant_MemoryBox", "box_id"),
    IndexDefinition("PersonalAssistant_MemoryBox", "thread_id"),
    IndexDefinition("PersonalAssistant_MemoryBox", "started_at"),

    # ConversationTrace indexes (NEW)
    IndexDefinition("PersonalAssistant_ConversationTrace", "trace_id"),
    IndexDefinition("PersonalAssistant_ConversationTrace", "started_at"),
    IndexDefinition("PersonalAssistant_ConversationTrace", "last_activity"),
]


# Schema documentation (not executed by migration - for reference only)
MEMORYBOX_SCHEMA_DOC = """
// MemoryBox - Topic-coherent conversation segment
CREATE (box:PersonalAssistant:MemoryBox {
  box_id: randomUUID(),
  thread_id: $thread_id,
  started_at: timestamp(),
  topic: $topic,
  keywords: $keywords,
  events: $events_array,
  content_summary: $summary
})

// ConversationTrace - Linked narrative chain across sessions
CREATE (trace:PersonalAssistant:ConversationTrace {
  trace_id: randomUUID(),
  theme: $theme,
  started_at: timestamp(),
  last_activity: timestamp(),
  event_count: 1
})

// Link box to trace
CREATE (box)-[:PART_OF_TRACE {
  linked_at: timestamp()
}]->(trace)

// Link memory boxes for topic continuity
CREATE (current_box)-[:CONTINUES_FROM]->(previous_box)
"""


# Sample queries to validate existing schema
VALIDATION_QUERIES = [
    "MATCH (c:Case) RETURN count(c) as case_count",
    "MATCH (cl:Client) RETURN count(cl) as client_count",
    "CALL db.indexes() YIELD label, properties RETURN label, properties",
]


# =============================================================================
# Logging Setup
# =============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging to file and console"""
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("migration_memorybox")
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
    """Manages MemoryBox and ConversationTrace schema migration"""

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
        """Check which MemoryBox/ConversationTrace indexes already exist"""
        self.logger.info("Checking for existing MemoryBox/ConversationTrace indexes...")

        try:
            result = self.execute_query("CALL db.indexes() YIELD label, properties RETURN label, properties")
            existing = []

            if result and hasattr(result, 'result_set'):
                for row in result.result_set:
                    label = row[0]
                    props = row[1] if len(row) > 1 else []

                    if label in ["PersonalAssistant_MemoryBox", "PersonalAssistant_ConversationTrace"]:
                        for prop in props:
                            index_str = f"{label}({prop})"
                            existing.append(index_str)
                            self.logger.info(f"  Found existing index: {index_str}")

            if not existing:
                self.logger.info("  No existing MemoryBox/ConversationTrace indexes found")

            return existing
        except Exception as e:
            self.logger.warning(f"Could not check existing indexes: {e}")
            return []

    def create_indexes(self) -> bool:
        """Create MemoryBox and ConversationTrace indexes"""
        self.logger.info("=" * 80)
        self.logger.info("Creating MemoryBox/ConversationTrace indexes...")
        self.logger.info("=" * 80)

        existing = self.check_existing_indexes()
        created_count = 0
        skipped_count = 0

        for index_def in MEMORYBOX_INDEXES:
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

    def create_test_memorybox(self) -> Optional[str]:
        """Create a test MemoryBox node"""
        self.logger.info("=" * 80)
        self.logger.info("Creating test MemoryBox node...")
        self.logger.info("=" * 80)

        test_box_id = f"__MIGRATION_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}__"

        query = """
        CREATE (box:PersonalAssistant_MemoryBox {
            box_id: $box_id,
            thread_id: 'test_thread_123',
            topic: 'Migration test - topic continuity',
            keywords: ['test', 'migration'],
            started_at: timestamp(),
            content_summary: 'Test MemoryBox created by migration script'
        })
        RETURN box.box_id as box_id
        """

        try:
            result = self.execute_query(query, {"box_id": test_box_id})

            if not self.dry_run and result and hasattr(result, 'result_set') and result.result_set:
                created_id = result.result_set[0][0]
                self.logger.info(f"SUCCESS: Created test MemoryBox: {created_id}")
                return created_id
            elif self.dry_run:
                self.logger.info(f"[DRY RUN] Would create test MemoryBox: {test_box_id}")
                return test_box_id
            else:
                self.logger.error("Failed to create test MemoryBox node")
                return None
        except Exception as e:
            self.logger.error(f"Error creating test MemoryBox: {e}")
            return None

    def create_test_trace(self) -> Optional[str]:
        """Create a test ConversationTrace node"""
        self.logger.info("=" * 80)
        self.logger.info("Creating test ConversationTrace node...")
        self.logger.info("=" * 80)

        test_trace_id = f"__MIGRATION_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}__"

        query = """
        CREATE (trace:PersonalAssistant_ConversationTrace {
            trace_id: $trace_id,
            theme: 'Migration test trace',
            started_at: timestamp(),
            last_activity: timestamp(),
            event_count: 1
        })
        RETURN trace.trace_id as trace_id
        """

        try:
            result = self.execute_query(query, {"trace_id": test_trace_id})

            if not self.dry_run and result and hasattr(result, 'result_set') and result.result_set:
                created_id = result.result_set[0][0]
                self.logger.info(f"SUCCESS: Created test ConversationTrace: {created_id}")
                return created_id
            elif self.dry_run:
                self.logger.info(f"[DRY RUN] Would create test ConversationTrace: {test_trace_id}")
                return test_trace_id
            else:
                self.logger.error("Failed to create test ConversationTrace node")
                return None
        except Exception as e:
            self.logger.error(f"Error creating test ConversationTrace: {e}")
            return None

    def delete_test_node(self, node_type: str, id_field: str, node_id: str) -> bool:
        """Delete a test node"""
        self.logger.info(f"Deleting test {node_type}: {node_id}")

        query = f"""
        MATCH (n:{node_type} {{{id_field}: $id}})
        DELETE n
        RETURN count(n) as deleted_count
        """

        try:
            result = self.execute_query(query, {"id": node_id})

            if not self.dry_run and result and hasattr(result, 'result_set') and result.result_set:
                deleted = result.result_set[0][0]
                self.logger.info(f"SUCCESS: Deleted {deleted} test {node_type}(s)")
                return True
            elif self.dry_run:
                self.logger.info(f"[DRY RUN] Would delete test {node_type}: {node_id}")
                return True
            else:
                self.logger.error(f"Failed to delete test {node_type}")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting test {node_type}: {e}")
            return False

    def drop_indexes(self) -> bool:
        """Drop ConversationTrace indexes (rollback)"""
        self.logger.info("=" * 80)
        self.logger.info("Rolling back ConversationTrace indexes...")
        self.logger.info("=" * 80)
        self.logger.info("NOTE: MemoryBox indexes created in earlier migration will NOT be dropped")
        self.logger.info("")

        dropped_count = 0

        # Only drop ConversationTrace indexes (not MemoryBox - those were created earlier)
        trace_indexes = [idx for idx in MEMORYBOX_INDEXES
                        if idx.label == "PersonalAssistant_ConversationTrace"]

        for index_def in trace_indexes:
            try:
                self.logger.info(f"Dropping index: {index_def}")
                self.execute_query(index_def.drop_query())
                dropped_count += 1
                self.logger.info(f"  SUCCESS: Dropped {index_def}")
            except Exception as e:
                # Index might not exist - log as warning
                self.logger.warning(f"  Could not drop {index_def}: {e}")

        self.logger.info(f"\nRollback summary: {dropped_count} ConversationTrace indexes dropped")
        return True

    def run_migration(self) -> bool:
        """Execute full migration"""
        self.logger.info("=" * 80)
        self.logger.info("STARTING MEMORYBOX/CONVERSATIONTRACE SCHEMA MIGRATION")
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

        # Step 4: Create test MemoryBox node
        test_box_id = self.create_test_memorybox()
        if not test_box_id:
            self.logger.error("ABORT: Test MemoryBox creation failed")
            return False

        # Step 5: Create test ConversationTrace node
        test_trace_id = self.create_test_trace()
        if not test_trace_id:
            self.logger.error("ABORT: Test ConversationTrace creation failed")
            return False

        # Step 6: Delete test nodes
        if not self.delete_test_node("PersonalAssistant_MemoryBox", "box_id", test_box_id):
            self.logger.warning("Warning: Could not delete test MemoryBox - manual cleanup may be required")

        if not self.delete_test_node("PersonalAssistant_ConversationTrace", "trace_id", test_trace_id):
            self.logger.warning("Warning: Could not delete test ConversationTrace - manual cleanup may be required")

        # Step 7: Final validation
        self.logger.info("=" * 80)
        self.logger.info("Running final validation...")
        self.logger.info("=" * 80)

        final_indexes = self.check_existing_indexes()
        self.logger.info(f"Total MemoryBox/ConversationTrace indexes: {len(final_indexes)}")

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

        # Check MemoryBox/ConversationTrace indexes
        self.logger.info("")
        existing = self.check_existing_indexes()

        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("VALIDATION COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"Existing MemoryBox/ConversationTrace indexes: {len(existing)}/{len(MEMORYBOX_INDEXES)}")

        if len(existing) == 0:
            self.logger.info("\nNo MemoryBox/ConversationTrace indexes found - migration has not been run")
        elif len(existing) < len(MEMORYBOX_INDEXES):
            self.logger.warning("\nPartial MemoryBox/ConversationTrace schema detected - migration may be incomplete")
        else:
            self.logger.info("\nMemoryBox/ConversationTrace schema is fully migrated")

        return True

    def run_rollback(self) -> bool:
        """Rollback ConversationTrace schema changes"""
        self.logger.info("=" * 80)
        self.logger.info("ROLLING BACK CONVERSATIONTRACE SCHEMA")
        self.logger.info("=" * 80)

        if not self.connect():
            return False

        # Drop ConversationTrace indexes only
        if not self.drop_indexes():
            self.logger.error("Rollback failed")
            return False

        # Check for ConversationTrace nodes (don't delete, just report)
        self.logger.info("")
        self.logger.info("Checking for ConversationTrace nodes...")

        try:
            result = self.execute_query(
                "MATCH (t:PersonalAssistant_ConversationTrace) RETURN count(t) as node_count"
            )

            if result and hasattr(result, 'result_set') and result.result_set:
                node_count = result.result_set[0][0]

                if node_count > 0:
                    self.logger.warning(f"Found {node_count} ConversationTrace nodes still in database")
                    self.logger.warning("These nodes were NOT deleted - they contain conversation history")
                else:
                    self.logger.info("No ConversationTrace nodes found")
        except Exception as e:
            self.logger.warning(f"Could not check for ConversationTrace nodes: {e}")

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
        description="Add MemoryBox and ConversationTrace indexes to Roscoe FalkorDB graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run migration
  python add_memorybox_schema.py

  # Preview changes without executing
  python add_memorybox_schema.py --dry-run

  # Validate schema status
  python add_memorybox_schema.py --validate

  # Rollback ConversationTrace indexes
  python add_memorybox_schema.py --rollback

Environment Variables:
  FALKORDB_HOST    FalkorDB host (default: roscoe-graphdb)
  FALKORDB_PORT    FalkorDB port (default: 6379)

Notes:
  - MemoryBox indexes were created in add_personal_assistant_schema.py
  - This migration adds ConversationTrace indexes
  - Rollback only drops ConversationTrace indexes (not MemoryBox)
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
        help="Remove ConversationTrace indexes (reverses migration)"
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
