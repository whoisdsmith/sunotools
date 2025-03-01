# Project Overview

## API I

This project, `suno-api`, is a Next.js-based API designed to interact with the Suno.ai music generation service.  It provides a RESTful interface for generating music, retrieving audio information, and managing user-related data, mirroring many actions available on the sunozara.com website (which seems to be a related platform).  It supports both 'simple' and 'custom' generation modes, allowing for varied levels of user control.  It heavily leverages `playwright` to interact with the underlying Suno.ai service.  The `get_songs_info.js` file is a standalone script showing usage.

Here's a breakdown of the project based on the provided files:

**Project Structure:**

* **`api/API I/`:** This is the root directory for the API project.
* **`src/app/api/`:** Contains the Next.js API routes, defining individual endpoints. Each route (e.g., `clip`, `concat`, `generate`, etc.) handles specific API requests.
* **`src/app/components`:**  Likely contains React components for a web UI, including a `Footer` and `Header`, and `Logo`, and `Section`. It also contains a component named `Swagger`, likely for displaying Swagger/OpenAPI documentation.
* **`src/app/docs`:** Includes the `page.tsx` file, which provides the API documentation page, and `swagger-suno-api.json` OpenAPI specification file.
* **`src/lib/`:** Contains utility functions and the core `SunoApi.ts` class (inferred, not shown in file list), which encapsulates the interaction with Suno.ai. `utils.ts` is also present, and defines `corsHeaders`.
* **`Dockerfile` & `docker-compose.yml`:**  Configuration for containerization, allowing the API to be run in a Docker environment.  The `Dockerfile` uses a two-stage build (builder and production) for optimized image size.  It warns if `SUNO_COOKIE` is not set. It installs playwright's chromium browser.
* **`.dockerignore`:** Specifies files/directories to exclude from the Docker build context.
* **`.env.example`:**  Provides an example environment file with necessary configuration variables like `SUNO_COOKIE`, `TWOCAPTCHA_KEY`, and browser preferences.
* **`.gitignore`, `.eslintrc.json`, `.prettierrc`:** Standard configuration files for Git, ESLint (linting), and Prettier (code formatting), respectively.
* **`next.config.mjs`:** Next.js configuration file, specifically configuring webpack to handle `.ttf` and `.html` files and disabling server minification.
* **`package.json` & `package-lock.json`:**  Node.js project metadata and dependency management files. They list dependencies and scripts for building, running, and linting the application.  It also includes development dependencies for TypeScript, Tailwind CSS, and ESLint.
* **`pnpm-lock.yaml`:** A lockfile used by the pnpm package manager to ensure consistent installations of dependencies across different environments
* **`postcss.config.js`:** Configuration for PostCSS, including Tailwind CSS and Autoprefixer.
* **`get_songs_info.js`:** A standalone JavaScript file demonstrates how to fetch song information from the API using `axios`.

**Key Functionality (Inferred from API Routes):**

* **`/api/generate`:**  Basic music generation based on a prompt, potentially with options for instrumental music and a model choice (defaulting to `chirp-v3-5`).  It has an optional `wait_audio` parameter to control synchronous/asynchronous behavior.
* **`/v1/chat/completions`:** Provides an OpenAI-compatible API endpoint for generating music, making it easier to integrate with existing tools and frameworks designed for OpenAI's API.
* **`/api/custom_generate`:** Allows for more detailed music generation, enabling users to specify lyrics, tags, and a title.
* **`/api/generate_lyrics`:** Generates lyrics based on a provided prompt.
* **`/api/get`:** Retrieves information about one or more audio clips. Can fetch multiple clips by IDs or all clips, with pagination support.
* **`/api/get_limit`:**  Likely retrieves information about the user's remaining credits or usage quota.
* **`/api/extend_audio`**:  Extends an existing audio clip, creating a longer version.
* **`/api/generate_stems`**:  Creates separate audio and music tracks (stem tracks).
* **`/api/get_aligned_lyrics`:** Retrieves timestamps for lyrics.
* **`/api/clip`:** Retrieves information about a specific audio clip using a `clipId`.
* **`/api/concat`:** Concatenates multiple audio clips into a single audio file.
* **`OPTIONS`** requests are handled for each endpoint to support CORS.

**Key Technologies:**

* **Next.js:**  A React framework for building server-rendered and statically generated web applications, used here for its API routes functionality.
* **TypeScript:**  A superset of JavaScript that adds static typing.
* **Playwright:**  A Node.js library for automating web browsers (Chromium, Firefox, WebKit).  This is likely used to interact with the Suno.ai website, as there isn't a public API.
* **Axios:**  A promise-based HTTP client used in `get_songs_info.js` and likely internally within the API routes for making requests.
* **Docker:**  Containerization technology used to package the API and its dependencies for easy deployment.
* **Tailwind CSS:** A utility-first CSS framework for rapidly building custom user interfaces.
* **ESLint & Prettier:**  Tools for code linting and formatting, respectively.
* **Swagger/OpenAPI:** Used for API documentation (inferred from `next-swagger-doc` and the presence of `swagger-ui-react`).
* **Pino**: A very low overhead Node.js logger
* **2captcha:** A captcha solving service (from `@2captcha/captcha-solver` and `TWOCAPTCHA_KEY`).

**Important Considerations (and Inferences):**

* **Authentication:** The `README.md` mentions a login/register endpoint, but the route for these are not provided here. The API routes use cookie-based authentication (from the `cookies()` import). The `SUNO_COOKIE` environment variable is crucial for accessing Suno.ai.
* **Rate Limiting:** The `README.md` specifies rate limits (60 requests/min for authenticated users, 30 for unauthenticated).  This suggests there's middleware or logic within the API routes to enforce these limits.
* **Asynchronous Operations:** The `wait_audio` parameter for `/api/generate` and `/api/custom_generate` implies that the music generation process can be asynchronous. The API likely uses a queue or background task system to handle the potentially long-running generation process.
* **Headless Browser:** The `Dockerfile` explicitly installs `xvfb` (X Virtual Framebuffer) and disables GPU acceleration, which are common configurations for running Playwright in a headless (no GUI) environment within a Docker container.
* **Production Setup:** The `Dockerfile` is structured for production builds.  It includes separate build and production stages for optimization.
* **Proxy from Environment:** axios's config is loading proxy settings from the environment, as seen from presence of the 'proxy-from-env' package.

