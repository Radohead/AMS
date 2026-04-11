"""
部门管理模块测试

用例编号:
- TEST-DEPT-001: test_list_departments          - 获取部门列表
- TEST-DEPT-002: test_create_department        - 创建部门
- TEST-DEPT-003: test_update_department         - 更新部门
- TEST-DEPT-004: test_delete_department         - 删除部门(含子部门/员工检查)
"""
import pytest


class TestDepartmentList:
    """部门列表测试"""

    def test_list_departments_success(self, client, test_department, auth_headers):
        """TEST-DEPT-001: 获取部门列表"""
        response = client.get("/api/departments/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "技术部"

    def test_list_departments_by_parent(self, client, test_department, auth_headers):
        """TEST-DEPT-001b: 按父部门筛选 - 获取顶级部门"""
        # 不传 parent_id 参数会返回顶级部门（parent_id is None）
        response = client.get("/api/departments/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # 返回顶级部门
        for dept in data:
            assert dept["parent_id"] is None

    def test_list_departments_tree(self, client, test_department, auth_headers):
        """TEST-DEPT-001c: 获取部门树形结构"""
        response = client.get("/api/departments/tree", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestDepartmentCreate:
    """创建部门测试"""

    def test_create_department_success(self, client, auth_headers):
        """TEST-DEPT-002: 创建新部门"""
        response = client.post(
            "/api/departments/",
            headers=auth_headers,
            json={
                "name": "市场部",
                "code": "MARKET",
                "description": "市场部门"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "市场部"
        assert data["code"] == "MARKET"
        assert data["is_active"] is True

    def test_create_sub_department(self, client, test_department, auth_headers):
        """TEST-DEPT-002b: 创建子部门"""
        response = client.post(
            "/api/departments/",
            headers=auth_headers,
            json={
                "name": "前端组",
                "code": "FRONTEND",
                "parent_id": test_department.id,
                "description": "前端开发组"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "前端组"
        assert data["parent_id"] == test_department.id

    def test_create_department_duplicate_code(self, client, test_department, auth_headers):
        """TEST-DEPT-002c: 部门编码重复"""
        response = client.post(
            "/api/departments/",
            headers=auth_headers,
            json={
                "name": "另一个技术部",
                "code": test_department.code,
                "description": "会失败"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestDepartmentUpdate:
    """更新部门测试"""

    def test_update_department_success(self, client, test_department, auth_headers):
        """TEST-DEPT-003: 更新部门信息"""
        response = client.put(
            f"/api/departments/{test_department.id}",
            headers=auth_headers,
            json={
                "name": "研发部",
                "description": "研发部门更新"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "研发部"
        assert data["description"] == "研发部门更新"

    def test_update_department_not_found(self, client, auth_headers):
        """TEST-DEPT-003b: 更新不存在的部门"""
        response = client.put(
            "/api/departments/99999",
            headers=auth_headers,
            json={"name": "新名称"}
        )
        assert response.status_code == 404

    def test_update_department_deactivate(self, client, test_department, auth_headers):
        """TEST-DEPT-003c: 禁用部门"""
        response = client.put(
            f"/api/departments/{test_department.id}",
            headers=auth_headers,
            json={"is_active": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False


class TestDepartmentDelete:
    """删除部门测试"""

    def test_delete_department_success(self, client, auth_headers):
        """TEST-DEPT-004: 删除空部门"""
        # 先创建一个空部门
        create_response = client.post(
            "/api/departments/",
            headers=auth_headers,
            json={
                "name": "待删除部门",
                "code": "TO_DELETE",
                "description": "可以被删除"
            }
        )
        dept_id = create_response.json()["id"]

        # 删除该部门
        response = client.delete(
            f"/api/departments/{dept_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "deleted" in response.json()["message"]

    def test_delete_department_with_children(self, client, test_department, auth_headers):
        """TEST-DEPT-004b: 不能删除有子部门的部门"""
        # 创建子部门
        child_response = client.post(
            "/api/departments/",
            headers=auth_headers,
            json={
                "name": "子部门",
                "code": "CHILD",
                "parent_id": test_department.id
            }
        )
        child_id = child_response.json()["id"]

        # 尝试删除父部门
        response = client.delete(
            f"/api/departments/{test_department.id}",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "children" in response.json()["detail"]

    def test_delete_department_with_employees(self, client, test_department, test_employee, auth_headers):
        """TEST-DEPT-004c: 不能删除有员工的部门"""
        response = client.delete(
            f"/api/departments/{test_department.id}",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "employees" in response.json()["detail"]

    def test_delete_department_not_found(self, client, auth_headers):
        """TEST-DEPT-004d: 删除不存在的部门"""
        response = client.delete(
            "/api/departments/99999",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestDepartmentGet:
    """获取部门详情测试"""

    def test_get_department_success(self, client, test_department, auth_headers):
        """TEST-DEPT-005: 获取部门详情"""
        response = client.get(
            f"/api/departments/{test_department.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_department.id
        assert data["name"] == "技术部"

    def test_get_department_not_found(self, client, auth_headers):
        """TEST-DEPT-005b: 获取不存在的部门"""
        response = client.get("/api/departments/99999", headers=auth_headers)
        assert response.status_code == 404
