from calibre.customize import InterfaceActionBase

class rndbseries(InterfaceActionBase):

    name = "RNDB Series Checker"
    description = "Checks local series and all releases"
    author = "Nyk"
    version = (0, 1, 0)
    minimum_calibre_version = (9, 0, 0)

    actual_plugin       = __name__ + '.ui:InterfacePlugin'

# For testing, run from command line with this:
# calibre-debug -e __init__.py
if __name__ == '__main__':
    try:
        from qt.core import QApplication
    except ImportError:
        from PyQt5.Qt import QApplication
    from calibre.gui2.preferences import test_widget
    app = QApplication([])
    test_widget('Advanced', 'Plugins')