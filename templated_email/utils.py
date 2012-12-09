
#From http://stackoverflow.com/questions/2687173/django-how-can-i-get-a-block-from-a-template
from django.template import Context
from django.template.loader_tags import BlockNode, ExtendsNode


class BlockNotFound(Exception):
    pass


def _get_node(template, context=Context(), name='subject', block_lookups={}):
    for node in template:
        if isinstance(node, BlockNode) and node.name == name:
            #Rudimentary handling of extended templates, for issue #3
            for i in xrange(len(node.nodelist)):
                n = node.nodelist[i]
                if isinstance(n, BlockNode) and n.name in block_lookups:
                    node.nodelist[i] = block_lookups[n.name]
            return node.render(context)
        elif isinstance(node, ExtendsNode):
            lookups = dict([(n.name, n) for n in node.nodelist if isinstance(n, BlockNode)])
            lookups.update(block_lookups)
            return _get_node(node.get_parent(context), context, name, lookups)
    raise BlockNotFound("Node '%s' could not be found in template." % name)
