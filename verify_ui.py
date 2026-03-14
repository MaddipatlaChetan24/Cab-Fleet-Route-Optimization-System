from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})

    # Log console messages
    page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))
    
    page.goto("http://localhost:8000/")
    
    print("Page loaded. Setting employees to 15.")
    page.fill("#employees_input", "15")
    
    print("Clicking optimize...")
    page.click("#submit-btn")
    
    print("Waiting for optimization response visualization...")
    try:
        page.wait_for_selector(".route-card-gen", timeout=15000)
        time.sleep(2) # ensure gsap animations finish
    except Exception as e:
        print("Timeout waiting for route cards")
    
    screenshot_path = "/Users/chetan/.gemini/antigravity/brain/8ed3baa2-109a-4c2d-9e94-9145348344f2/dashboard_final_metrics.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    
    try:
        before = page.inner_text("#dist-before")
        after = page.inner_text("#dist-after")
        savings = page.inner_text("#savings-pct")
        co2 = page.inner_text("#co2-total-saved")
        trees = page.inner_text("#tree-equiv")
        fuel = page.inner_text("#fuel-saved")
        cost = page.inner_text("#cost-saved")
        
        print(f"\n--- Metrics Extracted ---")
        print(f"Before Dist : {before} km")
        print(f"After Dist  : {after} km")
        print(f"Savings     : {savings} %")
        print(f"CO2 Saved   : {co2} kg")
        print(f"Tree Equiv  : {trees}")
        print(f"Fuel Saved  : {fuel} L")
        print(f"Cost Saved  : {cost} INR")
    except Exception as e:
        print("Error extracting metrics:", e)
        
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