**Overall, this project provides a robust, well-structured API for interacting with Suno.ai, built with modern web technologies and designed for ease of use and integration.** The use of Playwright suggests that it's automating interactions with the Suno.ai website rather than using a formal API. The inclusion of Swagger documentation is a strong point for usability.

---

## API II

This project, "API III", is a Node.js application designed to interact with Suno, likely to generate or manipulate audio.  It's packaged for deployment using Docker and Docker Compose.

Here's a breakdown:

1. **Dockerized Application:** The core is a Node.js application built using a multi-stage Dockerfile.
    * **Build Stage (`builder`):** Uses `node:lts-bookworm` as the base. Installs all dependencies (including development dependencies) using `npm install`, copies the source code, and runs the build process (`npm run build`). This stage compiles and prepares the application for production. The output is placed in a `.next` folder (indicating this might be a Next.js project).
    * **Production Stage:** Also uses `node:lts-bookworm`.  Installs necessary system dependencies, specifically libraries required by Playwright (a browser automation library) like `libnss3`, `libdbus-1-3`, and others, including `xvfb` (X Virtual Framebuffer) for headless browser operation. It then installs only production dependencies (`npm install --only=production`). Crucially, it copies the built application from the `builder` stage (`/.next` directory).
    * **Playwright Setup:** Downloads the Chromium browser with dependencies and sets it up to run in a Docker environment. The commands `mkdir -p /home/sbx_user1051/.cache && chmod -R 777 /home/sbx_user1051/.cache` ensures correct permissions are configured for Playwright. It also sets environment variables (`PLAYWRIGHT_BROWSERS_PATH`, `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD`) to control Playwright. Disables GPU acceleration which indicates the playwright won't use GPU to run.
    * **Suno Cookie Handling:**  Takes a `SUNO_COOKIE` as a build argument and environment variable.  This cookie is essential for authenticating with the Suno service.  A warning is displayed during build if the cookie isn't provided, indicating that users will need to manually supply it in request headers.
    * **Exposed Port and Command:** Exposes port 3000 and runs the application using `npm run start`.

2. **Docker Compose Orchestration:** The `docker-compose.yml` file defines a single service, `suno-api`.
    * **Build Context:** Builds the Docker image from the current directory (`.`).
    * **Suno Cookie:** Passes the `SUNO_COOKIE` environment variable from the host system (using `.env` file).
    * **Volume Mount:** Mounts the `./public` directory from the host to `/app/public` inside the container. This likely serves static assets.
    * **Port Mapping:** Maps port 3000 on the host to port 3000 inside the container, making the API accessible.
    * **Environment File:** Reads environment variables from a `.env` file.

3. **`drag-instructions.jpg`:** This image file's presence suggests there might be some UI element or instructions related to drag-and-drop functionality, possibly within the application's interface or documentation. Since it's a JPEG, we can't know the content, just that it's an image.

In summary, this project provides a Dockerized API, built with Node.js and Playwright, that likely interacts with the Suno service, requiring a `SUNO_COOKIE` for authentication.  The use of Playwright strongly suggests that the API interacts with Suno through web scraping or browser automation.  The Docker setup makes it easy to deploy and run the API in a consistent environment. The provided image is likely instructional.

---

## API IV

This project, "API IV", is a FastAPI-based web service that acts as a wrapper around the Suno.ai music generation service.  It allows users to generate music, fetch song feeds, generate lyrics, retrieve existing lyrics, and get account credit information.

**Key Features and Functionality:**

* **Authentication and Authorization:** The API uses a cookie-based authentication system, leveraging a `SESSION_ID` and `COOKIE` environment variable to interact with Suno.ai. It also fetches and maintains a JWT (`token`) from `clerk.suno.com` for authorized API calls.  A background thread (`keep_alive` in `cookie.py`) periodically updates this token to maintain a persistent session. The `get_token` dependency in `deps.py` manages token provision for API endpoints.
* **Music Generation:**
  * `/generate`:  Generates music based on user-provided parameters (title, lyrics, style) defined in `schemas.CustomModeGenerateParam`.
  * `/generate/description-mode`:  Generates music using a song description, defined in `schemas.DescriptionModeGenerateParam`. Both endpoints call the `generate_music` utility function.
* **Feed Retrieval:** `/feed/{aid}`:  Fetches a song feed (likely metadata about recently created songs) using an identifier (`aid`).  Uses the `get_feed` function.
* **Lyrics Generation and Retrieval:**
  * `/generate/lyrics/`:  Generates lyrics based on a user-provided prompt.  Uses the `generate_lyrics` function.
  * `/lyrics/{lid}`: Retrieves lyrics using a lyrics identifier (`lid`). Uses the `get_lyrics` function.
* **Account Credits:** `/get_credits`: Retrieves the user's remaining Suno.ai credits. Uses the `get_credits` function.
* **Error Handling:**  All API endpoints include robust error handling, raising `HTTPException` with appropriate status codes (400, 500) and error messages.
* **CORS:**  The API enables Cross-Origin Resource Sharing (CORS) for all origins, methods, and headers, making it accessible from any frontend application.
* **Dockerized Deployment:** The project includes `Dockerfile` and `docker-compose.yml` files for easy containerization and deployment.  The Docker setup uses a slim Python 3.10 base image, installs dependencies from `requirements.txt`, and runs the application using Uvicorn. The `.dockerignore` file specifies files and directories to exclude from the Docker build context.
* **Environment Variables:** The `.env.example` file shows the required environment variables (`BASE_URL`, `SESSION_ID`, `COOKIE`). The `.gitignore` file correctly excludes the `.env` file to prevent sensitive information from being committed to version control.

**File Structure Summary:**

* **`main.py`:**  The main FastAPI application file, defining the API endpoints and their corresponding handlers.
* **`cookie.py`:**  Manages the Suno.ai authentication cookie and token, including a background thread for keeping the token alive.  Initializes `suno_auth` with environment variables.
* **`deps.py`:** Contains dependency functions, specifically `get_token`, used to inject the authentication token into API endpoints.
* **`utils.py`:** (Implied, not shown in the provided code, but referenced)  This file likely contains the core logic for interacting with the Suno.ai API, including functions like `generate_music`, `get_feed`, `generate_lyrics`, and `get_credits`.
* **`schemas.py`:** (Implied) This file would define the Pydantic models for request and response data validation.
* **`Dockerfile` and `docker-compose.yml`:**  Files for containerizing and deploying the API.
* **`.dockerignore`, `.env.example`, `.gitignore`, `.idea/.gitignore`:** Configuration files for Docker, environment variables, Git, and the IDE (likely PyCharm).
* **`images/cover.png`:** a placeholder image, likely related to the project's presentation or documentation, though unused by the code itself.
* **`requirements.txt`:** (Implied) This file would list the project's Python dependencies.

