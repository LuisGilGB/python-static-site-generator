from textnode import TextType, TextNode
from htmlnode import LeafNode
import re

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
        if len(splits) == 1:
            result.append(old_node)
            continue
        for i in range(0, len(splits)):
            split = splits[i]
            this_type = TextType.NORMAL
            if i % 2 == 1:
                this_type = text_type
            if len(split) > 0:
                result.append(TextNode(split, this_type))
    return result

def split_nodes_image(old_nodes):
    result = []
    for old_node in old_nodes:
        matches = extract_markdown_images(old_node.text)
        if len(matches) == 0:
            result.append(old_node)
            continue
        pending_text = old_node.text
        for match in matches:
            formatted_match = f"![{match[0]}]({match[1]})"
            splits = pending_text.split(formatted_match)
            if splits[0] != "":
                result.append(TextNode(splits[0], TextType.NORMAL))
            result.append(TextNode(match[0], TextType.IMAGE, match[1]))
            pending_text = splits[1]
        if len(pending_text) > 0:
            result.append(TextNode(pending_text, TextType.NORMAL))
    return result

def split_nodes_link(old_nodes):
    result = []
    for old_node in old_nodes:
        matches = extract_markdown_links(old_node.text)
        if len(matches) == 0:
            result.append(old_node)
            continue
        pending_text = old_node.text
        for match in matches:
            formatted_match = f"[{match[0]}]({match[1]})"
            splits = pending_text.split(formatted_match)
            if splits[0] != "":
                result.append(TextNode(splits[0], TextType.NORMAL))
            result.append(TextNode(match[0], TextType.LINK, match[1]))
            pending_text = splits[1]
        if len(pending_text) > 0:
            result.append(TextNode(pending_text, TextType.NORMAL))
    return result

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def text_to_textnodes(input):
    result = [TextNode(input, TextType.NORMAL)]
    result = split_nodes_link(result)
    result = split_nodes_image(result)
    result = split_nodes_delimiter(result, '**', TextType.BOLD)
    result = split_nodes_delimiter(result, '_', TextType.ITALIC)
    result = split_nodes_delimiter(result, '`', TextType.CODE)
    return result

