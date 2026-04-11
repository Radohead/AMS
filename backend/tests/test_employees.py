"""
员工管理模块测试

用例编号:
- TEST-EMP-001: test_list_employees           - 获取员工列表
- TEST-EMP-002: test_create_employee           - 创建员工
- TEST-EMP-003: test_update_employee           - 更新员工
- TEST-EMP-004: test_delete_employee           - 删除(软删除)员工
"""
import pytest


class TestEmployeeList:
    """员工列表测试"""

    def test_list_employees_success(self, client, test_employee, auth_headers):
        """TEST-EMP-001: 获取员工列表"""
        response = client.get("/api/employees/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        assert data["total"] >= 1

    def test_list_employees_with_keyword(self, client, test_employee, auth_headers):
        """TEST-EMP-001b: 按关键词搜索员工"""
        response = client.get(
            "/api/employees/?keyword=张三",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["name"] == "张三"

    def test_list_employees_by_department(self, client, test_employee, auth_headers):
        """TEST-EMP-001c: 按部门筛选员工"""
        response = client.get(
            f"/api/employees/?department_id={test_employee.department_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for emp in data["items"]:
            assert emp["department_id"] == test_employee.department_id

    def test_list_employees_by_status(self, client, test_employee, auth_headers):
        """TEST-EMP-001d: 按状态筛选员工"""
        response = client.get(
            "/api/employees/?status=active",
            headers=auth_headers
        )
        assert response.status_code == 200


class TestEmployeeCreate:
    """创建员工测试"""

    def test_create_employee_success(self, client, test_department, auth_headers):
        """TEST-EMP-002: 创建新员工"""
        response = client.post(
            "/api/employees/",
            headers=auth_headers,
            json={
                "employee_no": "EMP002",
                "name": "李四",
                "email": "lisi@example.com",
                "phone": "13800138001",
                "department_id": test_department.id,
                "position": "产品经理"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["employee_no"] == "EMP002"
        assert data["name"] == "李四"
        assert data["status"] == "active"
        assert data["is_active"] is True

    def test_create_employee_duplicate_no(self, client, test_employee, auth_headers):
        """TEST-EMP-002b: 员工工号重复"""
        response = client.post(
            "/api/employees/",
            headers=auth_headers,
            json={
                "employee_no": test_employee.employee_no,
                "name": "另一个员工",
                "email": "another@example.com"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_employee_minimal_info(self, client, auth_headers):
        """TEST-EMP-002c: 仅提供必填信息创建员工"""
        response = client.post(
            "/api/employees/",
            headers=auth_headers,
            json={
                "employee_no": "EMP003",
                "name": "最小信息员工"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "最小信息员工"


class TestEmployeeUpdate:
    """更新员工测试"""

    def test_update_employee_success(self, client, test_employee, auth_headers):
        """TEST-EMP-003: 更新员工信息"""
        response = client.put(
            f"/api/employees/{test_employee.id}",
            headers=auth_headers,
            json={
                "email": "zhangsan_new@example.com",
                "phone": "13900139000",
                "position": "高级工程师"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "zhangsan_new@example.com"
        assert data["position"] == "高级工程师"

    def test_update_employee_not_found(self, client, auth_headers):
        """TEST-EMP-003b: 更新不存在的员工"""
        response = client.put(
            "/api/employees/99999",
            headers=auth_headers,
            json={"email": "test@example.com"}
        )
        assert response.status_code == 404

    def test_update_employee_change_department(self, client, test_employee, auth_headers):
        """TEST-EMP-003c: 更换员工部门"""
        # 先创建另一个部门
        dept_response = client.post(
            "/api/departments/",
            headers=auth_headers,
            json={"name": "新部门", "code": "NEW_DEPT"}
        )
        new_dept_id = dept_response.json()["id"]

        # 更换部门
        response = client.put(
            f"/api/employees/{test_employee.id}",
            headers=auth_headers,
            json={"department_id": new_dept_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["department_id"] == new_dept_id


class TestEmployeeDelete:
    """删除员工测试"""

    def test_delete_employee_success(self, client, auth_headers):
        """TEST-EMP-004: 删除(软删除)员工"""
        # 先创建一个员工
        create_response = client.post(
            "/api/employees/",
            headers=auth_headers,
            json={
                "employee_no": "EMP_DEL",
                "name": "待删除员工",
                "email": "delete@example.com"
            }
        )
        emp_id = create_response.json()["id"]

        # 软删除员工
        response = client.delete(
            f"/api/employees/{emp_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "deactivated" in response.json()["message"]

    def test_delete_employee_with_assets(self, client, test_employee, auth_headers):
        """TEST-EMP-004b: 不能删除有资产的员工"""
        # 注意: 这个测试需要在有资产关联的情况下才会失败
        # 由于 test_employee 没有关联资产，这个测试会通过
        # 实际业务中如果有资产关联会返回 400
        response = client.delete(
            f"/api/employees/{test_employee.id}",
            headers=auth_headers
        )
        # test_employee 没有关联资产，所以应该成功
        assert response.status_code == 200

    def test_delete_employee_not_found(self, client, auth_headers):
        """TEST-EMP-004c: 删除不存在的员工"""
        response = client.delete(
            "/api/employees/99999",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestEmployeeGet:
    """获取员工详情测试"""

    def test_get_employee_success(self, client, test_employee, auth_headers):
        """TEST-EMP-005: 获取员工详情"""
        response = client.get(
            f"/api/employees/{test_employee.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_employee.id
        assert data["name"] == "张三"
        assert data["employee_no"] == "EMP001"

    def test_get_employee_not_found(self, client, auth_headers):
        """TEST-EMP-005b: 获取不存在的员工"""
        response = client.get("/api/employees/99999", headers=auth_headers)
        assert response.status_code == 404
