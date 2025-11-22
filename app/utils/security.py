"""
Security utility functions and helpers
"""

import hashlib
import hmac
import secrets
import string
from typing import Optional, Dict, Any, List
import re
from datetime import datetime, timezone
import ipaddress
import structlog

# TODO: Add password breach checking
# TODO: Add advanced threat detection
# TODO: Add geographic IP analysis
# TODO: Add device fingerprinting
# TODO: Add behavioral analysis
# TODO: Add ML-based fraud detection

logger = structlog.get_logger()


class SecurityUtils:
    """
    Collection of security utility functions
    
    TODO: Add cryptographic utilities
    TODO: Add secure random generators
    TODO: Add hash verification utilities
    TODO: Add timing attack protection
    """
    
    @staticmethod
    def generate_secure_token(length: int = 32, url_safe: bool = True) -> str:
        """Generate cryptographically secure random token"""
        if url_safe:
            return secrets.token_urlsafe(length)
        else:
            return secrets.token_hex(length)
    
    @staticmethod
    def generate_password(length: int = 16, include_symbols: bool = True) -> str:
        """Generate a secure random password"""
        letters = string.ascii_letters
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if include_symbols else ""
        
        alphabet = letters + digits + symbols
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Ensure password contains at least one character from each category
        if not any(c.islower() for c in password):
            password = password[:-1] + secrets.choice(string.ascii_lowercase)
        if not any(c.isupper() for c in password):
            password = password[:-1] + secrets.choice(string.ascii_uppercase)
        if not any(c.isdigit() for c in password):
            password = password[:-1] + secrets.choice(string.digits)
        if include_symbols and not any(c in symbols for c in password):
            password = password[:-1] + secrets.choice(symbols)
        
        return password
    
    @staticmethod
    def hash_data(data: str, salt: Optional[str] = None) -> str:
        """Hash data with optional salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        combined = f"{data}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def verify_hash(data: str, hashed: str, salt: str) -> bool:
        """Verify data against hash with salt"""
        expected_hash = SecurityUtils.hash_data(data, salt)
        return hmac.compare_digest(expected_hash, hashed)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove path separators and dangerous characters
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip('. ')
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = f"{name[:240]}.{ext}" if ext else sanitized[:255]
        
        return sanitized or 'unnamed_file'
    
    @staticmethod
    def is_safe_redirect_url(url: str, allowed_hosts: List[str]) -> bool:
        """Check if redirect URL is safe"""
        if not url:
            return False
        
        # Block javascript: and data: URLs
        if url.lower().startswith(('javascript:', 'data:', 'vbscript:')):
            return False
        
        # Allow relative URLs
        if url.startswith('/') and not url.startswith('//'):
            return True
        
        # Check absolute URLs against allowed hosts
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower() in [host.lower() for host in allowed_hosts]
        except Exception:
            return False
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """Check if IP address is private"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False
    
    @staticmethod
    def extract_ip_from_request(request_headers: Dict[str, str], 
                              remote_addr: str) -> str:
        """Extract real IP address from request"""
        # Check common forwarded IP headers
        forwarded_headers = [
            'X-Forwarded-For',
            'X-Real-IP',
            'CF-Connecting-IP',  # Cloudflare
            'X-Cluster-Client-IP',
            'X-Forwarded',
            'Forwarded-For',
            'Forwarded'
        ]
        
        for header in forwarded_headers:
            if header in request_headers:
                # X-Forwarded-For can contain multiple IPs
                ip_list = request_headers[header].split(',')
                for ip in ip_list:
                    clean_ip = ip.strip()
                    if SecurityUtils.validate_ip_address(clean_ip):
                        return clean_ip
        
        return remote_addr or '0.0.0.0'


