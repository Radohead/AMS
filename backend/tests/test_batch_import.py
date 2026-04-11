"""
批量导入模块测试

用例编号:
- TEST-IMP-001: test_import_template_download      - 下载导入模板
- TEST-IMP-002: test_import_assets_success         - 成功导入资产
- TEST-IMP-003: test_import_missing_required_field  - 缺少必填字段
- TEST-IMP-004: test_import_invalid_category        - 无效分类编码
- TEST-IMP-005: test_import_invalid_file_type       - 无效文件类型
- TEST-IMP-006: test_import_partial_success        - 部分成功（部分行失败）
"""
import pytest
from io import BytesIO
from openpyxl import Workbook


def make_excel_bytes(rows: list) -> bytes:
    """构建 Excel 文件字节数据"""
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def make_asset_headers() -> list:
    return [
        "资产名称", "分类编码", "资产类型", "品牌", "型号", "序列号",
        "购买日期", "购买价格", "保修截止", "部门编码", "存放位置",
        "数量", "单位", "描述", "备注",
    ]


class TestBatchImportTemplate:
    """导入模板下载测试"""

    def test_import_template_download(
        self, client, admin_user, test_category
    ):
        """TEST-IMP-001: 下载资产导入模板"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        response = client.get(
            "/api/assets/import/template",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith(
            "application/vnd.openxmlformats"
        )
        assert "attachment" in response.headers["content-disposition"]


class TestBatchImport:
    """批量导入功能测试"""

    def test_import_assets_success(
        self, client, admin_user, test_category
    ):
        """TEST-IMP-002: 成功导入多条资产"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 构造 Excel 数据：2条有效数据
        rows = [
            make_asset_headers(),
            ["导入资产A", "ELECTRONIC", "固定资产", "联想", "ThinkPad", "SN001", "2024-01-15", "5000", "2027-01-15", None, "A101", 1, "台", "测试导入", "备注A"],
            ["导入资产B", "ELECTRONIC", "fixed", "戴尔", "XPS15", "SN002", "2024-02-01", "8000", "", None, "B202", 1, "台", "", "备注B"],
        ]
        excel_bytes = make_excel_bytes(rows)

        response = client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("导入测试.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["success"] == 2
        assert data["failed"] == 0
        assert len(data["imported_assets"]) == 2
        assert data["imported_assets"][0]["name"] == "导入资产A"
        assert data["imported_assets"][1]["name"] == "导入资产B"

    def test_import_missing_required_field(
        self, client, admin_user, test_category
    ):
        """TEST-IMP-003: 缺少必填字段（资产名称）"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        rows = [
            make_asset_headers(),
            ["", "ELECTRONIC", "固定资产", "联想", "", "", "", "", "", "", "", 1, "", "", ""],
        ]
        excel_bytes = make_excel_bytes(rows)

        response = client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("缺少必填.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["success"] == 0
        assert data["failed"] == 1
        assert any(e["field"] == "name" for e in data["errors"])

    def test_import_invalid_category(
        self, client, admin_user, test_category
    ):
        """TEST-IMP-004: 无效的分类编码"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        rows = [
            make_asset_headers(),
            ["测试资产", "NOTEXIST", "固定资产", "", "", "", "", "", "", "", "", 1, "", "", ""],
        ]
        excel_bytes = make_excel_bytes(rows)

        response = client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("无效分类.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["failed"] == 1
        assert any(e["field"] == "category_code" for e in data["errors"])

    def test_import_invalid_file_type(
        self, client, admin_user, test_category
    ):
        """TEST-IMP-005: 上传无效文件类型"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        response = client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("data.txt", b"not an excel", "text/plain")},
        )
        assert response.status_code == 400
        assert "不支持的文件格式" in response.json()["detail"]

    def test_import_partial_success(
        self, client, admin_user, test_category
    ):
        """TEST-IMP-006: 部分成功（第一行有效，第二行分类无效）"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        rows = [
            make_asset_headers(),
            ["部分成功资产", "ELECTRONIC", "固定资产", "", "", "", "", "", "", "", "", 1, "", "", ""],
            ["失败资产", "INVALID_CODE", "固定资产", "", "", "", "", "", "", "", "", 1, "", "", ""],
        ]
        excel_bytes = make_excel_bytes(rows)

        response = client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("部分导入.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["success"] == 1
        assert data["failed"] == 1
        assert data["imported_assets"][0]["name"] == "部分成功资产"
        assert any(e["row"] == 2 for e in data["errors"])

    def test_import_without_permission(
        self, client, test_user
    ):
        """无资产创建权限的用户不能导入"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = login_resp.json()["access_token"]

        rows = [
            make_asset_headers(),
            ["无权限导入", "ELECTRONIC", "固定资产", "", "", "", "", "", "", "", "", 1, "", "", ""],
        ]
        excel_bytes = make_excel_bytes(rows)

        response = client.post(
            "/api/assets/import",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("无权限.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        assert response.status_code in (403, 401)
