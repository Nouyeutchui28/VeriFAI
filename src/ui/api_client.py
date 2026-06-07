import streamlit as st
import requests
import asyncio
import websockets
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

import os
from src.core.retry_utils import retry_callable, CircuitBreaker

# Allow overriding backend URLs via environment variables or Streamlit secrets
API_BASE_URL = os.environ.get("VERIFAI_API_BASE_URL") or "http://localhost:8001/api"
WS_BASE_URL = os.environ.get("VERIFAI_WS_BASE_URL") or "ws://localhost:8001"
INSFORGE_AUTH_URL = "https://inkgfmi3.us-east.insforge.app/api/auth"
INSFORGE_REST_URL = "https://inkgfmi3.us-east.insforge.app/rest/v1"

class VeriFAILLMAPIClient:
    """Client for VeriFAI LLM backend API."""

    def __init__(self):
        self.base_url = st.secrets.get("api_base_url", API_BASE_URL) if isinstance(st, type) else API_BASE_URL
        self.ws_url = st.secrets.get("ws_base_url", WS_BASE_URL) if isinstance(st, type) else WS_BASE_URL
        self.auth_url = INSFORGE_AUTH_URL
        self.rest_url = INSFORGE_REST_URL
        self.token = st.session_state.get("access_token")
        
        # Load InsForge project config
        self.project_config = self._load_project_config()
        self.api_key = self.project_config.get("api_key")
        self._cb = CircuitBreaker(fail_threshold=5, reset_timeout=30)
        self._session = requests.Session()

    def _request_with_retry(self, method: str, url: str, **kwargs):
        def _call():
            resp = self._session.request(method, url, **kwargs)
            # Raise for HTTP errors to trigger retry
            resp.raise_for_status()
            return resp

        return retry_callable(_call, retries=2, backoff_factor=0.5, exceptions=(Exception,), circuit=self._cb)

    def _load_project_config(self) -> Dict:
        """Load InsForge project configuration."""
        import json
        import os
        config_path = os.path.join(os.getcwd(), ".insforge", "project.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {}

    def get_headers(self):
        """Get request headers with auth token and API key."""
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # Authentication methods
    def login(self, oauth_provider: str, oauth_id: str, email: str, name: str, oauth_token: str, picture_url: str = None) -> Dict:
        """Login with OAuth."""
        try:
            resp = self._request_with_retry("POST", f"{self.base_url}/auth/login", json={
                    "oauth_provider": oauth_provider,
                    "oauth_id": oauth_id,
                    "email": email,
                    "name": name,
                    "oauth_token": oauth_token,
                    "picture_url": picture_url
                })
            return resp.json()
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {"error": str(e)}

    def refresh_token(self, refresh_token: str) -> Dict:
        """Refresh access token."""
        try:
            resp = self._request_with_retry("POST", f"{self.base_url}/auth/refresh", json={"refresh_token": refresh_token})
            return resp.json()
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return {"error": str(e)}

    # Scan methods
    def submit_scan(self, project_name: str = None, repo_url: str = None) -> Dict:
        """Submit a new scan."""
        try:
            resp = self._request_with_retry("POST", f"{self.base_url}/scans/submit", json={"project_name": project_name, "repo_url": repo_url}, headers=self.get_headers())
            return resp.json()
        except Exception as e:
            logger.error(f"Submit scan error: {str(e)}")
            return {"error": str(e)}

    def get_scan(self, scan_id: str) -> Dict:
        """Get scan details."""
        try:
            resp = self._request_with_retry("GET", f"{self.base_url}/scans/{scan_id}", headers=self.get_headers())
            return resp.json()
        except Exception as e:
            logger.error(f"Get scan error: {str(e)}")
            return {"error": str(e)}

    def get_scan_history(self, limit: int = 50) -> Dict:
        """Get user's scan history."""
        try:
            resp = self._request_with_retry("GET", f"{self.base_url}/scans/history?limit={limit}", headers=self.get_headers())
            return resp.json()
        except Exception as e:
            # Handle connection errors gracefully with a helpful message
            logger.error(f"Get history error: {str(e)}")
            err_msg = str(e)
            if "Connection refused" in err_msg or "Failed to establish a new connection" in err_msg:
                return {"error": "Backend unreachable. Is the backend server running at {}?".format(self.base_url)}
            return {"error": err_msg}

    def update_scan_status(self, scan_id: str, status: str, **kwargs) -> Dict:
        """Update scan status."""
        try:
            resp = self._request_with_retry("PATCH", f"{self.base_url}/scans/{scan_id}", json={"status": status, **kwargs}, headers=self.get_headers())
            return resp.json()
        except Exception as e:
            logger.error(f"Update scan error: {str(e)}")
            return {"error": str(e)}

    # Result methods
    def save_results(self, scan_id: str, code_snippet: str = None, semgrep_json: dict = None,
                    llm_analysis: str = None, patches: str = None, severity_count: dict = None) -> Dict:
        """Save analysis results."""
        try:
            resp = self._request_with_retry("POST", f"{self.base_url}/results/{scan_id}", json={
                    "scan_id": scan_id,
                    "code_snippet": code_snippet,
                    "semgrep_json": semgrep_json,
                    "llm_analysis": llm_analysis,
                    "patches": patches,
                    "severity_count": severity_count
                }, headers=self.get_headers())
            return resp.json()
        except Exception as e:
            logger.error(f"Save results error: {str(e)}")
            return {"error": str(e)}

    def get_results(self, scan_id: str) -> Dict:
        """Get analysis results."""
        try:
            resp = self._request_with_retry("GET", f"{self.base_url}/results/{scan_id}", headers=self.get_headers())
            return resp.json()
        except Exception as e:
            logger.error(f"Get results error: {str(e)}")
            return {"error": str(e)}

    # Chat methods
    def save_message(self, scan_id: str, role: str, content: str) -> Dict:
        """Save chat message."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/",
                json={"scan_id": scan_id, "role": role, "content": content},
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Save message error: {str(e)}")
            return {"error": str(e)}

    def get_chat_history(self, scan_id: str) -> Dict:
        """Get chat history."""
        try:
            response = requests.get(
                f"{self.base_url}/chat/{scan_id}",
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get chat history error: {str(e)}")
            return {"error": str(e)}

    # WebSocket methods
    async def connect_scan_updates(self, scan_id: str, callback):
        """Connect to WebSocket for real-time scan updates."""
        try:
            uri = f"{self.ws_url}/ws/scan/{scan_id}"
            async with websockets.connect(uri) as websocket:
                # Send initial ping
                await websocket.send(json.dumps({"type": "ping"}))

                # Listen for updates
                async for message in websocket:
                    data = json.loads(message)
                    await callback(data)
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")

    # InsForge Auth methods
    def signin(self, email: str, password: str) -> Dict:
        """Sign in with email and password via InsForge."""
        try:
            response = requests.post(
                f"{self.auth_url}/sessions?client_type=server",
                json={"email": email, "password": password},
                headers={"apikey": self.api_key, "Content-Type": "application/json"},
                timeout=15
            )
            if not response.ok:
                try:
                    return response.json()
                except:
                    return {"error": response.text}
            return response.json()
        except Exception as e:
            logger.error(f"Signin error: {str(e)}")
            return {"error": str(e)}

    def signup(self, email: str, password: str, name: str = None) -> Dict:
        """Sign up with email and password via InsForge."""
        try:
            # Only include non-None values
            data = {"email": email, "password": password}
            if name:
                data["name"] = name
                
            response = requests.post(
                f"{self.auth_url}/users?client_type=server",
                json=data,
                headers={"apikey": self.api_key, "Content-Type": "application/json"},
                timeout=15
            )
            if not response.ok:
                try:
                    return response.json()
                except:
                    return {"error": response.text}
            return response.json()
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            return {"error": str(e)}

    def verify_token_insforge(self, email: str, otp: str) -> Dict:
        """Verify email with InsForge using OTP code."""
        try:
            response = requests.post(
                f"{self.auth_url}/email/verify?client_type=server",
                json={"email": email, "otp": otp},
                headers={"apikey": self.api_key, "Content-Type": "application/json"},
                timeout=15
            )
            if not response.ok:
                try:
                    return response.json()
                except:
                    return {"error": response.text}
            return response.json()
        except Exception as e:
            logger.error(f"Verify token error: {str(e)}")
            return {"error": str(e)}

    # InsForge Database methods
    def save_scan_insforge(self, data: Dict) -> Dict:
        """Save a scan record to InsForge Database."""
        try:
            response = requests.post(
                f"{self.rest_url}/scans",
                json=data,
                headers={
                    "apikey": self.api_key,
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                },
                timeout=15
            )
            if not response.ok:
                return {"error": response.text}
            return response.json()
        except Exception as e:
            logger.error(f"DB Save Scan error: {str(e)}")
            return {"error": str(e)}

    def save_result_insforge(self, data: Dict) -> Dict:
        """Save analysis results to InsForge Database."""
        try:
            response = requests.post(
                f"{self.rest_url}/results",
                json=data,
                headers={
                    "apikey": self.api_key,
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                },
                timeout=15
            )
            if not response.ok:
                return {"error": response.text}
            return response.json()
        except Exception as e:
            logger.error(f"DB Save Result error: {str(e)}")
            return {"error": str(e)}

    def update_result_fixed_code_insforge(self, result_id: str, fixed_code: str) -> Dict:
        """Update an existing result with the autofixed code."""
        try:
            response = requests.patch(
                f"{self.rest_url}/results?id=eq.{result_id}",
                json={"fixed_code": fixed_code[:10000]}, # Store up to 10k chars
                headers={
                    "apikey": self.api_key,
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation"
                },
                timeout=15
            )
            if not response.ok:
                return {"error": response.text}
            return response.json()
        except Exception as e:
            logger.error(f"DB Update Result error: {str(e)}")
            return {"error": str(e)}

    # Admin Management methods
    def get_all_users_insforge(self) -> Dict:
        """Fetch all users from InsForge (Admin)."""
        try:
            response = requests.get(
                f"{self.auth_url}/users",
                headers={
                    "apikey": self.api_key,
                    "Authorization": f"Bearer {self.api_key}", # Using API key as admin token
                    "Content-Type": "application/json"
                }
            )
            if not response.ok:
                return {"error": response.text}
            return response.json()
        except Exception as e:
            logger.error(f"Get all users error: {str(e)}")
            return {"error": str(e)}

    def get_all_scans_insforge(self) -> Dict:
        """Fetch all scans from InsForge Database (Admin)."""
        try:
            response = requests.get(
                f"{self.rest_url}/scans",
                headers={
                    "apikey": self.api_key,
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=15
            )
            if not response.ok:
                return {"error": response.text}
            return response.json()
        except Exception as e:
            logger.error(f"Get all scans error: {str(e)}")
            return {"error": str(e)}

    def get_summary_stats_insforge(self) -> Dict:
        """Fetch summary statistics for the dashboard using real data."""
        try:
            user_id = st.session_state.user_info.get("id")
            if not user_id:
                return {"total_scans": 0, "vulnerabilities": 0, "fixed_issues": 0, "security_score": 100}

            # Fetch user's scans
            response = requests.get(
                f"{self.rest_url}/scans?user_id=eq.{user_id}",
                headers={
                    "apikey": self.api_key,
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                timeout=15
            )
            scans = response.json() if response.ok else []
            
            # Fetch user's results by joining with scans
            # InsForge (PostgREST) supports resource embedding (joins)
            response = requests.get(
                f"{self.rest_url}/results?scans.user_id=eq.{user_id}&select=*,scans!inner(user_id)",
                headers={
                    "apikey": self.api_key,
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                timeout=15
            )
            results = response.json() if response.ok else []
            
            total_scans = len(scans)
            total_vulns = 0
            total_fixed = 0
            
            for res in results:
                sc = res.get("severity_count", {})
                if isinstance(sc, dict):
                    total_vulns += sum(sc.values())
                if res.get("fixed_code"):
                    total_fixed += 1
            
            # Calculate a basic security score
            score = 100
            if total_scans > 0:
                # Deduct points for vulnerabilities, weighted by severity if possible
                # Simple version: score = max(0, 100 - (total_vulns * 2) + (total_fixed * 3))
                score = max(0, min(100, 100 - (total_vulns - total_fixed)))

            return {
                "total_scans": total_scans,
                "vulnerabilities": total_vulns,
                "fixed_issues": total_fixed,
                "security_score": score
            }
        except Exception as e:
            logger.error(f"Get stats error: {str(e)}")
            return {"total_scans": 0, "vulnerabilities": 0, "fixed_issues": 0, "security_score": 100}

    def get_severity_stats_insforge(self) -> Dict:
        """Fetch severity distribution for charts."""
        try:
            user_id = st.session_state.user_info.get("id")
            if not user_id:
                return {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

            response = requests.get(
                f"{self.rest_url}/results?scans.user_id=eq.{user_id}&select=*,scans!inner(user_id)",
                headers={
                    "apikey": self.api_key,
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                timeout=15
            )
            results = response.json() if response.ok else []
            
            stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for res in results:
                sc = res.get("severity_count", {})
                if isinstance(sc, dict):
                    for sev, count in sc.items():
                        s = sev.lower()
                        if s in stats:
                            stats[s] += count
            
            return {k.capitalize(): v for k, v in stats.items()}
        except Exception as e:
            logger.error(f"Get severity stats error: {str(e)}")
            return {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

def get_api_client() -> VeriFAILLMAPIClient:
    """Get API client instance."""
    return VeriFAILLMAPIClient()