In essence, this project provides a well-structured, secure, and deployable API for interacting with Suno.ai, making it easier for developers to integrate Suno.ai's music and lyrics generation capabilities into their own applications. The continuous token refresh ensures a smooth and uninterrupted service.

---

## tuantinhte1234-suno-api4

This project, `tuantinhte1234-suno-api4`, is an unofficial, open-source API for interacting with Suno.ai's music generation service.  It allows users to generate music, extend existing audio clips, create lyrics, and retrieve song information programmatically. The project leverages Playwright for browser automation and 2Captcha for CAPTCHA solving, enabling integration with other AI agents and services.

**Key Features and Capabilities:**

* **Music Generation:** Generates music based on text prompts, with options for instrumental tracks and custom mode (specifying lyrics, style, title, etc.).  It implements both a standard `/api/generate` endpoint and an OpenAI-compatible `/v1/chat/completions` endpoint.
* **Audio Extension:** Extends existing audio clips using the `/api/extend_audio` endpoint, allowing for longer and more complex musical creations. Users can also extend a clip from any point.
* **Lyrics Generation:** Generates lyrics from a prompt using the `/api/generate_lyrics` endpoint.
* **Stem Generation:** Generates separate vocal and instrumental tracks (stems) using the `/api/generate_stems` endpoint.
* **Lyric Alignment:** Provides timestamps for individual words in the lyrics with `/api/get_aligned_lyrics`.
* **Clip Concatenation:** Generates the whole song from multiple clips.
* **Information Retrieval:**  Retrieves metadata about generated songs (ID, title, cover image, lyrics, audio/video URLs, status) via `/api/get` and `/api/clip`, and account credit limits via `/api/get_limit`.
* **CAPTCHA Handling:** Integrates with the 2Captcha service to automatically solve hCaptcha challenges presented by Suno.  Uses Playwright (with optional ghost-cursor for realistic mouse movements) to simulate user interaction within a browser context.
* **Deployment Options:** Supports deployment via Vercel (one-click deployment) and Docker, as well as local execution.
* **API Documentation:** Includes comprehensive API documentation using Swagger, accessible at `/docs`.
* **OpenAI Compatibility:**  Provides an endpoint (`/v1/chat/completions`) that mimics the OpenAI API format, simplifying integration with tools and platforms designed for OpenAI.
* **Asynchronous/Synchronous Generation:** Supports both asynchronous and synchronous modes for music generation.  The `wait_audio` parameter controls whether the API waits for generation to complete before responding.
* **Configurability:** Uses environment variables (`SUNO_COOKIE`, `TWOCAPTCHA_KEY`, `BROWSER`, `BROWSER_HEADLESS`, `BROWSER_GHOST_CURSOR`, `BROWSER_LOCALE`) to manage API keys, browser settings, and CAPTCHA handling behavior.

**Project Structure:**

* **`src/app/`:** Contains the Next.js application code, including API routes and React components.
  * **`api/`:** Defines the various API endpoints, each implemented as a separate route handler.
  * **`components/`:**  Reusable React components (Footer, Header, Logo, Section, Swagger).
  * **`docs/`:** Contains the Swagger API documentation (JSON file and a page to render it).
  * **`v1/`:**  Contains the OpenAI-compatible API endpoint.
* **`src/lib/`:** Contains core logic.
  * **`SunoApi.ts`:**  The main class responsible for interacting with the Suno.ai website.  Handles authentication, CAPTCHA solving, music generation, and information retrieval. It includes comprehensive methods to manage all supported features.
  * **`utils.ts`:**  Utility functions, including `sleep` (for pausing execution), `waitForRequests` (for handling asynchronous CAPTCHA solving), and `corsHeaders` (for setting CORS headers).
* **`public/`:** Contains static assets, including the Swagger JSON file and images.
* **`Dockerfile` and `docker-compose.yml`:**  Enable containerized deployment.
* **Configuration files:** `next.config.mjs`, `package.json`, `postcss.config.js`, `tailwind.config.ts`, `tsconfig.json`, `.eslintrc.json`, `.prettierrc` for setting up the Next.js application, linting, styling, and TypeScript.

**Technical Details:**

1. **Authentication:** Uses the user's Suno.ai account cookie (`SUNO_COOKIE`) to authenticate requests.  The `SunoApi` class manages session tokens and keeps the session alive.
2. **Browser Automation:** Employs Playwright to automate interactions with the Suno.ai website, primarily for CAPTCHA solving.  It can launch Chromium or Firefox, and supports headless mode.
3. **CAPTCHA Solving:** Utilizes the 2Captcha service (paid) to resolve hCaptcha challenges. The `getCaptcha` method in `SunoApi.ts` orchestrates the CAPTCHA solving process.
4. **API Endpoints:** Each API endpoint is defined as a separate route handler within the `src/app/api/` directory.  These handlers use the `SunoApi` class to interact with Suno.ai.
5. **Error Handling:** Includes error handling for common issues, such as invalid requests, payment requirements (402 status), and internal server errors.
6. **CORS:** Configures CORS headers to allow requests from any origin.
7. **Logging:** Implements request and response logging.

**How to Use:**

