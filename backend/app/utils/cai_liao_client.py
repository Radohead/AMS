"""
草料二维码 API 客户端

文档: https://www.baidu.com/search.html?q=草料二维码API
"""
import httpx
from typing import Optional, Dict, Any, List
from app.core.config import settings


class CaiLiaoClient:
    """草料二维码 API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'CAI_LIAO_API_KEY', None)
        self.base_url = "https://v2.api.haozhukeji.com"  # 草料API地址
        self.timeout = 30

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_qrcode(
        self,
        qrcode_name: str,
        content: str,
        template_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建二维码

        Args:
            qrcode_name: 二维码名称
            content: 二维码内容
            template_id: 模板ID (可选)
            extra_data: 额外数据 (可选)

        Returns:
            创建结果，包含 qrcode_id 和 url
        """
        if not self.api_key:
            raise ValueError("未配置草料API密钥")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/qrcode/add",
                headers=self._get_headers(),
                json={
                    "qrcode_name": qrcode_name,
                    "content": content,
                    "template_id": template_id,
                    "extra_data": extra_data
                }
            )

            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.text}")

            data = response.json()

            if data.get("errcode") != 0:
                raise Exception(f"创建二维码失败: {data.get('errmsg', '未知错误')}")

            return {
                "qrcode_id": data.get("data", {}).get("qrcode_id"),
                "url": data.get("data", {}).get("url"),
                "qrcode_url": data.get("data", {}).get("qrcode_url")
            }

    async def batch_create_qrcodes(
        self,
        qrcodes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量创建二维码

        Args:
            qrcodes: 二维码列表，每个包含 name 和 content

        Returns:
            批量创建结果
        """
        if not self.api_key:
            raise ValueError("未配置草料API密钥")

        async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
            response = await client.post(
                f"{self.base_url}/qrcode/batch_add",
                headers=self._get_headers(),
                json={"qrcodes": qrcodes}
            )

            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.text}")

            data = response.json()

            return {
                "success": data.get("errcode") == 0,
                "total": len(qrcodes),
                "data": data.get("data", [])
            }

    async def get_qrcode_info(self, qrcode_id: str) -> Dict[str, Any]:
        """
        获取二维码信息

        Args:
            qrcode_id: 二维码ID

        Returns:
            二维码详细信息
        """
        if not self.api_key:
            raise ValueError("未配置草料API密钥")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/qrcode/info",
                headers=self._get_headers(),
                params={"qrcode_id": qrcode_id}
            )

            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.text}")

            data = response.json()

            if data.get("errcode") != 0:
                raise Exception(f"获取二维码失败: {data.get('errmsg', '未知错误')}")

            return data.get("data", {})

    async def get_qrcode_stats(self, qrcode_id: str) -> Dict[str, Any]:
        """
        获取二维码统计信息

        Args:
            qrcode_id: 二维码ID

        Returns:
            扫描统计信息
        """
        if not self.api_key:
            raise ValueError("未配置草料API密钥")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/qrcode/stats",
                headers=self._get_headers(),
                params={"qrcode_id": qrcode_id}
            )

            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.text}")

            data = response.json()

            if data.get("errcode") != 0:
                raise Exception(f"获取统计失败: {data.get('errmsg', '未知错误')}")

            return data.get("data", {})

    async def get_scan_logs(
        self,
        qrcode_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        获取扫描日志

        Args:
            qrcode_id: 二维码ID
            page: 页码
            page_size: 每页数量

        Returns:
            扫描日志列表
        """
        if not self.api_key:
            raise ValueError("未配置草料API密钥")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/qrcode/scan_logs",
                headers=self._get_headers(),
                params={
                    "qrcode_id": qrcode_id,
                    "page": page,
                    "page_size": page_size
                }
            )

            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.text}")

            data = response.json()

            return {
                "total": data.get("data", {}).get("total", 0),
                "logs": data.get("data", {}).get("list", [])
            }

    async def update_qrcode(
        self,
        qrcode_id: str,
        content: Optional[str] = None,
        qrcode_name: Optional[str] = None
    ) -> bool:
        """
        更新二维码内容

        Args:
            qrcode_id: 二维码ID
            content: 新的二维码内容
            qrcode_name: 新的名称

        Returns:
            是否成功
        """
        if not self.api_key:
            raise ValueError("未配置草料API密钥")

        update_data = {}
        if content:
            update_data["content"] = content
        if qrcode_name:
            update_data["qrcode_name"] = qrcode_name

        if not update_data:
            return True

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/qrcode/update",
                headers=self._get_headers(),
                json={
                    "qrcode_id": qrcode_id,
                    **update_data
                }
            )

            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.text}")

            data = response.json()

            return data.get("errcode") == 0

    async def delete_qrcode(self, qrcode_id: str) -> bool:
        """
        删除二维码

        Args:
            qrcode_id: 二维码ID

        Returns:
            是否成功
        """
        if not self.api_key:
            raise ValueError("未配置草料API密钥")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/qrcode/delete",
                headers=self._get_headers(),
                json={"qrcode_id": qrcode_id}
            )

            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.text}")

            data = response.json()

            return data.get("errcode") == 0

    async def download_qrcode(
        self,
        qrcode_id: str,
        format: str = "png",
        size: int = 300
    ) -> bytes:
        """
        下载二维码图片

        Args:
            qrcode_id: 二维码ID
            format: 图片格式 (png/jpg/svg)
            size: 图片尺寸

        Returns:
            图片二进制数据
        """
        if not self.api_key:
            raise ValueError("未配置草料API密钥")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/qrcode/download",
                headers=self._get_headers(),
                params={
                    "qrcode_id": qrcode_id,
                    "format": format,
                    "size": size
                }
            )

            if response.status_code != 200:
                raise Exception(f"下载失败: {response.text}")

            return response.content


# 全局客户端实例
_cailiao_client = None


def get_cailiao_client() -> CaiLiaoClient:
    """获取草料客户端实例"""
    global _cailiao_client
    if _cailiao_client is None:
        _cailiao_client = CaiLiaoClient()
    return _cailiao_client
