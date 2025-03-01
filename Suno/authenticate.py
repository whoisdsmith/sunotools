"""
Authentication module for Suno.com

Handles user authentication and session management.
"""

import re
import requests
import json
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class SunoAuthenticator:
    """Handles authentication with Suno.com to access user content."""
    
    BASE_URL = "https://suno.com"
    LOGIN_URL = "https://suno.com/login"
    API_URL = "https://suno.com/api"
    
    def __init__(self):
        """Initialize the authenticator."""
        self.session = requests.Session()
        self.user_info = {}
        
        # Set up common headers to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        })
    
    def login(self, email, password):
        """
        Log in to Suno.com with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            tuple: (requests.Session, dict) - Authenticated session and user info
        """
        try:
            # First, get the login page to extract any needed tokens
            logger.info("Fetching login page")
            login_page = self.session.get(self.LOGIN_URL)
            login_page.raise_for_status()
            
            # Extract CSRF token or other required form fields
            soup = BeautifulSoup(login_page.text, 'html.parser')
            csrf_token = None
            
            # Look for hidden input fields that might contain CSRF token
            csrf_field = soup.find('input', {'name': 'csrf_token'}) or \
                         soup.find('input', {'name': '_csrf'}) or \
                         soup.find('meta', {'name': 'csrf-token'})
            
            if csrf_field:
                csrf_token = csrf_field.get('value', None) or csrf_field.get('content', None)
                logger.debug(f"Found CSRF token: {csrf_token}")
            
            # Extract any additional required fields
            form_data = {
                'email': email,
                'password': password,
            }
            
            if csrf_token:
                form_data['csrf_token'] = csrf_token
            
            # Look for the form action URL
            login_form = soup.find('form', {'id': 'login-form'}) or soup.find('form')
            form_action = self.LOGIN_URL
            
            if login_form and login_form.get('action'):
                form_action = urljoin(self.BASE_URL, login_form.get('action'))
                logger.debug(f"Found form action URL: {form_action}")
            
            # Try different login endpoints
            login_endpoints = [
                form_action,
                f"{self.API_URL}/auth/login",
                f"{self.API_URL}/login",
                f"{self.BASE_URL}/api/auth/login"
            ]
            
            logged_in = False
            
            for endpoint in login_endpoints:
                try:
                    logger.info(f"Attempting login with endpoint: {endpoint}")
                    
                    # Update headers for the login request
                    headers = {
                        'Content-Type': 'application/json',
                        'Referer': self.LOGIN_URL,
                        'Origin': self.BASE_URL,
                    }
                    
                    # Try login with JSON payload first
                    json_response = self.session.post(
                        endpoint, 
                        json=form_data,
                        headers=headers
                    )
                    
                    if json_response.status_code < 400:
                        logger.info("Login successful with JSON payload")
                        logged_in = True
                        break
                    
                    # If that fails, try with form data
                    form_response = self.session.post(
                        endpoint,
                        data=form_data,
                        headers={**headers, 'Content-Type': 'application/x-www-form-urlencoded'}
                    )
                    
                    if form_response.status_code < 400:
                        logger.info("Login successful with form data")
                        logged_in = True
                        break
                        
                except Exception as e:
                    logger.warning(f"Login attempt failed with endpoint {endpoint}: {e}")
                    continue
                    
            if not logged_in:
                logger.error("All login attempts failed")
                return None, {}
            
            # Check if we're actually logged in by visiting the profile page
            logger.info("Verifying login by checking profile")
            profile_response = self.session.get(f"{self.BASE_URL}/profile")
            
            if "login" in profile_response.url.lower():
                logger.error("Login verification failed - redirected to login page")
                return None, {}
            
            # Extract user info from the profile page
            self.user_info = self._extract_user_info(profile_response.text)
            
            if not self.user_info:
                logger.warning("Logged in but couldn't extract user info")
            
            return self.session, self.user_info
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return None, {}
    
    def _extract_user_info(self, page_content):
        """
        Extract user information from the profile page.
        
        Args:
            page_content: HTML content of the profile page
            
        Returns:
            dict: User information
        """
        user_info = {}
        
        try:
            # Try to find user info in embedded script tags (common pattern)
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Look for user data in script tags
            scripts = soup.find_all('script')
            
            for script in scripts:
                if not script.string:
                    continue
                    
                # Look for user data in common patterns
                user_data_patterns = [
                    r'window\.__USER__\s*=\s*({.*?});',
                    r'user\s*:\s*({.*?}),',
                    r'userData\s*=\s*({.*?});',
                    r'"user"\s*:\s*({.*?}),'
                ]
                
                for pattern in user_data_patterns:
                    matches = re.search(pattern, script.string, re.DOTALL)
                    if matches:
                        try:
                            user_data = json.loads(matches.group(1))
                            logger.debug(f"Found user data: {user_data}")
                            return user_data
                        except json.JSONDecodeError:
                            continue
            
            # If we can't find user info in scripts, look for it in the page content
            # Look for username
            username_element = soup.find('span', {'class': 'username'}) or \
                              soup.find('h1', {'class': 'profile-name'}) or \
                              soup.find('div', {'class': 'user-name'})
            
            if username_element:
                user_info['username'] = username_element.text.strip()
            
            # Look for user ID
            user_id_meta = soup.find('meta', {'name': 'user-id'}) or \
                          soup.find('div', {'data-user-id': True})
            
            if user_id_meta:
                user_info['id'] = user_id_meta.get('content') or user_id_meta.get('data-user-id')
            
        except Exception as e:
            logger.error(f"Error extracting user info: {e}")
        
        return user_info
