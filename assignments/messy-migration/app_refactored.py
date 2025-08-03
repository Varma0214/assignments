"""
Refactored User Management API
Addresses security vulnerabilities and improves code quality
"""
from flask import Flask, request, jsonify
import sqlite3
import json
import hashlib
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@dataclass
class User:
    """User data model"""
    id: Optional[int]
    name: str
    email: str
    password_hash: str

class DatabaseManager:
    """Database connection and query management"""
    
    def __init__(self, db_path: str = 'users.db'):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> list:
        """Execute a query with parameters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an update query with parameters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

class UserValidator:
    """Input validation for user data"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        return len(password) >= 6
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate name format"""
        return len(name.strip()) >= 2
    
    @staticmethod
    def validate_user_data(data: Dict[str, Any], required_fields: list) -> Tuple[bool, str]:
        """Validate user data"""
        # Check required fields
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        # Validate email
        if not UserValidator.validate_email(data['email']):
            return False, "Invalid email format"
        
        # Validate password (for create/update operations)
        if 'password' in data and not UserValidator.validate_password(data['password']):
            return False, "Password must be at least 6 characters long"
        
        # Validate name
        if 'name' in data and not UserValidator.validate_name(data['name']):
            return False, "Name must be at least 2 characters long"
        
        return True, ""

class UserService:
    """Business logic for user operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_all_users(self) -> list:
        """Get all users (without passwords)"""
        query = "SELECT id, name, email FROM users"
        return self.db_manager.execute_query(query)
    
    def get_user_by_id(self, user_id: int) -> Optional[Tuple]:
        """Get user by ID"""
        query = "SELECT id, name, email FROM users WHERE id = ?"
        result = self.db_manager.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def create_user(self, name: str, email: str, password: str) -> int:
        """Create a new user"""
        password_hash = self.hash_password(password)
        query = "INSERT INTO users (name, email, password) VALUES (?, ?, ?)"
        self.db_manager.execute_update(query, (name, email, password_hash))
        
        # Get the ID of the created user
        query = "SELECT id FROM users WHERE email = ?"
        result = self.db_manager.execute_query(query, (email,))
        return result[0][0] if result else None
    
    def update_user(self, user_id: int, name: str, email: str) -> bool:
        """Update user information"""
        query = "UPDATE users SET name = ?, email = ? WHERE id = ?"
        affected_rows = self.db_manager.execute_update(query, (name, email, user_id))
        return affected_rows > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        query = "DELETE FROM users WHERE id = ?"
        affected_rows = self.db_manager.execute_update(query, (user_id,))
        return affected_rows > 0
    
    def search_users(self, name: str) -> list:
        """Search users by name"""
        query = "SELECT id, name, email FROM users WHERE name LIKE ?"
        return self.db_manager.execute_query(query, (f'%{name}%',))
    
    def authenticate_user(self, email: str, password: str) -> Optional[int]:
        """Authenticate user login"""
        password_hash = self.hash_password(password)
        query = "SELECT id FROM users WHERE email = ? AND password = ?"
        result = self.db_manager.execute_query(query, (email, password_hash))
        return result[0][0] if result else None

# Initialize services
db_manager = DatabaseManager()
user_service = UserService(db_manager)

def create_error_response(message: str, status_code: int = 400) -> Tuple[Dict, int]:
    """Create standardized error response"""
    return {"error": message}, status_code

def create_success_response(data: Dict, status_code: int = 200) -> Tuple[Dict, int]:
    """Create standardized success response"""
    return {"success": True, "data": data}, status_code

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "User Management System",
        "version": "2.0.0"
    })

