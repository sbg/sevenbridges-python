from sevenbridges.meta.fields import HrefField, StringField
from sevenbridges.meta.resource import Resource


class Link(Resource):
    """
    Pagination links.
    """
    href = HrefField()
    rel = StringField(read_only=True)
    method = StringField(read_only=True)

    def __str__(self):
        return (
            f'<Link: method={self.method}, rel={self.rel}, href={self.href}>'
        )


class VolumeLink(Resource):
    """
    Pagination links for volumes.
    """
    next = HrefField()

    def __str__(self):
        return f'<VolumeLink: next={self.next}>'
