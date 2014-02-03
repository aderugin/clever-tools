from sorl.thumbnail.shortcuts import get_thumbnail

def fail_safe_thumbnail(image, geometry_string, **options):
    ''' fail safe get_thumbnail '''
    try:
        return get_thumbnail(image, geometry_string, **options).url
    except:
        return None
