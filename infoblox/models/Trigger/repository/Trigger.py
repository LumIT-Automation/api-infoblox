from django.db import connection
from django.db import transaction
from django.utils.html import strip_tags

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper
from infoblox.helpers.Log import Log


class Trigger:

    # Tables: trigger_data, trigger_condition.



    ####################################################################################################################
    # Trigger. Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int, loadConditions: bool) -> dict:
        o = dict()
        c = connection.cursor()

        try:
            if id:
                if loadConditions:
                    c.execute("SELECT trigger_data.id, trigger_data.`name`, trigger_data.dst_asset_id, trigger_data.`action`, trigger_data.enabled, "
                        "group_concat(trigger_condition.id, '::', src_asset_id, '::', `condition` SEPARATOR ' | ') as conditions "
                        "FROM trigger_data "
                        "LEFT JOIN trigger_condition ON trigger_condition.trigger_id = trigger_data.id "                
                        "WHERE trigger_data.id = %s "
                        "GROUP BY trigger_data.`name`, trigger_data.`action` ", [
                            id
                    ])

                    o = DBHelper.asDict(c)[0]

                    try:
                        conditions = o.get("conditions", "").split("|")
                        o["conditions"] = list()
                        for condition in conditions:
                            try:
                                o["conditions"].append({
                                    "condition_id": int(condition.split("::")[0]),
                                    "src_asset_id": int(condition.split("::")[1]),
                                    "condition": condition.split("::")[2].strip()
                                })
                            except IndexError:
                                pass
                    except AttributeError:
                        o["conditions"] = list()
                else:
                    c.execute(
                        "SELECT * FROM trigger_data "
                        "WHERE id = %s ", [
                            id
                        ])

                    o = DBHelper.asDict(c)[0]

            return o
        except IndexError:
            raise CustomException(status=404, payload={"database": "Non existent trigger"})
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
    def modify(id: int, data: dict) -> None:
        sql = ""
        values = []
        c = connection.cursor()

        # %s placeholders and values for SET.
        for k, v in data.items():
            sql += k + "=%s,"
            values.append(strip_tags(v)) # no HTML allowed.

        values.append(id)

        try:
            c.execute("UPDATE trigger_data SET " + sql[:-1] + " WHERE id = %s", values) # user data are filtered by the serializer.
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and (e.args[0] == 1062 or e.args[0] == 1452):
                        raise CustomException(status=400, payload={"database": "Duplicated trigger or non existent asset"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list(loadConditions: bool, filter: dict = None) -> list:
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

            if loadConditions:
                c.execute("SELECT trigger_data.id, trigger_data.`name`, trigger_data.dst_asset_id, trigger_data.`action`, trigger_data.enabled, "
                    "group_concat(trigger_condition.id, '::', src_asset_id, '::', `condition` SEPARATOR ' | ') as conditions "
                    "FROM trigger_data "
                    "LEFT JOIN trigger_condition ON trigger_condition.trigger_id = trigger_data.id "
                    "WHERE " + filterWhere + " " 
                    "GROUP BY trigger_data.`name`, trigger_data.`action` ",
                        filterArgs
                )

                o = DBHelper.asDict(c)
                for t in o:
                    try:
                        conditions = t.get("conditions", "").split("|")
                        t["conditions"] = list()
                        for condition in conditions:
                            try:
                                t["conditions"].append({
                                    "condition_id": int(condition.split("::")[0]),
                                    "src_asset_id": int(condition.split("::")[1]),
                                    "condition": condition.split("::")[2].strip()
                                })
                            except IndexError:
                                pass
                    except AttributeError:
                        t["conditions"] = list()
            else:
                c.execute(
                    "SELECT * FROM trigger_data "
                    "WHERE " + filterWhere + " "
                    "GROUP BY trigger_data.`action` ",
                        filterArgs
                    )

                o = DBHelper.asDict(c)

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
                    and e.args and e.args[0] and (e.args[0] == 1062 or e.args[0] == 1452):
                        raise CustomException(status=400, payload={"database": "Duplicated trigger or non existent asset"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Conditions. Public static methods
    ####################################################################################################################

    @staticmethod
    def addCondition(triggerId: int, srcAssetId: int, condition: str) -> None:
        c = connection.cursor()

        try:
            c.execute("INSERT INTO trigger_condition (`trigger_id`, `src_asset_id`, `condition`) "
                "VALUES (%s, %s, %s)", [
                    triggerId,
                    srcAssetId,
                    condition
            ])
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and (e.args[0] == 1062 or e.args[0] == 1452):
                raise CustomException(status=400, payload={"database": "Duplicated or wrong data"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def deleteCondition(triggerId: int, conditionId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM trigger_condition WHERE id = %s", [
                conditionId
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
