import logging
import os
import sys
from time import sleep


if __name__ == "__main__":
    os.environ.setdefault("EXPERIMENTOR_SETTINGS_MODULE", "calibration_settings")

    this_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(this_dir)

    from experimentor.core.app import ExperimentApp

    app = ExperimentApp(gui=True, logger=logging.INFO)

    while app.is_running:
        sleep(1)
    app.finalize()
