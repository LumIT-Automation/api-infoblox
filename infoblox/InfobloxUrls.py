from django.urls import path

from .controllers import Root
from .controllers.Asset import Asset, Assets
from .controllers.Trigger import Trigger, Triggers, TriggerCondition, TriggerConditions
from .controllers.Infoblox import NetworksTree, NetworkContainers, NetworkContainerNetworks, Network, Networks, Ipv4, Ipv4s, Vlans, Vlan, AssignCloudNetwork, Ranges, Range, DismissCloudNetworks, ModifyCloudNetwork
from .controllers.Permission import Authorizations, IdentityGroups, IdentityGroup, Roles, Permission, Permissions
from .controllers.Configuration import Configuration
from .controllers.History import History, ActionHistory


urlpatterns = [
    path('', Root.RootController.as_view()),

    path('identity-group/<str:identityGroupIdentifier>/', IdentityGroup.PermissionIdentityGroupController.as_view(), name='permission-identity-group'),
    path('identity-groups/', IdentityGroups.PermissionIdentityGroupsController.as_view(), name='permission-identity-groups'),
    path('roles/', Roles.PermissionRolesController.as_view(), name='permission-roles'),
    path('permissions/', Permissions.PermissionsController.as_view(), name='permissions'),
    path('permission/<int:permissionId>/', Permission.PermissionController.as_view(), name='permission'),

    path('authorizations/', Authorizations.AuthorizationsController.as_view(), name='authorizations'),

    path('configuration/<str:configType>/', Configuration.ConfigurationController.as_view(), name='configuration'),

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
    path('<int:assetId>/assign-cloud-network/', AssignCloudNetwork.InfobloxAssignCloudNetworkController.as_view(), name='infoblox-network-assign-network'),
    path('<int:assetId>/modify-cloud-network/<str:networkAddress>/', ModifyCloudNetwork.InfobloxModifyCloudNetworkController.as_view(), name='infoblox-network-modify-network'),
    path('<int:assetId>/dismiss-cloud-networks/', DismissCloudNetworks.InfobloxDismissCloudNetworksController.as_view(), name='infoblox-network-dismiss-networks'),

    # Log history.
    path('history/', History.HistoryLogsController.as_view(), name='f5-log-history'),
    path('action-history/', ActionHistory.ActionHistoryLogsController.as_view(), name='f5-log-action-history'),
]
