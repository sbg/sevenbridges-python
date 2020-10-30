from sevenbridges.models.enums import FileApiFormats
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
        file_class_list = [
            FileApiFormats.FILE.lower(),
            FileApiFormats.FOLDER.lower()
        ]
        if item['class'].lower() in file_class_list:
            _secondary_files = []
            for _file in item.get('secondaryFiles', []):
                _secondary_files.append({'id': _file['path']})
            data = {
                'id': item['path']
            }
            # map class to type
            if item['class'].lower() == FileApiFormats.FOLDER.lower():
                data['type'] = 'folder'
            else:
                data['type'] = 'file'

            # map cwl 1 file name
            if 'basename' in item:
                data['name'] = item['basename']

            data.update(
                {k: item[k] for k in item if k not in ['path', 'basename']}
            )
            if _secondary_files:
                data.update({
                    '_secondary_files': _secondary_files,
                    'fetched': True
                })
            return File(api=api, **data)
    else:
        return item
