from infoblox.models.Permission.repository.Permission import Permission



class PermissionWorkflow(Permission):
    def __init__(self, permissionId: int = 0, *args, **kwargs):
        super().__init__(permissionId, *args, **kwargs)

        self.permissionTable = "group_workflow_network"
        self.privilegesList = "workflow"

        # Tables: group_workflow_network, identity_group, workflow, network
