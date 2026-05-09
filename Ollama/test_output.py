import importlib
m = importlib.import_module('main')
oc = m.OutputCapture('Logs/temp_test_output.txt')
with oc as out:
    out.write('Test ASCII line\n')
    out.write('Checkmark: \u2713 and Cross: \u2717\n')
print('WROTE')
