import streamlit as st
import requests
import asyncio
import websockets
import json
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

import os
from ..core.retry_utils import retry_callable, CircuitBreaker

# Allow overriding backend URLs via environment variables or Streamlit secrets
API_BASE_URL = os.environ.get("API_BASE_URL") or "http://localhost:8000/api"
WS_BASE_URL = os.environ.get("VERIFAI_WS_BASE_URL") or "ws://localhost:8000"

class VeriFAILLMAPIClient:
    """Client for VeriFAI LLM backend API."""

    def __init__(self):
        self.base_url = st.secrets.get("api_base_url", API_BASE_URL) if isinstance(st, type) else API_BASE_URL
        self.ws_url = st.secrets.get("ws_base_url", WS_BASE_URL) if isinstance(st, type) else WS_BASE_URL
        self.token = st.session_state.get("access_token")
        
        self._cb = CircuitBreaker(fail_threshold=5, reset_timeout=30)
        self._session = requests.Session()

    def _request_with_retry(self, method: str, url: str, **kwargs):
        def _call():
            resp = self._session.request(method, url, **kwargs)
            # Raise for HTTP errors to trigger retry
            resp.raise_for_status()
            return resp

        return retry_callable(_call, retries=2, backoff_factor=0.5, exceptions=(Exception,), circuit=self._cb)

    def get_headers(self):
        """Get request headers with auth token."""
        headers = {
            "Content-Type": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # Authentication methods
    def signin(self, email: str, password: str) -> Dict:
        """Simulate signin using local backend OAuth login."""
        name = email.split('@')[0].capitalize()
        # Mock OAuth payload using the email
        return self.login(
            oauth_provider="local",
            oauth_id=email,
            email=email,
            name=name,
            oauth_token="mock_token_123"
        )
        
    def signup(self, email: str, password: str, name: str = None) -> Dict:
        """Simulate signup using local backend OAuth login."""
        if not name:
            name = email.split('@')[0].capitalize()
        return self.login(
            oauth_provider="local",
            oauth_id=email,
            email=email,
            name=name,
            oauth_token="mock_token_123"
        )

    def verify_token_insforge(self, email: str, otp: str) -> Dict:
        """Mock OTP verification."""
        name = email.split('@')[0].capitalize()
        return self.login("local", email, email, name, "mock_token_123")

    def recover_password(self, email: str) -> Dict:
        """Mock password recovery."""
        return {"message": "Success"}

    def reset_password(self, email: str, otp: str, new_password: str) -> Dict:
        """Mock password reset."""
        return {"message": "Success"}

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
            # Map FastAPI TokenResponse to the structure the frontend expects
            data = resp.json()
            if "access_token" in data:
                return {
                    "accessToken": data["access_token"],
                    "user": data["user"]
                }
            return data
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

    def get_summary_stats(self) -> Dict:
        """Fetch summary statistics for the dashboard using local DB."""
        try:
            # We fetch all scans and iterate to build summary stats natively.
            scans = self.get_scan_history(limit=100)
            if isinstance(scans, dict) and "error" in scans:
                return {"total_scans": 0, "vulnerabilities": 0, "fixed_issues": 0, "security_score": 100}

            total_scans = len(scans)
            total_vulns = 0
            total_fixed = 0

            for scan in scans:
                res = self.get_results(scan.get("id"))
                if not isinstance(res, dict) or "error" in res:
                    continue
                
                sc = res.get("severity_count", {})
                if isinstance(sc, dict):
                    total_vulns += sum(sc.values())
                if res.get("patches"):
                    total_fixed += 1

            score = 100
            if total_scans > 0:
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

    def get_severity_stats(self) -> Dict:
        """Fetch severity distribution for charts using local DB."""
        try:
            scans = self.get_scan_history(limit=100)
            if isinstance(scans, dict) and "error" in scans:
                return {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

            stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for scan in scans:
                res = self.get_results(scan.get("id"))
                if not isinstance(res, dict) or "error" in res:
                    continue
                
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
