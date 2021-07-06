# ##############################################################################
#  Copyright (c) 2021 Aquiles Carattino, Dispertech B.V.                       #
#  start_lightsheet.py is part of disperscripts                                #
#  This file is released under an MIT license.                                 #
#  See LICENSE.md.MD for more information.                                        #
# ##############################################################################

import time

import yaml
from PyQt5.QtWidgets import QApplication

from LightSheet.models.experiment import LightSheetExperiment
from LightSheet.view.microscope_window import LightsheetWindow
from experimentor.lib.log import log_to_screen, get_logger

if __name__ == "__main__":
    logger = get_logger()
    handler = log_to_screen(logger=logger)
    experiment = LightSheetExperiment()
    experiment.load_configuration('lightsheet.yml', yaml.UnsafeLoader)
    executor = experiment.initialize()
    while executor.running():
        time.sleep(.1)

    app = QApplication([])
    microscope_window = LightsheetWindow(experiment)
    microscope_window.show()
    app.exec()
    experiment.finalize()
