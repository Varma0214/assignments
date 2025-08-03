import pytest
import json
from app.main import app
from app.models import url_store

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Clear the store before each test
        url_store._mappings.clear()
        yield client

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'URL Shortener API'

def test_api_health(client):
    """Test API health endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'URL Shortener API is running' in data['message']

def test_shorten_url_success(client):
    """Test successful URL shortening"""
    test_url = "https://www.example.com/very/long/url"
    response = client.post('/api/shorten',
                          json={'url': test_url},
                          content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'short_code' in data
    assert 'short_url' in data
    assert len(data['short_code']) == 6
    assert data['short_url'].startswith('http://localhost:5000/')

def test_shorten_url_invalid_json(client):
    """Test URL shortening with invalid JSON"""
    response = client.post('/api/shorten',
                          data='invalid json',
                          content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_shorten_url_missing_url(client):
    """Test URL shortening with missing URL"""
    response = client.post('/api/shorten',
                          json={},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_shorten_url_invalid_url(client):
    """Test URL shortening with invalid URL"""
    response = client.post('/api/shorten',
                          json={'url': 'not-a-url'},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_redirect_success(client):
    """Test successful URL redirection"""
    # First create a short URL
    test_url = "https://www.example.com/test"
    shorten_response = client.post('/api/shorten',
                                 json={'url': test_url},
                                 content_type='application/json')
    
    short_code = shorten_response.get_json()['short_code']
    
    # Test redirect
    response = client.get(f'/{short_code}')
    assert response.status_code == 302
    assert response.location == test_url

def test_redirect_not_found(client):
    """Test redirect with non-existent short code"""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_stats_success(client):
    """Test successful stats retrieval"""
    # First create a short URL
    test_url = "https://www.example.com/stats-test"
    shorten_response = client.post('/api/shorten',
                                 json={'url': test_url},
                                 content_type='application/json')
    
    short_code = shorten_response.get_json()['short_code']
    
    # Test stats before any clicks
    response = client.get(f'/api/stats/{short_code}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['url'] == test_url
    assert data['clicks'] == 0
    assert 'created_at' in data

def test_stats_with_clicks(client):
    """Test stats after clicking the short URL"""
    # First create a short URL
    test_url = "https://www.example.com/click-test"
    shorten_response = client.post('/api/shorten',
                                 json={'url': test_url},
                                 content_type='application/json')
    
    short_code = shorten_response.get_json()['short_code']
    
    # Click the short URL multiple times
    for _ in range(3):
        client.get(f'/{short_code}')
    
    # Check stats
    response = client.get(f'/api/stats/{short_code}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['clicks'] == 3

def test_stats_not_found(client):
    """Test stats for non-existent short code"""
    response = client.get('/api/stats/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_url_without_scheme(client):
    """Test URL shortening with URL that doesn't have a scheme"""
    test_url = "www.example.com/no-scheme"
    response = client.post('/api/shorten',
                          json={'url': test_url},
                          content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'short_code' in data

def test_thread_safety():
    """Test that URLStore is thread-safe"""
    import threading
    import time
    
    # Test that multiple threads can safely access the store
    results = []
    
    def add_mapping(thread_id):
        try:
            mapping = url_store.add_mapping(f"test{thread_id}", f"https://example{thread_id}.com")
            results.append(mapping.short_code)
        except Exception as e:
            results.append(f"error: {e}")
    
    # Create multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=add_mapping, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # All operations should succeed
    assert len(results) == 5
    assert all(not result.startswith('error:') for result in results)

def test_404_error_handler(client):
    """Test 404 error handler"""
    response = client.get('/nonexistent/endpoint')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data