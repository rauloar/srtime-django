import requests
import json

base_url = "http://127.0.0.1:9000/api/v1"

# Login
print("🔐 Autenticando...")
response = requests.post(f"{base_url}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ Token obtenido")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test employees endpoint
    print("\n👥 Probando endpoint /employees/...")
    response = requests.get(f"{base_url}/employees/?skip=0&limit=2", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        employees = data if isinstance(data, list) else data.get('results', [])
        print(f"✅ Empleados: {len(employees)}")
        if employees:
            emp = employees[0]
            print(f"\n📋 Primer empleado:")
            print(f"  - user_id: {emp.get('user_id')}")
            print(f"  - name: {emp.get('name')}")
            print(f"  - email: {emp.get('email')}")
            print(f"  - phone: {emp.get('phone')}")
            print(f"  - mobile_phone: {emp.get('mobile_phone')} {'✅' if 'mobile_phone' in emp else '❌'}")
            print(f"  - country: {emp.get('country')} {'✅' if 'country' in emp else '❌'}")
            print(f"  - birthday: {emp.get('birthday')} {'✅' if 'birthday' in emp else '❌'}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test devices endpoint
    print("\n🖥️  Probando endpoint /devices/...")
    response = requests.get(f"{base_url}/devices/?skip=0&limit=2", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        devices = data if isinstance(data, list) else data.get('results', [])
        print(f"✅ Dispositivos: {len(devices)}")
        if devices:
            dev = devices[0]
            print(f"\n📋 Primer dispositivo:")
            print(f"  - name: {dev.get('name')}")
            print(f"  - ip: {dev.get('ip')}")
            print(f"  - zone: {dev.get('zone')}")
            print(f"  - zone_rel: {dev.get('zone_rel')} {'✅' if 'zone_rel' in dev else '❌'}")
            print(f"  - zone_name: {dev.get('zone_name')} {'✅' if 'zone_name' in dev else '❌'}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test schedules/employee-shifts endpoint
    print("\n📅 Probando endpoint /schedules/employee-shifts/...")
    response = requests.get(f"{base_url}/schedules/employee-shifts/?skip=0&limit=2", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        shifts = data if isinstance(data, list) else data.get('results', [])
        print(f"✅ Asignaciones: {len(shifts)}")
        if shifts:
            shift = shifts[0]
            print(f"\n📋 Primera asignación:")
            print(f"  - scope: {shift.get('scope')} {'✅' if 'scope' in shift else '❌'}")
            print(f"  - employee: {shift.get('employee')}")
            print(f"  - department: {shift.get('department')} {'✅' if 'department' in shift else '❌'}")
            print(f"  - shift: {shift.get('shift')}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test attendance/daily-attendance endpoint
    print("\n📊 Probando endpoint /attendance/daily-attendance/...")
    response = requests.get(f"{base_url}/attendance/daily-attendance/?skip=0&limit=2", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        attendance = data if isinstance(data, list) else data.get('results', [])
        print(f"✅ Registros: {len(attendance)}")
        if attendance:
            att = attendance[0]
            print(f"\n📋 Primer registro:")
            print(f"  - employee: {att.get('employee')}")
            print(f"  - date: {att.get('date')}")
            print(f"  - status: {att.get('status')}")
            print(f"  - schedule_type: {att.get('schedule_type')} {'✅' if 'schedule_type' in att else '❌'}")
            print(f"  - source_logs_count: {att.get('source_logs_count')} {'✅' if 'source_logs_count' in att else '❌'}")
            print(f"  - is_absent: {att.get('is_absent')} {'✅' if 'is_absent' in att else '❌'}")
    else:
        print(f"❌ Error: {response.text}")
        
else:
    print(f"❌ Error en login: {response.text}")