1. **Obtain Cookie:** Obtain the `SUNO_COOKIE` from the Suno.ai website using browser developer tools.
2. **2Captcha Setup:** Create a 2Captcha account, obtain an API key (`TWOCAPTCHA_KEY`), and fund the account.
3. **Deployment:** Deploy the project using Vercel, Docker, or run it locally.
4. **Configuration:** Set environment variables (either in a `.env` file or through the deployment platform's settings).
5. **API Calls:** Make API calls to the deployed endpoints, providing the necessary parameters.  Example code snippets are provided in the README files (Python and JavaScript).
6. **Multiple Accounts:** Overriding the `SUNO_COOKIE` environment variable is possible by specifying the cookies in the `Cookie` header of the request.

**Areas for Improvement/Future Development:**

* GPTs, Coze, and LangChain integration documentation (mentioned as "coming soon" in the README).
* More robust error handling and reporting.
* Potentially explore alternative CAPTCHA solving methods or services.
* Add support for more fine-grained control over music generation parameters.
* Caching improvements for `SunoApi` instances.
* WebKit support.

In summary, `tuantinhte1234-suno-api4` is a well-structured and documented project providing a functional API for Suno.ai's music generation capabilities. It effectively addresses the challenges of authentication, CAPTCHA solving, and asynchronous operations, offering a valuable tool for developers and researchers.

---

## Sunozara

This README.md provides comprehensive documentation for the Sunozara.com API. Here's a summarized breakdown:

**1. Overview:**

* **Base URL:** `https://sunozara.com/api`
* The API provides endpoints for user authentication, audio management, category and language management, user profiles and favorites, articles, audiobooks, episodes, phone verification, locations, subscriptions, tags, products, and coupons.

**2. Authentication:**

* **Login (`/login` - POST):**  Takes email and password, returns a token and user data.
* **Register (`/register` - POST):**  Takes name, email, password, and password confirmation.

**3. Core Functionality - Audio Management (`/audios`):**

* **CRUD Operations:**  Standard RESTful endpoints for managing audio content.
  * **Get All:**  `GET /audios` (supports pagination, category, and language filters).
  * **Upload:** `POST /audios` (multipart/form-data for file uploads: title, description, category, language, audio file, cover image).
  * **Get Details:** `GET /audios/{id}`.
  * **Update:** `PUT /audios/{id}` (multipart/form-data, similar to upload).
  * **Delete:** `DELETE /audios/{id}`.
* **Authentication:** All audio endpoints require a `Bearer {token}` in the Authorization header.

**4. Categories and Languages:**

* **Categories (`/categories`):**
  * **Get All:** `GET /categories`.
  * **Create:** `POST /categories` (name, description).
* **Languages (`/languages`):**
  * **Get All:** `GET /languages`.
  * **Add:** `POST /languages` (name, code).
* **Authentication:** Requires a `Bearer {token}`.

**5. User Management (`/user`):**

* **Profile:**
  * **Get:** `GET /user/profile`.
  * **Update:** `PUT /user/profile` (name, email, avatar - file upload).
* **Favorites:**
  * **Get:** `GET /user/favorites`.
  * **Add:** `POST /user/favorites/{audio_id}`.
  * **Remove:** `DELETE /user/favorites/{audio_id}`.
* **Authentication:** Requires a `Bearer {token}`.

**6. Additional APIs:**

* **Articles (`/api/articles` - GET):**  Supports pagination and category filtering.
* **Audio Books (`/api/audiobooks` - GET):** Supports pagination, category, and language filtering.
* **Episodes (`/api/episodes/{audiobook_id}` - GET):**  Retrieves episodes for a specific audiobook.
* **Phone Verification (`/api/auth/verify-phone` - POST):**  Verifies a phone number with an OTP.
* **Locations (`/api/locations` - GET).**
* **Subscription (`/api/subscriptions` - GET):** Retrieves subscription plans.
* **Tags (`/api/tags` - GET).**
* **Products (`/api/products` - GET):** Supports pagination and category filtering.
* **Coupons (`/api/coupons/verify` - POST):** Verifies a coupon code.
* **Authentication:** Most of these APIs require a bearer token, as indicated in the documentation.

**7. Error Handling:**

* Clear definitions of common HTTP error codes: 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), and 422 (Validation Error), with example JSON responses.

**8. Rate Limiting:**

* **Authenticated Users:** 60 requests/minute.
* **Unauthenticated Users:** 30 requests/minute.
* **Exceeding Limit:** Returns a 429 (Too Many Requests) error.

**9. Testing and Support:**

* **Testing Tools:** Suggests Postman, cURL, or any HTTP client.  Includes a cURL example.
* **Support Contacts:**  Provides email addresses for general and technical support.

**Key Strengths of the Documentation:**

* **Well-Organized:** Uses clear headings and subheadings.
* **Comprehensive:** Covers all major API features.
* **Detailed:** Includes request methods, URLs, headers, body parameters (with examples), and response examples.
* **Practical:**  Provides guidance on testing and support.
* **Authentication Focused:** Clearly emphasizes when a Bearer token is necessary.
* **Error Handling:** Includes standard error response formats.

**Overall, this is excellent API documentation, providing all the necessary information for developers to integrate with the Sunozara.com platform.**

---

## sayanroy058-suno-api-new

This project, `sayanroy058-suno-api-new`, is an unofficial, open-source API for interacting with Suno.ai's music generation service.  It's built using Next.js and TypeScript, providing a RESTful API that allows users to generate music, lyrics, and manage their Suno account programmatically. The project is designed to be easily integrated into other applications, including AI agents like GPTs.  It also provides example scripts (`generate_song.py`, `streamlit_app.py`) demonstrating basic API usage.

Here's a breakdown of its key components and functionalities:

**Core Functionality:**

* **Music Generation:**
  * `/api/generate`:  Generates music based on a simple text prompt.  Allows specifying whether to create an instrumental version and selecting a model (e.g., "chirp-v4", "chirp-v3-5").  Supports a "wait_audio" parameter for synchronous or asynchronous operation.
  * `/api/custom_generate`:  Provides a "Custom Mode" for more fine-grained control, allowing users to specify lyrics, music style (tags), title, and model. It also includes a "wait_audio" parameter.
  * `/v1/chat/completions`:  Mimics the OpenAI `/v1/chat/completions` API endpoint, making it compatible with OpenAI clients. This simplifies integration with applications that already use the OpenAI API.
  * `/api/extend_audio`: Extends the length of an existing song.  It requires an `audio_id` and can optionally take a prompt, style tags, a title, and a specific time point (`continue_at`) to extend from.
  * `/api/concat`:  Combines audio clips to generate a whole song from extensions. It requires a `clip_id` for the base audio to be extended.
  * `/api/generate_stems`: Generates separate vocal and instrumental tracks (stems) for a given song.

* **Lyric Generation:**
  * `/api/generate_lyrics`: Creates lyrics based on a text prompt.

* **Audio & Account Management:**
  * `/api/get`:  Retrieves information about generated songs, either by ID (comma-separated) or all songs for the account.  Supports pagination.
  * `/api/get_limit`:  Provides information about the user's remaining Suno credits and usage limits.
  * `/api/get_aligned_lyrics`: Get list of timestamps for each word in the lyrics.
  * `/api/clip`: Get clip information based on ID passed as query parameter `id`.

