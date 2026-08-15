"""
POST
{"pageProperties":{"resultType":31,"itemType":1,"listId":5334710,"listSku":null,"itemsPerPage":50,"searchQuery":null,"startDateAdded":null},"sortProperties":{"overrideSortColumn":1,"overrideSortDirection":0},"filterProperties":{"hasFiltersSelected":false,"filteredListItemIds":[],"showHidden":false}}
https://www.edelweiss.plus/api/list-views/items
POST
apiView: standard,advanced
["1642736236","1642736260","1642736252","1642736244","1642735965","164273618X","1642735973","1642736198","1642735981","1642736120","1642736279","1642736023","1642736074","1642735779","1642735760","1642735906","1642735744","1642735817","1642735752","1642735795","1642735736","1642735809","1642735493","1642735787","1642735434","1642735515","164273621X","1642735523","1642735418","1642735485","1642735507","1642735469","1642736007","164273540X","1642734985","1642735442","1642735396","1642735477","1642735043","1642735590","1642735450","1642735604","1642735140","1642735884","1642734861","1642735426","1642734993","1642735000","1642734942","1642734896"]
https://www.edelweiss.plus/api/v2/products/descriptions?apiView=standard,advanced
curl 'https://www.edelweiss.plus/api/v1/collaborativeTitleLists/titles' \

  --data-raw '["1642736236","1642736260","1642736252","1642736244","1642735965","164273618X","1642735973","1642736198","1642735981","1642736120","1642736279","1642736023","1642736074","1642735779","1642735760","1642735906","1642735744","1642735817","1642735752","1642735795","1642735736","1642735809","1642735493","1642735787","1642735434","1642735515","164273621X","1642735523","1642735418","1642735485","1642735507","1642735469","1642736007","164273540X","1642734985","1642735442","1642735396","1642735477","1642735043","1642735590","1642735450","1642735604","1642735140","1642735884","1642734861","1642735426","1642734993","1642735000","1642734942","1642734896"]'
curl "https://www.edelweiss.plus/api/v2/products/images,categories,videos,dynamicAttributes,links,audienceRanges,catalogAttributes,completionSummary,honors,contributors,related,subrights,product?apiView=standard,advanced&catalogId=5334710" -ContentType 'application/json' -d '["1642736236","1642736260","1642736252","1642736244","1642735965","164273618X","1642735973","1642736198","1642735981","1642736120","1642736279","1642736023","1642736074","1642735779","1642735760","1642735906","1642735744","1642735817","1642735752","1642735795","1642735736","1642735809","1642735493","1642735787","1642735434","1642735515","164273621X","1642735523","1642735418","1642735485","1642735507","1642735469","1642736007","164273540X","1642734985","1642735442","1642735396","1642735477","1642735043","1642735590","1642735450","1642735604","1642735140","1642735884","1642734861","1642735426","1642734993","1642735000","1642734942","1642734896"]'
"""

import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode

base = "https://www.edelweiss.plus/api/list-views/items"

data = json.dumps(
    {
        "pageProperties": {
            "resultType": 31,
            "itemType": 1,
            "listId": 5334710,
            "listSku": None,
            "itemsPerPage": 500,
            "searchQuery": None,
            "startDateAdded": None,
        },
        "sortProperties": {"overrideSortColumn": 1, "overrideSortDirection": 0},
        "filterProperties": {
            "hasFiltersSelected": False,
            "filteredListItemIds": [],
            "showHidden": False,
        },
    }
).encode('utf-8')

req = Request(
    base,
    data=data,
    method="POST",
    headers={"Content-Type": "application/json"},
)

with urlopen(req) as resp:
    print(resp.status)
    obj = json.loads(resp.read().decode("utf-8"))
    with open("items.json", "w") as f:
        json.dump(obj["unfilteredListItemIds"], f, indent=4, ensure_ascii=False)

base = "https://www.edelweiss.plus/api/v2/products/"
fields = [
    #"images",
    #"categories",
    #"videos",
    #"dynamicAttributes",
    #"links",
    #"audienceRanges",
    #"catalogAttributes",
    #"completionSummary",
    #"honors",
    #"contributors",
    #"related",
    #"subrights",
    "product",
    "name",
    "series",
    "pubDate",
    "onSaleDate",    
    #"sku": "1642736236",
    #"ean": "9781642736236",
    #"familyItem": "1642736236",
    #"name": "The Wrong Way to Use Healing Magic Volume 7",
    #"subName": "Light Novel",
    #"fullName": "The Wrong Way to Use Healing Magic Volume 7: Light Novel",
    #"author": "Kurokata, Kurokata",
    #"series": "The Wrong Way to Use Healing Magic",
    #"supplier": "One Peace Books",
    #"pubDate": "2027-04-20T00:00:00",
    #"onSaleDate": "2027-04-20T00:00:00",
    #"prices":
    #"formattedPrices": "$15.95 USD, $22.95 CAD",
    #"formattedAudienceRanges": "Ages 12 And Up, Grades 7 And Up",
    #"cartonQuantity": 50,
    #"pages": "284",
    #"firstPrintRun": "N/A",
    #"discountCode": "LON",
    #"category": "Comics & Graphic Novels / Light Novel",
    #"categoryCode": "CGN004320",
    #"format": "Trade Paperback",
    #"formatCode": "BC:B102",
    #"measurements": "7 in H | 5 in W",
    #"spine": "7in H | 5in W",
    #"publishingStatus": "Forthcoming",
    #"language": "English",
    #"retailPrice": 15.95,
    #"industryCategory": "CGN004320",
    #"contributorsWithType": "Kurokata Kurokata, KeG KeG (Illustrated by)"
]

apiView = [
    'standard',
    'advanced',
]

query = urlencode(
    {
        "apiView": ','.join(apiView),
        "catalogId": 5334710,
    }
)

data = json.dumps(
    obj["unfilteredListItemIds"]
).encode("utf-8")

#data = obj["unfilteredListItemIds"]

req = Request(
    base + ','.join(fields) + "?" + query ,
    data=data,
    method="POST",
    headers={"Content-Type": "application/json"},
)

with urlopen(req) as resp:
    print(resp.status)
    obj2 = json.loads(resp.read().decode("utf-8"))
    with open("items2.json", "w") as f:
        json.dump(obj2, f, indent=4, ensure_ascii=False)