@app.route('/users', methods=['GET'])
def get_all_users():
    """Get all users"""
    try:
        users = user_service.get_all_users()
        user_list = [
            {"id": user[0], "name": user[1], "email": user[2]}
            for user in users
        ]
        return jsonify({"users": user_list})
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return create_error_response("Internal server error", 500)

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user by ID"""
    try:
        user = user_service.get_user_by_id(user_id)
        if user:
            return jsonify({
                "id": user[0],
                "name": user[1],
                "email": user[2]
            })
        else:
            return create_error_response("User not found", 404)
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return create_error_response("Internal server error", 500)

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        # Parse request data
        if not request.is_json:
            return create_error_response("Content-Type must be application/json")
        
        data = request.get_json()
        
        # Validate required fields
        is_valid, error_message = UserValidator.validate_user_data(
            data, ['name', 'email', 'password']
        )
        if not is_valid:
            return create_error_response(error_message)
        
        # Check if user already exists
        existing_query = "SELECT id FROM users WHERE email = ?"
        existing = db_manager.execute_query(existing_query, (data['email'],))
        if existing:
            return create_error_response("User with this email already exists", 409)
        
        # Create user
        user_id = user_service.create_user(
            data['name'], data['email'], data['password']
        )
        
        logger.info(f"User created successfully with ID: {user_id}")
        return create_success_response({
            "id": user_id,
            "name": data['name'],
            "email": data['email']
        }, 201)
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return create_error_response("Internal server error", 500)

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    try:
        # Parse request data
        if not request.is_json:
            return create_error_response("Content-Type must be application/json")
        
        data = request.get_json()
        
        # Validate required fields
        is_valid, error_message = UserValidator.validate_user_data(
            data, ['name', 'email']
        )
        if not is_valid:
            return create_error_response(error_message)
        
        # Check if user exists
        existing_user = user_service.get_user_by_id(user_id)
        if not existing_user:
            return create_error_response("User not found", 404)
        
        # Check if email is already taken by another user
        email_check_query = "SELECT id FROM users WHERE email = ? AND id != ?"
        email_exists = db_manager.execute_query(email_check_query, (data['email'], user_id))
        if email_exists:
            return create_error_response("Email already taken by another user", 409)
        
        # Update user
        success = user_service.update_user(user_id, data['name'], data['email'])
        if success:
            logger.info(f"User {user_id} updated successfully")
            return create_success_response({
                "id": user_id,
                "name": data['name'],
                "email": data['email']
            })
        else:
            return create_error_response("Failed to update user", 500)
            
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        return create_error_response("Internal server error", 500)

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        # Check if user exists
        existing_user = user_service.get_user_by_id(user_id)
        if not existing_user:
            return create_error_response("User not found", 404)
        
        # Delete user
        success = user_service.delete_user(user_id)
        if success:
            logger.info(f"User {user_id} deleted successfully")
            return create_success_response({"message": "User deleted successfully"})
        else:
            return create_error_response("Failed to delete user", 500)
            
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return create_error_response("Internal server error", 500)

@app.route('/search', methods=['GET'])
def search_users():
    """Search users by name"""
    try:
        name = request.args.get('name')
        if not name:
            return create_error_response("Please provide a name to search")
        
        users = user_service.search_users(name)
        user_list = [
            {"id": user[0], "name": user[1], "email": user[2]}
            for user in users
        ]
        return jsonify({"users": user_list})
        
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        return create_error_response("Internal server error", 500)

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        # Parse request data
        if not request.is_json:
            return create_error_response("Content-Type must be application/json")
        
        data = request.get_json()
        
        # Validate required fields
        if not data or 'email' not in data or 'password' not in data:
            return create_error_response("Email and password are required")
        
        # Validate email format
        if not UserValidator.validate_email(data['email']):
            return create_error_response("Invalid email format")
        
        # Authenticate user
        user_id = user_service.authenticate_user(data['email'], data['password'])
        if user_id:
            logger.info(f"User {user_id} logged in successfully")
            return create_success_response({
                "user_id": user_id,
                "message": "Login successful"
            })
        else:
            return create_error_response("Invalid email or password", 401)
            
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return create_error_response("Internal server error", 500)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return create_error_response("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return create_error_response("Internal server error", 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True) 