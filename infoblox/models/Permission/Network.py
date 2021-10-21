from django.db import connection

from infoblox.models.Infoblox.Network import Network as InfobloxNetwork
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer as InfobloxNetworkContainer

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper

from infoblox.helpers.Log import Log

class Network:
    def __init__(self, assetId: int, networkId: int = 0, networkName: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.networkId = id
        self.networkName = networkName



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def exists(self) -> bool:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM `network` WHERE `network` = %s AND id_asset = %s", [
                self.networkName,
                self.assetId
            ])
            o = DBHelper.asDict(c)

            return bool(int(o[0]['c']))

        except Exception:
            return False
        finally:
            c.close()



    def info(self) -> dict:
        c = connection.cursor()
        try:
            c.execute("SELECT * FROM `network` WHERE `network` = %s AND id_asset = %s", [
                self.networkName,
                self.assetId
            ])

            return DBHelper.asDict(c)[0]

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    def delete(self) -> None:
        c = connection.cursor()
        try:
            c.execute("DELETE FROM `network` WHERE `network` = %s AND id_asset = %s", [
                self.networkName,
                self.assetId
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def add(assetId, networkName) -> int:
        c = connection.cursor()

        if networkName == "any":
            try:
                c.execute("INSERT INTO `network` (id_asset, `network`) VALUES (%s, %s)", [
                    assetId,
                    networkName
                ])

                return c.lastrowid

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            # Check if assetId/networkName is a valid Infoblox network (at the time of the insertion).
            infobloxNetworks = InfobloxNetwork.list(assetId)["data"] + InfobloxNetworkContainer.list(assetId)["data"]

            for v in infobloxNetworks:

                if v["network"] == networkName:
                    try:
                        c.execute("INSERT INTO `network` (id_asset, `network`) VALUES (%s, %s)", [
                            assetId,
                            networkName
                        ])

                        return c.lastrowid

                    except Exception as e:
                        raise CustomException(status=400, payload={"database": e.__str__()})
                    finally:
                        c.close()
