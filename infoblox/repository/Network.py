from django.db import connection
from django.db import transaction

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper
from infoblox.helpers.Log import Log


class Network:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId: int, networkName: str) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM `network` WHERE `network` = %s AND id_asset = %s", [
                networkName,
                assetId
            ])

            return DBHelper.asDict(c)[0]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(assetId: int, networkName: str) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM `network` WHERE `network` = %s AND id_asset = %s", [
                networkName,
                assetId
            ])
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
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
