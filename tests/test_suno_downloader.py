import time
import pytest
import asyncio
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from playwright.async_api import Page, Browser, BrowserContext
from aiohttp import ClientSession
from suno_downloader import SunoDownloader, SongMetadata, CONFIG


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test outputs"""
    return tmp_path


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary directory for logs"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return str(log_dir)


@pytest.fixture
def downloader(temp_dir, temp_log_dir):
    """Create a SunoDownloader instance with temporary directories"""
    return SunoDownloader(output_dir=str(temp_dir), log_dir=temp_log_dir)


@pytest.fixture
def mock_page():
    """Create a mock Playwright page"""
    page = AsyncMock(spec=Page)
    return page


@pytest.fixture
def mock_context():
    """Create a mock Playwright browser context"""
    context = AsyncMock(spec=BrowserContext)
    return context


@pytest.fixture
def mock_browser():
    """Create a mock Playwright browser"""
    browser = AsyncMock(spec=Browser)
    return browser


@pytest.fixture
def sample_song_metadata():
    """Create a sample SongMetadata instance"""
    return SongMetadata(
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        genre="Test Genre",
        year="2024",
        lyrics="Test lyrics",
        gpt_prompt="Test prompt",
        cover_url="https://example.com/cover.jpg",
        mp3_url="https://example.com/song.mp3"
    )


@pytest.mark.asyncio
async def test_login_success(downloader, mock_page, mock_context, mock_browser):
    """Test successful login"""
    # Mock successful login flow
    mock_page.goto = AsyncMock()
    mock_page.fill = AsyncMock()
    mock_page.click = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()

    # Mock wait_for_selector to handle both initial form and post-login check
    mock_page.wait_for_selector = AsyncMock()
    mock_page.wait_for_selector.side_effect = [
        Mock(),  # First selector wait succeeds
        Mock()   # Second selector wait succeeds
    ]

    # Mock the login check sequence
    mock_page.query_selector = AsyncMock()
    mock_page.query_selector.side_effect = [
        Mock(),  # Initial check - login form exists
        None     # After login - form doesn't exist (logged in)
    ]

    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.cookies = AsyncMock(
        return_value=[{"name": "test", "value": "test"}])

    with patch('playwright.async_api.async_playwright') as mock_playwright:
        mock_playwright.return_value.chromium.launch = AsyncMock(
            return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        result = await downloader.login("test@example.com", "password")

        assert result == True
        mock_page.goto.assert_called_once_with(CONFIG['suno_login_url'])
        mock_page.fill.assert_any_call(
            'input[type="email"]', "test@example.com")
        mock_page.fill.assert_any_call('input[type="password"]', "password")
        assert mock_page.wait_for_selector.call_count == 2


@pytest.mark.asyncio
async def test_login_failure(downloader, mock_page, mock_context, mock_browser):
    """Test failed login"""
    # Mock failed login flow
    mock_page.goto = AsyncMock()
    mock_page.fill = AsyncMock()
    mock_page.click = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()
    # Login form exists = not logged in
    mock_page.query_selector = AsyncMock(return_value=Mock())

    mock_context.new_page = AsyncMock(return_value=mock_page)

    with patch('playwright.async_api.async_playwright') as mock_playwright:
        mock_playwright.return_value.chromium.launch = AsyncMock(
            return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        result = await downloader.login("test@example.com", "wrong_password")

        assert result == False


@pytest.mark.asyncio
async def test_scrape_song_urls(downloader, mock_page, mock_context):
    """Test song URL scraping"""
    # Mock song elements
    mock_elements = [
        AsyncMock(get_attribute=AsyncMock(return_value="/song/1")),
        AsyncMock(get_attribute=AsyncMock(return_value="/song/2")),
        AsyncMock(get_attribute=AsyncMock(
            return_value="https://suno.ai/song/3"))
    ]

    # Set up page mocks
    mock_page.goto = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.evaluate = AsyncMock(
        side_effect=[100, 50, 100, 100])  # Simulate scroll changes
    mock_page.query_selector_all = AsyncMock(return_value=mock_elements)
    mock_page.wait_for_timeout = AsyncMock()

    # Set up context before using it
    mock_context.new_page = AsyncMock(return_value=mock_page)
    downloader.context = mock_context
    downloader.browser = AsyncMock()  # Add browser mock

    urls = await downloader.scrape_song_urls()

    # Verify results
    assert len(urls) == 3
    assert "https://suno.ai/song/1" in urls
    assert "https://suno.ai/song/2" in urls
    assert "https://suno.ai/song/3" in urls

    # Verify interactions
    mock_page.goto.assert_called_once_with(CONFIG['suno_profile_url'])
    mock_page.wait_for_selector.assert_called_once_with(
        '.song-list, .song-grid',
        timeout=CONFIG['selector_timeout']
    )
    assert mock_page.evaluate.call_count >= 2
    mock_page.query_selector_all.assert_called_once_with('a[href*="/song/"]')


@pytest.mark.asyncio
async def test_download_file_with_progress(downloader, temp_dir):
    """Test file downloading with progress"""
    test_content = b"Test file content" * 1000
    test_url = "https://example.com/test.mp3"
    test_filepath = temp_dir / "test.mp3"

    # Mock aiohttp response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"content-length": str(len(test_content))}

    # Create proper async iterator for chunks
    async def mock_iter_chunked(chunk_size):
        yield test_content
    mock_response.content.iter_chunked = mock_iter_chunked

    # Mock aiohttp session with proper async context manager
    mock_session = AsyncMock(spec=ClientSession)
    mock_session.get.return_value.__aenter__.return_value = mock_response

    result = await downloader.download_file_with_progress(
        mock_session, test_url, test_filepath
    )

    assert result == True
    assert test_filepath.exists()
    assert test_filepath.stat().st_size > 0


@pytest.mark.asyncio
async def test_process_song(downloader, mock_page, mock_context, sample_song_metadata):
    """Test complete song processing"""
    test_url = "https://suno.ai/song/test"

    # Mock browser setup
    with patch('playwright.async_api.async_playwright') as mock_playwright:
        mock_playwright.return_value.chromium.launch = AsyncMock(
            return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)

        # Mock metadata extraction
        downloader.extract_song_metadata = AsyncMock(
            return_value=sample_song_metadata)

        # Mock download methods
        downloader.download_file_with_progress = AsyncMock(return_value=True)
        downloader.add_metadata_to_mp3 = AsyncMock()
        downloader.save_text_file = AsyncMock()

        # Mock session
        mock_session = AsyncMock(spec=ClientSession)

        await downloader.process_song(test_url, mock_session)

        # Verify progress was saved
        assert test_url in downloader.progress
        assert downloader.progress[test_url]['completed'] == True
        assert 'timestamp' in downloader.progress[test_url]


@pytest.mark.asyncio
async def test_rate_limiting(downloader):
    """Test rate limiting functionality"""
    start_time = time.time()

    # Make multiple requests
    for _ in range(3):
        await downloader.rate_limit()

    elapsed = time.time() - start_time

    # Should take at least 2 * rate_limit_delay seconds
    assert elapsed >= 2 * CONFIG['rate_limit_delay']


def test_sanitize_filename(downloader):
    """Test filename sanitization"""
    test_cases = [
        ("Hello:World", "Hello_World"),
        ("Test/File*Name", "Test_File_Name"),
        ('File"With?Invalid<Chars>', "File_With_Invalid_Chars"),
        ("Normal File Name", "Normal File Name")
    ]

    for input_name, expected in test_cases:
        assert downloader.sanitize_filename(input_name) == expected


@pytest.mark.asyncio
async def test_error_handling(downloader, mock_page, mock_context):
    """Test error handling during song processing"""
    test_url = "https://suno.ai/song/error-test"

    # Mock session
    mock_session = AsyncMock(spec=ClientSession)

    # Simulate an error during metadata extraction
    downloader.extract_song_metadata = AsyncMock(
        side_effect=Exception("Test error"))

    await downloader.process_song(test_url, mock_session)

    # Verify error was recorded in progress
    assert test_url in downloader.progress
    assert downloader.progress[test_url]['completed'] == False
    assert 'error' in downloader.progress[test_url]
    assert 'Test error' in downloader.progress[test_url]['error']
