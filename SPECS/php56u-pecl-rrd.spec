# IUS spec file for php56u-pecl-rrd, forked from:
#
# remirepo/fedora spec file for php-pecl-rrd
#
# Copyright (c) 2011-2015 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%global pecl_name rrd
%global ini_name  40-%{pecl_name}.ini
%global php_base php56u

%bcond_without zts

Summary:      PHP Bindings for rrdtool
Name:         %{php_base}-pecl-%{pecl_name}
Version:      1.1.3
Release:      1.ius%{?dist}
License:      BSD
Group:        Development/Languages
URL:          http://pecl.php.net/package/rrd

Source0:      http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRequires: %{php_base}-devel
BuildRequires: rrdtool
BuildRequires: pkgconfig(librrd) >= 1.3.0
BuildRequires: %{php_base}-pear

Requires(post): %{php_base}-pear
Requires(postun): %{php_base}-pear
Requires:     php(zend-abi) = %{php_zend_api}
Requires:     php(api) = %{php_core_api}

Conflicts:    rrdtool-php

# provide the stock name
Provides:     php-pecl-%{pecl_name} = %{version}
Provides:     php-pecl-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides:     php-%{pecl_name} = %{version}
Provides:     php-%{pecl_name}%{?_isa} = %{version}
Provides:     %{php_base}-%{pecl_name} = %{version}
Provides:     %{php_base}-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides:     php-pecl(%{pecl_name}) = %{version}
Provides:     php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:     %{php_base}-pecl(%{pecl_name}) = %{version}
Provides:     %{php_base}-pecl(%{pecl_name})%{?_isa} = %{version}

# conflict with the stock name
Conflicts: php-pecl-%{pecl_name} < %{version}

%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_provides_in: %filter_provides_in %{php_ztsextdir}/.*\.so$}
%{?filter_setup}


%description
Procedural and simple OO wrapper for rrdtool - data logging and graphing
system for time series data.


%prep
%setup -c -q

mv %{pecl_name}-%{version} NTS

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    -e '/LICENSE/s/role="doc"/role="src"/' \
    -i package.xml

cat > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF

%if %{with zts}
cp -r  NTS ZTS
%endif


%build
pushd NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}
popd

%if %{with zts}
pushd ZTS
%{_bindir}/zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
popd
%endif


%install
make install -C NTS INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

%if %{with zts}
make install -C ZTS INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Test & Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
%if %{with zts}
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}
%endif

%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

pushd NTS

# See https://bugzilla.redhat.com/1224530 - segfault on ARM
%ifnarch %{arm}
if pkg-config librrd --atleast-version=1.5.0
then
  : ignore test failed with rrdtool greater than 1.5
  rm tests/rrd_{016,017}.phpt
fi
if ! pkg-config librrd --atleast-version=1.4.0
then
  : ignore test failed with rrdtool less than 1.4
  rm tests/rrd_{012,017}.phpt
fi

make -C tests/data clean
make -C tests/data all

TEST_PHP_EXECUTABLE=%{_bindir}/php \
TEST_PHP_ARGS="-n -d extension_dir= -d extension=$PWD/modules/%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{_bindir}/php -n run-tests.php --show-diff
%endif

popd


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ]; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%files
%{!?_licensedir:%global license %%doc}
%license NTS/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{pecl_name}.xml

%if %{with zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Thu Jul 21 2016 Carl George <carl.george@rackspace.com> - 1.1.3-1.ius
- Port from Fedora to IUS
- Don't install/register tests
- Handle license properly
- Install package.xml as %%{pecl_name}.xml, not %%{name}.xml

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun May 24 2015 Remi Collet <remi@fedoraproject.org> - 1.1.3-6
- ignore failed tests with rrdtool 1.5
  FTBFS detected by Koschei, reported upstream
- skip test suite on arm

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 19 2014 Remi Collet <rcollet@redhat.com> - 1.1.3-4
- rebuild for https://fedoraproject.org/wiki/Changes/Php56

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Apr 24 2014 Remi Collet <rcollet@redhat.com> - 1.1.3-2
- add numerical prefix to extension configuration file

* Wed Jan 15 2014 Remi Collet <remi@fedoraproject.org> - 1.1.3-1
- Update to 1.1.3 (stable)
- drop merged patch

* Tue Jan 14 2014 Remi Collet <remi@fedoraproject.org> - 1.1.2-1
- Update to 1.1.2 (stable)
- install doc in pecl doc_dir
- install tests in pecl test_dir
- add conditional build of ZTS extension

* Mon Sep 09 2013 Remi Collet <remi@fedoraproject.org> - 1.1.1-2
- patch for build warning
- patch to fix test result with recent rrdtool

* Mon Sep 09 2013 Remi Collet <remi@fedoraproject.org> - 1.1.1-1
- Update to 1.1.1

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Mar 22 2013 Remi Collet <rcollet@redhat.com> - 1.1.0-3
- rebuild for http://fedoraproject.org/wiki/Features/Php55

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Aug 12 2012 Remi Collet <remi@fedoraproject.org> - 1.1.0-1
- Version 1.1.0 (stable), api 1.1.0 (stable)

* Tue Jul 31 2012 Remi Collet <remi@fedoraproject.org> - 1.0.5-4
- ignore test results (fails with rrdtool 1.4.7)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 19 2012 Remi Collet <remi@fedoraproject.org> - 1.0.5-3
- build against php 5.4

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Nov 18 2011 Remi Collet <remi@fedoraproject.org> 1.0.5-1
- update to 1.0.5
- change license from PHP to BSD

* Tue Aug 16 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.4-1
- Version 1.0.4 (stable) - API 1.0.4 (stable)
- fix filters

* Fri Apr 29 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.3-1
- Version 1.0.3 (stable) - API 1.0.3 (stable)
- no change in sources

* Wed Apr 20 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.2-1
- Version 1.0.2 (stable) - API 1.0.2 (stable)
- no change in sources

* Sat Apr 16 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.1-1
- Version 1.0.1 (stable) - API 1.0.1 (stable)
- no change in sources
- remove generated Changelog (only latest version, no real value)

* Tue Apr 12 2011 Remi Collet <Fedora@FamilleCollet.com> 1.0.0-1
- Version 1.0.0 (stable) - API 1.0.0 (stable)
- remove all patches merged by upstream

* Sat Mar 05 2011 Remi Collet <Fedora@FamilleCollet.com> 0.10.0-2
- improved patches
- implement rrd_strversion

* Fri Mar 04 2011 Remi Collet <Fedora@FamilleCollet.com> 0.10.0-1
- Version 0.10.0 (stable) - API 0.10.0 (beta)
- remove patches, merged upstream
- add links to 5 new upstream bugs

* Mon Jan 03 2011 Remi Collet <Fedora@FamilleCollet.com> 0.9.0-1
- Version 0.9.0 (beta) - API 0.9.0 (beta)
- initial RPM

