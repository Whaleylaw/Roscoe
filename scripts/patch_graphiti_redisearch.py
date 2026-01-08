#!/usr/bin/env python3
"""
Patch Graphiti FalkorDB Driver to Escape RediSearch Reserved Words

This fixes the bug where legal terms like COMPLAINT, PETITION, etc. crash
RediSearch fulltext queries because they're treated as operators instead of
search terms.

Usage:
    python patch_graphiti_redisearch.py
"""

import re

# RediSearch reserved words that need escaping
# See: https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/query_syntax/
REDISEARCH_RESERVED_WORDS = {
    # Boolean operators
    'AND', 'OR', 'NOT',
    # Legal terms that happen to be reserved
    'COMPLAINT', 'PETITION', 'INTERROGATORIES', 'REQUEST', 'PRODUCTION',
    'DOCUMENTS', 'DISCOVERY', 'MOTION', 'ORDER', 'JUDGMENT',
    # Other common reserved words
    'OPTIONAL', 'AS', 'IS', 'NULL', 'TRUE', 'FALSE',
}


def create_patched_build_fulltext_query():
    """Create patched version of build_fulltext_query that escapes reserved words."""

    patch_code = '''
def build_fulltext_query(
    self, query: str, group_ids: list[str] | None = None, max_query_length: int = 128
) -> str:
    """
    Build a fulltext query string for FalkorDB using RedisSearch syntax.

    PATCHED VERSION: Escapes RediSearch reserved words to prevent syntax errors.

    FalkorDB uses RedisSearch-like syntax where:
    - Field queries use @ prefix: @field:value
    - Multiple values for same field: (@field:value1|value2)
    - Text search doesn't need @ prefix for content fields
    - AND is implicit with space: (@group_id:value) (text)
    - OR uses pipe within parentheses: (@group_id:value1|value2)
    """
    if group_ids is None or len(group_ids) == 0:
        group_filter = ''
    else:
        group_values = '|'.join(group_ids)
        group_filter = f'(@group_id:{group_values})'

    sanitized_query = self.sanitize(query)

    # Remove stopwords from the sanitized query
    query_words = sanitized_query.split()

    # PATCH: Escape RediSearch reserved words by wrapping in quotes
    REDISEARCH_RESERVED_WORDS = {
        'AND', 'OR', 'NOT',
        'COMPLAINT', 'PETITION', 'INTERROGATORIES', 'REQUEST', 'PRODUCTION',
        'DOCUMENTS', 'DISCOVERY', 'MOTION', 'ORDER', 'JUDGMENT',
        'OPTIONAL', 'AS', 'IS', 'NULL', 'TRUE', 'FALSE',
    }

    escaped_words = []
    for word in query_words:
        # Skip stopwords
        if word.lower() in STOPWORDS:
            continue
        # Escape reserved words by wrapping in double quotes
        if word.upper() in REDISEARCH_RESERVED_WORDS:
            escaped_words.append(f'"{word}"')
        else:
            escaped_words.append(word)

    sanitized_query = ' | '.join(escaped_words)

    # If the query is too long return no query
    if len(sanitized_query.split(' ')) + len(group_ids or '') >= max_query_length:
        return ''

    full_query = group_filter + ' (' + sanitized_query + ')'

    return full_query
'''

    return patch_code


def patch_file(file_path: str):
    """Apply the patch to the FalkorDB driver file."""

    print("=" * 70)
    print("PATCHING GRAPHITI FALKORDB DRIVER")
    print("=" * 70)
    print(f"File: {file_path}")
    print()

    # Read the file
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

    # Check if already patched
    if 'PATCH: Escape RediSearch reserved words' in content:
        print("✅ File is already patched!")
        print("   No changes needed.")
        return True

    # Find the build_fulltext_query method
    pattern = r'(    def build_fulltext_query\([\s\S]*?)(        filtered_words = \[word for word in query_words if word\.lower\(\) not in STOPWORDS\]\n        sanitized_query = \' \| \'\.join\(filtered_words\))'

    replacement = r'''\1        # PATCH: Escape RediSearch reserved words by wrapping in quotes
        REDISEARCH_RESERVED_WORDS = {
            'AND', 'OR', 'NOT',
            'COMPLAINT', 'PETITION', 'INTERROGATORIES', 'REQUEST', 'PRODUCTION',
            'DOCUMENTS', 'DISCOVERY', 'MOTION', 'ORDER', 'JUDGMENT',
            'OPTIONAL', 'AS', 'IS', 'NULL', 'TRUE', 'FALSE',
        }

        escaped_words = []
        for word in query_words:
            # Skip stopwords
            if word.lower() in STOPWORDS:
                continue
            # Escape reserved words by wrapping in double quotes
            if word.upper() in REDISEARCH_RESERVED_WORDS:
                escaped_words.append(f'"{word}"')
            else:
                escaped_words.append(word)

        sanitized_query = ' | '.join(escaped_words)'''

    patched_content = re.sub(pattern, replacement, content)

    if patched_content == content:
        print("❌ Could not find the code to patch!")
        print("   The file structure may have changed.")
        return False

    # Write the patched file
    try:
        with open(file_path, 'w') as f:
            f.write(patched_content)
        print("✅ File successfully patched!")
        print()
        print("Changes:")
        print("  - Added RediSearch reserved word detection")
        print("  - Reserved words now wrapped in double quotes")
        print("  - Legal terms (COMPLAINT, PETITION, etc.) will work correctly")
        print()
        print("Restart roscoe-agents container to apply changes.")
        return True
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python patch_graphiti_redisearch.py <path_to_falkordb_driver.py>")
        print()
        print("Example:")
        print("  python patch_graphiti_redisearch.py /usr/local/lib/python3.11/site-packages/graphiti_core/driver/falkordb_driver.py")
        sys.exit(1)

    file_path = sys.argv[1]
    success = patch_file(file_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
