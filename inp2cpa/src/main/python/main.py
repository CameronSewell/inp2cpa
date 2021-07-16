from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property
from PyQt5.QtWidgets import QMainWindow

import sys
from mainwindow import inp2cpaApp

class AppContext(ApplicationContext):
    def run(self):
        # self.window.resize(1125, 720)
        self.window.show()
        return appctxt.app.exec_()

    def get_design(self):
        qtCreatorFile = self.get_resource("inp2cpaWindow.ui")
        return qtCreatorFile

    @cached_property
    def window(self):
        return inp2cpaApp(self.get_design())


if __name__ == "__main__":
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
    