* **CAPTCHA Handling:**  The API uses `2Captcha` (or `ruCaptcha` for users in Russia/Belarus), a paid service, to automatically solve hCAPTCHAs that Suno uses. It leverages `Playwright` with `rebrowser-patches` to simulate a browser, handle CAPTCHA challenges, and maintain the Suno session.  Environment variables (`TWOCAPTCHA_KEY`, `BROWSER`, `BROWSER_HEADLESS`, etc.) control the CAPTCHA solving behavior.  The `getCaptcha()` method in `SunoApi.ts` handles the CAPTCHA solving logic.  It launches a browser, interacts with the Suno website, and waits for the user to solve the CAPTCHA.

* **Session Management:**  The `SunoApi.ts` class handles session management with Suno's servers.  It fetches and maintains authentication tokens using the provided `SUNO_COOKIE` environment variable (or a cookie provided in the request header).  The `keepAlive()` method periodically renews the session to prevent timeouts.

**Project Structure:**

* **`src/app/`**: Contains the Next.js application.
  * **`api/`**:  Defines the API routes (endpoints).  Each route (e.g., `generate`, `custom_generate`, `get_limit`) is implemented as a separate file handling GET and/or POST requests.
  * **`components/`**:  Reusable React components (e.g., `Header`, `Footer`, `Swagger` for API documentation).
  * **`docs/`**:  Contains API documentation in Markdown and a Swagger/OpenAPI specification (`swagger-suno-api.json`).
  * **`v1/chat/completions/`**:  Implements the OpenAI-compatible API endpoint.

* **`src/lib/`**:  Contains core logic.
  * **`SunoApi.ts`**:  The main class that handles interactions with the Suno service, including authentication, music generation, lyric generation, and CAPTCHA solving.
  * **`utils.ts`**:  Utility functions (e.g., `sleep`, `isPage`, `waitForRequests` for CAPTCHA handling, CORS headers).

* **`public/`**:  Static assets, including a copy of the Swagger specification.

* **`examples/`**:  Python examples demonstrating how to use the API.
  * `generate_song.py`: A command-line script to generate a song.
  * `streamlit_app.py`:  A simple Streamlit web application for generating songs through a UI.

* **`Dockerfile` and `docker-compose.yml`**:  For containerized deployment using Docker.

* **`next.config.mjs`**: Next.js configuration file.

* **`package.json`**:  Project dependencies and scripts.

* **`README.md` (and translated versions)**:  Project documentation.

**Deployment:**

* **Vercel:** The project is designed for easy one-click deployment to Vercel.  The `README.md` file includes a "Deploy with Vercel" button.
* **Docker:**  `Dockerfile` and `docker-compose.yml` are provided for containerized deployment.
* **Local:**  The project can be run locally using `npm install` and `npm run dev`.

**Key Technologies:**

* **Next.js:**  A React framework for building server-rendered and statically generated web applications.
* **TypeScript:**  A superset of JavaScript that adds static typing.
* **Playwright:**  A Node.js library for automating web browsers.
* **rebrowser-playwright-core & ghost-cursor-playwright:** For solving captcha challenges.
* **2Captcha/ruCaptcha:**  A paid service for solving CAPTCHAs.
* **Axios:**  A promise-based HTTP client for making API requests.
* **Pino:**  A fast JSON logger.

**In summary,** `sayanroy058-suno-api-new` is a well-structured, comprehensive project providing a robust API for interacting with Suno.ai.  It handles the complexities of authentication, session management, and CAPTCHA solving, allowing developers to easily integrate Suno's music generation capabilities into their own applications. It's deployable via Vercel, Docker, or locally.  The extensive documentation, multiple languages in the README, and API examples make it accessible to a wide range of users.

---

## redwan002117-suno-api

This project, `redwan002117-suno-api`, is an unofficial, open-source API for interacting with Suno.ai's music generation service. It allows users to programmatically generate music, extend existing audio clips, generate lyrics, and retrieve song information.  The project is built using Node.js, Next.js, and Playwright, and can be deployed locally, with Docker, or on Vercel.

Here's a breakdown of its key features and components:

**Key Features:**

* **Music Generation:**  Generates music via text prompts, mimicking Suno.ai's functionality.  Supports both a "simple" mode (where Suno handles lyrics) and a "custom" mode (where the user provides lyrics, genre, and title).
* **API Endpoints:**  Provides a REST API with various endpoints for different functionalities, including:
  * `/api/generate`: Generates music from a prompt.
  * `/api/custom_generate`: Generates music with user-provided lyrics, genre, and title.
  * `/api/generate_lyrics`: Generates lyrics from a prompt.
  * `/api/get`: Retrieves music information by ID(s).
  * `/api/get_limit`:  Gets the user's remaining credit/quota.
  * `/api/extend_audio`: Extends an existing audio clip.
  * `/api/generate_stems`: Creates separate vocal and instrumental tracks.
  * `/api/get_aligned_lyrics`: Gets timestamps for each word in the lyrics.
  * `/api/clip`: Get clip information based on ID.
  * `/api/concat`: Generate the whole song from extensions.
  * `/v1/chat/completions`: OpenAI API compatible endpoint for music generation.
* **OpenAI API Compatibility:** Offers a `/v1/chat/completions` endpoint, making it compatible with tools and clients designed for OpenAI's API.
* **CAPTCHA Handling:** Integrates with the 2Captcha service to automatically solve hCaptcha challenges presented by Suno.ai. This uses Playwright with rebrowser patches for browser automation.
* **Deployment Options:** Supports one-click deployment to Vercel, local execution with Node.js, and containerization using Docker/Docker Compose.
* **Configuration:** Uses environment variables (e.g., `SUNO_COOKIE`, `TWOCAPTCHA_KEY`) for configuration, allowing customization of browser behavior (headless mode, locale, etc.).
* **API Documentation:** Includes Swagger documentation (accessible at `/docs` in the deployed application) for easy API exploration and testing.

**Project Structure:**

* **`src/app`:** Contains the Next.js application code.
  * `api`: Defines the API routes and their logic. Each route handles a specific Suno.ai functionality.
  * `components`: Reusable React components (Header, Footer, Swagger UI, etc.).
  * `docs`:  Contains the Swagger API documentation (JSON file and a page to render it).
  * `v1`: Contains routes compatible with the OpenAI API.
