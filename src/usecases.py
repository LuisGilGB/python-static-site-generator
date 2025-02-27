from textnode import TextType, TextNode
from htmlnode import LeafNode

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.NORMAL:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("I", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, { "href": text_node.url })
        case TextType.IMAGE:
            return LeafNode("img", "", { "src": text_node.url, "alt": text_node.value })
        case _:
            raise ValueError("Unsupported text node")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    result = []
    for old_node in old_nodes:
        splits = old_node.text.split(delimiter)
        for i in range(0, len(splits)):
            this_type = TextType.NORMAL
            if i % 2 == 1:
                this_type = text_type 
            result.append(TextNode(splits[i], this_type))
    return result

