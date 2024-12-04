import asyncio
import json
import logging
import signal
import ujson

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


async def get_client_token() -> str:
    # To reject connection raise centrifuge.UnauthorizedError() exception:
    # raise centrifuge.UnauthorizedError()

    logging.info("get client token called")

    # REPLACE with your own logic to get token from the backend!
    example_token = (
        "yourtoken"
    )

    return example_token


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

    async def on_join(self, ctx: ServerJoinContext) -> None:
        logging.info("join in server-side sub: %s", ctx)

    async def on_leave(self, ctx: ServerLeaveContext) -> None:
        logging.info("leave in server-side sub: %s", ctx)


class SubscriptionEventLoggerHandler(SubscriptionEventHandler):
    """Check out comments of SubscriptionEventHandler methods to see when they are called."""

    async def on_subscribing(self, ctx: SubscribingContext) -> None:
        logging.info("subscribing: %s", ctx)

    async def on_subscribed(self, ctx: SubscribedContext) -> None:
        logging.info("subscribed: %s", ctx)

    async def on_unsubscribed(self, ctx: UnsubscribedContext) -> None:
        logging.info("unsubscribed: %s", ctx)

    async def on_publication(self, ctx: PublicationContext) -> None:
        logging.info("publication: %s", ctx.pub.data)

    async def on_join(self, ctx: JoinContext) -> None:
        logging.info("join: %s", ctx)

    async def on_leave(self, ctx: LeaveContext) -> None:
        logging.info("leave: %s", ctx)

    async def on_error(self, ctx: SubscriptionErrorContext) -> None:
        logging.error("subscription error: %s", ctx)


async def run_example():
    client = Client(
        "wss://notpx.app/connection/websocket",
        events=ClientEventLoggerHandler(),
        get_token=get_client_token,
        headers={
            'Upgrade': 'websocket',
            'Origin': 'https://app.notpx.app',
            'Cache-Control': 'no-cache',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Pragma': 'no-cache',
            'Connection': 'Upgrade',
            'Sec-WebSocket-Key': 'E9GZmLb54xUx2VS6raIOog==',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'Sec-WebSocket-Version': '13',
            'Sec-WebSocket-Protocol': 'centrifuge-protobuf',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
        },
        use_protobuf=True,
        name='js',
    )

    await client.connect()

    for _ in range(10):
        data = {"type":0,"pixelId":1,"color":"#BE0039"}
        await client.rpc(method='repaint', data=json.dumps(data).encode('utf-8'))
        await asyncio.sleep(1)

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(run_example())
