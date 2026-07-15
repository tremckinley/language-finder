from discovery.sitemap import extract_sitemaps_from_robots,parse_sitemap_xml

def test_robots_extract():
    r=extract_sitemaps_from_robots("Sitemap: https://a.com/sitemap.xml")
    assert r==['https://a.com/sitemap.xml']

def test_parse_urlset():
    x='<urlset><url><loc>https://a.com/en</loc></url></urlset>'
    assert parse_sitemap_xml(x)['urls']==['https://a.com/en']