* **`src/lib`:**
  * `SunoApi.ts`:  The core class that encapsulates the logic for interacting with Suno.ai.  It handles authentication, CAPTCHA solving, and API requests.  It uses a caching mechanism to avoid recreating the API client unnecessarily.
  * `utils.ts`: Utility functions, including a `sleep` function for adding delays, hCaptcha handling helper, and CORS headers.
* **`public`:** Contains static assets, including a Swagger JSON file and images.
* **Configuration Files:**  Includes files for Next.js (`next.config.mjs`), Tailwind CSS (`tailwind.config.ts`, `postcss.config.js`), TypeScript (`tsconfig.json`), ESLint (`.eslintrc.json`), and Prettier (`.prettierrc`).
* **Docker Support:** `Dockerfile` and `docker-compose.yml` for containerized deployment.
* **README Files:** Provides comprehensive documentation in English, Chinese, and Russian.

**Workflow:**

1. **Authentication:** The API uses Suno.ai cookies for authentication. Users obtain their cookie from their browser's developer tools and provide it as an environment variable (`SUNO_COOKIE`).
2. **API Requests:**  API requests are made to the Next.js API routes defined in `src/app/api`.
3. **Suno API Interaction:** The `SunoApi` class handles the low-level interaction with Suno.ai.  It manages session tokens, handles CAPTCHAs using Playwright and 2Captcha, and makes requests to Suno.ai's internal API.
4. **CAPTCHA Solving:**  If Suno.ai requires a CAPTCHA, the `SunoApi` class launches a browser instance (Chromium or Firefox) using Playwright, navigates to Suno.ai, triggers the CAPTCHA, and uses the 2Captcha service to solve it. The token received from 2Captcha is then submitted to Suno.
5. **Response Handling:** The API routes process the responses from Suno.ai and return the results in a structured JSON format.
6. **Rate Limiting:** Includes rate limiting, to avoid getting the used suno account blocked.

**Dependencies:**

* **Next.js:** React framework for building the API and web interface.
* **Playwright:**  Browser automation library for interacting with Suno.ai and handling CAPTCHAs.  Specifically, it uses `rebrowser-playwright-core` which has patches to improve detection avoidance.
* **2Captcha:**  API for solving CAPTCHAs.
* **Axios:**  HTTP client for making requests to Suno.ai.
* **User-Agents:** Generates random user agent strings.
* **Pino:**  Logger for debugging and monitoring.
* **Swagger UI React:**  For rendering API documentation.
* **Tailwind CSS:**  Utility-first CSS framework for styling.
* **Other Utilities:** `cookie`, `js-cookie`, `tough-cookie`, `yn` (for boolean environment variables), `ghost-cursor-playwright` (for simulating human-like mouse movements, though currently its effectiveness is questionable).

In summary, `redwan002117-suno-api` provides a well-structured, documented, and deployable solution for programmatically interacting with Suno.ai's music generation service, overcoming the lack of an official API.  It handles authentication, CAPTCHA challenges, and provides a clean interface for developers to integrate Suno.ai's functionality into their own applications.

---

## gcui-art-suno-api

This project, `gcui-art-suno-api`, is an unofficial, open-source API for interacting with Suno.ai's music generation service.  It allows users to programmatically generate music, extend existing audio clips, generate lyrics, and retrieve song information, similar to how one might use the Suno.ai web interface. The project leverages Playwright for browser automation to interact with Suno and 2Captcha for automated CAPTCHA solving, which is a core dependency. It supports both local and Docker-based deployments, and is designed for integration with agents like GPTs.

Key features and aspects of the project include:

* **Core Functionality:** Mimics Suno.ai's web interface capabilities, providing API endpoints for generating music (with and without custom lyrics/styles), extending audio, generating lyrics, retrieving song metadata, getting user credit limits, generating stem tracks and getting lyric timestamps.
* **API Structure:**  Provides RESTful API endpoints.  The project includes `/api/generate` for standard prompt-based generation, `/api/custom_generate` for more granular control (lyrics, style, title), `/v1/chat/completions` for OpenAI API compatibility, and other utility endpoints.  It returns structured JSON responses.
* **CAPTCHA Handling:** Uses the `2Captcha` service and `Playwright` with `rebrowser-patches` to automatically solve hCaptcha challenges that Suno presents. This is a critical part of the system, as Suno frequently requires CAPTCHA verification.  The code includes mechanisms to launch a browser, interact with the CAPTCHA, and extract the resulting token.  Environment variables configure the 2Captcha API key and browser behavior (headless, locale, etc.).
* **Session Management:**  Manages Suno.ai sessions using cookies. It retrieves and maintains session tokens and handles "keep-alive" functionality to prevent session expiration.  The user's Suno.ai cookie (`SUNO_COOKIE`) is a crucial configuration parameter.
* **Deployment:** Supports one-click deployment to Vercel and Docker deployments.  The `Dockerfile` configures a Node.js environment, installs necessary dependencies (including Playwright and its browser dependencies), and sets environment variables. `docker-compose.yml` provides a simple way to build and run the API using Docker.
* **OpenAI Compatibility:**  Includes a `/v1/chat/completions` endpoint that adapts the `/api/generate` functionality to be compatible with OpenAI's API format, facilitating integration with OpenAI-based clients and agents.
* **Documentation:**  Provides comprehensive API documentation using Swagger (OpenAPI specification). The `swagger-suno-api.json` file defines the API structure, request/response formats, and parameters. A dedicated `/docs` page renders this documentation using Swagger UI.
* **Language Support:** Includes README files in English, Simplified Chinese, and Russian.
* **Error Handling:** Includes error handling in API routes, returning appropriate HTTP status codes and error messages.
* **Asynchronous Handling and Waiting:** Includes asynchronous mechanisms using the `sleep` method and waiting for the Suno service using the `wait_audio` option. It helps to control the audio file generation timing, particularly relevant for integrating with GPTs, where the API needs to wait for Suno to generate a file.
* **Dependencies:** `Playwright`, `@2captcha/captcha-solver`, `axios`, `next`, `react`, `tailwindcss`.
* **License**: LGPL-3.0-or-later

The `SunoApi.ts` file is the core of the project, implementing the logic for interacting with Suno.ai.  It handles authentication, CAPTCHA solving, sending requests to Suno.ai's internal API, and processing the responses.  The other files define API routes using Next.js, configure the application, and provide UI components for documentation and the main page.

