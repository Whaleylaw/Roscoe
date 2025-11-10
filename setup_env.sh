#!/bin/bash

# Setup script for PDF to Markdown Converter
# This script helps you configure your Supabase credentials

echo "PDF to Markdown Converter - Environment Setup"
echo "=============================================="
echo ""

# Check if .env file already exists
if [ -f .env ]; then
    echo "Found existing .env file."
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file. Exiting."
        exit 0
    fi
fi

# Prompt for Supabase URL
echo "Enter your Supabase URL (e.g., https://yourproject.supabase.co):"
read SUPABASE_URL

# Prompt for Supabase Service Role Key
echo ""
echo "Enter your Supabase Service Role Key:"
read -s SUPABASE_SERVICE_ROLE_KEY
echo ""

# Write to .env file
cat > .env << EOF
# Supabase Configuration
SUPABASE_URL=$SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY
EOF

echo ""
echo "✓ Environment configuration saved to .env"
echo ""
echo "To use these credentials, run:"
echo "  source .env  # or"
echo "  export \$(cat .env | xargs)"
echo ""
echo "Then you can run the converter:"
echo "  python pdf_to_markdown_converter.py --dry-run --limit 5"
