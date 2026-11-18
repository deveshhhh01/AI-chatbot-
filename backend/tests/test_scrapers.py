import pytest
from backend.app.scrapers.base_scraper import BaseScraper
from backend.app.scrapers.darglobal_scraper import DarGlobalScraper, DARGLOBAL_KEY_PROJECTS
from backend.app.scrapers.wasalt_scraper import WasaltScraper


class DummyScraper(BaseScraper):
    def scrape(self, limit=10):
        return []


def test_base_scraper_text_cleaning():
    scraper = DummyScraper(name="TestScraper", base_url="https://example.com")
    cleaned = scraper.clean_text("  Luxury   Villa in   Dubai  \n\t with pool   ")
    assert cleaned == "Luxury Villa in Dubai with pool"


def test_base_scraper_link_extraction():
    scraper = DummyScraper(name="TestScraper", base_url="https://example.com")
    html = """
    <html>
        <body>
            <a href="/project/villa-1">Villa 1</a>
            <a href="/project/villa-2#details">Villa 2</a>
            <a href="https://other.com/ext">External</a>
        </body>
    </html>
    """
    links = scraper.extract_links(html, filter_keyword="project")
    assert "https://example.com/project/villa-1" in links
    assert "https://example.com/project/villa-2" in links
    assert len(links) == 2


def test_darglobal_scraper_structure():
    scraper = DarGlobalScraper()
    assert scraper.name == "DarGlobalScraper"
    assert len(DARGLOBAL_KEY_PROJECTS) >= 10
    
    # Test key project definition integrity
    first = DARGLOBAL_KEY_PROJECTS[0]
    assert "name" in first
    assert "country" in first
    assert "city" in first
    assert "developer" in first
    assert first["url"].startswith("https://darglobal.co.uk")


def test_wasalt_scraper_parsing():
    scraper = WasaltScraper()
    assert scraper.name == "WasaltScraper"

    mock_html = """
    <html>
    <head><title>Apartment with 3 Bedrooms For Sale</title></head>
    <body>
    <script id="__NEXT_DATA__" type="application/json">
    {
        "props": {
            "pageProps": {
                "propertyDetailsV3": {
                    "id": "5841667",
                    "title": "Apartment with 3 Bedrooms",
                    "propertyInfo": {
                        "title": "Apartment with 3 Bedrooms",
                        "salePrice": 850000,
                        "currencyType": "SAR",
                        "country": "Saudi Arabia",
                        "city": "Riyadh",
                        "district": "Al-Mahdiyah",
                        "propertySubType": "Apartment",
                        "description": "<p>Spacious 3 bedroom apartment in Riyadh</p>"
                    },
                    "attributes": [
                        {"key": "noOfBedrooms", "name": "Bedrooms", "value": 3},
                        {"key": "builtUpArea", "name": "Built-Up Area", "value": "133"}
                    ]
                }
            }
        }
    }
    </script>
    </body>
    </html>
    """
    record = scraper._parse_property_html(mock_html, "https://wasalt.sa/en/property/sale/apartment-with-3-bedrooms-5841667")
    assert record is not None
    assert record["source"] == "Wasalt"
    assert record["project_name"] == "Apartment with 3 Bedrooms"
    assert record["location"]["city"] == "Riyadh"
    assert record["location"]["country"] == "Saudi Arabia"
    assert record["price"]["amount"] == 850000.0
    assert record["price"]["currency"] == "SAR"
    assert record["bedrooms"] == 3
    assert record["area_sqm"] == 133.0
    assert record["source_url"] == "https://wasalt.sa/en/property/sale/apartment-with-3-bedrooms-5841667"
