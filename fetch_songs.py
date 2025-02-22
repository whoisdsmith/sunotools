import requests
import json
import math
import time
import random
import uuid
from urllib.parse import urlparse, parse_qs


class SunoAPI:
    BASE_URL = "https://studio-api.prod.suno.com"
    CLERK_BASE_URL = "https://clerk.suno.com"
    CLERK_VERSION = "5.15.0"

    def __init__(self, cookie_string):
        self.client = requests.Session()
        self.cookie_string = cookie_string
        self.sid = None
        self.jwt = None
        self.device_id = self._extract_device_id()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
        self._set_headers()
        self._set_cookies()

    def _extract_device_id(self):
        cookies = self._parse_cookies()
        return cookies.get("ajs_anonymous_id", str(uuid.uuid4()))

    def _parse_cookies(self):
        return {k: v for k, v in (pair.split("=", 1) for pair in self.cookie_string.split("; ") if "=" in pair)}

    def _set_headers(self):
        self.client.headers.update({
            "Affiliate-Id": "undefined",
            "Device-Id": f'"{self.device_id}"',
            "x-suno-client": "Android prerelease-4nt180t 1.0.42",
            "X-Requested-With": "com.suno.android",
            "sec-ch-ua": '"Chromium";v="130", "Android WebView";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
            "Origin": "https://suno.com",
            "Referer": "https://suno.com/",
        })

    def _set_cookies(self):
        cookies = self._parse_cookies()
        for key, value in cookies.items():
            self.client.cookies.set(key, value, domain=".suno.com")

    async def init(self):
        await self._get_auth_token()
        await self.keep_alive(initial=True)
        return self

    async def _get_auth_token(self):
        getSessionUrl = f"{self.CLERK_BASE_URL}/v1/client?_is_native=true&_clerk_js_version={self.CLERK_VERSION}"

        client_cookie_value = self.client.cookies.get("__client")
        if not client_cookie_value:
            print("=" * 50)
            print("ERROR: Could not find __client cookie in your provided cookie string.")
            print("Please follow these steps CAREFULLY:")
            print(
                "1. Open your browser (Chrome, Edge, or Firefox) and go to suno.com.  Log in.")
            print("2. Open the developer tools (F12).")
            print("3. Go to the 'Network' tab.")
            print("4. IMPORTANT:  Filter the requests by 'Fetch/XHR'.  This is crucial.")
            print("5. Look for a request to clerk.suno.com, specifically /v1/client.")
            print(
                "   If you don't see it, try refreshing the suno.com page while the Network tab is open.")
            print("6. Click on that /v1/client request.")
            print("7. In the 'Headers' section, find 'Request Headers'.")
            print(
                "8. Locate the 'cookie:' header.  Copy the ENTIRE value of that header.")
            print(
                "9. Paste that ENTIRE cookie string into the cookie_string variable in main().")
            print("=" * 50)
            raise Exception(
                "Missing __client cookie.  See detailed instructions above.")

        # Debug print
        print(
            f"Attempting authentication with __client cookie: {client_cookie_value}")

        try:
            response = self.client.get(getSessionUrl, headers={
                                       "Authorization": client_cookie_value})
            response.raise_for_status()
            self.sid = response.json()["response"]["last_active_session_id"]
            if not self.sid:
                raise Exception(
                    "Failed to get session ID.  Check your SUNO_COOKIE.")
        except requests.exceptions.RequestException as e:
            print("=" * 50)
            print(f"ERROR during Clerk authentication: {e}")
            print(
                f"Response status code: {e.response.status_code if e.response else 'No response'}")
            print(
                f"Response text:\n{e.response.text if e.response else 'No response'}")
            print("=" * 50)
            raise  # Re-raise the exception to stop execution

    async def keep_alive(self, initial=False):
        if not self.sid:
            raise Exception("Session ID not set. Call init() first.")

        renewUrl = f"{self.CLERK_BASE_URL}/v1/client/sessions/{self.sid}/tokens?_is_native=true&_clerk_js_version={self.CLERK_VERSION}"
        client_cookie_value = self.client.cookies.get(
            "__client")  # Re-check for safety

        if not client_cookie_value:  # Re-added check.
            raise Exception(
                "Could not find __client cookie during keep_alive.  Make sure your SUNO_COOKIE is correct.")

        response = self.client.post(
            renewUrl, headers={"Authorization": client_cookie_value})
        response.raise_for_status()

        self.jwt = response.json()["jwt"]
        if not initial:
          print("Session kept alive.")
        self.client.headers["Authorization"] = f"Bearer {self.jwt}"

    async def fetch_page(self, page_num, max_retries=3, retry_delay=2):
        params = {"page": page_num}
        url = f"{self.BASE_URL}/api/feed/v2"
        for attempt in range(max_retries):
            try:
                response = self.client.get(url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(
                    f"Attempt {attempt + 1}/{max_retries} failed for page {page_num}: {e}")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * \
                        (2 ** attempt) + random.uniform(0, 1)
                    print(f"Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    print(
                        f"Max retries reached for page {page_num}. Skipping.")
                    return None

    async def fetch_all_songs(self, output_file="suno_songs.json"):

        first_page = await self.fetch_page(0)
        if not first_page:
            print("Could not fetch the first page. Exiting.")
            return

        total_songs = first_page.get("num_total_results", 0)
        if total_songs == 0:
            print("No songs found.  Is your account logged in?")
            return

        songs_per_page = len(first_page.get("clips", []))
        total_pages = math.ceil(total_songs / songs_per_page)

        print(f"Total songs: {total_songs}, Total pages: {total_pages}")

        all_songs = {
            "clips": first_page["clips"],
            "num_total_results": total_songs,
            "fetched_pages": [0]
        }

        for page in range(1, total_pages):
            print(f"Fetching page {page} of {total_pages - 1}...")
            page_data = await self.fetch_page(page)
            if page_data:
                all_songs["clips"].extend(page_data["clips"])
                all_songs["fetched_pages"].append(page)
                time.sleep(random.uniform(1, 3))
            else:
                print(f"Skipping page {page} due to fetch error.")
            await self.keep_alive()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_songs, f, indent=2)

        print(
            f"Successfully saved {len(all_songs['clips'])} songs to {output_file}")


