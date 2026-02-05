from capture.selectors import PLATFORM_SELECTORS
from config.settings import SCREENSHOT_TIMEOUT_MS


class BaseCaptureStrategy:
    def capture(self, page, url: str, selectors: dict) -> tuple[bytes, str]:
        """Navega a la URL, captura screenshot y extrae texto.

        Returns:
            tuple: (screenshot_bytes, extracted_text)
        """
        page.goto(url, wait_until="networkidle", timeout=SCREENSHOT_TIMEOUT_MS)

        # Intentar cerrar popups de login/cookies
        self._dismiss_popups(page, selectors)

        # Esperar contenido principal
        try:
            page.wait_for_selector(selectors["wait_for"], timeout=15000)
        except Exception:
            pass  # Continuar aunque no encuentre el selector

        # Scroll para cargar contenido lazy
        page.evaluate("window.scrollBy(0, 300)")
        page.wait_for_timeout(1500)

        # Extraer texto
        text = self._extract_text(page, selectors["text_content"])

        # Capturar screenshot
        screenshot = self._take_screenshot(page, selectors["post_container"])

        return screenshot, text

    def _dismiss_popups(self, page, selectors: dict):
        """Intenta cerrar modales de login/cookies. Falla silenciosamente."""
        try:
            dismiss_sel = selectors.get("dismiss_login", "")
            if dismiss_sel:
                for sel in dismiss_sel.split(","):
                    sel = sel.strip()
                    btn = page.query_selector(sel)
                    if btn and btn.is_visible():
                        btn.click()
                        page.wait_for_timeout(1000)
                        break
        except Exception:
            pass

    def _extract_text(self, page, selector: str) -> str:
        try:
            elements = page.query_selector_all(selector)
            texts = []
            for el in elements:
                try:
                    t = el.inner_text()
                    if t and t.strip():
                        texts.append(t.strip())
                except Exception:
                    continue
            return "\n".join(texts)
        except Exception:
            return ""

    def _take_screenshot(self, page, container_selector: str) -> bytes:
        """Captura screenshot del contenedor del post, o viewport completo como fallback."""
        try:
            for sel in container_selector.split(","):
                sel = sel.strip()
                element = page.query_selector(sel)
                if element and element.is_visible():
                    return element.screenshot(type="png")
        except Exception:
            pass
        # Fallback: screenshot del viewport
        return page.screenshot(type="png", full_page=False)


class InstagramStrategy(BaseCaptureStrategy):
    """Estrategia especifica para Instagram."""

    def capture(self, page, url: str, selectors: dict) -> tuple[bytes, str]:
        # Instagram a veces muestra un overlay de login
        page.goto(url, wait_until="networkidle", timeout=SCREENSHOT_TIMEOUT_MS)
        self._dismiss_popups(page, selectors)
        page.wait_for_timeout(2000)

        # Segundo intento de cerrar popup
        self._dismiss_popups(page, selectors)

        try:
            page.wait_for_selector(selectors["wait_for"], timeout=15000)
        except Exception:
            pass

        page.evaluate("window.scrollBy(0, 200)")
        page.wait_for_timeout(1000)

        text = self._extract_text(page, selectors["text_content"])
        screenshot = self._take_screenshot(page, selectors["post_container"])
        return screenshot, text


class FacebookStrategy(BaseCaptureStrategy):
    """Estrategia especifica para Facebook."""
    pass


class TwitterStrategy(BaseCaptureStrategy):
    """Estrategia especifica para X/Twitter."""
    pass


class TikTokStrategy(BaseCaptureStrategy):
    """Estrategia especifica para TikTok. Espera extra para carga de video."""

    def capture(self, page, url: str, selectors: dict) -> tuple[bytes, str]:
        page.goto(url, wait_until="networkidle", timeout=SCREENSHOT_TIMEOUT_MS)
        self._dismiss_popups(page, selectors)

        # TikTok necesita mas tiempo para cargar el contenido
        page.wait_for_timeout(3000)
        self._dismiss_popups(page, selectors)

        try:
            page.wait_for_selector(selectors["wait_for"], timeout=15000)
        except Exception:
            pass

        text = self._extract_text(page, selectors["text_content"])
        screenshot = self._take_screenshot(page, selectors["post_container"])
        return screenshot, text
