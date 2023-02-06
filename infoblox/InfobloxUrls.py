from django.urls import path

from .controllers import Root
from .controllers.Infoblox.Asset import Asset, Assets
from .controllers.Infoblox import NetworksTree, NetworkContainers, NetworkContainerNetworks, Network, Networks, Ipv4, Ipv4s, Vlans, Vlan
from .controllers.Permission import Authorizations, IdentityGroups, IdentityGroup, Roles, Permission, Permissions
from .controllers import History


urlpatterns = [
    path('', Root.RootController.as_view()),

    path('identity-group/<str:identityGroupIdentifier>/', IdentityGroup.PermissionIdentityGroupController.as_view(), name='permission-identity-group'),
    path('identity-groups/', IdentityGroups.PermissionIdentityGroupsController.as_view(), name='permission-identity-groups'),
    path('roles/', Roles.PermissionRolesController.as_view(), name='permission-roles'),
    path('permissions/', Permissions.PermissionsController.as_view(), name='permissions'),
    path('permission/<int:permissionId>/', Permission.PermissionController.as_view(), name='permission'),

    path('authorizations/', Authorizations.AuthorizationsController.as_view(), name='authorizations'),

    path('assets/', Assets.InfobloxAssetsController.as_view(), name='infoblox-assets'),
    path('asset/<int:assetId>/', Asset.InfobloxAssetController.as_view(), name='infoblox-asset'),

    path('<int:assetId>/tree/', NetworksTree.InfobloxNetworksTreeController.as_view(), name='infoblox-network-tree'),
    path('<int:assetId>/vlan/<int:vlanId>/', Vlan.InfobloxVlanController.as_view(), name='infoblox-vlans'),
    path('<int:assetId>/vlans/', Vlans.InfobloVlansController.as_view(), name='infoblox-vlans'),
    path('<int:assetId>/network/<str:networkAddress>/', Network.InfobloxNetworkController.as_view(), name='infoblox-network-info'),
    path('<int:assetId>/networks/', Networks.InfobloxNetworksController.as_view(), name='infoblox-networks'),
    path('<int:assetId>/network-container/<str:networkAddress>/<str:mask>/networks/', NetworkContainerNetworks.InfobloxNetworkContainerNetworksController.as_view(), name='infoblox-network-container-info'),
    path('<int:assetId>/network-containers/', NetworkContainers.InfobloxNetworkContainersController.as_view(), name='infoblox-network-containers'),
    path('<int:assetId>/ipv4/<str:ipv4address>/', Ipv4.InfobloxIpv4Controller.as_view(), name='infoblox-ipv4'),
    path('<int:assetId>/ipv4s/', Ipv4s.InfobloxIpv4sController.as_view(), name='infoblox-ipv4s'),

    # Log history.
    path('history/', History.HistoryLogsController.as_view(), name='f5-log-history'),
]
