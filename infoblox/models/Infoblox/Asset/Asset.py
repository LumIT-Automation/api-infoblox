from django.utils.html import strip_tags
from django.db import connection
from django.db import transaction
from django.core.cache import cache

from infoblox.helpers.Log import Log
from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper



class Asset:
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        if not cache.get("ASSETS"):
            c = connection.cursor()

            try:
                c.execute("SELECT * FROM asset WHERE id = %s", [
                    self.assetId
                ])

                a = DBHelper.asDict(c)[0]
                a["auth"] = {
                    "username": a["username"],
                    "password": a["password"],
                }

                del(
                    a["username"],
                    a["password"]
                )

                cache.set("ASSETS", a, 10)
                return a

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()
        else:
            # Fetching from cache instead of MySQL for when massive threaded calls result in too many sql connections.
            return cache.get("ASSETS")



    def modify(self, data: dict) -> None:
        sql = ""
        values = []

        c = connection.cursor()

        if self.__exists():
            # Build SQL query according to dict fields.
            for k, v in data.items():
                sql += k+"=%s,"
                values.append(strip_tags(v)) # no HTML allowed.

            try:
                c.execute("UPDATE asset SET "+sql[:-1]+" WHERE id = "+str(self.assetId),
                    values
                )

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": {"message": "Non existent Infoblox endpoint"}})



    def delete(self) -> None:
        c = connection.cursor()

        if self.__exists():
            try:
                c.execute("DELETE FROM asset WHERE id = %s", [
                    self.assetId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": {"message": "Non existent Infoblox endpoint"}})



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> dict:
        c = connection.cursor()
        try:
            c.execute("SELECT id, address, fqdn, baseurl, tlsverify, datacenter, environment, position FROM asset")

            return dict({
                "data": {
                    "items": DBHelper.asDict(c)
                }
            })

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> None:
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
                c.execute("INSERT INTO asset "+keys+" VALUES ("+s[:-1]+")",
                    values
                )
                aId = c.lastrowid

                # When inserting an asset, add the "any" network (Permission).
                from infoblox.models.Permission.Network import Network as PermissionNetwork
                PermissionNetwork.add(aId, "any")

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __exists(self) -> int:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM asset WHERE id = %s", [
                self.assetId
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])

        except Exception:
            return 0
        finally:
            c.close()
