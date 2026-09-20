APPIMAGE="$(pwd)/Cursor-x86_64.AppImage"

sudo tee /etc/apparmor.d/cursor-appimage << EOF
abi <abi/4.0>,
include <tunables/global>

profile cursor-appimage $APPIMAGE flags=(unconfined) {
  userns,
  include if exists <local/cursor-appimage>
}
EOF

sudo systemctl reload apparmor

update-desktop-database ~/.local/share/applications/
