r = run_command('/app/bin/ducktype', 'index.duck',
    				'create_classes.duck',
    				'memos.duck',
    				'jumping.duck',
    				'exceptions.duck',
    				'day-off.duck')
if r.returncode() != 0
  # it failed
endif
output = r.stdout().strip()
errortxt = r.stderr().strip()

