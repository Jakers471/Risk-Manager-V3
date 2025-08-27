"""
Unit tests for ProjectXClient.

Tests endpoint path/payload and 401→retry path with mocked responses.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Dict, Any

from risk_manager_v2.core.client import ProjectXClient, ProjectXError
from risk_manager_v2.core.config import ConfigStore
from risk_manager_v2.core.auth import AuthManager


class TestProjectXClient(unittest.TestCase):
    """Test cases for ProjectXClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock(spec=ConfigStore)
        self.config.get_api_url.return_value = "https://gateway-api-demo.s2f.projectx.com"
        self.config.get.return_value = 30  # timeout
        
        self.auth = Mock(spec=AuthManager)
        self.session = Mock()
        self.auth.get_session.return_value = self.session
        
        self.client = ProjectXClient(self.config, self.auth)
    
    def test_place_order_correct_payload(self):
        """Test place order endpoint with correct payload."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "orderId": 12345,
            "success": True,
            "errorCode": 0,
            "errorMessage": None
        }
        self.session.post.return_value = mock_response
        
        # Call the method
        result = self.client.place_order(
            account_id="465",
            contract_id="CON.F.US.DA6.M25",
            order_type=2,  # Market order
            side=1,        # Ask (sell)
            size=1,
            limit_price=None,
            stop_price=None,
            trail_price=None
        )
        
        # Verify the request was made with correct payload
        self.session.post.assert_called_once()
        call_args = self.session.post.call_args
        
        # Check URL
        self.assertEqual(
            call_args[0][0],
            "https://gateway-api-demo.s2f.projectx.com/api/Order/place"
        )
        
        # Check payload
        expected_payload = {
            "accountId": 465,
            "contractId": "CON.F.US.DA6.M25",
            "type": 2,
            "side": 1,
            "size": 1,
            "limitPrice": None,
            "stopPrice": None,
            "trailPrice": None,
            "customTag": None,
            "linkedOrderId": None
        }
        actual_payload = call_args[1]['json']
        self.assertEqual(actual_payload, expected_payload)
        
        # Check result
        self.assertEqual(result["orderId"], 12345)
        self.assertTrue(result["success"])
    
    def test_401_retry_flow(self):
        """Test 401→validate→reauth→retry flow."""
        # Mock first response: 401 Unauthorized
        mock_401_response = Mock()
        mock_401_response.status_code = 401
        mock_401_response.text = "Unauthorized"
        
        # Mock second response: 200 OK after reauth
        mock_200_response = Mock()
        mock_200_response.status_code = 200
        mock_200_response.json.return_value = {
            "success": True,
            "positions": []
        }
        
        # Configure session to return 401 first, then 200
        self.session.post.side_effect = [mock_401_response, mock_200_response]
        
        # Mock auth flow
        self.auth.validate_token.return_value = False  # First validation fails
        self.auth.refresh_token.return_value = True    # Reauth succeeds
        
        # Call the method
        result = self.client.get_open_positions("536")
        
        # Verify auth flow was called
        self.auth.validate_token.assert_called_once()
        self.auth.refresh_token.assert_called_once()
        
        # Verify request was made twice (original + retry)
        self.assertEqual(self.session.post.call_count, 2)
        
        # Verify result
        self.assertEqual(result, [])
    
    def test_rate_limit_bars_endpoint(self):
        """Test that bars endpoint uses correct rate limit bucket."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "bars": []
        }
        self.session.post.return_value = mock_response
        
        # Call market data bars endpoint
        result = self.client.get_market_data_bars(
            contract_id="CON.F.US.RTY.Z24",
            start_time="2024-12-01T00:00:00Z",
            end_time="2024-12-31T21:00:00Z",
            unit=3,
            unit_number=1
        )
        
        # Verify the request was made to correct endpoint
        call_args = self.session.post.call_args
        self.assertEqual(
            call_args[0][0],
            "https://gateway-api-demo.s2f.projectx.com/api/History/retrieveBars"
        )
        
        # Verify result
        self.assertEqual(result, [])
    
    def test_position_search_endpoint(self):
        """Test position search endpoint."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "positions": [
                {
                    "accountId": 536,
                    "contractId": "CON.F.US.GMET.J25",
                    "size": 5,
                    "avgPrice": 1604.50
                }
            ]
        }
        self.session.post.return_value = mock_response
        
        # Call the method
        result = self.client.get_open_positions("536")
        
        # Verify the request was made with correct payload
        call_args = self.session.post.call_args
        self.assertEqual(
            call_args[0][0],
            "https://gateway-api-demo.s2f.projectx.com/api/Position/search"
        )
        
        expected_payload = {"accountId": 536}
        actual_payload = call_args[1]['json']
        self.assertEqual(actual_payload, expected_payload)
        
        # Verify result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["contractId"], "CON.F.US.GMET.J25")
        self.assertEqual(result[0]["size"], 5)


if __name__ == "__main__":
    unittest.main()
