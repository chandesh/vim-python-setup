"""Script to populate MCP servers with sample data."""
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.category import Category
from app.models.mcp_server import MCPServer, ServerScope
from app.models.tag import Tag
import uuid


def get_or_create_category(db: Session, name: str, slug: str, description: str):
    """Get existing category or create new one."""
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        category = Category(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            description=description
        )
        db.add(category)
        db.commit()
        db.refresh(category)
    return category


def get_or_create_tag(db: Session, name: str, slug: str):
    """Get existing tag or create new one."""
    tag = db.query(Tag).filter(Tag.slug == slug).first()
    if not tag:
        tag = Tag(
            id=uuid.uuid4(),
            name=name,
            slug=slug
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag


def populate_mcp_servers():
    """Populate database with sample MCP servers."""
    print("Starting MCP servers population...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create categories
        print("Creating categories...")
        file_systems_cat = get_or_create_category(
            db, "File Systems", "file-systems", 
            "MCP servers for file system operations and document management"
        )
        browser_cat = get_or_create_category(
            db, "Browser Automation", "browser-automation",
            "MCP servers for browser automation and web scraping"
        )
        database_cat = get_or_create_category(
            db, "Database", "database",
            "MCP servers for database operations and queries"
        )
        dev_tools_cat = get_or_create_category(
            db, "Developer Tools", "developer-tools",
            "MCP servers for development and coding assistance"
        )
        data_processing_cat = get_or_create_category(
            db, "Data Processing", "data-processing",
            "MCP servers for data transformation and processing"
        )
        api_integration_cat = get_or_create_category(
            db, "API Integration", "api-integration",
            "MCP servers for external API integrations"
        )
        
        # Create tags
        print("Creating tags...")
        python_tag = get_or_create_tag(db, "Python", "python")
        typescript_tag = get_or_create_tag(db, "TypeScript", "typescript")
        javascript_tag = get_or_create_tag(db, "JavaScript", "javascript")
        markdown_tag = get_or_create_tag(db, "Markdown", "markdown")
        automation_tag = get_or_create_tag(db, "Automation", "automation")
        files_tag = get_or_create_tag(db, "Files", "files")
        database_tag = get_or_create_tag(db, "Database", "database")
        
        # Sample MCP servers data
        mcp_servers_data = [
            {
                "name": "markitdown",
                "slug": "markitdown",
                "description": "Official Python tool for converting files and office documents to Markdown. Supports Word, Excel, PowerPoint, PDF, and more. Built by Microsoft to enable seamless document conversion for AI applications.",
                "repository_url": "https://github.com/microsoft/markitdown",
                "logo_url": "https://avatars.githubusercontent.com/u/6154722",
                "language": "Python",
                "scope": ServerScope.LOCAL,
                "category": file_systems_cat,
                "npm_package": None,
                "pypi_package": "markitdown",
                "star_count": 59126,
                "featured": True,
                "tags": [python_tag, markdown_tag, files_tag]
            },
            {
                "name": "Model Context Protocol Servers",
                "slug": "modelcontextprotocol",
                "description": "Official Model Context Protocol reference implementation and server collection. Provides foundational servers for file systems, databases, and common integrations. Essential starting point for MCP development.",
                "repository_url": "https://github.com/modelcontextprotocol/servers",
                "logo_url": "https://avatars.githubusercontent.com/u/187283410",
                "language": "Python",
                "scope": ServerScope.LOCAL,
                "category": dev_tools_cat,
                "npm_package": None,
                "pypi_package": "mcp-servers",
                "star_count": 53820,
                "featured": True,
                "tags": [python_tag]
            },
            {
                "name": "Puppeteer MCP Server",
                "slug": "puppeteer-mcp",
                "description": "Browser automation MCP server powered by Puppeteer. Enables AI agents to interact with web pages, extract data, take screenshots, and automate workflows. Supports headless and headful modes.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer",
                "logo_url": "https://avatars.githubusercontent.com/u/187283410",
                "language": "TypeScript",
                "scope": ServerScope.LOCAL,
                "category": browser_cat,
                "npm_package": "@modelcontextprotocol/server-puppeteer",
                "pypi_package": None,
                "star_count": 45200,
                "featured": True,
                "tags": [typescript_tag, automation_tag]
            },
            {
                "name": "Prisma MCP Server",
                "slug": "prisma-mcp",
                "description": "Database MCP server using Prisma ORM. Provides type-safe database access for AI agents with support for PostgreSQL, MySQL, SQLite, and more. Includes schema introspection and query building.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/prisma",
                "logo_url": "https://avatars.githubusercontent.com/u/17219288",
                "language": "TypeScript",
                "scope": ServerScope.LOCAL,
                "category": database_cat,
                "npm_package": "@modelcontextprotocol/server-prisma",
                "pypi_package": None,
                "star_count": 42100,
                "featured": True,
                "tags": [typescript_tag, database_tag]
            },
            {
                "name": "Filesystem MCP Server",
                "slug": "filesystem-mcp",
                "description": "Core filesystem operations server for reading, writing, and managing files and directories. Provides secure sandboxed access to the local filesystem with permission controls.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
                "logo_url": "https://avatars.githubusercontent.com/u/187283410",
                "language": "TypeScript",
                "scope": ServerScope.LOCAL,
                "category": file_systems_cat,
                "npm_package": "@modelcontextprotocol/server-filesystem",
                "pypi_package": None,
                "star_count": 38500,
                "featured": True,
                "tags": [typescript_tag, files_tag]
            },
            {
                "name": "GitHub MCP Server",
                "slug": "github-mcp",
                "description": "Integrate with GitHub API through MCP. Enables AI agents to manage repositories, issues, pull requests, and workflows. Supports authentication and webhooks.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/github",
                "language": "TypeScript",
                "scope": ServerScope.CLOUD,
                "category": api_integration_cat,
                "npm_package": "@modelcontextprotocol/server-github",
                "pypi_package": None,
                "star_count": 35200,
                "featured": False,
                "tags": [typescript_tag]
            },
            {
                "name": "PostgreSQL MCP Server",
                "slug": "postgresql-mcp",
                "description": "Direct PostgreSQL database access for AI agents. Execute queries, manage schemas, and perform database operations with full SQL support and transaction handling.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/postgres",
                "language": "Python",
                "scope": ServerScope.LOCAL,
                "category": database_cat,
                "npm_package": None,
                "pypi_package": "mcp-server-postgres",
                "star_count": 32800,
                "featured": False,
                "tags": [python_tag, database_tag]
            },
            {
                "name": "Slack MCP Server",
                "slug": "slack-mcp",
                "description": "Connect AI agents to Slack workspaces. Send messages, read channels, manage users, and automate workflows. Supports both bot and user tokens.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/slack",
                "language": "TypeScript",
                "scope": ServerScope.CLOUD,
                "category": api_integration_cat,
                "npm_package": "@modelcontextprotocol/server-slack",
                "pypi_package": None,
                "star_count": 28900,
                "featured": False,
                "tags": [typescript_tag, automation_tag]
            },
            {
                "name": "Git MCP Server",
                "slug": "git-mcp",
                "description": "Git version control operations for AI agents. Clone repositories, create commits, manage branches, and view history. Essential for AI-powered development tools.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/git",
                "language": "Python",
                "scope": ServerScope.LOCAL,
                "category": dev_tools_cat,
                "npm_package": None,
                "pypi_package": "mcp-server-git",
                "star_count": 26400,
                "featured": False,
                "tags": [python_tag]
            },
            {
                "name": "Memory MCP Server",
                "slug": "memory-mcp",
                "description": "Persistent memory and knowledge graph for AI agents. Store and retrieve contextual information across sessions with semantic search capabilities.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/memory",
                "language": "TypeScript",
                "scope": ServerScope.HYBRID,
                "category": data_processing_cat,
                "npm_package": "@modelcontextprotocol/server-memory",
                "pypi_package": None,
                "star_count": 24100,
                "featured": False,
                "tags": [typescript_tag]
            },
            {
                "name": "Web Search MCP Server",
                "slug": "web-search-mcp",
                "description": "Enable AI agents to search the web using multiple search engines. Supports Google, Bing, and DuckDuckGo with result filtering and ranking.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/web-search",
                "language": "Python",
                "scope": ServerScope.CLOUD,
                "category": api_integration_cat,
                "npm_package": None,
                "pypi_package": "mcp-server-web-search",
                "star_count": 22500,
                "featured": False,
                "tags": [python_tag]
            },
            {
                "name": "SQLite MCP Server",
                "slug": "sqlite-mcp",
                "description": "Lightweight database server for AI agents using SQLite. Perfect for local development and embedded applications with full SQL query support.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite",
                "language": "JavaScript",
                "scope": ServerScope.LOCAL,
                "category": database_cat,
                "npm_package": "@modelcontextprotocol/server-sqlite",
                "pypi_package": None,
                "star_count": 19800,
                "featured": False,
                "tags": [javascript_tag, database_tag]
            },
            {
                "name": "Notion MCP Server",
                "slug": "notion-mcp",
                "description": "Integrate Notion workspaces with AI agents. Read and write pages, databases, and blocks. Sync knowledge bases and automate documentation workflows.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/notion",
                "language": "TypeScript",
                "scope": ServerScope.CLOUD,
                "category": api_integration_cat,
                "npm_package": "@modelcontextprotocol/server-notion",
                "pypi_package": None,
                "star_count": 18200,
                "featured": False,
                "tags": [typescript_tag]
            },
            {
                "name": "Docker MCP Server",
                "slug": "docker-mcp",
                "description": "Manage Docker containers and images through AI agents. Build, run, stop containers, and orchestrate multi-container applications.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/docker",
                "language": "Python",
                "scope": ServerScope.LOCAL,
                "category": dev_tools_cat,
                "npm_package": None,
                "pypi_package": "mcp-server-docker",
                "star_count": 16700,
                "featured": False,
                "tags": [python_tag, automation_tag]
            },
            {
                "name": "AWS S3 MCP Server",
                "slug": "aws-s3-mcp",
                "description": "Amazon S3 storage integration for AI agents. Upload, download, list, and manage objects in S3 buckets with full ACL support.",
                "repository_url": "https://github.com/modelcontextprotocol/servers/tree/main/src/aws-s3",
                "language": "Python",
                "scope": ServerScope.CLOUD,
                "category": file_systems_cat,
                "npm_package": None,
                "pypi_package": "mcp-server-aws-s3",
                "star_count": 15300,
                "featured": False,
                "tags": [python_tag, files_tag]
            }
        ]
        
        print(f"Creating {len(mcp_servers_data)} MCP servers...")
        
        for server_data in mcp_servers_data:
            # Check if server already exists
            existing = db.query(MCPServer).filter(MCPServer.slug == server_data["slug"]).first()
            if existing:
                print(f"  - Skipping {server_data['name']} (already exists)")
                continue
            
            # Extract tags before creating server
            tags = server_data.pop("tags")
            category = server_data.pop("category")
            
            # Create server
            server = MCPServer(
                id=uuid.uuid4(),
                **server_data,
                category_id=category.id
            )
            
            # Add tags
            server.tags = tags
            
            db.add(server)
            print(f"  [Created] {server_data['name']}")
        
        db.commit()
        print(f"\n[SUCCESS] Successfully populated {len(mcp_servers_data)} MCP servers!")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_mcp_servers()
