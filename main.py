import asyncio
import json
import logging
import signal
import zlib
from playwright.async_api import async_playwright, Page, Response

from centrifuge import (
    CentrifugeError,
    Client,
    ClientEventHandler,
    ConnectedContext,
    ConnectingContext,
    DisconnectedContext,
    ErrorContext,
    JoinContext,
    LeaveContext,
    PublicationContext,
    SubscribedContext,
    SubscribingContext,
    SubscriptionErrorContext,
    UnsubscribedContext,
    SubscriptionEventHandler,
    ServerSubscribedContext,
    ServerSubscribingContext,
    ServerUnsubscribedContext,
    ServerPublicationContext,
    ServerJoinContext,
    ServerLeaveContext,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
# Configure centrifuge-python logger.
cf_logger = logging.getLogger("centrifuge")
cf_logger.setLevel(logging.DEBUG)

COLORS_BY_PIXEL_ID: dict[int, str] = {}


class ClientEventLoggerHandler(ClientEventHandler):
    """Check out comments of ClientEventHandler methods to see when they are called."""

    async def on_connecting(self, ctx: ConnectingContext) -> None:
        logging.info("connecting: %s", ctx)

    async def on_connected(self, ctx: ConnectedContext) -> None:
        logging.info("connected: %s", ctx)

    async def on_disconnected(self, ctx: DisconnectedContext) -> None:
        logging.info("disconnected: %s", ctx)

    async def on_error(self, ctx: ErrorContext) -> None:
        logging.error("client error: %s", ctx)

    async def on_subscribed(self, ctx: ServerSubscribedContext) -> None:
        logging.info("subscribed server-side sub: %s", ctx)

    async def on_subscribing(self, ctx: ServerSubscribingContext) -> None:
        logging.info("subscribing server-side sub: %s", ctx)

    async def on_unsubscribed(self, ctx: ServerUnsubscribedContext) -> None:
        logging.info("unsubscribed from server-side sub: %s", ctx)

    async def on_publication(self, ctx: ServerPublicationContext) -> None:
        logging.info("publication from server-side sub: %s", ctx.pub.data)

        if ctx.channel == 'pixel:message':
            data = zlib.decompress(ctx.pub.data, wbits=-15)

            data_json = json.loads(data)
            for color, pixels in data_json.items():
                for pixel in pixels:
                    COLORS_BY_PIXEL_ID[pixel] = color

            print(f'Обновлена карта пикселей, новый размер: {len(COLORS_BY_PIXEL_ID)}')

        elif ctx.channel == 'event:message':
            data = json.loads(ctx.pub.data)
        else:
            print('unknown channel')
            return

    async def on_join(self, ctx: ServerJoinContext) -> None:
        logging.info("join in server-side sub: %s", ctx)

    async def on_leave(self, ctx: ServerLeaveContext) -> None:
        logging.info("leave in server-side sub: %s", ctx)


async def run_notpixel_things(token: str) -> None:
    client = Client(
        "wss://notpx.app/connection/websocket",
        events=ClientEventLoggerHandler(),
        token=token,
        headers={
            'Upgrade': 'websocket',
            'Origin': 'https://app.notpx.app',
            'Cache-Control': 'no-cache',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Pragma': 'no-cache',
            'Connection': 'Upgrade',
            'Sec-WebSocket-Key': '//jNMlRl1l5YgO7iuNvhjA==',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'Sec-WebSocket-Version': '13',
            'Sec-WebSocket-Protocol': 'centrifuge-protobuf',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
        },
        use_protobuf=True,
    )

    await client.connect()

    target_color: str = '000000'
    pixel_id: int = 88876

    while True:
        await asyncio.sleep(0.2)

        color: str | None = COLORS_BY_PIXEL_ID.get(pixel_id)
        if color is None or color != target_color:
            continue

        data = {"type": 0, "pixelId": pixel_id, "color": "#00CCC0"}
        await client.rpc(method='repaint', data=json.dumps(data).encode('utf-8'))

    await asyncio.Future()


async def run_browser() -> None:
    async with async_playwright() as playwright:
        async with await playwright.chromium.launch_persistent_context(
            user_data_dir='mytelegrambrowser',
            channel='chrome',
            headless=False,
        ) as context:
            page: Page = await context.new_page()

            async def handle_response(response: Response) -> None:
                if response.url == 'https://notpx.app/api/v1/users/me':
                    data = await response.json()
                    websocket_token: str = data['websocketToken']
                    print('Я достал токен!', websocket_token)

                    await context.close()

                    asyncio.create_task(run_notpixel_things(websocket_token))

            page.on('response', handle_response)

            await page.goto('https://web.telegram.org/k/#-2337207150')

            await asyncio.sleep(2)

            await page.get_by_text('LAUNCH APP').click()

            await asyncio.Future()



if __name__ == "__main__":
    asyncio.run(run_browser())
