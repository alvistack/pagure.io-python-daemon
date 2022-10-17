# Copyright 2022 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

Name: python-daemon
Epoch: 100
Version: 2.3.1
Release: 1%{?dist}
BuildArch: noarch
Summary: Library to implement a well-behaved Unix daemon process
License: Apache-2.0
URL: https://pypi.org/project/python-daemon/#history
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: fdupes
BuildRequires: python-rpm-macros
BuildRequires: python3-devel
BuildRequires: python3-docutils
BuildRequires: python3-setuptools

%description
This library implements the well-behaved daemon specification of PEP
3143, "Standard daemon process library".

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
%py3_build

%install
%py3_install
find %{buildroot}%{python3_sitelib} -type f -name '*.pyc' -exec rm -rf {} \;
fdupes -qnrps %{buildroot}%{python3_sitelib}

%check

%if 0%{?suse_version} > 1500
%package -n python%{python3_version_nodots}-daemon
Summary: Library to implement a well-behaved Unix daemon process
Requires: python3
Requires: python3-setuptools
Requires: python3-lockfile >= 0.10
Provides: python3-daemon = %{epoch}:%{version}-%{release}
Provides: python3dist(daemon) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-daemon = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(daemon) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-daemon = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(daemon) = %{epoch}:%{version}-%{release}

%description -n python%{python3_version_nodots}-daemon
This library implements the well-behaved daemon specification of PEP
3143, "Standard daemon process library".

%files -n python%{python3_version_nodots}-daemon
%license  LICENSE.ASF-2
%{python3_sitelib}/*
%endif

%if !(0%{?suse_version} > 1500)
%package -n python3-daemon
Summary: Library to implement a well-behaved Unix daemon process
Requires: python3
Requires: python3-setuptools
Requires: python3-lockfile >= 0.10
Provides: python3-daemon = %{epoch}:%{version}-%{release}
Provides: python3dist(daemon) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}-daemon = %{epoch}:%{version}-%{release}
Provides: python%{python3_version}dist(daemon) = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}-daemon = %{epoch}:%{version}-%{release}
Provides: python%{python3_version_nodots}dist(daemon) = %{epoch}:%{version}-%{release}

%description -n python3-daemon
This library implements the well-behaved daemon specification of PEP
3143, "Standard daemon process library".

%files -n python3-daemon
%license  LICENSE.ASF-2
%{python3_sitelib}/*
%endif

%changelog
