"""
自定义字段模块测试

用例编号:
- TEST-CF-001: test_create_text_field           - 创建文本字段
- TEST-CF-002: test_create_select_field         - 创建下拉字段
- TEST-CF-003: test_get_category_fields        - 获取分类字段列表
- TEST-CF-004: test_update_field                - 更新字段
- TEST-CF-005: test_delete_field                - 删除字段
- TEST-CF-006: test_batch_create_fields         - 批量创建字段
- TEST-CF-007: test_invalid_field_type          - 无效字段类型
- TEST-CF-008: test_duplicate_field_name        - 重复字段名
- TEST-CF-009: test_get_templates              - 获取字段模板
- TEST-CF-010: test_apply_template             - 应用模板到分类
"""
import pytest


class TestCustomField:
    """自定义字段功能测试"""

    def test_create_text_field(
        self, client, admin_user, test_category
    ):
        """TEST-CF-001: 创建文本类型的自定义字段"""
        # 登录
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 创建字段
        response = client.post(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "color",
                "field_label": "颜色",
                "field_type": "text",
                "placeholder": "请输入颜色",
                "required": False,
                "sort_order": 1
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "color"
        assert data["field_label"] == "颜色"
        assert data["field_type"] == "text"
        assert data["category_id"] == test_category.id

    def test_create_select_field(
        self, client, admin_user, test_category
    ):
        """TEST-CF-002: 创建下拉类型的自定义字段"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 创建下拉字段
        response = client.post(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "size",
                "field_label": "尺寸",
                "field_type": "select",
                "options": ["S", "M", "L", "XL", "XXL"],
                "required": True,
                "sort_order": 2
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "size"
        assert data["field_type"] == "select"
        assert data["options"] == ["S", "M", "L", "XL", "XXL"]
        assert data["required"] == True

    def test_get_category_fields(
        self, client, admin_user, test_category
    ):
        """TEST-CF-003: 获取分类的自定义字段列表"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 先创建几个字段
        for field_name in ["field_a", "field_b"]:
            client.post(
                f"/api/custom-fields/category/{test_category.id}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "field_name": field_name,
                    "field_label": f"字段{field_name}",
                    "field_type": "text",
                    "sort_order": 1
                }
            )

        # 获取字段列表
        response = client.get(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        # 验证字段按 sort_order 排序
        for i in range(len(data) - 1):
            assert data[i]["sort_order"] <= data[i + 1]["sort_order"]

    def test_update_field(
        self, client, admin_user, test_category
    ):
        """TEST-CF-004: 更新自定义字段"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 创建字段
        create_resp = client.post(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "update_test",
                "field_label": "测试字段",
                "field_type": "text",
                "required": False
            }
        )
        field_id = create_resp.json()["id"]

        # 更新字段
        response = client.put(
            f"/api/custom-fields/{field_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_label": "更新后的字段",
                "required": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["field_label"] == "更新后的字段"
        assert data["required"] == True
        assert data["field_name"] == "update_test"  # 未修改

    def test_delete_field(
        self, client, admin_user, test_category
    ):
        """TEST-CF-005: 删除自定义字段"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 创建字段
        create_resp = client.post(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "to_delete",
                "field_label": "待删除字段",
                "field_type": "text"
            }
        )
        field_id = create_resp.json()["id"]

        # 删除字段
        response = client.delete(
            f"/api/custom-fields/{field_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "字段已删除"

        # 验证字段已删除
        get_resp = client.get(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        fields = get_resp.json()
        assert not any(f["id"] == field_id for f in fields)

    def test_batch_create_fields(
        self, client, admin_user, test_category
    ):
        """TEST-CF-006: 批量创建自定义字段"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 批量创建
        response = client.post(
            f"/api/custom-fields/category/{test_category.id}/batch",
            headers={"Authorization": f"Bearer {token}"},
            json=[
                {
                    "field_name": "batch_field_1",
                    "field_label": "批量字段1",
                    "field_type": "text"
                },
                {
                    "field_name": "batch_field_2",
                    "field_label": "批量字段2",
                    "field_type": "select",
                    "options": ["选项1", "选项2"]
                }
            ]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 2
        assert len(data["fields"]) == 2

    def test_invalid_field_type(
        self, client, admin_user, test_category
    ):
        """TEST-CF-007: 无效的字段类型"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        response = client.post(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "invalid_type",
                "field_label": "无效类型字段",
                "field_type": "invalid_type_here"
            }
        )

        assert response.status_code == 400
        assert "无效的字段类型" in response.json()["detail"]

    def test_duplicate_field_name(
        self, client, admin_user, test_category
    ):
        """TEST-CF-008: 重复的字段名"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 创建第一个字段
        client.post(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "duplicate",
                "field_label": "第一个",
                "field_type": "text"
            }
        )

        # 尝试创建同名字段
        response = client.post(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "duplicate",
                "field_label": "第二个",
                "field_type": "text"
            }
        )

        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]

    def test_select_without_options(
        self, client, admin_user, test_category
    ):
        """TEST-CF-009: 下拉字段未提供选项"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        response = client.post(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "no_options",
                "field_label": "无选项下拉",
                "field_type": "select"
                # 缺少 options
            }
        )

        assert response.status_code == 400
        assert "需要提供 options" in response.json()["detail"]

    def test_get_templates(
        self, client, admin_user
    ):
        """TEST-CF-010: 获取字段模板列表"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        response = client.get(
            "/api/custom-fields/templates",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_field_not_found(
        self, client, admin_user
    ):
        """TEST-CF-011: 字段不存在"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        response = client.put(
            "/api/custom-fields/99999",
            headers={"Authorization": f"Bearer {token}"},
            json={"field_label": "更新"}
        )

        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]

    def test_without_permission(
        self, client, test_user, test_category
    ):
        """TEST-CF-012: 无资产更新权限"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = login_resp.json()["access_token"]

        response = client.post(
            f"/api/custom-fields/category/{test_category.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "no_perm",
                "field_label": "无权限字段",
                "field_type": "text"
            }
        )

        assert response.status_code in (403, 401)
