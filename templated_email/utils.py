
#From http://stackoverflow.com/questions/2687173/django-how-can-i-get-a-block-from-a-template
from django.template import Context
from django.template.loader_tags import BlockNode, ExtendsNode

class BlockNotFound(Exception):
    pass

def _get_node(template, context=Context(), name='subject'):
    for node in template:
        if isinstance(node, BlockNode) and node.name == name:
            return node.render(context)
        elif isinstance(node, ExtendsNode):
            return _get_node(node.nodelist, context, name)
    raise BlockNotFound("Node '%s' could not be found in template." % name)
