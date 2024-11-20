from django.urls import path

from .controllers import Root, RawTxtController
from .controllers.Asset import Asset, Assets
from .controllers.Trigger import Trigger, Triggers, TriggerCondition, TriggerConditions
from .controllers.Infoblox import NetworksTree, NetworkContainers, NetworkContainerNetworks, Network, Networks, Ipv4, Ipv4s, Vlans, Vlan, Ranges, Range
from .controllers.Infoblox.Usecases import DeleteAccountCloudNetworks, AssignCloudNetwork, ModifyCloudNetwork, \
    CloudNetworkExtAttrs, DeleteCloudNetwork, ModifyCloudNetworksAccount
from .controllers.Permission import Authorizations, IdentityGroups, IdentityGroup, Roles, Permission, Permissions, AuthorizationsWorkflow, Workflows, PermissionsWorkflow, PermissionWorkflow
from .controllers.Configuration import Configurations, Configuration
from .controllers.History import History, ActionHistory
from .controllers.Helpers import Locks


urlpatterns = [
    path('', Root.RootController.as_view()),

    path('identity-group/<str:identityGroupIdentifier>/', IdentityGroup.PermissionIdentityGroupController.as_view(), name='permission-identity-group'),
    path('identity-groups/', IdentityGroups.PermissionIdentityGroupsController.as_view(), name='permission-identity-groups'),
    path('roles/', Roles.PermissionRolesController.as_view(), name='permission-roles'),
    path('permissions/', Permissions.PermissionsController.as_view(), name='permissions'),
    path('permission/<int:permissionId>/', Permission.PermissionController.as_view(), name='permission'),

    path('workflows/', Workflows.WorkflowsController.as_view(), name='workflows'),
    path('permissions-workflow/', PermissionsWorkflow.PermissionsWorkflowController.as_view(), name='permissions-workflow'),
    path('permission-workflow/<int:permissionId>/', PermissionWorkflow.PermissionWorkflowController.as_view(), name='permission-workflow'),

    path('authorizations/', Authorizations.AuthorizationsController.as_view(), name='authorizations'),
    path('workflow-authorizations/', AuthorizationsWorkflow.AuthorizationsWorkflowController.as_view(), name='workflow-authorizations'),

    path('doc/<str:fileName>/', RawTxtController.InfobloxRawTxtController.as_view(), name='txt'),

    path('configurations/', Configurations.ConfigurationsController.as_view(), name='configuration'),
    path('configuration/<int:configId>/', Configuration.ConfigurationController.as_view(), name='configuration'),

    path('assets/', Assets.InfobloxAssetsController.as_view(), name='infoblox-assets'),
    path('asset/<int:assetId>/', Asset.InfobloxAssetController.as_view(), name='infoblox-asset'),

    path('triggers/', Triggers.InfobloxTriggersController.as_view(), name='infoblox-triggers'),
    path('trigger/<int:triggerId>/', Trigger.InfobloxTriggerController.as_view(), name='infoblox-trigger'),
    path('trigger/<int:triggerId>/conditions/', TriggerConditions.InfobloxTriggersConditionsController.as_view(), name='infoblox-trigger-conditions'),
    path('trigger/<int:triggerId>/condition/<int:conditionId>/', TriggerCondition.InfobloxTriggerConditionController.as_view(), name='infoblox-trigger-condition'),

    path('<int:assetId>/tree/', NetworksTree.InfobloxNetworksTreeController.as_view(), name='infoblox-network-tree'),
    path('<int:assetId>/vlan/<int:vlanId>/', Vlan.InfobloxVlanController.as_view(), name='infoblox-vlan'),
    path('<int:assetId>/vlans/', Vlans.InfobloxVlansController.as_view(), name='infoblox-vlans'),
    path('<int:assetId>/network/<str:networkAddress>/', Network.InfobloxNetworkController.as_view(), name='infoblox-network-info'),
    path('<int:assetId>/networks/', Networks.InfobloxNetworksController.as_view(), name='infoblox-networks'),
    path('<int:assetId>/network-container/<str:networkAddress>/<str:mask>/networks/', NetworkContainerNetworks.InfobloxNetworkContainerNetworksController.as_view(), name='infoblox-network-container-networks'),
    path('<int:assetId>/network-containers/', NetworkContainers.InfobloxNetworkContainersController.as_view(), name='infoblox-network-containers'),
    path('<int:assetId>/ranges/', Ranges.InfobloxRangesController.as_view(), name='infoblox-ranges'),
    path('<int:assetId>/range/<str:startAddr>/<str:endAddr>/', Range.InfobloxRangeController.as_view(), name='infoblox-range'),
    path('<int:assetId>/ipv4/<str:ipv4address>/', Ipv4.InfobloxIpv4Controller.as_view(), name='infoblox-ipv4'),
    path('<int:assetId>/ipv4s/', Ipv4s.InfobloxIpv4sController.as_view(), name='infoblox-ipv4s'),

    # Use cases.
    path('<int:assetId>/assign-cloud-network/', AssignCloudNetwork.InfobloxAssignCloudNetworkController.as_view(), name='infoblox-assign-cloud-network'),
    path('<int:assetId>/modify-cloud-network/<str:networkAddress>/', ModifyCloudNetwork.InfobloxModifyCloudNetworkController.as_view(), name='infoblox-modify-cloud-network'),
    path('<int:assetId>/modify-account-cloud-network/<str:accountId>/', ModifyCloudNetworksAccount.InfobloxModifyCloudNetworksAccountController.as_view(), name='infoblox-modify-cloud-network-account'),
    path('<int:assetId>/delete-cloud-network/<str:networkAddress>/', DeleteCloudNetwork.InfobloxDeleteCloudNetworkController.as_view(), name='infoblox-delete-cloud-network'),
    path('<int:assetId>/delete-account-cloud-networks/', DeleteAccountCloudNetworks.InfobloxDeleteAccountCloudNetworksController.as_view(), name='infoblox-delete-account-cloud-networks'),
    path('<int:assetId>/list-cloud-extattrs/<str:extattr>/', CloudNetworkExtAttrs.InfobloxCloudNetworkExtAttrsController.as_view(), name='infoblox-cloud-extattrs'),

    # Locks
    path('locks/', Locks.InfobloxWorkflowLocksController.as_view(), name='infoblox-workflow-locks'),

    # Log history.
    path('history/', History.HistoryLogsController.as_view(), name='infoblox-log-history'),
    path('action-history/', ActionHistory.ActionHistoryLogsController.as_view(), name='infoblox-log-action-history'),
]
