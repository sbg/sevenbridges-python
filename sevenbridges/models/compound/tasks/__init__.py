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
            _secondary_files = []
            for _file in item.get('secondaryFiles', []):
                _secondary_files.append({'id': _file['path']})
            data = {
                'id': item['path']
            }
            data.update({k: item[k] for k in item if k != 'path'})
            if _secondary_files:
                data.update({
                    '_secondary_files': _secondary_files,
                    'fetched': True
                })
            return File(api=api, **data)
    else:
        return item
