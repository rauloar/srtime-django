from playwright.sync_api import sync_playwright
import time

URL = "http://localhost:8001"
USER = "raul"
PASS = "zkr15ldi12"

def run():
    print("[INFO] Starting Browser Test...")
    with sync_playwright() as p:
        try:
             browser = p.chromium.launch(headless=False, channel="chrome", args=["--start-maximized"])
        except:
             print("[WARN] Chrome not found, using bundled Chromium...")
             browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        try:
            print(f"[INFO] Navigating to {URL}")
            page.goto(URL)

            # Login
            print("[INFO] Logging in...")
            page.fill("input[placeholder='Usuario']", USER)
            page.fill("input[placeholder='Contraseña']", PASS)
            page.click("button[type='submit']")
            
            # Wait for dashboard
            page.wait_for_url("**/dashboard")
            print("[OK] Login successful")

            # Navigate to Devices (Directly, as Sidebar is hidden on Dashboard)
            print("[INFO] Navigating to Devices...")
            page.goto(f"{URL}/devices")
            page.wait_for_selector("text=Puerta Principal", timeout=10000)
            
            # Select device
            print("👆 Selecting Device...")
            page.click("text=Puerta Principal")
            
            # Test "Refrescar Info"
            print("🔄 Testing 'Refrescar Info'...")
            page.click("text=Refrescar Info")
            time.sleep(2) 
            
            # Check for error toast
            if page.is_visible(".toast-error") or page.is_visible("text=Error"):
                 print("❌ Error detected during Refrescar Info")
                 page.screenshot(path="error_refrescar.png")
            else:
                 print("✅ Refrescar Info triggered")

            # Test "Funciones Adicionales"
            print("⚙️ Testing 'Funciones Adicionales'...")
            page.click("text=Funciones Adicionales")
            
            # Test "Sincronizar Hora"
            print("⏰ Testing 'Sincronizar Hora'...")
            page.click("text=Sincronizar Hora")
            time.sleep(2)

            if page.is_visible(".toast-error") or page.is_visible("text=Error"):
                 print("❌ Error detected during Sincronizar Hora")
                 page.screenshot(path="error_sync.png")
            else:
                 print("✅ Sincronizar Hora triggered")
            
            print("🎉 Test Sequence Completed. Keeping browser open for 5 seconds...")
            time.sleep(5)

        except Exception as e:
            print(f"❌ Test Failed: {e}")
            page.screenshot(path="failure.png")
            print("📸 Screenshot saved to failure.png")
        finally:
            browser.close()

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        # We need to access 'page' to screenshot. Refactoring 'run' or just using global/closure if needed.
        # Simple fix: Move try/except inside run or just print. 
        # Actually, let's just make run() catch and screenshot.
