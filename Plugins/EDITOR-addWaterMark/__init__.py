from calibre.customize import EditBookToolPlugin

class addWaterMark(EditBookToolPlugin):

    name = "Add Water Marks"
    description = "Adding watermarks to your epub's"
    author = "Nyk"
    version = (0, 1, 0)
    minimum_calibre_version = (9, 0, 0)
    supported_platforms = ["windows", "osx", "linux"]