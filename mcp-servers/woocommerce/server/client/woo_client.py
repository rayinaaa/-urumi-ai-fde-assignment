"""
Async WooCommerce REST API client with full error handling, pagination, and retry awareness.
"""
from typing import Any, Dict, List, Optional
import httpx
from server.config import settings

class WooCommerceAPIException(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details

class WooCommerceClient:
    def __init__(
        self,
        store_url: Optional[str] = None,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        verify_ssl: Optional[bool] = None,
    ):
        self.store_url = (store_url or settings.WOOCOMMERCE_STORE_URL).rstrip("/")
        self.base_url = f"{self.store_url}/wp-json/wc/v3"
        self.auth = (
            consumer_key or settings.WOOCOMMERCE_CONSUMER_KEY,
            consumer_secret or settings.WOOCOMMERCE_CONSUMER_SECRET,
        )
        self.verify_ssl = verify_ssl if verify_ssl is not None else settings.WOOCOMMERCE_VERIFY_SSL
        self.timeout = httpx.Timeout(20.0, connect=10.0)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Urumi-WooCommerce-MCP/1.0",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Clean params to remove None values
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}

        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    auth=self.auth,
                    headers=self._get_headers(),
                    params=clean_params if clean_params else None,
                    json=json_data,
                )
                
                # Check for HTTP errors
                if response.is_error:
                    try:
                        err_payload = response.json()
                        err_message = err_payload.get("message", response.text)
                    except Exception:
                        err_message = response.text
                    raise WooCommerceAPIException(
                        message=f"WooCommerce API error [{response.status_code}]: {err_message}",
                        status_code=response.status_code,
                        details=response.text,
                    )

                return response.json()
            except httpx.ConnectError as e:
                raise WooCommerceAPIException(f"Failed to connect to WooCommerce store at {self.store_url}: {str(e)}")
            except httpx.TimeoutException:
                raise WooCommerceAPIException(f"Timeout connecting to WooCommerce store ({url})")
            except WooCommerceAPIException:
                raise
            except Exception as e:
                raise WooCommerceAPIException(f"Unexpected error communicating with WooCommerce API: {str(e)}")

    # -------------------------------------------------------------
    # Products API
    # -------------------------------------------------------------
    async def list_products(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: str = "publish",
        min_price: Optional[str] = None,
        max_price: Optional[str] = None,
        stock_status: Optional[str] = None,
        sku: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch list of products from WooCommerce catalog."""
        params = {
            "page": page,
            "per_page": min(per_page, 100),
            "search": search,
            "category": category,
            "status": status,
            "min_price": min_price,
            "max_price": max_price,
            "stock_status": stock_status,
            "sku": sku,
        }
        return await self._request("GET", "products", params=params)

    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product in WooCommerce catalog."""
        return await self._request("POST", "products", json_data=product_data)

    # -------------------------------------------------------------
    # Orders API
    # -------------------------------------------------------------
    async def list_orders(
        self,
        page: int = 1,
        per_page: int = 10,
        status: Optional[str] = None,
        customer: Optional[int] = None,
        search: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch list of orders from WooCommerce store."""
        params = {
            "page": page,
            "per_page": min(per_page, 100),
            "status": status,
            "customer": customer,
            "search": search,
            "after": after,
            "before": before,
        }
        return await self._request("GET", "orders", params=params)

    async def get_order(self, order_id: int) -> Dict[str, Any]:
        """Fetch a specific order by ID."""
        return await self._request("GET", f"orders/{order_id}")

    async def update_order_status(self, order_id: int, status: str) -> Dict[str, Any]:
        """Update the status of an existing order."""
        return await self._request("PUT", f"orders/{order_id}", json_data={"status": status})
