import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ArtInstituteService:
    BASE_URL = "https://api.artic.edu/api/v1"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "TravelPlanner/1.0"
        })

    def search_artworks(self, query: str, limit: int = 10) -> Optional[Dict[Any, Any]]:
        """Search for artworks in the Art Institute collection"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/artworks/search",
                params={"q": query, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error searching artworks: {e}")
            return None

    def get_artwork(self, artwork_id: str) -> Optional[Dict[Any, Any]]:
        """Get a specific artwork by ID"""
        try:
            response = self.session.get(f"{self.BASE_URL}/artworks/{artwork_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching artwork {artwork_id}: {e}")
            return None

    def validate_place_exists(self, external_api_id: str) -> bool:
        """Validate that a place (artwork) exists in the Art Institute API"""
        try:
            response = self.session.get(f"{self.BASE_URL}/artworks/{external_api_id}")
            return response.status_code == 200
        except requests.RequestException:
            return False