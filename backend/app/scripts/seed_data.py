"""Extended seed script with real agents and MCP servers from aiagentslist.com.

This script populates the database with real-world data.
"""

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models import (
    Category, Tag, Agent, MCPServer,
    PricingModel, ServerScope
)


def seed_extended_categories(db: Session):
    """Create extended categories."""
    categories = [
        {"name": "Productivity", "slug": "productivity", "description": "AI agents for productivity and workflow automation"},
        {"name": "Development", "slug": "development", "description": "AI tools for software development and coding"},
        {"name": "Content Creation", "slug": "content-creation", "description": "AI agents for creating content, images, and media"},
        {"name": "Data Analysis", "slug": "data-analysis", "description": "AI tools for data analysis and insights"},
        {"name": "Customer Service", "slug": "customer-service", "description": "AI agents for customer support and service"},
        {"name": "Marketing", "slug": "marketing", "description": "AI tools for marketing and advertising"},
        {"name": "Sales", "slug": "sales", "description": "AI agents for sales automation and CRM"},
        {"name": "Finance", "slug": "finance", "description": "AI tools for financial analysis and management"},
        {"name": "Research", "slug": "research", "description": "AI agents for research and knowledge discovery"},
        {"name": "Communication", "slug": "communication", "description": "AI tools for communication and collaboration"},
    ]
    
    created = []
    for cat_data in categories:
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


