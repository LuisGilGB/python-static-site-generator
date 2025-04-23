from os import mkdir
from textnode import TextType, TextNode
from blocknode import BlockType
from htmlnode import LeafNode, ParentNode
import re
import os

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.NORMAL:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, { "href": text_node.url })
        case TextType.IMAGE:
            return LeafNode("img", "", { "src": text_node.url, "alt": text_node.text })
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

def markdown_to_blocks(md):
    blocks = []
    lines = md.split('\n\n')
    for line in lines:
        line = line.strip()
        if line != "":
            blocks.append(line)
    return blocks

def is_ordered_list(text):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        expected_num = i + 1
        if not re.match(f'^{expected_num}\\. ', line):
            return False
    return True

def block_to_block_type(md_block):
    if re.match(r'^#{1,6} ', md_block) is not None:
        return BlockType.HEADING
    if re.match(r'^```[\s\S]*```$', md_block, re.DOTALL) is not None:
        return BlockType.CODE
    if re.match(r'^> .*(\n>.*)*$', md_block) is not None:
        return BlockType.QUOTE
    if re.match(r'^- .*(\n- .*)*$', md_block) is not None:
        return BlockType.UNORDERED_LIST
    if is_ordered_list(md_block):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html_blocks = []
    for block in blocks:
        block_type = block_to_block_type(block)
        html_block = block_node_to_html_node(block_type, block)
        if html_block is not None:
            html_blocks.append(html_block)
    return ParentNode("div", html_blocks)

def text_to_children(text):
    children = []
    text_nodes = text_to_textnodes(text)
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children

def block_node_to_html_node(block_type, content):
    if block_type == BlockType.CODE:
        lines = content.strip().split('\n')
        if lines[0].startswith('```'):
            # Remove language if present
            if len(lines[0]) > 3:
                lines = lines[1:]
            else:
                lines = lines[1:]
        if lines and lines[-1].startswith('```'):
            lines = lines[:-1]
        code_text = '\n'.join(lines)
        return ParentNode("pre", [LeafNode("code", code_text)])

    if block_type == BlockType.HEADING:
        heading_level = 0
        for char in content:
            if char == '#':
                heading_level += 1
            else:
                break
        # Must be followed by a space
        if len(content) > heading_level and content[heading_level] == ' ':
            heading_text = content[heading_level+1:].strip()
            return ParentNode(f"h{heading_level}", text_to_children(heading_text))
        else:
            # Not a valid heading, treat as paragraph
            return ParentNode("p", text_to_children(content.strip()))

    if block_type == BlockType.QUOTE:
        lines = content.splitlines()
        clean_lines = [line[2:] if line.startswith('> ') else (line[1:] if line.startswith('>') else line) for line in lines]
        clean_text = '\n'.join(clean_lines)
        return ParentNode("blockquote", text_to_children(clean_text))

    if block_type == BlockType.UNORDERED_LIST:
        lines = content.splitlines()
        items = [line[2:] if line.startswith('- ') else line for line in lines if line.strip().startswith('-')]
        if not items:
            return None
        li_nodes = [ParentNode('li', text_to_children(item.strip())) for item in items]
        return ParentNode("ul", li_nodes)

    if block_type == BlockType.ORDERED_LIST:
        lines = content.splitlines()
        items = [re.sub(r'^\d+\. ', '', line).strip() for line in lines if re.match(r'^\d+\. ', line)]
        if not items:
            return None
        li_nodes = [ParentNode('li', text_to_children(item)) for item in items]
        return ParentNode("ol", li_nodes)

    if block_type == BlockType.PARAGRAPH:
        content = ' '.join(content.split('\n'))
        return ParentNode("p", text_to_children(content.strip()))

    raise ValueError("Unsupported block type")

def extract_title(markdown):
    lines = markdown.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:]
    raise Exception("No title found in markdown")

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, 'r') as markdown_file:
        markdown = markdown_file.read()
    with open(template_path, 'r') as template_file:
        template = template_file.read()
    html_string = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html_string)
    template = template.replace("href=\"/", f"href=\"{basepath}")
    template = template.replace("src=\"/", f"src=\"{basepath}")

    if not os.path.exists(os.path.dirname(dest_path)):
        mkdir(os.path.dirname(dest_path))
    with open(dest_path, 'w') as dest_file:
        dest_file.write(template)
