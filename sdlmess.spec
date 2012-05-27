Name:			sdlmess
Version:		0.146
#define sversion	%(sed -e "s/\\.//" <<<%{version})
%define sversion	%(sed -r -e "s/\\.//" -e "s/(.*)u(.)/\\1/" <<<%{version})
%define uversion	%(sed -r -e "s/(.*u)(.)/\\2/;t;c\\0" <<<%{version})
Release:		%mkrel 1

Summary:	SDL MESS emulates a large variety of different systems
License:	Freeware
Group:		Emulators
URL:		http://www.mess.org/
#http://mamedev.org/downloader.php?&file=mame%{sversion}s.zip
Source0:	mame%{sversion}s.zip
Source1:	http://www.mess.org/files/mess%{sversion}s.zip
Source2:	sdlmess-wrapper
Source3:	sdlmame-extra.tar.bz2
#Sources 10+ : u1, u2 etc zip files containing changelogs and patches (if any)
%if %{uversion}
%(for ((i=1 ; i<=%{uversion} ; i++)) ; do echo Source$((9+i)):  http://www.mess.org/files/mess%{sversion}u${i}_diff.zip ;done)
%endif

# Needed to workaround gcc 4.4.x x86_64 internal compiler error
Patch0:		sdlmame-0.146-gcc4.4-ice.patch

BuildRequires:	SDL-devel
BuildRequires:	SDL_ttf-devel
BuildRequires:	expat-devel
BuildRequires:	zlib-devel
BuildRequires:	libxinerama-devel
BuildRequires:	gtk2-devel
BuildRequires:	libGConf2-devel
BuildRequires:	perl
# Workaround
BuildRequires:	libxrender-devel >= 0.9.6

%description
SDL MESS is a free emulator which emulates a large variety of different 
systems (computers and home entertainment systems).
It uses SDL, and is based on MESS.

%prep
%setup -c -n %{name}-%{version} -q
unzip -qq mame.zip
unzip -qqo %{SOURCE1}
%if %{mdvver} < 201100
%ifarch x86_64
%patch0 -p1
%endif
%endif

#files missing : ui.bdf, keymaps
tar xvjf %{SOURCE3}
#fixes doc line endings, + needed before patching
find . -type f -not -name "*.png" -not -name "*.gif" -not -name "*.bmp" \
 -not -name "*.ico" -not -name "*.zip" | xargs perl -pi -e 's/\r\n?/\n/g'
%if %{uversion}
%(for ((i=1 ; i<=%{uversion} ; i++)) ; do echo "unzip -qq %{SOURCE$((9+i))}" ; echo "perl -pi -e 's/\r\n/\n/g' mess%{sversion}u${i}.diff" ; echo "patch -p0 -N -s --fuzz=0 -E < mess%{sversion}u${i}.diff" ; done)
%endif

%build
#fullname is prefix+name+suffix+suffix64+suffixdebug(+suffixexe)
#optimizing for specific processor adds suffixes:
#DEBUG=1 to build the debugger
#SYMBOLS=1 to build a -debug package
#set ARCHOPTS for architecture-specific optimizations
#(-march=,-msse3,-mcpu=,...)
#Arch is auto-detected now, DRC options are set accordingly
#no need for PTR64=1, PPC=1, X86_MIPS3_DRC=, X86_PPC_DRC=, etc
%make all TARGET=mess \
 PREFIX="sdl" \
 NOWERROR=1 \
 BUILD_ZLIB= \
 BUILD_EXPAT= \
 OPT_FLAGS="%{optflags}"

%install
%__rm -rf %{buildroot}
%__install -d -m 755 %{buildroot}%{_gamesbindir}
%__install -m 755 sdlmess* %{buildroot}/%{_gamesbindir}/sdlmess.real

#various directories and files
%__install -d -m 755 %{buildroot}%{_gamesdatadir}/sdlmess/artwork
%__install -m 644 artwork/* %{buildroot}%{_gamesdatadir}/sdlmess/artwork/
%__install -d -m 755 %{buildroot}%{_gamesdatadir}/sdlmess/hash
%__install -m 644 hash/* %{buildroot}%{_gamesdatadir}/sdlmess/hash/

#keymaps
%__install -d -m 755 %{buildroot}%{_gamesdatadir}/sdlmess/keymaps
%__install -m 644 keymaps/* %{buildroot}%{_gamesdatadir}/sdlmess/keymaps/

#font
%__install -m 644 ui.bdf %{buildroot}%{_gamesdatadir}/sdlmess/

#sysinfo.dat
%__install -m 644 sysinfo.dat %{buildroot}%{_gamesdatadir}/sdlmess/

#cfg, diff, nvram, obj, snap in home only

#tools
#useful to manage roms
%__install -m 755 chdman %{buildroot}%{_gamesbindir}/chdman-sdlmess
%__install -m 755 romcmp %{buildroot}%{_gamesbindir}/romcmp-sdlmess
#useful to create a new keymap
%__install -m 755 testkeys %{buildroot}%{_gamesbindir}/testkeys-sdlmess
#other tools : dat2html, messtest, messdocs, imgtool, jedutil, makemeta, regrep, srcclean

#wrapper
%__install -m 755 %{SOURCE2} %{buildroot}%{_gamesbindir}/sdlmess

%files
%defattr(0644,root,root,0755)
%doc docs/*
%attr(0755,root,games) %{_gamesbindir}/sdlmess*
%attr(0755,root,games) %{_gamesbindir}/*-sdlmess
%{_gamesdatadir}/sdlmess

%clean
%__rm -rf %{buildroot}

