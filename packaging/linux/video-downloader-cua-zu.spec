%global debug_package %{nil}

Name:           video-downloader-cua-zu
Version:        %{app_version}
Release:        1%{?dist}
Summary:        Desktop video downloader for supported websites
License:        MIT
URL:            https://github.com/XxZuPenguinxX/Video-Downloader-Cua-Zu
Source0:        video-downloader-cua-zu-bundle.tar.gz
Source1:        video-downloader-cua-zu.desktop
Source2:        LICENSE
BuildArch:      x86_64
Requires:       glibc >= 2.35
Requires:       libX11
Requires:       libXext
Requires:       libXrender
Requires:       libXft
Requires:       fontconfig
Requires:       zlib

%description
A desktop video downloader with English and Vietnamese interface options.

%prep
%setup -q -n video-downloader-cua-zu

%build

%install
install -d %{buildroot}/opt/video-downloader-cua-zu
cp -a . %{buildroot}/opt/video-downloader-cua-zu/
install -D -m 0755 /dev/stdin %{buildroot}/usr/bin/video-downloader-cua-zu <<'EOF'
#!/bin/sh
exec /opt/video-downloader-cua-zu/video-downloader-cua-zu "$@"
EOF
install -D -m 0644 %{SOURCE1} \
    %{buildroot}/usr/share/applications/video-downloader-cua-zu.desktop
install -D -m 0644 %{SOURCE2} %{buildroot}/usr/share/licenses/video-downloader-cua-zu/LICENSE

%files
/opt/video-downloader-cua-zu
/usr/bin/video-downloader-cua-zu
/usr/share/applications/video-downloader-cua-zu.desktop
/usr/share/licenses/video-downloader-cua-zu/LICENSE

%changelog
* Thu Oct 15 2026 Video Downloader Cua Zu contributors - %{app_version}-1
- Initial distro package
