from calibre.customize import StoreBase

class ElsciStore(StoreBase):

    name = "Elscione Store"
    description = "Searches for books on Elscione"
    author = "Nyk"
    version = (0, 1, 0)
    minimum_calibre_version = (9, 0, 0)
    formats = ["EPUB", "PDF"]
    drm_free_only = True

    actual_plugin       = __name__ + '.main:ElsciStorePlugin'