from django.utils.html import strip_tags
from django.db import connection
from django.db import transaction

from infoblox.helpers.Log import Log
from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper



class History:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(username: str, allUsersHistory: bool) -> dict:
        j = 0
        c = connection.cursor()

        try:
            if allUsersHistory:
                c.execute("SELECT "
                    "log.id, username, action, asset_id, status, date, type, network, address, gateway "
                    "FROM log "
                    "LEFT JOIN log_object ON log.object_id = log_object.id "
                    "ORDER BY date DESC"
                )
            else:
                c.execute("SELECT "
                    "log.id, username, action, asset_id, status, date, type, network, address, gateway "
                    "FROM log "
                    "LEFT JOIN log_object ON log.object_id = log_object.id "                    
                    "WHERE username = %s "
                    "ORDER BY date DESC", [
                        username
                    ]
                )

            items = DBHelper.asDict(c)
            for el in items:
                items[j]["date"] = str(el["date"]) # datetime.datetime() to string.
                j += 1

            return dict({
                "data": {
                    "items": items
                }
            })

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict, table: str) -> int:
        iId = 0

        if table:
            s = ""
            keys = "("
            values = []

            c = connection.cursor()

            # Build SQL query according to dict fields.
            for k, v in data.items():
                s += "%s,"
                keys += k+","
                values.append(strip_tags(v)) # no HTML allowed.

            keys = keys[:-1]+")"

            try:
                with transaction.atomic():
                    c.execute("INSERT INTO "+table+" "+keys+" VALUES ("+s[:-1]+")",
                        values
                    )
                    iId = c.lastrowid
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        return iId
