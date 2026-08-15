from PIL import Image
from io import BytesIO


def img_mani(data, prefs):
    img = Image.open(BytesIO(data))

    fmt = img.format or "JPEG"
    dpi = img.info.get("dpi", (300, 300))

    if (
        img.width > img.height
        and (img.width and img.height) > 400
        and prefs["mod_img_rota"]
    ):
        img = img.transpose(Image.Transpose.ROTATE_90)

    if prefs["mod_img_size_dimension"] and (
        prefs["mod_img_size_dimension.width"] < img.width
        or prefs["mod_img_size_dimension.height"] < img.height
    ):
        img.thumbnail(
            (
                prefs["mod_img_size_dimension.width"],
                prefs["mod_img_size_dimension.height"],
            ),
            resample=Image.LANCZOS,
        )

    if prefs["mod_img_grsc"]:
        if img.mode == "RGBA":
            img = img.convert("LA")
        else:
            img = img.convert("L")

    kwargs = {
        "format": fmt,
        "quality": prefs["mod_img_quality"],
        "subsampling": 0,
        "optimize": True,
        "progressive": True,
        "dpi": dpi,
    }

    output = BytesIO()

    img.save(output, **kwargs)

    # print(len(data),len(output.getvalue()))

    return output.getvalue()


def img_maxsize(data, quality):
    img = Image.open(BytesIO(data))

    fmt = img.format or "JPEG"
    dpi = img.info.get("dpi", (300, 300))

    output = BytesIO()

    kwargs = {
        "format": fmt,
        "quality": quality,
        "subsampling": 0,
        "optimize": True,
        "progressive": True,
        "dpi": dpi,
    }

    img.save(output, **kwargs)
