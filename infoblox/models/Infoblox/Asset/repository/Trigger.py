from django.db import connection
from django.db import transaction
from django.utils.html import strip_tags

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper
from infoblox.helpers.Log import Log


class Trigger:

    # table: trigger_data

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    # `trigger_name` varchar(64) NOT NULL,
    # `src_asset_id` int(11) NOT NULL,
    # `dst_asset_id` int(11) NOT NULL,
    # `trigger_condition` varchar(255) NOT NULL DEFAULT '',
    # `enabled` tinyint(1) NOT NULL,



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int) -> dict:
        c = connection.cursor()

        try:
            if id:
                c.execute("SELECT * FROM trigger_data WHERE id = %s", [
                    id
                ])

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"database": "non existent identity group"})
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(id: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM trigger_data WHERE id = %s", [
                id
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(id: int, enabled: bool) -> None:
        c = connection.cursor()

        try:
            c.execute(
                "UPDATE trigger_data SET enabled = %s "
                "WHERE id = %s", [
                    int(enabled),
                    id
                ]
            )
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list() -> list:
        c = connection.cursor()

        try:
            c.execute(
                "SELECT trigger_data.id, trigger_data.trigger_name, src_asset.fqdn AS src_fqdn, dst_asset.fqdn AS dst_fqdn, "
                "trigger_data.trigger_condition, trigger_data.enabled FROM trigget_data "
                "INNER JOIN asset AS src_asset ON src_asset.id = trigger_data.src_asset_id "
                "INNER JOIN asset AS dst_asset ON dst_asset.id = trigger_data.dst_asset_id "
            )

            return DBHelper.asDict(c)[0]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> int:
        s = ""
        keys = "("
        values = []

        c = connection.cursor()

        # Build SQL query according to dict fields (only whitelisted fields pass).
        for k, v in data.items():
            s += "%s,"
            keys += k + ","
            values.append(strip_tags(v)) # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                c.execute("INSERT INTO trigger_data "+keys+" VALUES ("+s[:-1]+")", values) # user data are filtered by the serializer.

                return c.lastrowid
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                        raise CustomException(status=400, payload={"database": "duplicated identity group"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def runCondition(triggerName: str,  srcAssetId: int, dstAssetId: int = None) -> list:
        c = connection.cursor()
        args = [ triggerName, srcAssetId ]
        queryFilter = ""

        try:
            if dstAssetId:
                queryFilter = "AND dst_asset_id = %s "
                args.append(dstAssetId)

            c.execute(
                "SELECT * FROM trigger_data "
                "WHERE trigger_name = %s "
                "AND src_asset_id = %s " + queryFilter + "AND enabled > 0",
                    args
                )

            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