---

## Comparison of APIs

**Here's a comparison table summarizing the key differences:**

| Feature          | API I (Next.js, Playwright)   | API III (Node.js, Playwright)  | API IV (FastAPI, Cookie-based) | tuantinhte1234-suno-api4 (Next.js, Playwright, 2Captcha) | Sunozara.com API (Official) | sayanroy058-suno-api-new (Next.js, Playwright, 2Captcha/ruCaptcha) | redwan002117-suno-api (Next.js, Playwright, 2Captcha) | gcui-art-suno-api (Next.js, Playwright, 2Captcha) |
|------------------|---------------------------------|--------------------------------|-------------------------------|--------------------------------------------------------|---------------------------|--------------------------------------------------------------------|---------------------------------------------------|-----------------------------------------------------|
| **Architecture** | Next.js (API Routes)        | Node.js (Likely Next.js)   | FastAPI (Python)             | Next.js (API Routes)                               | RESTful API               | Next.js (API Routes)                                            | Next.js (API Routes)                              | Next.js (API Routes)                                |
| **Language**     | TypeScript                     | JavaScript (likely)          | Python                        | TypeScript                                             | (Not specified)            | TypeScript                                                         | TypeScript                                        | TypeScript                                          |
| **Authentication** | `SUNO_COOKIE` (Cookie-based)   | `SUNO_COOKIE` (Cookie-based)   | `SESSION_ID`, `COOKIE`, JWT  | `SUNO_COOKIE` (Cookie-based, header override)      | Bearer Token               | `SUNO_COOKIE` (Cookie-based, header override)                   | `SUNO_COOKIE` (Cookie-based, header override)     | `SUNO_COOKIE` (Cookie-based, header override)         |
| **CAPTCHA**     | 2Captcha                       | No explicit mention            | Not applicable                 | 2Captcha, ghost-cursor                                | Not applicable             | 2Captcha/ruCaptcha, rebrowser-patches                           | 2Captcha, rebrowser-patches                     | 2Captcha, rebrowser-patches                         |
| **Browser Automation** | Playwright (Chromium)        | Playwright (Chromium)          | Not applicable                | Playwright (Chromium/Firefox)                        | Not applicable             | Playwright (Chromium/Firefox), rebrowser-patches                 | Playwright (Chromium/Firefox), rebrowser-patches   | Playwright (Chromium/Firefox), rebrowser-patches    |
| **Features**     | Generate, Custom Generate, Get, Extend, Stems, Lyrics, Concat  | (Limited Info)                | Generate, Feed, Lyrics, Credits | Generate, Custom Generate, Extend, Stems, Lyrics, Get, Concat, Get Limit, Align Lyrics  | User/Audio/Category Mgmt | Generate, Custom Generate, Extend, Stems, Lyrics, Get, Concat, Get Limit, Align Lyrics, Clip | Generate, Custom Generate, Extend, Stems, Lyrics, Get, Concat, Get Limit, Align Lyrics, Clip | Generate, Custom Generate, Extend, Stems, Lyrics, Get, Concat, Get Limit, Align Lyrics |
| **OpenAI Compatibility** | Yes (`/v1/chat/completions`) | No                             | No                             | Yes (`/v1/chat/completions`)                         | No                         | Yes (`/v1/chat/completions`)                                        | Yes (`/v1/chat/completions`)                       | Yes (`/v1/chat/completions`)                            |
| **Deployment**   | Docker, (Likely) Vercel      | Docker, Docker Compose         | Docker, Docker Compose         | Vercel, Docker, Local                                   | (Hosted)                  | Vercel, Docker, Local                                            | Vercel, Docker, Local                             | Vercel, Docker, Local                               |
| **Documentation** | Swagger/OpenAPI              | Limited                        | (Implied, not detailed)       | Swagger/OpenAPI, Multi-lingual README                  | README, Error Codes        | Swagger/OpenAPI, Multi-lingual README                           | Swagger/OpenAPI, Multi-lingual README             | Swagger/OpenAPI, Multi-lingual README                |
| **Asynchronous**  | `wait_audio` parameter     | (Likely)                      | (Not explicitly handled)     | `wait_audio` parameter                                 | (Not specified)            | `wait_audio` parameter                                             | `wait_audio` parameter                               | `wait_audio` parameter                           |
| **Official/Unofficial** | Unofficial                   | Unofficial                    | Unofficial                    | Unofficial                                            | Official                  | Unofficial                                                         | Unofficial                                        | Unofficial                                           |
| **Error Handling** | Basic HTTP Status Codes     | (Likely)                      | `HTTPException` (400, 500)    | HTTP Status Codes (402 for payment)                    | Detailed Error Codes       | HTTP Status Codes                                                  | HTTP Status Codes                                  | HTTP Status Codes                                    |
| **Rate Limiting** | 60 req/min (auth), 30 (unauth)| (Not specified)                | Not specified                   | (Implied, to avoid account blocking)                  | 60/30 req/min              | (Implied, to avoid account blocking)                               | (Implied, to avoid account blocking)               | (Implied, to avoid account blocking)                    |

**Key Differentiators and Detailed Comparison:**

1. **Architecture and Framework:**

    * **API I, tuantinhte1234-suno-api4, sayanroy058-suno-api-new, redwan002117-suno-api, gcui-art-suno-api:** All use Next.js for its API routes. This provides a straightforward way to create a serverless API within a React-based project.  Next.js handles routing, request parsing, and response formatting automatically.
    * **API III:**  Also likely uses Node.js, probably Next.js (based on the `.next` folder in the Dockerfile).  However, it provides less information about its specific implementation.
    * **API IV:**  Uses FastAPI (Python).  FastAPI is known for its performance, automatic data validation (using Pydantic), and built-in support for OpenAPI documentation.  This is a significantly different approach compared to the Next.js-based APIs.
    * **Sunozara.com API:**  Is a traditional RESTful API, the architecture details are not provided (could be anything).

