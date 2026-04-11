"""
工作流字段配置模块测试

用例编号:
- TEST-WF-001: test_create_workflow_field        - 创建工作流字段
- TEST-WF-002: test_get_workflow_fields        - 获取工作流字段列表
- TEST-WF-003: test_update_workflow_field       - 更新工作流字段
- TEST-WF-004: test_delete_workflow_field      - 删除工作流字段
- TEST-WF-005: test_batch_create_fields        - 批量创建字段
- TEST-WF-006: test_invalid_workflow_type      - 无效工作流类型
- TEST-WF-007: test_list_all_workflows         - 获取所有工作流配置
- TEST-WF-008: test_reset_workflow_fields      - 重置工作流字段
- TEST-WF-009: test_duplicate_field_name       - 重复字段名
- TEST-WF-010: test_select_without_options     - 下拉字段未提供选项
"""
import pytest


class TestWorkflowField:
    """工作流字段配置功能测试"""

    def test_create_workflow_field(
        self, client, admin_user
    ):
        """TEST-WF-001: 为分配工作流创建字段"""
        # 登录
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 创建工作流字段
        response = client.post(
            "/api/workflow-fields/assign",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "assign_purpose",
                "field_label": "领用用途",
                "field_type": "text",
                "required": True,
                "sort_order": 1
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "assign_purpose"
        assert data["field_label"] == "领用用途"
        assert data["workflow_type"] == "assign"
        assert data["required"] == True

    def test_create_select_workflow_field(
        self, client, admin_user
    ):
        """TEST-WF-002: 创建下拉类型工作流字段"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 创建下拉字段
        response = client.post(
            "/api/workflow-fields/repair",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "repair_priority",
                "field_label": "维修优先级",
                "field_type": "select",
                "options": ["低", "中", "高", "紧急"],
                "required": True,
                "default_value": "中"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["field_name"] == "repair_priority"
        assert data["field_type"] == "select"
        assert data["options"] == ["低", "中", "高", "紧急"]
        assert data["default_value"] == "中"

    def test_get_workflow_fields(
        self, client, admin_user
    ):
        """TEST-WF-003: 获取工作流的字段列表"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 先创建几个字段
        for field_name in ["wf_field_a", "wf_field_b"]:
            client.post(
                "/api/workflow-fields/transfer",
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
            "/api/workflow-fields/transfer",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_update_workflow_field(
        self, client, admin_user
    ):
        """TEST-WF-004: 更新工作流字段"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 创建字段
        create_resp = client.post(
            "/api/workflow-fields/scrap",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "scrap_test",
                "field_label": "测试字段",
                "field_type": "text",
                "required": False
            }
        )
        field_id = create_resp.json()["id"]

        # 更新字段
        response = client.put(
            f"/api/workflow-fields/{field_id}",
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
        assert data["field_name"] == "scrap_test"  # 未修改

    def test_delete_workflow_field(
        self, client, admin_user
    ):
        """TEST-WF-005: 删除工作流字段"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 创建字段
        create_resp = client.post(
            "/api/workflow-fields/check",
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
            f"/api/workflow-fields/{field_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "字段已删除"

    def test_batch_create_fields(
        self, client, admin_user
    ):
        """TEST-WF-006: 批量创建工作流字段"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 批量创建
        response = client.post(
            "/api/workflow-fields/return/batch",
            headers={"Authorization": f"Bearer {token}"},
            json=[
                {
                    "field_name": "return_reason",
                    "field_label": "退库原因",
                    "field_type": "textarea",
                    "required": True
                },
                {
                    "field_name": "return_condition",
                    "field_label": "资产状况",
                    "field_type": "select",
                    "options": ["良好", "轻微损坏", "严重损坏"]
                }
            ]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["created"] == 2
        assert len(data["fields"]) == 2

    def test_invalid_workflow_type(
        self, client, admin_user
    ):
        """TEST-WF-007: 无效的工作流类型"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        response = client.post(
            "/api/workflow-fields/invalid_type",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "test",
                "field_label": "测试",
                "field_type": "text"
            }
        )

        assert response.status_code == 400
        assert "无效的工作流类型" in response.json()["detail"]

    def test_list_all_workflows(
        self, client, admin_user
    ):
        """TEST-WF-008: 获取所有工作流配置"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        response = client.get(
            "/api/workflow-fields/",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "assign" in data
        assert "transfer" in data
        assert "repair" in data
        assert "scrap" in data

    def test_reset_workflow_fields(
        self, client, admin_user
    ):
        """TEST-WF-009: 重置工作流字段"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 先创建一些字段
        client.post(
            "/api/workflow-fields/assign",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "to_reset",
                "field_label": "待重置",
                "field_type": "text"
            }
        )

        # 重置
        response = client.post(
            "/api/workflow-fields/assign/reset",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted_count" in data

        # 验证字段已清空
        get_resp = client.get(
            "/api/workflow-fields/assign",
            headers={"Authorization": f"Bearer {token}"}
        )
        fields = get_resp.json()
        assert len(fields) == 0

    def test_duplicate_field_name(
        self, client, admin_user
    ):
        """TEST-WF-010: 重复的字段名"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        # 创建第一个字段
        client.post(
            "/api/workflow-fields/assign",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "duplicate_wf",
                "field_label": "第一个",
                "field_type": "text"
            }
        )

        # 尝试创建同名字段
        response = client.post(
            "/api/workflow-fields/assign",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "duplicate_wf",
                "field_label": "第二个",
                "field_type": "text"
            }
        )

        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]

    def test_select_without_options(
        self, client, admin_user
    ):
        """TEST-WF-011: 下拉字段未提供选项"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        response = client.post(
            "/api/workflow-fields/repair",
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

    def test_field_not_found(
        self, client, admin_user
    ):
        """TEST-WF-012: 字段不存在"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_resp.json()["access_token"]

        response = client.put(
            "/api/workflow-fields/99999",
            headers={"Authorization": f"Bearer {token}"},
            json={"field_label": "更新"}
        )

        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]

    def test_without_permission(
        self, client, test_user
    ):
        """TEST-WF-013: 无资产更新权限"""
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )
        token = login_resp.json()["access_token"]

        response = client.post(
            "/api/workflow-fields/assign",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "field_name": "no_perm",
                "field_label": "无权限字段",
                "field_type": "text"
            }
        )

        assert response.status_code in (403, 401)
