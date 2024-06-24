from __future__ import annotations
from typing import List

from infoblox.models.Permission.Privilege import Privilege

from infoblox.models.Permission.repository.Workflow import Workflow as Repository
from infoblox.models.Permission.repository.WorkflowPrivilege import WorkflowPrivilege as WorkflowPrivilegeRepository

from infoblox.helpers.Misc import Misc


class Workflow:
    def __init__(self, id: int = 0, workflow: str = "", loadPrivilege: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.workflow: str = workflow
        self.description: str = ""

        self.privileges: List[Privilege] = []

        self.__load(loadPrivilege=loadPrivilege)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def repr(self):
        return Misc.deepRepr(self)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(loadPrivilege: bool = True, selectWorkflow: list = None) -> List[Workflow]:
        selectWorkflow = selectWorkflow or []
        workflows = []

        try:
            for w in Repository.list(selectWorkflows=selectWorkflow):
                workflows.append(
                    Workflow(id=w["id"], loadPrivilege=loadPrivilege)
                )

            return workflows
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self, loadPrivilege: bool = True) -> None:
        try:
            info = Repository.get(id=self.id, workflow=self.workflow)

            if loadPrivilege:
                for privilegeId in WorkflowPrivilegeRepository.workflowPrivileges(workflowId=self.id):
                    self.privileges.append(
                        Privilege(privilegeId)
                    )
            else:
                del self.privileges

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
