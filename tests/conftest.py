"""
Pytest fixtures and environment setup for Urumi AI Platform tests.
"""
import pytest
import os
import sys

# Add project roots to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "gateway")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp-servers", "woocommerce")))
