Name:       automation-interface-api-infoblox-container
Version:    RH_VERSION
Release:    RH_RELEASE
Summary:    Automation Interface UI Backend, container image 

License:    GPLv3+
Source0:    RPM_SOURCE

Requires:   podman, buildah, at, cronie
Requires:   automation-interface-sso-container >= 2.0, automation-interface-log >= 1.2

BuildArch:  x86_64

%description
automation-interface-api-backend-container

%include %{_topdir}/SPECS/preinst.spec
%include %{_topdir}/SPECS/postinst.spec
%include %{_topdir}/SPECS/prerm.spec
%include %{_topdir}/SPECS/postrm.spec

%prep
%setup  -q #unpack tarball

%install
cp -rfa * %{buildroot}

%include %{_topdir}/SPECS/files.spec



