import re
import time
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

async def get_geolocation(geolocation: str):
    geolocator = Nominatim(user_agent="myGeocoderApp")
    location = geolocator.geocode(geolocation)
    if location:
        return location.latitude, location.longitude
    else:
        print("Location not found!")
        return None, None

async def extract_images(geolocation: str):
    latitude, longitude = await get_geolocation(geolocation)
    
    if latitude is None or longitude is None:
        return []
    
    print(f"Using geolocation: Latitude = {latitude}, Longitude = {longitude}")

    async def run(playwright) -> None:
        browser = await playwright.chromium.launch(headless=False)
        
        context = await browser.new_context(
            geolocation={"latitude": latitude, "longitude": longitude},
            permissions=["geolocation"]
        )

        page = await context.new_page()

        await page.goto("https://tinder.com/")

        await page.get_by_role("link", name="Log in").click()

        try:
            await page.locator("button:has-text('More Options')").wait_for(state="visible", timeout=1000)
            await page.locator("button:has-text('More Options')").click()
        except:
            print('No "More Options" button, continuing...')

        async with page.expect_popup() as page1_info:
            await page.get_by_label("Log in with Facebook").click()

        print('pop up opened')

        page1 = await page1_info.value
        await page1.locator("#email").fill("s1973sp@gmail.com")
        await page1.locator("#pass").fill("DaRkLaNd@16")

        await page.wait_for_load_state("domcontentloaded")

        await page1.locator("#pass").press("Enter")
        print('Arrived at login page')
        await page.wait_for_timeout(1000)

        await page1.get_by_label("Continue as Pranav").wait_for(state="visible", timeout=40000)
        await page1.get_by_label("Continue as Pranav").click()

        print('Successfully logged in')
        

        await page.wait_for_load_state("load")
        await page.evaluate("""(location) => {
                navigator.geolocation.latitude = location.latitude;
                navigator.geolocation.longitude = location.longitude;
            }""", {"latitude": latitude, "longitude": longitude})
        await page.wait_for_timeout(5000)
        print('Entering location')

        print('Successfully logged in')

            # Override geolocation using JavaScript to ensure consistent location
        await page.evaluate("""
            ({latitude, longitude}) => {
                // Override Geolocation API
                navigator.geolocation.getCurrentPosition = function(success) {
                    const position = {
                        coords: {
                            latitude: latitude,
                            longitude: longitude
                        }
                    };
                    success(position);
                };
            }
        """, {"latitude": latitude, "longitude": longitude})

        # Additional method to ensure location is set
        await page.evaluate("""
            ({latitude, longitude}) => {
                Object.defineProperty(navigator.geolocation, 'getCurrentPosition', {
                    value: function(success) {
                        success({
                            coords: {
                                latitude: latitude,
                                longitude: longitude
                            }
                        });
                    }
                });
            }
        """, {"latitude": latitude, "longitude": longitude})

        # Wait for location to be processed
        await page.wait_for_timeout(5000)
        print('Location set')

        # Refresh to ensure location takes effect
        await page.reload()
        await page.wait_for_load_state("load")
        await page.wait_for_timeout(5000)
    

        time.sleep(1)

        

        await page.wait_for_load_state("load")

        await page.wait_for_timeout(5000)
        time.sleep(10)

        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser')

        pattern = re.compile(r'url\("https://images-ssl\.gotinder\.com[^\)]+\)')

        image_urls = []
        for tag in soup.find_all(style=True):
            style = tag['style']
            matches = pattern.findall(style)
            for match in matches:
                url = match[5:-2] 
                if not url.endswith(".jpg"):
                    image_urls.append(url)

        for img_url in image_urls:
            print(img_url)
        
        await page.close()
        await context.close()
        await browser.close()
        return image_urls

    async with async_playwright() as playwright:
        images = await run(playwright)

    return images








# import re
# from playwright.sync_api import Playwright, sync_playwright
# import time
# from bs4 import BeautifulSoup
# from geopy.geocoders import Nominatim

# def get_geolocation(geolocation: str):
#     geolocator = Nominatim(user_agent="myGeocoderApp")
#     location = geolocator.geocode(geolocation)
#     if location:
#         return location.latitude, location.longitude
#     else:
#         print("Location not found!")
#         return None, None

# def extract_images(geolocation: str):
#     latitude, longitude = get_geolocation(geolocation)
    
#     if latitude is None or longitude is None:
#         return []
    
#     print(f"Using geolocation: Latitude = {latitude}, Longitude = {longitude}")

#     def run(playwright: Playwright) -> None:
#         browser = playwright.chromium.launch(headless=False)
        
#         context = browser.new_context(
#             geolocation={"latitude": latitude, "longitude": longitude},
#             permissions=["geolocation"]
#         )

#         page = context.new_page()

#         page.goto("https://tinder.com/")

#         page.get_by_role("link", name="Log in").click()

#         try:
#             page.locator("button:has-text('More Options')").wait_for(state="visible", timeout=1000)
#             page.locator("button:has-text('More Options')").click()
#         except:
#             print('No "More Options" button, continuing...')

#         with page.expect_popup() as page1_info:
#             page.get_by_label("Log in with Facebook").click()

#         page1 = page1_info.value
#         page1.locator("#email").fill("s1973sp@gmail.com")
#         page1.locator("#pass").fill("DaRkLaNd@16")

#         page.wait_for_load_state("domcontentloaded")

#         page1.locator("#pass").press("Enter")
#         print('Arrived at login page')

#         page1.get_by_label("Continue as Pranav").wait_for(state="visible", timeout=15000)
#         page1.get_by_label("Continue as Pranav").click()

#         print('Successfully logged in')

#         page.wait_for_load_state("load")
#         page.wait_for_timeout(5000)
#         print('Entering location')

#         time.sleep(1)

#         page.wait_for_load_state("load")

#         page.wait_for_timeout(5000)
#         time.sleep(10)

#         html_content = page.content()
#         soup = BeautifulSoup(html_content, 'html.parser')

#         pattern = re.compile(r'url\("https://images-ssl\.gotinder\.com[^\)]+\)')

#         image_urls = []
#         for tag in soup.find_all(style=True):
#             style = tag['style']
#             matches = pattern.findall(style)
#             for match in matches:
#                 url = match[5:-2] 
#                 if not url.endswith(".jpg"):
#                     image_urls.append(url)

#         for img_url in image_urls:
#             print(img_url)
        
#         time.sleep(10)

#         context.close()
#         browser.close()
#         return image_urls

#     with sync_playwright() as playwright:
#         images = run(playwright)

#     return images