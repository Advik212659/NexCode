import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_robots_txt():
    """Test /robots.txt endpoint"""
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    
    content = response.text
    assert "User-agent:" in content
    assert "Allow:" in content
    assert "Sitemap:" in content


def test_robots_txt_disallows_api():
    """Test that robots.txt disallows API routes"""
    response = client.get("/robots.txt")
    content = response.text
    assert "Disallow: /api/" in content


def test_sitemap_xml():
    """Test /sitemap.xml endpoint"""
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    
    content = response.text
    assert "<?xml version" in content
    assert "<urlset" in content
    assert "<url>" in content
    assert "<loc>" in content
    assert "</urlset>" in content


def test_sitemap_includes_root():
    """Test that sitemap includes root URL"""
    response = client.get("/sitemap.xml")
    content = response.text
    assert "https://localhost:9000/" in content


def test_sitemap_includes_health():
    """Test that sitemap includes health endpoint"""
    response = client.get("/sitemap.xml")
    content = response.text
    assert "https://localhost:9000/health" in content


def test_sitemap_has_required_tags():
    """Test that sitemap has all required XML tags"""
    response = client.get("/sitemap.xml")
    content = response.text
    
    assert "<lastmod>" in content
    assert "<changefreq>" in content
    assert "<priority>" in content


def test_favicon():
    """Test /favicon.ico endpoint"""
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert "image" in response.headers["content-type"]


def test_root_endpoint():
    """Test root endpoint returns HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_sitemap_xml_structure():
    """Test sitemap XML structure is valid"""
    response = client.get("/sitemap.xml")
    content = response.text
    
    # Check for proper XML declaration
    assert content.startswith("<?xml")
    
    # Check for namespace
    assert "xmlns=" in content
    
    # Check for URL entries
    assert content.count("<url>") >= 2  # At least root and health


def test_robots_txt_allows_indexing():
    """Test that robots.txt allows indexing"""
    response = client.get("/robots.txt")
    content = response.text
    assert "Allow: /" in content


def test_sitemap_priority_values():
    """Test that sitemap has valid priority values"""
    response = client.get("/sitemap.xml")
    content = response.text
    
    # Priority should be between 0.0 and 1.0
    import re
    priorities = re.findall(r'<priority>([\d.]+)</priority>', content)
    for priority in priorities:
        value = float(priority)
        assert 0.0 <= value <= 1.0


def test_sitemap_changefreq_values():
    """Test that sitemap has valid changefreq values"""
    response = client.get("/sitemap.xml")
    content = response.text
    
    valid_freqs = ['always', 'hourly', 'daily', 'weekly', 'monthly', 'yearly', 'never']
    import re
    freqs = re.findall(r'<changefreq>(\w+)</changefreq>', content)
    for freq in freqs:
        assert freq in valid_freqs


def test_robots_txt_sitemap_reference():
    """Test that robots.txt references sitemap.xml"""
    response = client.get("/robots.txt")
    content = response.text
    assert "sitemap.xml" in content.lower()


def test_seo_metadata_in_html():
    """Test that HTML response includes SEO metadata"""
    response = client.get("/")
    assert response.status_code == 200
    content = response.text
    
    # Check for title
    assert "<title>" in content
    assert "NexCode" in content
    
    # Check for meta description
    assert 'name="description"' in content
    
    # Check for viewport
    assert "viewport" in content
