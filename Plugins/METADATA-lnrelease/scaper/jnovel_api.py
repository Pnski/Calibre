
#https://labs.j-novel.club/app/v2/series?format=json&limit=250&skip=200
#https://labs.j-novel.club/app/v2/series?format=json&limit=500
#https://cdn.j-novel.club/pub/img/1200/webp/01K/Q/S/PARXFRW58AR4F3F8ZQHRV.png
"""
GET https://labs.j-novel.club/embed/{part ID}
GET https://labs.j-novel.club/embed/{part ID}/info.json
GET https://labs.j-novel.club/embed/{part ID}/lastpage.html
GET https://labs.j-novel.club/embed/{part ID}/data.xhtml

GET https://labs.j-novel.club/app/v1/releases
GET/POST https://labs.j-novel.club/app/v1/series
GET https://labs.j-novel.club/app/v1/series/{ID or slug}
GET https://labs.j-novel.club/app/v1/series/{ID or slug}/volumes
GET https://labs.j-novel.club/app/v1/series/{ID or slug}/aggregate
GET https://labs.j-novel.club/app/v1/volumes/{ID or slug}
GET https://labs.j-novel.club/app/v1/volumes/{ID or slug}/serie
GET https://labs.j-novel.club/app/v1/volumes/{ID or slug}/parts
GET https://labs.j-novel.club/app/v1/volumes/{ID or slug}/skus
GET https://labs.j-novel.club/app/v1/volumes/{ID or slug}/price
GET https://labs.j-novel.club/app/v1/parts/{ID or slug}
GET https://labs.j-novel.club/app/v1/parts/{ID or slug}/toc
GET https://labs.j-novel.club/app/v1/parts/{ID or slug}/volume
GET https://labs.j-novel.club/app/v1/parts/{ID or slug}/serie
GET https://labs.j-novel.club/app/v1/parts/{ID or slug}/data
GET https://labs.j-novel.club/app/v1/events
https://labs.j-novel.club/app/v1/events?sort=launch&start_date=2022-04-30T21%3A00%3A00.000Z&end_date=2022-05-31T21%3A00%3A00.000Z
https://cdn.j-novel.club/pub/img/1200/webp/01K/Q/S/PARXFRW58AR4F3F8ZQHRV.png
message SeriesQuery {
    string query = 1; // Search query
    Series.Type type = 2; // The type of series to include

    Sorting sort = 3; // How to sort the series
    enum Sorting {
        NEWEST = 0; // Sort by created, descending
        OLDEST = 1; // Sort by created, ascending
        AZ = 2; // Sort by title, ascending
        ZA = 3; // Sort by title, descending
    }

    bool only_follows = 4;
    bool only_catchups = 5;
}
https://cdn.j-novel.club/pub/img/{height}/{format}/{path...}

height:	120,240,360,480,600,720,840,960,1080,1200
format:	webp,avif,jpg
Full example URL: https://cdn.j-novel.club/pub/img/240/webp/01J/9/V/J9BYFSR8F77KXWT87AZR7.jpg
https://labs.j-novel.club/app/v2/parts/disowned-but-not-disheartened-life-is-good-with-overpowered-magic-volume-1-part-1/serie?format=json
"""