class ThreatDetector:
    """
    Security threat detection utilities
    
    TODO: Add machine learning models
    TODO: Add threat intelligence feeds
    TODO: Add behavioral analysis
    TODO: Add real-time blocking
    """
    
    def __init__(self):
        self.suspicious_patterns = [
            r'(?i)(union|select|insert|delete|drop|create|alter)',  # SQL injection
            r'(?i)(<script|javascript:|vbscript:|onload|onerror)',  # XSS
            r'(?i)(\.\.\/|\.\.\\|\.\.%2f|\.\.%5c)',  # Path traversal
            r'(?i)(cmd|exec|eval|system|shell_exec|passthru)',  # Command injection
        ]
        self.compiled_patterns = [re.compile(pattern) for pattern in self.suspicious_patterns]
    
    def detect_suspicious_input(self, input_data: str) -> List[str]:
        """Detect suspicious patterns in input data"""
        threats = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(input_data):
                threat_types = [
                    'SQL Injection',
                    'XSS Attack', 
                    'Path Traversal',
                    'Command Injection'
                ]
                threats.append(threat_types[i])
        
        return threats
    
    def is_brute_force_attempt(self, failed_attempts: int, 
                             time_window: int, 
                             threshold: int = 5) -> bool:
        """Detect brute force attack patterns"""
        return failed_attempts >= threshold
    
    def analyze_user_agent(self, user_agent: str) -> Dict[str, Any]:
        """Analyze user agent for suspicious patterns"""
        suspicious_indicators = []
        
        if not user_agent:
            suspicious_indicators.append('Empty user agent')
        elif len(user_agent) < 10:
            suspicious_indicators.append('Unusually short user agent')
        elif 'bot' in user_agent.lower() and 'googlebot' not in user_agent.lower():
            suspicious_indicators.append('Generic bot user agent')
        elif any(tool in user_agent.lower() for tool in ['curl', 'wget', 'python', 'postman']):
            suspicious_indicators.append('Automated tool detected')
        
        return {
            'is_suspicious': len(suspicious_indicators) > 0,
            'indicators': suspicious_indicators,
            'risk_score': min(len(suspicious_indicators) * 25, 100)
        }
    
    def check_request_anomalies(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for request anomalies"""
        anomalies = []
        risk_score = 0
        
        # Check for unusual request patterns
        if request_data.get('method') not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            anomalies.append('Unusual HTTP method')
            risk_score += 20
        
        # Check for suspicious headers
        headers = request_data.get('headers', {})
        if not headers.get('User-Agent'):
            anomalies.append('Missing User-Agent header')
            risk_score += 15
        
        # Check for oversized requests
        content_length = headers.get('Content-Length', '0')
        try:
            if int(content_length) > 10 * 1024 * 1024:  # 10MB
                anomalies.append('Unusually large request')
                risk_score += 25
        except ValueError:
            pass
        
        return {
            'anomalies': anomalies,
            'risk_score': min(risk_score, 100),
            'is_suspicious': risk_score > 50
        }


class CSRFProtection:
    """
    CSRF protection utilities
    
    TODO: Add token generation and validation
    TODO: Add SameSite cookie support
    TODO: Add Origin header validation
    """
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_csrf_token(token: str, expected_token: str) -> bool:
        """Validate CSRF token"""
        if not token or not expected_token:
            return False
        return hmac.compare_digest(token, expected_token)
    
    @staticmethod
    def validate_origin(origin: str, allowed_origins: List[str]) -> bool:
        """Validate request origin"""
        if not origin:
            return False
        return origin in allowed_origins


class InputValidator:
    """
    Input validation utilities
    
    TODO: Add schema validation
    TODO: Add custom validation rules
    TODO: Add sanitization options
    """
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        # Check for valid international format
        pattern = r'^\+?[\d]{10,15}$'
        return bool(re.match(pattern, cleaned))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def sanitize_html(html: str) -> str:
        """Basic HTML sanitization"""
        # Remove script tags and javascript
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(r'javascript:', '', html, flags=re.IGNORECASE)
        html = re.sub(r'vbscript:', '', html, flags=re.IGNORECASE)
        html = re.sub(r'on\w+\s*=', '', html, flags=re.IGNORECASE)
        
        return html


# TODO: Add encryption utilities
# TODO: Add digital signature utilities
# TODO: Add secure communication helpers
# TODO: Add compliance utilities (GDPR, HIPAA)
# TODO: Add security audit helpers