def seed_extended_tags(db: Session):
    """Create extended tags."""
    tags = [
        {"name": "Conversational AI", "slug": "conversational-ai", "description": "Chat and conversation capabilities"},
        {"name": "Code Generation", "slug": "code-generation", "description": "Automatic code writing"},
        {"name": "Image Generation", "slug": "image-generation", "description": "AI image creation"},
        {"name": "Text Analysis", "slug": "text-analysis", "description": "NLP and text processing"},
        {"name": "Automation", "slug": "automation", "description": "Workflow automation"},
        {"name": "API Integration", "slug": "api-integration", "description": "External API connections"},
        {"name": "Database", "slug": "database", "description": "Database operations"},
        {"name": "Web Scraping", "slug": "web-scraping", "description": "Data extraction"},
        {"name": "Browser Automation", "slug": "browser-automation", "description": "Browser control"},
        {"name": "File Systems", "slug": "file-systems", "description": "File management"},
        {"name": "Version Control", "slug": "version-control", "description": "Git and VCS"},
        {"name": "Security", "slug": "security", "description": "Security analysis"},
        {"name": "Knowledge & Memory", "slug": "knowledge-memory", "description": "AI memory systems"},
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


def seed_extended_agents(db: Session, categories, tags):
    """Create 25 real AI agents."""
    productivity_cat = next((c for c in categories if c.slug == "productivity"), None)
    dev_cat = next((c for c in categories if c.slug == "development"), None)
    content_cat = next((c for c in categories if c.slug == "content-creation"), None)
    customer_cat = next((c for c in categories if c.slug == "customer-service"), None)
    marketing_cat = next((c for c in categories if c.slug == "marketing"), None)
    research_cat = next((c for c in categories if c.slug == "research"), None)
    
    conv_tag = next((t for t in tags if t.slug == "conversational-ai"), None)
    code_tag = next((t for t in tags if t.slug == "code-generation"), None)
    image_tag = next((t for t in tags if t.slug == "image-generation"), None)
    auto_tag = next((t for t in tags if t.slug == "automation"), None)
    api_tag = next((t for t in tags if t.slug == "api-integration"), None)
    
    agents = [
        {
            "name": "ChatGPT",
            "slug": "chatgpt",
            "description": "ChatGPT is an AI-powered conversational agent by OpenAI that excels at natural language understanding, content generation, coding assistance, and problem-solving across diverse domains.",
            "short_description": "AI conversational agent by OpenAI",
            "website_url": "https://chat.openai.com",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": True,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Claude",
            "slug": "claude",
            "description": "Claude by Anthropic is an AI assistant designed to be helpful, harmless, and honest. Excels at complex reasoning, analysis, coding, and long-form content generation.",
            "short_description": "AI assistant by Anthropic",
            "website_url": "https://claude.ai",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": True,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "GitHub Copilot",
            "slug": "github-copilot",
            "description": "GitHub Copilot is an AI pair programmer that provides intelligent code suggestions, completions, and entire function implementations based on context.",
            "short_description": "AI-powered code completion",
            "website_url": "https://github.com/features/copilot",
            "category_id": dev_cat.id if dev_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": True,
            "tags": [code_tag] if code_tag else []
        },
        {
            "name": "Midjourney",
            "slug": "midjourney",
            "description": "Midjourney is an AI art generator that creates stunning, high-quality images from text descriptions using advanced diffusion models.",
            "short_description": "AI image generation tool",
            "website_url": "https://midjourney.com",
            "category_id": content_cat.id if content_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": True,
            "tags": [image_tag] if image_tag else []
        },
        {
            "name": "Gemini",
            "slug": "gemini",
            "description": "Google Gemini is a multimodal AI model that can understand and generate text, code, images, audio, and video with advanced reasoning capabilities.",
            "short_description": "Google's multimodal AI assistant",
            "website_url": "https://gemini.google.com",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": True,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Cursor",
            "slug": "cursor",
            "description": "Cursor is an AI-first code editor built on VSCode that provides intelligent code completion, generation, and editing with natural language.",
            "short_description": "AI-powered code editor",
            "website_url": "https://cursor.sh",
            "category_id": dev_cat.id if dev_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": True,
            "tags": [code_tag] if code_tag else []
        },
        {
            "name": "Perplexity AI",
            "slug": "perplexity-ai",
            "description": "Perplexity AI is an AI-powered search engine that provides accurate, cited answers to questions by synthesizing information from multiple sources.",
            "short_description": "AI-powered search engine",
            "website_url": "https://perplexity.ai",
            "category_id": research_cat.id if research_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": True,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Jasper AI",
            "slug": "jasper-ai",
            "description": "Jasper is an AI content generation platform for marketing teams, helping create blog posts, social media content, ads, and more.",
            "short_description": "AI marketing content generator",
            "website_url": "https://jasper.ai",
            "category_id": marketing_cat.id if marketing_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": False,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Copy.ai",
            "slug": "copy-ai",
            "description": "Copy.ai is an AI-powered copywriting tool that helps create marketing copy, product descriptions, social media posts, and more.",
            "short_description": "AI copywriting assistant",
            "website_url": "https://copy.ai",
            "category_id": marketing_cat.id if marketing_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Notion AI",
            "slug": "notion-ai",
            "description": "Notion AI is integrated into Notion workspace, helping users write, edit, summarize, and organize information more efficiently.",
            "short_description": "AI assistant for Notion",
            "website_url": "https://notion.so/product/ai",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": False,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Grammarly",
            "slug": "grammarly",
            "description": "Grammarly is an AI-powered writing assistant that checks grammar, spelling, punctuation, and provides style suggestions.",
            "short_description": "AI writing assistant",
            "website_url": "https://grammarly.com",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Intercom Fin",
            "slug": "intercom-fin",
            "description": "Intercom Fin is an AI customer service bot that can resolve up to 50% of support questions instantly using your support content.",
            "short_description": "AI customer support bot",
            "website_url": "https://intercom.com/fin",
            "category_id": customer_cat.id if customer_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": False,
            "tags": [conv_tag, auto_tag] if conv_tag and auto_tag else []
        },
        {
            "name": "Synthesia",
            "slug": "synthesia",
            "description": "Synthesia is an AI video generation platform that creates professional videos with AI avatars from text scripts.",
            "short_description": "AI video generation platform",
            "website_url": "https://synthesia.io",
            "category_id": content_cat.id if content_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": False,
            "tags": [image_tag] if image_tag else []
        },
        {
            "name": "Runway ML",
            "slug": "runway-ml",
            "description": "Runway is an AI-powered creative suite for video editing, generation, and manipulation with text-to-video capabilities.",
            "short_description": "AI creative video tools",
            "website_url": "https://runwayml.com",
            "category_id": content_cat.id if content_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [image_tag] if image_tag else []
        },
        {
            "name": "ElevenLabs",
            "slug": "elevenlabs",
            "description": "ElevenLabs provides AI voice generation and text-to-speech technology with highly realistic and expressive voices.",
            "short_description": "AI voice generation",
            "website_url": "https://elevenlabs.io",
            "category_id": content_cat.id if content_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [] 
        },
        {
            "name": "Zapier AI",
            "slug": "zapier-ai",
            "description": "Zapier AI helps automate workflows by connecting apps and services with AI-powered suggestions and natural language automation.",
            "short_description": "AI workflow automation",
            "website_url": "https://zapier.com/ai",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [auto_tag] if auto_tag else []
        },
        {
            "name": "Replit Ghostwriter",
            "slug": "replit-ghostwriter",
            "description": "Replit Ghostwriter is an AI pair programmer integrated into Replit IDE, providing code completion and generation.",
            "short_description": "AI coding assistant for Replit",
            "website_url": "https://replit.com/ai",
            "category_id": dev_cat.id if dev_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": False,
            "tags": [code_tag] if code_tag else []
        },
        {
            "name": "Tabnine",
            "slug": "tabnine",
            "description": "Tabnine is an AI code completion tool that works across multiple IDEs and supports many programming languages.",
            "short_description": "AI code completion for IDEs",
            "website_url": "https://tabnine.com",
            "category_id": dev_cat.id if dev_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [code_tag] if code_tag else []
        },
        {
            "name": "Codeium",
            "slug": "codeium",
            "description": "Codeium is a free AI-powered code completion tool that works with 70+ languages and integrates with popular IDEs.",
            "short_description": "Free AI code completion",
            "website_url": "https://codeium.com",
            "category_id": dev_cat.id if dev_cat else None,
            "pricing_model": PricingModel.FREE,
            "featured": False,
            "tags": [code_tag] if code_tag else []
        },
        {
            "name": "Otter.ai",
            "slug": "otter-ai",
            "description": "Otter.ai provides real-time transcription and meeting notes with AI-powered summaries and action items.",
            "short_description": "AI meeting transcription",
            "website_url": "https://otter.ai",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [auto_tag] if auto_tag else []
        },
        {
            "name": "Descript",
            "slug": "descript",
            "description": "Descript is an AI-powered audio and video editor that allows editing media files as easily as text documents.",
            "short_description": "AI audio/video editor",
            "website_url": "https://descript.com",
            "category_id": content_cat.id if content_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": []
        },
        {
            "name": "Fireflies.ai",
            "slug": "fireflies-ai",
            "description": "Fireflies.ai automatically records, transcribes, and analyzes meetings across various video conferencing platforms.",
            "short_description": "AI meeting assistant",
            "website_url": "https://fireflies.ai",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [auto_tag] if auto_tag else []
        },
        {
            "name": "Superhuman",
            "slug": "superhuman",
            "description": "Superhuman is an AI-powered email client that helps you achieve inbox zero with intelligent features and shortcuts.",
            "short_description": "AI email client",
            "website_url": "https://superhuman.com",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": False,
            "tags": [auto_tag] if auto_tag else []
        },
        {
            "name": "HubSpot AI",
            "slug": "hubspot-ai",
            "description": "HubSpot AI provides content generation, email writing, and CRM automation features integrated into HubSpot platform.",
            "short_description": "AI for HubSpot CRM",
            "website_url": "https://hubspot.com/products/artificial-intelligence",
            "category_id": marketing_cat.id if marketing_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": False,
            "tags": [auto_tag] if auto_tag else []
        },
        {
            "name": "Writesonic",
            "slug": "writesonic",
            "description": "Writesonic is an AI writing platform for creating articles, blog posts, ads, and marketing copy with SEO optimization.",
            "short_description": "AI content writing platform",
            "website_url": "https://writesonic.com",
            "category_id": marketing_cat.id if marketing_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Notion",
            "slug": "notion",
            "description": "Notion is an all-in-one workspace with AI capabilities for notes, docs, wikis, and project management.",
            "short_description": "All-in-one workspace with AI",
            "website_url": "https://notion.so",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [auto_tag] if auto_tag else []
        },
        {
            "name": "Stable Diffusion",
            "slug": "stable-diffusion",
            "description": "Stable Diffusion is an open-source AI image generation model that creates images from text descriptions.",
            "short_description": "Open-source AI image generator",
            "website_url": "https://stability.ai",
            "category_id": content_cat.id if content_cat else None,
            "pricing_model": PricingModel.FREE,
            "featured": False,
            "tags": [image_tag] if image_tag else []
        },
        {
            "name": "DALL-E",
            "slug": "dall-e",
            "description": "DALL-E by OpenAI creates realistic images and art from natural language descriptions.",
            "short_description": "OpenAI's image generation AI",
            "website_url": "https://openai.com/dall-e",
            "category_id": content_cat.id if content_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": False,
            "tags": [image_tag] if image_tag else []
        },
        {
            "name": "Anthropic Claude API",
            "slug": "claude-api",
            "description": "Claude API provides programmatic access to Anthropic's Claude models for building AI applications.",
            "short_description": "API access to Claude",
            "website_url": "https://anthropic.com/api",
            "category_id": dev_cat.id if dev_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": False,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Replicate",
            "slug": "replicate",
            "description": "Replicate runs machine learning models in the cloud with a simple API for AI image, video, and text generation.",
            "short_description": "Run ML models via API",
            "website_url": "https://replicate.com",
            "category_id": dev_cat.id if dev_cat else None,
            "pricing_model": PricingModel.PAID,
            "featured": False,
            "tags": [api_tag] if api_tag else []
        },
        {
            "name": "Character.AI",
            "slug": "character-ai",
            "description": "Character.AI lets you create and chat with AI characters with distinct personalities and conversation styles.",
            "short_description": "Chat with AI characters",
            "website_url": "https://character.ai",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Anthropic Console",
            "slug": "anthropic-console",
            "description": "Anthropic Console provides a web interface for testing and developing with Claude AI models.",
            "short_description": "Claude development console",
            "website_url": "https://console.anthropic.com",
            "category_id": dev_cat.id if dev_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [code_tag] if code_tag else []
        },
        {
            "name": "Hugging Face",
            "slug": "hugging-face",
            "description": "Hugging Face is an AI community platform providing access to thousands of open-source ML models and datasets.",
            "short_description": "Open-source AI model hub",
            "website_url": "https://huggingface.co",
            "category_id": dev_cat.id if dev_cat else None,
            "pricing_model": PricingModel.FREEMIUM,
            "featured": False,
            "tags": [api_tag] if api_tag else []
        },
        {
            "name": "Pi AI",
            "slug": "pi-ai",
            "description": "Pi is a personal AI assistant by Inflection AI designed for supportive and empathetic conversations.",
            "short_description": "Personal AI by Inflection AI",
            "website_url": "https://pi.ai",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREE,
            "featured": False,
            "tags": [conv_tag] if conv_tag else []
        },
        {
            "name": "Bard (now Gemini)",
            "slug": "bard",
            "description": "Bard, now rebranded as Gemini, is Google's conversational AI service for creative and informative interactions.",
            "short_description": "Google's AI chatbot",
            "website_url": "https://bard.google.com",
            "category_id": productivity_cat.id if productivity_cat else None,
            "pricing_model": PricingModel.FREE,
            "featured": False,
            "tags": [conv_tag] if conv_tag else []
        },
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
    
    db.commit()
    print(f"Created {len(created)} agents")
    return created


def seed_extended_mcp_servers(db: Session, categories, tags):
    """Create 25 real MCP servers from aiagentslist.com."""
    dev_cat = next((c for c in categories if c.slug == "development"), None)
    data_cat = next((c for c in categories if c.slug == "data-analysis"), None)
    comm_cat = next((c for c in categories if c.slug == "communication"), None)
    
    api_tag = next((t for t in tags if t.slug == "api-integration"), None)
    db_tag = next((t for t in tags if t.slug == "database"), None)
    browser_tag = next((t for t in tags if t.slug == "browser-automation"), None)
    file_tag = next((t for t in tags if t.slug == "file-systems"), None)
    vc_tag = next((t for t in tags if t.slug == "version-control"), None)
    sec_tag = next((t for t in tags if t.slug == "security"), None)
    mem_tag = next((t for t in tags if t.slug == "knowledge-memory"), None)
    
    servers = [
        {
            "name": "markitdown",
            "slug": "markitdown-mcp",
            "description": "Microsoft's official Python tool for converting files and office documents to Markdown format. Supports various file types.",
            "repository_url": "https://github.com/microsoft/markitdown",
            "language": "Python",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "pypi_package": "markitdown",
            "star_count": 59126,
            "featured": True,
            "tags": [file_tag] if file_tag else []
        },
        {
            "name": "Model Context Protocol Servers",
            "slug": "mcp-servers-official",
            "description": "Official Model Context Protocol server implementations from the MCP team.",
            "repository_url": "https://github.com/modelcontextprotocol/servers",
            "language": "Python",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "star_count": 53820,
            "featured": True,
            "tags": []
        },
        {
            "name": "Prisma MCP",
            "slug": "prisma-mcp",
            "description": "Next-generation ORM for Node.js & TypeScript supporting PostgreSQL, MySQL, MariaDB, SQL Server, SQLite, MongoDB and CockroachDB.",
            "repository_url": "https://github.com/prisma/prisma",
            "language": "TypeScript",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "npm_package": "@prisma/client",
            "star_count": 42565,
            "featured": True,
            "tags": [db_tag] if db_tag else []
        },
        {
            "name": "MindsDB MCP",
            "slug": "mindsdb-mcp",
            "description": "AI's query engine - Platform for building AI that can answer questions over large scale federated data.",
            "repository_url": "https://github.com/mindsdb/mindsdb",
            "language": "Python",
            "scope": ServerScope.LOCAL,
            "category_id": data_cat.id if data_cat else None,
            "pypi_package": "mindsdb",
            "star_count": 32125,
            "featured": True,
            "tags": [db_tag] if db_tag else []
        },
        {
            "name": "GitHub MCP Server",
            "slug": "github-mcp-server",
            "description": "GitHub's official MCP Server for version control operations and repository management.",
            "repository_url": "https://github.com/github/mcp-server",
            "language": "Go",
            "scope": ServerScope.CLOUD,
            "category_id": dev_cat.id if dev_cat else None,
            "star_count": 15738,
            "featured": True,
            "tags": [vc_tag] if vc_tag else []
        },
        {
            "name": "Screenpipe",
            "slug": "screenpipe-mcp",
            "description": "AI app store powered by 24/7 desktop history. Open source, 100% local, dev friendly with 24/7 screen and mic recording.",
            "repository_url": "https://github.com/mediar-ai/screenpipe",
            "language": "TypeScript",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "npm_package": "screenpipe",
            "star_count": 15023,
            "featured": True,
            "tags": [vc_tag] if vc_tag else []
        },
        {
            "name": "Playwright MCP",
            "slug": "playwright-mcp",
            "description": "Microsoft's Playwright MCP server for browser automation and testing.",
            "repository_url": "https://github.com/microsoft/playwright-mcp",
            "language": "TypeScript",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "npm_package": "playwright-mcp",
            "star_count": 11899,
            "featured": True,
            "tags": [browser_tag] if browser_tag else []
        },
        {
            "name": "Filestash",
            "slug": "filestash-mcp",
            "description": "A file manager / web client for SFTP, S3, FTP, WebDAV, Git, Minio, LDAP, CalDAV, CardDAV, MySQL, Backblaze.",
            "repository_url": "https://github.com/mickael-kerjean/filestash",
            "language": "JavaScript",
            "scope": ServerScope.CLOUD,
            "category_id": dev_cat.id if dev_cat else None,
            "star_count": 11420,
            "featured": False,
            "tags": [file_tag] if file_tag else []
        },
        {
            "name": "Pydantic AI",
            "slug": "pydantic-ai-mcp",
            "description": "Agent Framework / shim to use Pydantic with LLMs for browser automation.",
            "repository_url": "https://github.com/pydantic/pydantic-ai",
            "language": "Python",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "pypi_package": "pydantic-ai",
            "star_count": 10239,
            "featured": False,
            "tags": [browser_tag] if browser_tag else []
        },
        {
            "name": "Pipedream",
            "slug": "pipedream-mcp",
            "description": "Connect APIs, remarkably fast. Free for developers.",
            "repository_url": "https://github.com/PipedreamHQ/pipedream",
            "language": "JavaScript",
            "scope": ServerScope.CLOUD,
            "category_id": dev_cat.id if dev_cat else None,
            "npm_package": "@pipedream/platform",
            "star_count": 9990,
            "featured": False,
            "tags": [api_tag] if api_tag else []
        },
        {
            "name": "Figma Context MCP",
            "slug": "figma-context-mcp",
            "description": "MCP server to provide Figma layout information to AI coding agents like Cursor.",
            "repository_url": "https://github.com/GLips/Figma-Context-MCP",
            "language": "TypeScript",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "npm_package": "figma-context-mcp",
            "star_count": 8152,
            "featured": False,
            "tags": [api_tag] if api_tag else []
        },
        {
            "name": "Inbox Zero",
            "slug": "inbox-zero-mcp",
            "description": "The world's best AI personal assistant for email. Open source app to help you reach inbox zero fast.",
            "repository_url": "https://github.com/elie222/inbox-zero",
            "language": "TypeScript",
            "scope": ServerScope.CLOUD,
            "category_id": comm_cat.id if comm_cat else None,
            "npm_package": "inbox-zero",
            "star_count": 8050,
            "featured": False,
            "tags": []
        },
        {
            "name": "Cognee",
            "slug": "cognee-mcp",
            "description": "Memory for AI Agents in 5 lines of code.",
            "repository_url": "https://github.com/topoteretes/cognee",
            "language": "Python",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "pypi_package": "cognee",
            "star_count": 5540,
            "featured": False,
            "tags": [mem_tag] if mem_tag else []
        },
        {
            "name": "Ghidra MCP",
            "slug": "ghidra-mcp",
            "description": "MCP Server for Ghidra reverse engineering platform.",
            "repository_url": "https://github.com/LaurieWired/GhidraMCP",
            "language": "Java",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "star_count": 5148,
            "featured": False,
            "tags": [sec_tag] if sec_tag else []
        },
        {
            "name": "WhatsApp MCP",
            "slug": "whatsapp-mcp",
            "description": "WhatsApp MCP server for messaging integration.",
            "repository_url": "https://github.com/lharries/whatsapp-mcp",
            "language": "Go",
            "scope": ServerScope.LOCAL,
            "category_id": comm_cat.id if comm_cat else None,
            "star_count": 4099,
            "featured": False,
            "tags": []
        },
        {
            "name": "Playwright MCP (Execute Automation)",
            "slug": "mcp-playwright",
            "description": "Playwright Model Context Protocol Server - Tool to automate browsers and web applications.",
            "repository_url": "https://github.com/executeautomation/mcp-playwright",
            "language": "TypeScript",
            "scope": ServerScope.LOCAL,
            "category_id": dev_cat.id if dev_cat else None,
            "npm_package": "mcp-playwright",
            "star_count": 3878,
            "featured": False,
            "tags": [browser_tag] if browser_tag else []
        },
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
    
    db.commit()
    print(f"Created {len(created)} MCP servers")
    return created


def main():
    """Main seed function."""
    print("Starting extended database seeding with real data...")
    print("Data sourced from: https://aiagentslist.com\n")
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        categories = seed_extended_categories(db)
        tags = seed_extended_tags(db)
        agents = seed_extended_agents(db, categories, tags)
        mcp_servers = seed_extended_mcp_servers(db, categories, tags)
        
        print("\n" + "="*50)
        print("Extended seeding complete!")
        print("="*50)
        print(f"Categories: {len(categories)}")
        print(f"Tags: {len(tags)}")
        print(f"Agents: {len(agents)}")
        print(f"MCP Servers: {len(mcp_servers)}")
        print("="*50)
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
