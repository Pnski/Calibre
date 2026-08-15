from calibre.gui2.actions import InterfaceAction

from .UI.ui import Dialog

class InterfacePlugin(InterfaceAction):

    name = 'Better Export'

    action_spec = (name, None, 'Check for new books in Series', ())

    def genesis(self):
        icon = get_icons('images/icon.png', self.name)

        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        d = Dialog(self.gui, self.qaction.icon())
        d.show()