import sys
import asyncio
import threading
from uuid import uuid4
from typing import Callable, Optional
from capture.browser import BrowserManager
from capture.strategies import (
    BaseCaptureStrategy,
    InstagramStrategy,
    FacebookStrategy,
    TwitterStrategy,
    TikTokStrategy,
)
from capture.selectors import PLATFORM_SELECTORS
from core.models import Platform, PostResult, ComplianceStatus
from utils.image_helpers import save_screenshot, create_thumbnail


def _run_in_playwright_thread(func, *args, **kwargs):
    """Ejecuta una funcion en un thread separado con su propio event loop.

    En Windows, Playwright necesita ProactorEventLoop para crear subprocesos.
    Streamlit ya tiene su propio event loop (Tornado), lo que causa conflicto.
    Este wrapper ejecuta Playwright en un thread aislado.
    """
    result = [None]
    exception = [None]

    def target():
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
        finally:
            loop.close()

    thread = threading.Thread(target=target)
    thread.start()
    thread.join()

    if exception[0]:
        raise exception[0]
    return result[0]


class CaptureService:
    """Orquestador de captura: recibe URLs, delega a estrategias, retorna PostResult."""

    def __init__(self):
        self.strategies = {
            Platform.INSTAGRAM: InstagramStrategy(),
            Platform.FACEBOOK: FacebookStrategy(),
            Platform.TWITTER: TwitterStrategy(),
            Platform.TIKTOK: TikTokStrategy(),
        }

    def _do_capture_single(self, browser_manager: BrowserManager, url: str, platform: Platform) -> PostResult:
        """Captura una sola URL (debe ejecutarse dentro del thread de Playwright)."""
        post_id = str(uuid4())
        context = browser_manager.new_context()
        page = context.new_page()
        try:
            strategy = self.strategies.get(platform, BaseCaptureStrategy())
            selectors = PLATFORM_SELECTORS.get(platform.value, {})

            if not selectors:
                selectors = {
                    "post_container": "main, article, body",
                    "text_content": "p, h1, h2, span",
                    "wait_for": "body",
                    "dismiss_login": "",
                }

            screenshot_bytes, text = strategy.capture(page, url, selectors)

            screenshot_path = save_screenshot(post_id, screenshot_bytes)
            thumbnail_path = create_thumbnail(screenshot_path)

            return PostResult(
                post_id=post_id,
                url=url,
                platform=platform,
                extracted_text=text,
                screenshot_path=screenshot_path,
                thumbnail_path=thumbnail_path,
                status=ComplianceStatus.PENDIENTE,
            )
        except Exception as e:
            return PostResult(
                post_id=post_id,
                url=url,
                platform=platform,
                status=ComplianceStatus.ERROR,
                error_message=str(e),
            )
        finally:
            try:
                page.close()
                context.close()
            except Exception:
                pass

    def _do_capture_batch(self, urls: list[tuple[str, Platform]]) -> list[PostResult]:
        """Ejecuta el batch completo dentro del thread de Playwright."""
        browser_manager = BrowserManager()
        browser_manager.start()
        results = []
        try:
            for i, (url, platform) in enumerate(urls):
                result = self._do_capture_single(browser_manager, url, platform)
                results.append(result)
        finally:
            browser_manager.close()
        return results

    def capture_batch(
        self,
        urls: list[tuple[str, Platform]],
        progress_callback: Optional[Callable] = None,
    ) -> list[PostResult]:
        """Captura un batch de URLs en un thread separado (compatible con Windows + Streamlit)."""
        if progress_callback:
            progress_callback(0.0, f"Iniciando captura de {len(urls)} URLs...")

        results = _run_in_playwright_thread(self._do_capture_batch, urls)

        if progress_callback:
            progress_callback(1.0, f"Captura completada: {len(urls)} URLs procesadas")

        return results
