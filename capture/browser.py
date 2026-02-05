from playwright.sync_api import sync_playwright


class BrowserManager:
    """Administra el ciclo de vida del navegador Playwright (sync_api).

    Uso: crear por batch, cerrar al finalizar.
    NO almacenar en session_state (no es serializable).
    """

    def __init__(self):
        self._playwright = None
        self._browser = None

    def start(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        )

    def new_context(self):
        return self._browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="es-CO",
        )

    def close(self):
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
        if self._playwright:
            try:
                self._playwright.stop()
            except Exception:
                pass
