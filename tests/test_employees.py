import pytest

@pytest.fixture(name="test_dept")
def fixture_test_dept(client, auth_headers):
    # Pre-create a department for employee tests
    response = client.post("/departments", json={"name": "Engineering"}, headers=auth_headers)
    assert response.status_code == 201
    return response.json()

def test_employee_unauthorized(client):
    # Get employee details without auth header
    response = client.get("/employee/1")
    assert response.status_code == 401

def test_employee_crud(client, auth_headers, admin_headers, test_dept):
    dept_id = test_dept["id"]
    
    # 1. Create Employee (user auth allowed)
    emp_payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "salary": 75000.0,
        "joining_date": "2026-08-15",
        "is_active": True,
        "department_id": dept_id
    }
    response_create = client.post("/employee", json=emp_payload, headers=auth_headers)
    assert response_create.status_code == 201
    emp_data = response_create.json()
    assert emp_data["name"] == "Alice Smith"
    assert emp_data["email"] == "alice@example.com"
    emp_id = emp_data["id"]
    
    # Verify nested department is returned
    assert emp_data["department"] is not None
    assert emp_data["department"]["name"] == "Engineering"

    # 2. Get Employee
    response_get = client.get(f"/employee/{emp_id}", headers=auth_headers)
    assert response_get.status_code == 200
    assert response_get.json()["name"] == "Alice Smith"

    # 3. Update Employee
    update_payload = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "salary": 80000.0,
        "joining_date": "2026-08-15",
        "is_active": True,
        "department_id": dept_id
    }
    response_update = client.put(f"/employee/{emp_id}", json=update_payload, headers=auth_headers)
    assert response_update.status_code == 200
    assert response_update.json()["name"] == "Alice Johnson"
    assert response_update.json()["salary"] == 80000.0

    # 4. Delete Employee - Admin Authorization Checks
    # Standard user auth should be rejected (403 Forbidden)
    response_delete_user = client.delete(f"/employee/{emp_id}", headers=auth_headers)
    assert response_delete_user.status_code == 403
    assert response_delete_user.json()["detail"] == "Access denied"
    
    # Admin auth should succeed (200 OK)
    response_delete_admin = client.delete(f"/employee/{emp_id}", headers=admin_headers)
    assert response_delete_admin.status_code == 200
    assert response_delete_admin.json()["message"] == " Employee was successfully deleted"

def test_get_all_employees_filtering_and_sorting(client, auth_headers, test_dept):
    dept_id = test_dept["id"]
    
    # Create two employees
    client.post("/employee", json={
        "name": "John Doe",
        "email": "john@example.com",
        "salary": 90000.0,
        "joining_date": "2026-08-15",
        "is_active": True,
        "department_id": dept_id
    }, headers=auth_headers)
    
    client.post("/employee", json={
        "name": "Jane Smith",
        "email": "jane@example.com",
        "salary": 60000.0,
        "joining_date": "2026-08-15",
        "is_active": True,
        "department_id": dept_id
    }, headers=auth_headers)

    # 1. Test filtering by department
    response_filter = client.get("/employees?department=Engineering", headers=auth_headers)
    assert response_filter.status_code == 200
    data_filter = response_filter.json()
    assert len(data_filter) == 2
    assert all(e["department"]["name"] == "Engineering" for e in data_filter)

    # 2. Test sorting by salary (asc)
    response_sort_asc = client.get("/employees?sort_by=salary&order=asc", headers=auth_headers)
    assert response_sort_asc.status_code == 200
    data_sort_asc = response_sort_asc.json()
    assert data_sort_asc[0]["salary"] == 60000.0
    assert data_sort_asc[1]["salary"] == 90000.0

    # 3. Test sorting by salary (desc)
    response_sort_desc = client.get("/employees?sort_by=salary&order=desc", headers=auth_headers)
    assert response_sort_desc.status_code == 200
    data_sort_desc = response_sort_desc.json()
    assert data_sort_desc[0]["salary"] == 90000.0
    assert data_sort_desc[1]["salary"] == 60000.0
