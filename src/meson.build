pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
modulair = join_paths(pkgdatadir, 'timetable')
gnome = import('gnome')

# GTK4 dependency
gtk_dep = dependency('gtk4', version: '>= 4.0')

gnome.compile_resources('timetable',
  'timetable.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'timetable.in',
  output: 'timetable',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

timetable_sources = [
  '__init__.py',
  'config.py',
  'DayGrid.py',
  'main.py',
  'MainWindow.py',
  'CalendarWindow.py',
  'SequenceWindow.py',
  'TimeTableStore.py',
  'WeekGrid.py',
  'utils.py'
]

install_data(timetable_sources, install_dir: moduledir)
