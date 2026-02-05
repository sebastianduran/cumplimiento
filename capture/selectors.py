"""Selectores CSS por plataforma, aislados para facil mantenimiento."""

PLATFORM_SELECTORS = {
    "instagram": {
        "post_container": "article[role='presentation'], main article, article",
        "text_content": "div._a9zs, span._ap3a, h1, div[class*='Caption']",
        "wait_for": "article",
        "dismiss_login": "button:has-text('Not Now'), button:has-text('Ahora no'), [role='dialog'] button:first-child",
    },
    "facebook": {
        "post_container": "div[data-pagelet='FeedUnit'], div.x1yztbdb, div[role='article']",
        "text_content": "div[data-ad-preview='message'], div.xdj266r, div[dir='auto']",
        "wait_for": "div[role='main']",
        "dismiss_login": "div[role='dialog'] [aria-label='Close'], div[role='dialog'] [aria-label='Cerrar']",
    },
    "twitter": {
        "post_container": "article[data-testid='tweet']",
        "text_content": "div[data-testid='tweetText']",
        "wait_for": "article[data-testid='tweet']",
        "dismiss_login": "[data-testid='xMigrationBottomBar'] button, [role='dialog'] button[aria-label='Close']",
    },
    "tiktok": {
        "post_container": "div[class*='DivVideoContainer'], div[class*='video-card'], div[class*='tiktok-web-player']",
        "text_content": "div[class*='DivDescription'], span[class*='SpanText'], h1",
        "wait_for": "div[id='app']",
        "dismiss_login": "button[class*='close'], div[class*='login'] button, [data-e2e='modal-close-inner-button']",
    },
}
