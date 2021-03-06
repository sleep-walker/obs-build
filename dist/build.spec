#
# spec file for package build
#
# Copyright (c) 2016 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#
# needsrootforbuild
# needsbinariesforbuild


Name:           build
Summary:        A Script to Build SUSE Linux RPMs
License:        GPL-2.0+ and GPL-2.0
Group:          Development/Tools/Building
Version:        20160531
Release:        0
Source:         obs-build-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
%if 0%{?suse_version} > 1200
# required for test suite
BuildRequires:  build-mkbaselibs
%endif
# Keep the following dependencies in sync with obs-worker package
Requires:       bash
Requires:       binutils
Requires:       perl
Requires:       tar
%if 0%{?fedora}
Requires:       perl-MD5
Requires:       perl-TimeDate
%endif
Conflicts:      bsdtar < 2.5.5
%if 0%{?suse_version} > 1000
# None of them are actually required for core features.
# Perl helper scripts use them.
Recommends:     perl(Date::Language)
Recommends:     perl(Date::Parse)
Recommends:     perl(LWP::UserAgent)
Recommends:     perl(Pod::Usage)
Recommends:     perl(Time::Zone)
Recommends:     perl(URI)
Recommends:     perl(XML::Parser)
Recommends:     perl(Net::SSL)
Recommends:     perl(YAML)
Recommends:     perl(YAML::LibYAML)
Recommends:     bsdtar
Recommends:     qemu-linux-user
%endif

%if 0%{?suse_version} > 1120 || ! 0%{?suse_version}
Requires:       build-mkbaselibs
%endif

%if 0%{?suse_version} > 1120 || 0%{?mdkversion}
Recommends:     build-mkdrpms
%endif

%description
This package provides a script for building RPMs for SUSE Linux in a
chroot environment.


%if 0%{?suse_version} > 1120 || ! 0%{?suse_version}

%package mkbaselibs
Summary:        Tools to generate base lib packages
# NOTE: this package must not have dependencies which may break boot strapping (eg. perl modules)
Group:          Development/Tools/Building

%description mkbaselibs
This package contains the parts which may be installed in the inner build system
for generating base lib packages.

%package mkdrpms
Summary:        Tools to generate delta rpms
Group:          Development/Tools/Building
Requires:       deltarpm
# XXX: we wanted to avoid that but mkdrpms needs Build::Rpm::rpmq
Requires:       build

%description mkdrpms
This package contains the parts which may be installed in the inner build system
for generating delta rpm packages.

%endif

%define initvm_arch %{_host_cpu}
%if %{_host_cpu} == "i686"
%define initvm_arch i586
%endif
%package initvm-%{initvm_arch}
Summary:        Virtualization initializer for emulated cross architecture builds
Group:          Development/Tools/Building
Requires:       build
BuildRequires:  gcc
BuildRequires:  glibc-devel
Provides:       build-initvm
Obsoletes:      build-initvm
%if 0%{?suse_version} > 1200
BuildRequires:  glibc-devel-static
%endif

%description initvm-%{initvm_arch}
This package provides a script for building RPMs for SUSE Linux in a
chroot or a secure virtualized

%prep
%setup -q -n obs-build-%version

%build
%if 0%{?suse_version}
# initvm
make CFLAGS="$RPM_BUILD_FLAGS" initvm-all
%endif

%install
# initvm
%if 0%{?suse_version}
make DESTDIR=$RPM_BUILD_ROOT initvm-install
strip $RPM_BUILD_ROOT/usr/lib/build/initvm.*
export NO_BRP_STRIP_DEBUG="true"
chmod 0644 $RPM_BUILD_ROOT/usr/lib/build/initvm.*
%endif

# main
make DESTDIR=$RPM_BUILD_ROOT install
cd $RPM_BUILD_ROOT/usr/lib/build/configs/
%if "0%{?suse_version}" == "1315" && 0%{?is_opensuse}
# super special leap distro
 ln -s sl42.1.conf default.conf
%else
%if 0%{?suse_version}
%if 0%{?sles_version}
 ln -s sles%{sles_version}.conf default.conf
%else
 V=%suse_version
 ln -s sl${V:0:2}.${V:2:1}.conf default.conf
%endif
test -e default.conf || exit 1
%endif
%endif

%check
if [ `whoami` != "root" ]; then
  echo "WARNING: Not building as root, tests did not run!"
  exit 0
fi
# get back the default.conf link
cp -av $RPM_BUILD_ROOT/usr/lib/build/configs/default.conf configs/
# do not get confused when building this already with build:
export BUILD_IGNORE_2ND_STAGE=1
# use our own build code
export BUILD_DIR=$PWD
cd test
# target is autodetected
%if 0%{?sles_version}
echo "SLES config differs currently on purpose between OBS and build script."
echo "Skipping test case"
exit 0
%endif
%if 0%{?qemu_user_space_build}
echo "test suite is not prepared to run using qemu linux user"
echo "Skipping test case"
exit 0
%endif
./testbuild.sh /.build.binaries/

%files
%defattr(-,root,root)
%doc README
/usr/bin/build
/usr/bin/buildvc
/usr/bin/unrpm
/usr/lib/build
%config(noreplace) /usr/lib/build/emulator/emulator.sh
%{_mandir}/man1/build.1*
%{_mandir}/man1/unrpm.1*
%{_mandir}/man1/vc.1*
%if 0%{?suse_version}
%exclude /usr/lib/build/initvm.*
%endif

%if 0%{?suse_version} > 1120 || ! 0%{?suse_version}
%exclude /usr/lib/build/mkbaselibs
%exclude /usr/lib/build/baselibs*
%exclude /usr/lib/build/mkdrpms

%files mkbaselibs
%defattr(-,root,root)
%dir /usr/lib/build
/usr/lib/build/mkbaselibs
/usr/lib/build/baselibs*

%files mkdrpms
%defattr(-,root,root)
%dir /usr/lib/build
/usr/lib/build/mkdrpms
%endif

%if 0%{?suse_version}
%files initvm-%{initvm_arch}
%defattr(-,root,root)
/usr/lib/build/initvm.*
%endif

%changelog
