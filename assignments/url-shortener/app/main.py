from flask import Flask, jsonify, request, redirect, url_for
from .models import url_store
from .utils import is_valid_url, generate_short_code, format_timestamp, sanitize_url
import json

app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "URL Shortener API"
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        "status": "ok",
        "message": "URL Shortener API is running"
    })

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """
    Shorten a URL endpoint
    
    Expected JSON payload:
    {
        "url": "https://www.example.com/very/long/url"
    }
    
    Returns:
    {
        "short_code": "abc123",
        "short_url": "http://localhost:5000/abc123"
    }
    """
    try:
        # Parse request data
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 400
        
        try:
            data = request.get_json()
        except Exception:
            return jsonify({
                "error": "Invalid JSON in request body"
            }), 400
        
        if not data or 'url' not in data:
            return jsonify({
                "error": "URL is required in request body"
            }), 400
        
        original_url = data['url'].strip()
        
        # Sanitize URL first (add scheme if missing)
        original_url = sanitize_url(original_url)
        
        # Validate URL
        if not is_valid_url(original_url):
            return jsonify({
                "error": "Invalid URL provided"
            }), 400
        
        # Generate short code
        short_code = generate_short_code()
        
        # Store the mapping
        mapping = url_store.add_mapping(short_code, original_url)
        
        # Generate short URL
        short_url = f"http://localhost:5000/{short_code}"
        
        return jsonify({
            "short_code": short_code,
            "short_url": short_url
        }), 201
        
    except Exception as e:
        return jsonify({
            "error": "Internal server error"
        }), 500

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """
    Redirect to original URL
    
    Args:
        short_code: The short code to redirect from
        
    Returns:
        Redirect to original URL or 404 if not found
    """
    # Get the mapping
    mapping = url_store.get_mapping(short_code)
    
    if not mapping:
        return jsonify({
            "error": "Short code not found"
        }), 404
    
    # Increment click count
    url_store.increment_clicks(short_code)
    
    # Redirect to original URL
    return redirect(mapping.original_url, code=302)

@app.route('/api/stats/<short_code>')
def get_stats(short_code):
    """
    Get analytics for a short code
    
    Args:
        short_code: The short code to get stats for
        
    Returns:
        JSON with URL, clicks, and creation timestamp
    """
    mapping = url_store.get_mapping(short_code)
    
    if not mapping:
        return jsonify({
            "error": "Short code not found"
        }), 404
    
    return jsonify({
        "url": mapping.original_url,
        "clicks": mapping.clicks,
        "created_at": format_timestamp(mapping.created_at)
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)