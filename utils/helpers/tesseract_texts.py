
TEXTS_FOR_ACTION = {
    'login' : ["ZALOG", "TNOGUI", "TALDGIL!", "TAUDGILI SIE", "ZALocud"]
}


def check_if_text_from_image_includes_the_text(text_from_image, texts_to_check):

    ### MAKE THE TEXTS TO ALWAYS BE COMPARED IN SMALL CAPS
    if len(text_from_image) <= 0:
        return False

    if isinstance(text_from_image, str):
        text_from_image = text_from_image.lower()
    
    if isinstance(texts_to_check, str):
        texts_to_check = [texts_to_check.lower()]
    else:
        texts_to_check = [text.lower() for text in texts_to_check]

    print(texts_to_check)
    for text in texts_to_check:
        if text in text_from_image:
            return True
    # if texts_to_check in text_from_image:
    #     return True
    return False