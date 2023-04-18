from django.db import connection
from django.db import transaction
from django.utils.html import strip_tags

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper
from infoblox.helpers.Log import Log


class Trigger:

    # table: trigger_data

    # `id` int(11) NOT NULL AUTO_INCREMENT,
    # `name` varchar(64) NOT NULL,
    # `src_asset_id` int(11) NOT NULL,
    # `dst_asset_id` int(11) NOT NULL,
    # `condition` varchar(255) NOT NULL DEFAULT '',
    # `enabled` tinyint(1) NOT NULL,



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int) -> dict:
        c = connection.cursor()

        try:
            if id:
                c.execute("SELECT trigger_data.id, trigger_data.`name`, "
                    "trigger_data.dst_asset_id, trigger_data.`action`, trigger_data.enabled, "
                    "trigger_condition.id as id_trigger_condition, trigger_condition.src_asset_id, `trigger_condition.condition` "
                    "FROM trigger_data "
                    "INNER JOIN trigger_condition ON trigger_condition.trigger_id = trigger_data.id "
                    "WHERE id = %s", [
                        id
                ])

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"database": "non existent trigger"})
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
    def deleteCondition(id: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM trigger_condition WHERE id = %s", [
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
    def list(filter: dict = None) -> list:
        filter = filter or {}

        filterWhere = ""
        filterArgs = list()

        c = connection.cursor()

        try:
            for k, v in filter.items():
                if k in ("name", "src_asset_id", "dst_asset_id", "enabled"):
                    filterWhere += k + ' = %s AND '

                    if k == "enabled":
                        v = int(v)
                    filterArgs.append(v)

            if filterWhere:
                filterWhere = filterWhere[:-4]
            else:
                filterWhere = "1"

            c.execute("SELECT trigger_data.id, trigger_data.`name`, trigger_data.dst_asset_id, trigger_data.`action`, trigger_data.enabled, "
                "group_concat(src_asset_id, '::', `condition` SEPARATOR ' | ') as conditions "
                "FROM trigger_data "
                "INNER JOIN trigger_condition ON trigger_condition.trigger_id = trigger_data.id "                
                "WHERE " + filterWhere + " " 
                "GROUP BY trigger_data.`action` ",
                    filterArgs
            )

            o = DBHelper.asDict(c)
            for t in o:
                conditions = t["conditions"].split("|")

                t["conditions"] = list()
                for condition in conditions:
                    try:
                        t["conditions"].append({
                            "src_asset_id": int(condition.split("::")[0]),
                            "condition": condition.split("::")[1].strip()
                        })
                    except IndexError:
                        pass

            return o
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
                        raise CustomException(status=400, payload={"database": "duplicated trigger data"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def addCondition(triggerId: int, srcAssetId: int, condition: str) -> None:
        c = connection.cursor()

        try:
            c.execute("INSERT INTO trigger_condition (`trigger_id`, `src_asset_id`, `condition`) VALUES (%s, %s, %s)", [
                triggerId, srcAssetId, condition
            ])

        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                raise CustomException(status=400, payload={"database": "duplicated trigger data"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def runConditionList(triggerName: str, srcAssetId: int, dstAssetId: int = None) -> list:
        c = connection.cursor()
        args = [ triggerName, srcAssetId ]
        queryFilter = ""

        try:
            if dstAssetId:
                queryFilter = "AND dst_asset_id = %s "
                args.append(dstAssetId)

            c.execute(
                "SELECT * FROM trigger_data "
                "WHERE name = %s "
                "AND src_asset_id = %s " + queryFilter + "AND enabled > 0",
                    args
                )

            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
