from django.utils.html import strip_tags
from django.db import connection
from django.db import transaction
from django.core.cache import cache

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper


class Asset:

    # table: asset.



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId: int) -> dict:
        if not cache.get("ASSET"+str(assetId)):
            c = connection.cursor()

            try:
                c.execute("SELECT * FROM asset WHERE id = %s", [
                    assetId
                ])

                info = DBHelper.asDict(c)[0]
                cache.set("ASSET"+str(assetId), info, 10)
                return info
            except IndexError:
                raise CustomException(status=404, payload={"database": "non existent asset"})
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()
        else:
            # Fetching from cache instead of MySQL for when massive threaded calls result in too many sql connections.
            return cache.get("ASSET"+str(assetId))



    @staticmethod
    def modify(assetId: int, data: dict) -> None:
        sql = ""
        values = []

        c = connection.cursor()

        # Build SQL query according to dict fields.
        for k, v in data.items():
            sql += k+"=%s,"
            values.append(strip_tags(v)) # no HTML allowed.

        try:
            c.execute("UPDATE asset SET "+sql[:-1]+" WHERE id = "+str(assetId), # user data are filtered by the serializer.
                values
            )
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                raise CustomException(status=400, payload={"database": "duplicated asset"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(assetId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM asset WHERE id = %s", [
                assetId
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list() -> list:
        c = connection.cursor()

        try:
            c.execute(
                "SELECT id, address, fqdn, baseurl, tlsverify, datacenter, environment, position "
                "FROM asset"
            )

            return DBHelper.asDict(c)
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

        # Build SQL query according to (validated) input fields.
        for k, v in data.items():
            s += "%s,"
            keys += k+","
            values.append(strip_tags(v)) # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                c.execute("INSERT INTO asset "+keys+" VALUES ("+s[:-1]+")", # user data are filtered by the serializer.
                    values
                )
                return c.lastrowid
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                raise CustomException(status=400, payload={"database": "duplicated asset"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
