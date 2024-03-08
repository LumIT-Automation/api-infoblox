import json
from json.decoder import JSONDecodeError

from django.utils.html import strip_tags
from django.db import connection

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper


class Configuration:

    # Table: configuration.



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(configType: str) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT id, config_type, configuration FROM configuration WHERE config_type = %s", [
                configType
            ])

            o = DBHelper.asDict(c)[0]
            if "configuration" in o:
                try:
                    o["configuration"] = json.loads(o["configuration"])
                except JSONDecodeError:
                    o["configuration"] = []

            return o
        except IndexError:
            return {"id": 0, "config_type": configType, "configuration": []}
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(id: int, configuration: dict) -> None:
        c = connection.cursor()

        if not configuration:
            configuration = []

        try:
            c.execute("UPDATE configuration SET configuration=%s WHERE id=%s", [
                strip_tags(
                    json.dumps(configuration)
                ),
                id
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
