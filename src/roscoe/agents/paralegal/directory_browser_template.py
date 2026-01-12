"""
HTML template for interactive directory browser.
Used by generate_directory_browser tool.
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directory Browser - {root_path}</title>
    <style>
        :root {{
            --navy: #1e3a5f;
            --navy-light: #2c4a6e;
            --gold: #c9a227;
            --beige: #f8f7f4;
            --light-beige: #f5f3ed;
            --border: #d4c5a9;
            --text: #2c3e50;
            --text-light: #8b7355;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--beige);
            color: var(--text);
            line-height: 1.6;
        }}

        header {{
            background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
            color: white;
            padding: 1.5rem 2rem;
            border-bottom: 3px solid var(--gold);
        }}

        .firm-header h1 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}

        .firm-header h2 {{
            font-size: 1rem;
            font-weight: 400;
            opacity: 0.9;
        }}

        .metadata {{
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            gap: 2rem;
            font-size: 0.875rem;
            opacity: 0.9;
        }}

        main {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            min-height: calc(100vh - 200px);
        }}

        .tree-node {{
            margin-left: 20px;
        }}

        .tree-item {{
            display: flex;
            align-items: center;
            padding: 0.5rem;
            cursor: pointer;
            border-radius: 4px;
            transition: background 0.2s;
        }}

        .tree-item:hover {{
            background: var(--light-beige);
        }}

        .tree-item.file:hover {{
            background: var(--light-beige);
            border: 1px solid var(--border);
        }}

        .chevron {{
            width: 16px;
            height: 16px;
            margin-right: 0.5rem;
            color: var(--text-light);
            transition: transform 0.2s;
        }}

        .chevron.expanded {{
            transform: rotate(90deg);
        }}

        .icon {{
            font-size: 1.25rem;
            margin-right: 0.5rem;
        }}

        .icon.folder {{
            color: var(--gold);
        }}

        .name {{
            flex: 1;
            font-size: 0.875rem;
        }}

        .meta {{
            font-size: 0.75rem;
            color: var(--text-light);
            margin-left: 1rem;
        }}

        .children {{
            display: none;
            margin-left: 20px;
        }}

        .children.expanded {{
            display: block;
        }}

        .view-btn {{
            opacity: 0;
            padding: 0.25rem 0.75rem;
            background: var(--navy);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: opacity 0.2s;
        }}

        .tree-item:hover .view-btn {{
            opacity: 1;
        }}

        .view-btn:hover {{
            background: var(--gold);
            color: var(--navy);
        }}

        @media print {{
            header {{
                background: white;
                color: var(--navy);
                border-bottom: 2px solid var(--gold);
            }}

            .view-btn {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="firm-header">
            <h1>⚖️ Whaley Law Firm</h1>
            <h2>Workspace Directory Browser</h2>
        </div>
        <div class="metadata">
            <span><strong>Root:</strong> {root_path}</span>
            <span><strong>Generated:</strong> {timestamp}</span>
            <span><strong>Contents:</strong> {file_count} files, {folder_count} folders</span>
        </div>
    </header>

    <main id="directory-tree"></main>

    <script>
        // Embedded directory data
        const directoryData = {tree_json};

        // File type to viewer type mapping
        const FILE_TYPE_MAP = {{
            'pdf': ['pdf', '📄'],
            'doc': ['docx', '📝'],
            'docx': ['docx', '📝'],
            'xls': ['md', '📊'],
            'xlsx': ['md', '📊'],
            'html': ['html', '🌐'],
            'htm': ['html', '🌐'],
            'md': ['md', '📋'],
            'txt': ['md', '📋'],
            'png': ['pdf', '🖼️'],
            'jpg': ['pdf', '🖼️'],
            'jpeg': ['pdf', '🖼️'],
            'gif': ['pdf', '🖼️'],
        }};

        function getFileInfo(extension) {{
            return FILE_TYPE_MAP[extension] || ['md', '📄'];
        }}

        function formatSize(bytes) {{
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }}

        function formatDate(timestamp) {{
            return new Date(timestamp * 1000).toLocaleDateString();
        }}

        function handleFileClick(filePath, fileExtension) {{
            const [viewerType, icon] = getFileInfo(fileExtension);

            // Send message to parent window to open file
            window.parent.postMessage({{
                type: 'open_document',
                payload: {{
                    path: filePath,
                    type: viewerType,
                    source: 'directory_browser'
                }}
            }}, window.location.origin);

            // Visual feedback
            console.log('Opening file:', filePath, 'as', viewerType);
        }}

        function toggleFolder(element) {{
            const chevron = element.querySelector('.chevron');
            const children = element.nextElementSibling;

            if (chevron && children) {{
                chevron.classList.toggle('expanded');
                children.classList.toggle('expanded');
            }}
        }}

        function renderTree(node, container) {{
            const isFolder = node.type === 'folder';

            // Create item element
            const item = document.createElement('div');
            item.className = `tree-item ${{node.type}}`;

            if (isFolder) {{
                // Folder: chevron + icon + name + count
                const chevron = document.createElement('span');
                chevron.className = 'chevron';
                chevron.textContent = '▶';
                item.appendChild(chevron);

                const icon = document.createElement('span');
                icon.className = 'icon folder';
                icon.textContent = '📁';
                item.appendChild(icon);

                const name = document.createElement('span');
                name.className = 'name';
                const count = node.children ? node.children.length : 0;
                name.textContent = `${{node.name}} (${{count}})`;
                item.appendChild(name);

                item.onclick = () => toggleFolder(item);

                // Create children container
                const childrenContainer = document.createElement('div');
                childrenContainer.className = 'children';

                if (node.children) {{
                    node.children.forEach(child => {{
                        renderTree(child, childrenContainer);
                    }});
                }}

                container.appendChild(item);
                container.appendChild(childrenContainer);

            }} else {{
                // File: spacer + icon + name + meta + button
                const spacer = document.createElement('span');
                spacer.style.width = '16px';
                spacer.style.marginRight = '0.5rem';
                item.appendChild(spacer);

                const [viewerType, emoji] = getFileInfo(node.extension || '');
                const icon = document.createElement('span');
                icon.className = 'icon';
                icon.textContent = emoji;
                item.appendChild(icon);

                const name = document.createElement('span');
                name.className = 'name';
                name.textContent = node.name;
                item.appendChild(name);

                if (node.size) {{
                    const meta = document.createElement('span');
                    meta.className = 'meta';
                    meta.textContent = formatSize(node.size);
                    item.appendChild(meta);
                }}

                const viewBtn = document.createElement('button');
                viewBtn.className = 'view-btn';
                viewBtn.textContent = 'View';
                viewBtn.onclick = (e) => {{
                    e.stopPropagation();
                    handleFileClick(node.path, node.extension || '');
                }};
                item.appendChild(viewBtn);

                item.onclick = () => {{
                    handleFileClick(node.path, node.extension || '');
                }};

                container.appendChild(item);
            }}
        }}

        // Render tree on load
        document.addEventListener('DOMContentLoaded', () => {{
            const container = document.getElementById('directory-tree');
            if (directoryData) {{
                renderTree(directoryData, container);
            }}
        }});
    </script>
</body>
</html>
"""