async def main():
    # VERY IMPORTANT: Get a fresh cookie string.
    cookie_string = "ajs_anonymous_id=e2c62440-30ba-43f3-b045-e54cff0136e3; _cfuvid=T.J72m_jtBoirPYnc4SLdHm30sBWWJjhutRCveX9YAQ-1740193527984-0.0.1.1-604800000; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8yc2pzbm9aejZxam5JOVlvNDJJOWtBRmFtUWsiLCJyb3RhdGluZ190b2tlbiI6InMybzVxMTF4cDM3YWFscmdtZ2RrYXNiaDNmcTRhdXl2MHY5ZXdvbXQifQ.s1lQQ1X0afe-0ZncU0YLsILgUoWMbC91Kr7JLzTLJZX2vo_z-8iu4E7mFuF2ObPo2Pg2dq9l4epDqTMBahW0mm3P_T0hXyKMgy6gddwNbpl7NrrBWqXCQUihXNt2zg21uCe2Ddi_fvZFaSwbYzvVV-Q33QQsKOLCPlV0pDUc72HesmiiZY5tqlxY6_WcNFY2yO4-8kZMjrukiz_Wc2_KpnMsASdN30-t-Z1OdRF4S5Q2-97LKxIjumY1PQLIqaGhQPR-T4rHvFf9kou3hUFMDLcikAiYKPkr-3bFvlujZnRH0Pt01jCjubhThZLsPo0dBO6IBYauRWenHQ0f9y3-jQ; __client_uat=1740194575; __client_uat_U9tcbTPE=1740194575; __cf_bm=nC17hsnBNoRnStQXCZbQctRZ6Qqb1jaaIR6gtGf1YEM-1740199100-1.0.1.1-jZYwN2bk.gdcQ58JI3OHliKPZR.sgFG93TrPzxbeBUr2of1y3MJADntckgJz2L0w9ov1qjMJF1Sd09zjRNLseQ"  # REPLACE THIS

    suno_api = SunoAPI(cookie_string)
    await suno_api.init()
    await suno_api.fetch_all_songs()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
