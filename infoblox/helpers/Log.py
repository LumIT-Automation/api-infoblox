import json
import logging
import traceback


class Log:
    @staticmethod
    def log(o: any, title: str = "") -> None:
        # Sends input logs to the configured logger (settings).
        log = logging.getLogger("django")
        if title:
            if "_" in title:
                for j in range(80):
                    title = title + "_"
            log.debug(title)

        try:
            if not isinstance(o, str):
                log.debug(json.dumps(o))
            else:
                log.debug(o)
        except Exception:
            log.debug(o)

        if title:
            title = ""
            for j in range(80):
                title = title + "_"
            log.debug(title)



    @staticmethod
    def logException(e: Exception) -> None:
        # Logs the stack trace information and the raw output if any.
        Log.log(traceback.format_exc(), 'Error')

        try:
            Log.log(e.raw, 'Raw infoblox data')
        except Exception:
            pass



    @staticmethod
    def actionLog(o: any, user: dict = None) -> None:
        user = user or {}

        # Sends input logs to the configured logger (settings).
        log = logging.getLogger("django")
        try:
            if "username" in user:
                log.debug("["+user['username']+"] "+o)
            else:
                log.debug(o)
        except Exception:
            pass
