# ohmi_audit
A program for managing audits by a certification company


## Running all tests at once in PyCharm

There are several convenient ways to run the entire test suite from PyCharm. Pick the one you prefer.

1) Using a Django Tests run configuration (recommended)
- Enable Django support (one-time):
  - File > Settings > Languages & Frameworks > Django
  - Check “Enable Django support”
  - Project root: D:\Study\Projects\PycharmProjects\ohmi_audit
  - Settings: ohmi_audit.settings
  - Manage script: D:\Study\Projects\PycharmProjects\ohmi_audit\manage.py
- Create a run configuration:
  - Run > Edit Configurations… > + > Django tests
  - Name: All tests
  - Target: All tests (or leave default)
  - Working directory: D:\Study\Projects\PycharmProjects\ohmi_audit
  - Apply and Run. This will execute all tests across the project.

2) Run from the Project tool window
- In the Project panel, right‑click the tests folder (D:\Study\Projects\PycharmProjects\ohmi_audit\tests)
- Choose “Run tests” (PyCharm will use the configured Django test runner) to execute the entire suite at once.

3) Using the manage.py tool inside PyCharm
- Tools > Run manage.py Task…
- Type: test and press Enter (optionally add -v 2 for verbose)
- This runs the same as command line but inside PyCharm.

4) Command line alternative (works the same)
- From the project root, run:
  - Windows: py -m pip install -r requirements.txt (first time only)
  - py manage.py test -v 2
  - Or: python manage.py test -v 2

Tips
- Run with Coverage: click the dropdown next to the Run button and select “Run with Coverage” to see per‑file coverage inside PyCharm.
- Test runner detection: If PyCharm doesn’t recognize tests as Django tests, ensure Django support is enabled (see step 1) and that DJANGO_SETTINGS_MODULE is ohmi_audit.settings.
- Environments: If you use a virtualenv/Poetry interpreter, make sure the PyCharm interpreter points to it so dependencies are available.