2. **Authentication:**

    * **All Unofficial Suno APIs:**  Rely on the `SUNO_COOKIE` environment variable.  This cookie is obtained from the user's browser session with Suno.ai and acts as a session identifier. This is a less secure approach than, for example, API keys or OAuth, as cookies can expire or be invalidated.  `tuantinhte1234-suno-api4`, `sayanroy058-suno-api-new`, `redwan002117-suno-api`, and `gcui-art-suno-api` support overriding this cookie in the `Cookie` request header, allowing multiple user accounts to be used without restarting the server.
    * **API IV (FastAPI):**  Uses a combination of `SESSION_ID` and `COOKIE` environment variables, *and* fetches a JWT from `clerk.suno.com`.  This approach suggests a more robust and secure authentication mechanism, potentially involving a dedicated authentication service (Clerk). The `keep_alive` background thread actively maintains this token.
    * **Sunozara.com API:** Uses standard Bearer token authentication, which is best practice for RESTful APIs.

3. **CAPTCHA Handling:**

    * **API I, tuantinhte1234-suno-api4, sayanroy058-suno-api-new, redwan002117-suno-api, gcui-art-suno-api:** All use 2Captcha (or ruCaptcha for `sayanroy058-suno-api-new`) to solve hCaptcha challenges.  They use Playwright to automate the browser interaction, navigate to Suno.ai, trigger the CAPTCHA, send it to 2Captcha, and submit the solution. `tuantinhte1234-suno-api4` mentions "ghost-cursor" (for more human-like mouse movements), while `sayanroy058-suno-api-new`, `redwan002117-suno-api`, and `gcui-art-suno-api` use `rebrowser-playwright-core` (Playwright with patches to improve detection avoidance).  This is a critical difference from API III and API IV.  These projects *must* handle CAPTCHAs because they are directly automating the browser.
    * **API III:**  Doesn't explicitly mention CAPTCHA handling, but it *does* use Playwright, suggesting it *might* handle them implicitly, or perhaps it relies on the CAPTCHA being solved *before* the API is called (unlikely).
    * **API IV (FastAPI):**  Doesn't use Playwright, so it doesn't need to handle CAPTCHAs directly.  It interacts with Suno.ai through a different mechanism (likely using the `SESSION_ID` and JWT to make requests to Suno's internal API).
    * **Sunozara.com API:**  Doesn't need CAPTCHA handling, as it's a direct, authorized API.

4. **Features (Suno.ai Interaction):**

    * **API I:**  Offers a good range of features, including basic and custom generation, extending audio, generating lyrics, getting song information, and creating stem tracks.
    * **API III:** Has very limited information; its features are mostly inferred.
    * **API IV (FastAPI):**  Focuses on generation, lyrics, getting feeds, and account credits.  It doesn't include features like extending audio or generating stems.
    * **tuantinhte1234-suno-api4, sayanroy058-suno-api-new, redwan002117-suno-api, gcui-art-suno-api:** These four projects have the most comprehensive set of features, closely mirroring the functionalities available on the Suno.ai website. They offer both basic and custom music generation, extending audio, generating lyrics, retrieving song information, checking account limits, creating stems, and retrieving aligned lyrics.
    * **Sunozara.com API:**  This is an official API for a platform related to suno.ai, so its features are focused on that platform, including user management, audio/category/language management.

5. **OpenAI API Compatibility:**

    * **API I, tuantinhte1234-suno-api4, sayanroy058-suno-api-new, redwan002117-suno-api, and gcui-art-suno-api:** All provide a `/v1/chat/completions` endpoint that mimics the OpenAI API.  This makes them very easy to integrate with tools and libraries that are designed to work with OpenAI. This is a significant advantage for developers who are already familiar with the OpenAI ecosystem.
    * **API III and API IV:**  Do *not* have this compatibility.
    * **Sunozara.com API:** Does *not* have this compatibility.

6. **Deployment:**

    * **API I, tuantinhte1234-suno-api4, sayanroy058-suno-api-new, redwan002117-suno-api, gcui-art-suno-api:** Support Vercel, Docker, and local deployment.  Vercel is particularly convenient for Next.js projects.
    * **API III:** Docker and Docker Compose only.
    * **API IV (FastAPI):** Docker and Docker Compose.
    * **Sunozara.com API:** Is a hosted API, so no deployment instructions are needed by its users.

7. **Documentation:**

    * **API I, tuantinhte1234-suno-api4, sayanroy058-suno-api-new, redwan002117-suno-api, gcui-art-suno-api:**  Use Swagger/OpenAPI for documentation. This is a standard way to document APIs, and it allows for automatic generation of client SDKs and interactive documentation interfaces (like Swagger UI).
    * **API III:**  Limited documentation.
    * **API IV (FastAPI):**  FastAPI *automatically* generates OpenAPI documentation, so while it's not explicitly mentioned, it's highly likely to be available.
    * **Sunozara.com API:**  Uses a README.md file, which is well structured and clear.

8. **Asynchronous Handling:**

    * **API I, tuantinhte1234-suno-api4, sayanroy058-suno-api-new, redwan002117-suno-api, gcui-art-suno-api:** All provide a `wait_audio` parameter for the generation endpoints.  This allows the caller to choose between synchronous and asynchronous behavior.  If `wait_audio` is true, the API will wait for Suno.ai to finish generating the audio before responding.  If it's false, the API will return immediately with a job ID, and the caller can then poll for the result later.
    * **API III:** Likely handles it implicitly, due to usage of Playwright.
    * **API IV (FastAPI):** Doesn't have an equivalent parameter.
    * **Sunozara.com API:**  No equivalent parameter.

**In Summary (Which one to choose?):**

* **For comprehensive Suno.ai feature coverage and ease of use (especially with OpenAI-compatible tools):** `tuantinhte1234-suno-api4`, `sayanroy058-suno-api-new`, `redwan002117-suno-api`, and `gcui-art-suno-api` are excellent choices. They are very similar, differing mainly in minor implementation details and which Playwright patches they use for captcha solving.
* **For a Python-based solution and a more robust authentication approach:** API IV (FastAPI) is the best choice. It prioritizes security and performance, but has fewer Suno features.
* **For a simple, documented starting point:** API I is a good option, although the other Next.js projects have largely surpassed it in features and robustness.
* **For the most minimal information:** API III.  Its documentation is extremely limited.
* **For a well documented official API, managing content for a site that provides access to Suno-generated content:** Sunozara.com API.

The choice ultimately depends on the specific needs of your project.  If you need to closely mimic the Suno.ai website functionality and want the convenience of OpenAI API compatibility, the Next.js projects with 2Captcha support are the best options. If security and a Python ecosystem are priorities, API IV is the way to go. And if you need to manage content for the Sunozara platform, the official API is your choice.
