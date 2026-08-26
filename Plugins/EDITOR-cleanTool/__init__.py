from calibre.customize import EditBookToolPlugin

class cleaningTool(EditBookToolPlugin):

    name = "Cleaning Tool"
    description = "Automatically cleaning unecessary stuff from epubs, and trys to give them a uniform look."
    author = "Nyk"
    version = (0, 1, 3)
    minimum_calibre_version = (9, 0, 0)
    supported_platforms = ["windows", "osx", "linux"]