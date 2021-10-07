from infoblox.helpers.Lang import Lang
from infoblox.helpers.Log import Log


class DataFilter:
    @staticmethod
    def filter(data: dict, field: str = "", value: str = "") -> dict:
        if data:
            # Filters the data dictionary according to the filter pattern (field) and value.
            if field and value:
                j = 0
                leaf = data
                leafFieldElement = ""
                filteredData = None
                dl = list()

                try:
                    field = Lang.stripQuotes(field)
                    value = Lang.stripQuotes(value)

                    # Get the data leaf element according to field.
                    # For example: field=data.x.y.z -> leaf=data['x']['y'] (it's a list); leafFieldElement=z.
                    valueElements = field.split(".")

                    if valueElements[0] == "data": # data.x.y.z
                        # "data." must be passed, but it's not reflecting our real internal data structure, so removing it.
                        valueElements.pop(0)

                        for v in valueElements: # x.y.z
                            leafFieldElement = v
                            if v in leaf:
                                if not isinstance(leaf[v], str):
                                    leaf = leaf[v]

                        # Apply the filter to this leaf element and get the filteredData list.
                        if leaf:
                            filteredData = DataFilter.getFilteredData(leaf, leafFieldElement, value)

                        # Overwrite data.
                        if len(valueElements) == 1:
                            # data = filteredData

                            j = 1
                            dl.append(filteredData)
                        else:
                            # data = {
                            #    "x": {
                            #        "y": filteredData
                            #    }
                            # }

                            valueElements.pop()
                            valueElements.reverse()

                            for v in valueElements:
                                if j == 0:
                                    # Assign the filteredData list to the leaf dictionary.
                                    dl.append({v: filteredData})  # dl[0]['v'] = filteredData.
                                else:
                                    dl.append({v: dl[j - 1]})

                                j = j + 1

                        data = dl[j - 1]
                    else:
                        data = []
                except Exception:
                    data = []

        return data



    @staticmethod
    def getFilteredData(leafObject: dict, leafFieldElement: str, value: str) -> object:
        f = []

        if isinstance(leafObject, list):
            filteredData = []

            for item in leafObject:
                if leafFieldElement in item:
                    if item[leafFieldElement] == value:
                        if item[leafFieldElement] == value:
                            filteredData.append(item)

            f = filteredData

        if isinstance(leafObject, dict):
            filteredData = {}

            for k, v in leafObject.items():
                if k == leafFieldElement and v == value:
                    filteredData = leafObject

            f = filteredData

        return f
