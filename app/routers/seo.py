from fastapi import APIRouter, Response
from datetime import datetime, timezone
import os

router = APIRouter()


@router.get("/robots.txt")
async def robots_txt():
    """Serve robots.txt for search engine crawling"""
    content = """User-agent: *
Allow: /
Disallow: /api/
Sitemap: https://localhost:9000/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")


@router.get("/sitemap.xml")
async def sitemap_xml():
    """Generate dynamic sitemap.xml for SEO"""
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://localhost:9000/</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://localhost:9000/health</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.5</priority>
    </url>
</urlset>"""
    return Response(content=sitemap, media_type="application/xml")


@router.get("/favicon.ico")
async def favicon():
    """Serve favicon (placeholder)"""
    # In production, serve an actual favicon file
    return Response(content=b"", media_type="image/x-icon")
