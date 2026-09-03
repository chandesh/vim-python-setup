"""Script to update existing agents and MCP servers with logo URLs."""
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.mcp_server import MCPServer


def update_agent_logos(db: Session):
    """Update agent logo URLs."""
    logo_updates = {
        "chatgpt": "https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg",
        "claude": "https://www.anthropic.com/images/icons/apple-touch-icon.png",
        "github-copilot": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        "midjourney": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Midjourney_Emblem.png",
        "gemini": "https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg",
        "cursor": "https://cursor.sh/brand/icon.svg",
        "perplexity-ai": "https://www.perplexity.ai/favicon.svg",
    }
    
    updated_count = 0
    for slug, logo_url in logo_updates.items():
        agent = db.query(Agent).filter(Agent.slug == slug).first()
        if agent:
            agent.logo_url = logo_url
            updated_count += 1
            print(f"  ✓ Updated {agent.name}")
        else:
            print(f"  ✗ Agent not found: {slug}")
    
    db.commit()
    return updated_count


def update_mcp_server_logos(db: Session):
    """Update MCP server logo URLs."""
    logo_updates = {
        "markitdown-mcp": "https://avatars.githubusercontent.com/u/6154722",
        "markitdown": "https://avatars.githubusercontent.com/u/6154722",
        "mcp-servers-official": "https://avatars.githubusercontent.com/u/187283410",
        "modelcontextprotocol": "https://avatars.githubusercontent.com/u/187283410",
        "prisma-mcp": "https://avatars.githubusercontent.com/u/17219288",
        "mindsdb-mcp": "https://avatars.githubusercontent.com/u/51025925",
        "github-mcp-server": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
        "github-mcp": "https://avatars.githubusercontent.com/u/187283410",
        "screenpipe-mcp": "https://avatars.githubusercontent.com/u/183546725",
        "playwright-mcp": "https://avatars.githubusercontent.com/u/6154722",
        "puppeteer-mcp": "https://avatars.githubusercontent.com/u/187283410",
        "prisma-mcp": "https://avatars.githubusercontent.com/u/17219288",
        "filesystem-mcp": "https://avatars.githubusercontent.com/u/187283410",
    }
    
    updated_count = 0
    for slug, logo_url in logo_updates.items():
        server = db.query(MCPServer).filter(MCPServer.slug == slug).first()
        if server:
            server.logo_url = logo_url
            updated_count += 1
            print(f"  ✓ Updated {server.name}")
        else:
            print(f"  ✗ Server not found: {slug}")
    
    db.commit()
    return updated_count


def main():
    """Main update function."""
    print("Updating logos for agents and MCP servers...\n")
    
    db = SessionLocal()
    
    try:
        print("Updating Agents:")
        agents_updated = update_agent_logos(db)
        
        print("\nUpdating MCP Servers:")
        servers_updated = update_mcp_server_logos(db)
        
        print("\n" + "="*50)
        print("Logo update complete!")
        print("="*50)
        print(f"Agents updated: {agents_updated}")
        print(f"MCP Servers updated: {servers_updated}")
        print("="*50)
        
    except Exception as e:
        print(f"Error during update: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
