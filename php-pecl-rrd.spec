# spec file for php-pecl-rrd
#
# Copyright (c) 2011-2013 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}

%global pecl_name rrd

Summary:      PHP Bindings for rrdtool
Name:         php-pecl-rrd
Version:      1.1.1
Release:      2%{?dist}
License:      BSD
Group:        Development/Languages
URL:          http://pecl.php.net/package/rrd

Source0:      http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

# Fix build warning   http://svn.php.net/viewvc?view=revision&revision=331314
# Fix test strictness http://svn.php.net/viewvc?view=revision&revision=331315
Patch0:        %{pecl_name}-svn.patch

BuildRequires: php-devel >= 5.3.2
BuildRequires: rrdtool
BuildRequires: rrdtool-devel >= 1.3.0
BuildRequires: php-pear

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:     php(zend-abi) = %{php_zend_api}
Requires:     php(api) = %{php_core_api}

Conflicts:    rrdtool-php
Provides:     php-pecl(%{pecl_name}) = %{version}
Provides:     php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:     php-%{pecl_name} = %{version}%{?pre}
Provides:     php-%{pecl_name}%{?_isa} = %{version}%{?pre}


# Filter private shared object
%{?filter_provides_in: %filter_provides_in %{_dir}/.*\.so$}
%{?filter_setup}


%description
Procedural and simple OO wrapper for rrdtool - data logging and graphing
system for time series data.


%prep 
%setup -c -q

cd %{pecl_name}-%{version}

%patch0 -p3 -b .svn

extver=$(sed -n '/#define PHP_RRD_VERSION/{s/.* "//;s/".*$//;p}' php_rrd.h)
if test "x${extver}" != "x%{version}%{?pre}"; then
   : Error: Upstream version is ${extver}, expecting %{version}.
   exit 1
fi
cd ..

cat > %{pecl_name}.ini << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF


%build
cd %{pecl_name}-%{version}
phpize
%configure

make %{?_smp_mflags}


%install
make install -C %{pecl_name}-%{version}%{?pre} INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
install -D -m 644 %{pecl_name}.ini %{buildroot}%{_sysconfdir}/php.d/%{pecl_name}.ini

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml


%check
cd %{pecl_name}-%{version}
php --no-php-ini \
    --define extension_dir=modules \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}


make -C tests/data clean
make -C tests/data all
make test NO_INTERACTION=1 | tee rpmtests.log

if  grep -q "FAILED TEST" rpmtests.log; then
  for t in tests/*diff; do
     echo "*** FAILED: $(basename $t .diff)"
     diff -u tests/$(basename $t .diff).exp tests/$(basename $t .diff).out || :
  done

  exit 1
fi


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%files
%doc %{pecl_name}-%{version}/CREDITS %{pecl_name}-%{version}/LICENSE
%config(noreplace) %{_sysconfdir}/php.d/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{name}.xml


%changelog
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

