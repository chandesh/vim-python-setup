"""Seed script to populate database with sample data.

Run this script to add sample categories, tags, agents, and MCP servers
for development and testing purposes.
"""

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models import (
    Category, Tag, Agent, MCPServer,
    PricingModel, ServerScope
)


def seed_categories(db: Session):
    """Create sample categories."""
    categories = [
        {
            "name": "Productivity",
            "slug": "productivity",
            "description": "AI agents for productivity and workflow automation",
            "icon_url": "https://example.com/icons/productivity.svg"
        },
        {
            "name": "Development",
            "slug": "development",
            "description": "AI tools for software development and coding",
            "icon_url": "https://example.com/icons/development.svg"
        },
        {
            "name": "Content Creation",
            "slug": "content-creation",
            "description": "AI agents for creating content, images, and media",
            "icon_url": "https://example.com/icons/content.svg"
        },
        {
            "name": "Data Analysis",
            "slug": "data-analysis",
            "description": "AI tools for data analysis and insights",
            "icon_url": "https://example.com/icons/data.svg"
        }
    ]
    
    created = []
    for cat_data in categories:
        # Skip if already exists
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
            db.flush()
            created.append(category)
        else:
            created.append(existing)
    
    db.commit()
    print(f"Created {len([c for c in created if c.id])} categories")
    return created


def seed_tags(db: Session):
    """Create sample tags."""
    tags = [
        {"name": "Conversational AI", "slug": "conversational-ai", "description": "Chat and conversation capabilities"},
        {"name": "Code Generation", "slug": "code-generation", "description": "Automatic code writing and generation"},
        {"name": "Image Generation", "slug": "image-generation", "description": "AI image creation tools"},
        {"name": "Text Analysis", "slug": "text-analysis", "description": "Natural language processing and analysis"},
        {"name": "Automation", "slug": "automation", "description": "Task and workflow automation"},
        {"name": "API Integration", "slug": "api-integration", "description": "Connect with external APIs"},
        {"name": "Database", "slug": "database", "description": "Database operations and queries"},
        {"name": "Web Scraping", "slug": "web-scraping", "description": "Extract data from websites"},
    ]
    
    created = []
    for tag_data in tags:
        existing = db.query(Tag).filter(Tag.slug == tag_data["slug"]).first()
        if not existing:
            tag = Tag(**tag_data)
            db.add(tag)
            db.flush()
            created.append(tag)
        else:
            created.append(existing)
    
    db.commit()
    print(f"Created {len([t for t in created if t.id])} tags")
    return created


def seed_agents(db: Session, categories, tags):
    """Create sample agents."""
    productivity_cat = next((c for c in categories if c.slug == "productivity"), None)
    dev_cat = next((c for c in categories if c.slug == "development"), None)
    content_cat = next((c for c in categories if c.slug == "content-creation"), None)
    
    conv_tag = next((t for t in tags if t.slug == "conversational-ai"), None)
    code_tag = next((t for t in tags if t.slug == "code-generation"), None)
    image_tag = next((t for t in tags if t.slug == "image-generation"), None)
    
    agents = [
        {
            "name": "ChatGPT",
            "slug": "chatgpt",
            "description": "ChatGPT is an AI-powered conversational agent by OpenAI that can help with writing, coding, analysis, and problem-solving.",
            "short_description": "AI conversational agent by OpenAI",
            "website_url": "https://chat.openai.com",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": True,
            "logo_url": "https://example.com/logos/chatgpt.png",
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Claude",
            "slug": "claude",
            "description": "Claude by Anthropic is an AI assistant focused on being helpful, harmless, and honest. Great for complex reasoning tasks.",
            "short_description": "AI assistant by Anthropic",
            "website_url": "https://claude.ai",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": True,
            "logo_url": "https://example.com/logos/claude.png",
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "GitHub Copilot",
            "slug": "github-copilot",
            "description": "GitHub Copilot is an AI pair programmer that helps you write code faster with context-aware suggestions.",
            "short_description": "AI-powered code completion tool",
            "website_url": "https://github.com/features/copilot",
            "category_id": dev_cat.id if dev_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": True,
            "logo_url": "https://example.com/logos/copilot.png",
            "tags": [code_tag] if code_tag else []
        },
        {
            "name": "Midjourney",
            "slug": "midjourney",
            "description": "Midjourney is an AI art generator that creates stunning images from text descriptions.",
            "short_description": "AI image generation tool",
            "website_url": "https://midjourney.com",
            "category_id": content_cat.id if content_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": True,
            "logo_url": "https://example.com/logos/midjourney.png",
            "tags": [image_tag] if image_tag else []
        }
    ]
    
    created = []
    for agent_data in agents:
        existing = db.query(Agent).filter(Agent.slug == agent_data["slug"]).first()
        if not existing:
            tags_to_add = agent_data.pop("tags", [])
            agent = Agent(**agent_data)
            agent.tags = tags_to_add
            db.add(agent)
            db.flush()
            created.append(agent)
        else:
            created.append(existing)
    
    db.commit()
    print(f"Created {len([a for a in created if a.id])} agents")
    return created


def seed_mcp_servers(db: Session, categories, tags):
    """Create sample MCP servers."""
    dev_cat = next((c for c in categories if c.slug == "development"), None)
    data_cat = next((c for c in categories if c.slug == "data-analysis"), None)
    
    api_tag = next((t for t in tags if t.slug == "api-integration"), None)
    db_tag = next((t for t in tags if t.slug == "database"), None)
    
    servers = [
        {
            "name": "PostgreSQL MCP Server",
            "slug": "postgresql-mcp",
            "description": "MCP server for PostgreSQL database operations. Enables AI agents to query and manipulate PostgreSQL databases.",
            "repository_url": "https://github.com/example/postgresql-mcp",
            "language": "Python",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "pypi_package": "postgresql-mcp-server",
            "star_count": 245,
            "featured": True,
            "tags": [db_tag] if db_tag else []
        },
        {
            "name": "REST API MCP Server",
            "slug": "rest-api-mcp",
            "description": "Generic REST API MCP server that allows AI agents to interact with any REST API endpoint.",
            "repository_url": "https://github.com/example/rest-api-mcp",
            "language": "TypeScript",
            "scope": ServerScope.CLOUD,
            "category_id": dev_cat.id if dev_cat else None,
            "npm_package": "rest-api-mcp-server",
            "star_count": 189,
            "featured": True,
            "tags": [api_tag] if api_tag else []
        }
    ]
    
    created = []
    for server_data in servers:
        existing = db.query(MCPServer).filter(MCPServer.slug == server_data["slug"]).first()
        if not existing:
            tags_to_add = server_data.pop("tags", [])
            server = MCPServer(**server_data)
            server.tags = tags_to_add
            db.add(server)
            db.flush()
            created.append(server)
        else:
            created.append(existing)
    
    db.commit()
    print(f"Created {len([s for s in created if s.id])} MCP servers")
    return created


def main():
    """Main seed function."""
    print("Starting database seeding...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Seed data
        categories = seed_categories(db)
        tags = seed_tags(db)
        agents = seed_agents(db, categories, tags)
        mcp_servers = seed_mcp_servers(db, categories, tags)
        
        print("\nSeeding complete!")
        print(f"Total: {len(categories)} categories, {len(tags)} tags, {len(agents)} agents, {len(mcp_servers)} MCP servers")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
