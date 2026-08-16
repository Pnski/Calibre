from calibre.customize import InterfaceActionBase

class rndbseries(InterfaceActionBase):

    name = "Better Export"
    description = "Exporting epub's with new settings"
    author = "Nyk"
    version = (0, 1, 1)
    minimum_calibre_version = (9, 0, 0)

    actual_plugin       = __name__ + '.main:InterfacePlugin'

    def is_customizable(self) -> bool:
        '''
        True to enable customization via
        Preferences->Plugins
        '''
        return False