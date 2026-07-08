import threading

import lark_oapi as lark

from config import APP_ID, APP_SECRET
from handlers import on_card_action, on_message
from storage import init_db
from sync_history import catch_up_all
from watcher import start_watcher


def main() -> None:
    if not APP_ID or not APP_SECRET:
        raise RuntimeError(
            "FEISHU_APP_ID / FEISHU_APP_SECRET 未配置，去 .env 里填好再启动 "
            "(App Secret 在飞书开放平台后台「凭证与基础信息」页面复制)"
        )

    init_db()
    start_watcher()  # 无人回复安抚(默认每群关闭，后台打开才生效)
    # 启动追赶：把掉线期间错过的群消息从游标往后补齐(断点重传)。后台线程跑，不挡 WS 启动。
    threading.Thread(target=catch_up_all, daemon=True, name="catch-up").start()

    event_handler = (
        lark.EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(on_message)
        .register_p2_card_action_trigger(on_card_action)
        .build()
    )

    ws_client = lark.ws.Client(
        APP_ID,
        APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO,
    )
    ws_client.start()


if __name__ == "__main__":
    main()
