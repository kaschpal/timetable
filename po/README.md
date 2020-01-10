# Create POT-Files

cd "~/.var/app/org.gnome.Builder/cache/gnome-builder/projects/Timetable/builds/de.uleutner.timetable.json-flatpak-org.gnome.Platform-x86_64-3.32-master"
ninja timetable-pot
ninja timetable-update-po

# in .po-files
# change 

"Content-Type: text/plain; charset=ASCII\n"

# to

"Content-Type: text/plain; charset=UTF-8\n"

