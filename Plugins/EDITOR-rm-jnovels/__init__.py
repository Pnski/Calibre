from calibre.customize import EditBookToolPlugin

class RMJnovels(EditBookToolPlugin):

    name = "JNovels Remover"
    description = "Automated removal for JNovels."
    author = "Nyk"
    version = (0, 1, 1)
    minimum_calibre_version = (9, 0, 0)
    supported_platforms = ["windows", "osx", "linux"]