from django.db import connection
from django.db import transaction

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper


class Network:

    # Table: network.



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int, assetId: int, network: str) -> dict:
        c = connection.cursor()

        try:
            if id:
                c.execute("SELECT * FROM `network` WHERE id = %s", [id])
            if assetId and network:
                c.execute("SELECT * FROM `network` WHERE `network` = %s AND id_asset = %s", [network, assetId])

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"database": "non existent network"})
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(id: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM `network` WHERE `id` = %s", [id])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(assetId, networkName) -> int:
        c = connection.cursor()

        try:
            with transaction.atomic():
                c.execute("INSERT INTO `network` (id_asset, `network`) VALUES (%s, %s)", [
                    assetId,
                    networkName
                ])

                return c.lastrowid
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                        raise CustomException(status=400, payload={"database": "duplicated network"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
