from sevenbridges.models.file import File


def map_input_output(item, api):
    """
    Maps item to appropriate sevebridges object.
    :param item: Input/Output value.
    :param api: Api instance.
    :return: Mapped object.
    """
    if isinstance(item, list):
        return [map_input_output(it, api) for it in item]

    elif isinstance(item, dict) and 'class' in item:
        if item['class'].lower() in ('file', 'directory'):
            return File(id=item['path'], api=api)

    else:
        return item
