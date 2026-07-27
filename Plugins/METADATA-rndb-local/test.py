from calibre.ebooks.metadata.sources.test import test_identify_plugin, title_test, test_identify

# Import your plugin package/module normally (CHANGE THIS to your real module name)
#import rndb_meta_local  # or whatever your package directory name is

test1 = [
    (
        {'title': "UNKNOWN", 'authors': ['Reki Kawahara']},
        [title_test("UNKNOWN")],
    )
]

test_identify_plugin('RNDB Local', test1)