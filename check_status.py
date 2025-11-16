#!/usr/bin/env python3
"""Quick script to check conversion status"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

client = create_client(url, key)

# Count files with markdown_path set
converted = client.table('doc_files').select('uuid', count='exact').eq('content_type', 'application/pdf').not_.is_('markdown_path', 'null').execute()

# Count files without markdown_path
remaining = client.table('doc_files').select('uuid', count='exact').eq('content_type', 'application/pdf').is_('markdown_path', 'null').execute()

print(f'✅ Files already converted: {converted.count}')
print(f'⏳ Files remaining: {remaining.count}')
print(f'📊 Total PDF files: {converted.count + remaining.count}')
