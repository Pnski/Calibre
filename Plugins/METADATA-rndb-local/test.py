from calibre.ebooks.metadata.sources.test import test_identify_plugin, title_test, test_identify

# Import your plugin package/module normally (CHANGE THIS to your real module name)
#import rndb_meta_local  # or whatever your package directory name is

test1 = [
    (
        {'title': "86—EIGHTY-SIX, Book 03: Run Through The Battlefront (Finish)", 'authors': ['Reki Kawahara']},
        [title_test("86—EIGHTY-SIX, Book 03: Run Through The Battlefront (Finish)")],
    )
]

test_identify_plugin('RNDB Local', test1)

test2 = [
    (
        {'title': 'Spice and Wolf'},
        [title_test('Spice')],
    ),
]
test_identify_plugin('RNDB Local', test2)