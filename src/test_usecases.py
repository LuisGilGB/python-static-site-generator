import unittest

from textnode import TextNode, TextType
from blocknode import BlockType
from usecases import text_node_to_html_node, split_nodes_delimiter, split_nodes_image, split_nodes_link, extract_markdown_links, extract_markdown_images, text_to_textnodes, markdown_to_blocks, block_to_block_type, markdown_to_html_node, extract_title


class TestTextToHTMLNode(unittest.TestCase):
    def test_bold(self):
        text_node = TextNode("Just build it", TextType.BOLD)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.to_html(), "<b>Just build it</b>")

    def test_link(self):
        text_node = TextNode("Visit", TextType.LINK, "https://mypage.com") 
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.to_html(), "<a href=\"https://mypage.com\">Visit</a>")

class TestSplitNodesDelimiter(unittest.TestCase):
    def test_no_nodes(self):
        result = split_nodes_delimiter([], "*", TextType.BOLD)
        self.assertEqual(len(result), 0)
    
    def test_text_without_inlines(self):
        original_node = TextNode("I'm just telling you bunch of stuff", TextType.NORMAL)
        result = split_nodes_delimiter([original_node], "*", TextType.BOLD)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, original_node.text)
        self.assertEqual(result[0].text_type, original_node.text_type)

    def test_single_bold(self):
        original_node = TextNode("I'm just telling you a *bunch* of stuff", TextType.NORMAL)
        result = split_nodes_delimiter([original_node], "*", TextType.BOLD)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "I'm just telling you a ")
        self.assertEqual(result[0].text_type, TextType.NORMAL)
        self.assertEqual(result[1].text, "bunch")
        self.assertEqual(result[1].text_type, TextType.BOLD)
        self.assertEqual(result[2].text, " of stuff")
        self.assertEqual(result[2].text_type, TextType.NORMAL)

    def test_single_italic(self):
        original_node = TextNode("I'm just telling you a _bunch_ of stuff", TextType.NORMAL)
        result = split_nodes_delimiter([original_node], "_", TextType.ITALIC)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "I'm just telling you a ")
        self.assertEqual(result[0].text_type, TextType.NORMAL)
        self.assertEqual(result[1].text, "bunch")
        self.assertEqual(result[1].text_type, TextType.ITALIC)
        self.assertEqual(result[2].text, " of stuff")
        self.assertEqual(result[2].text_type, TextType.NORMAL)
    
    def test_single_code(self):
        original_node = TextNode("I'm just telling you a `bunch` of stuff", TextType.NORMAL)
        result = split_nodes_delimiter([original_node], "`", TextType.CODE)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "I'm just telling you a ")
        self.assertEqual(result[0].text_type, TextType.NORMAL)
        self.assertEqual(result[1].text, "bunch")
        self.assertEqual(result[1].text_type, TextType.CODE)
        self.assertEqual(result[2].text, " of stuff")
        self.assertEqual(result[2].text_type, TextType.NORMAL)
    
    def test_multi_bold(self):
        original_node = TextNode("I'm *just* telling you a *bunch* of stuff", TextType.NORMAL)
        result = split_nodes_delimiter([original_node], "*", TextType.BOLD)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].text, "I'm ")
        self.assertEqual(result[0].text_type, TextType.NORMAL)
        self.assertEqual(result[1].text, "just")
        self.assertEqual(result[1].text_type, TextType.BOLD)
        self.assertEqual(result[2].text, " telling you a ")
        self.assertEqual(result[2].text_type, TextType.NORMAL)
        self.assertEqual(result[3].text, "bunch")
        self.assertEqual(result[3].text_type, TextType.BOLD)
        self.assertEqual(result[4].text, " of stuff")
        self.assertEqual(result[4].text_type, TextType.NORMAL)

class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png), capisci?",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.NORMAL),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.NORMAL),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
                TextNode(", capisci?", TextType.NORMAL),
            ],
            new_nodes,
        )

    def test_split_images_from_double_input(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png), capisci?",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node, node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.NORMAL),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.NORMAL),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
                TextNode(", capisci?", TextType.NORMAL),
                TextNode("This is text with an ", TextType.NORMAL),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.NORMAL),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
                TextNode(", capisci?", TextType.NORMAL),
            ],
            new_nodes,
        )

    def test_split_images_surrounding(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.NORMAL),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_images_only_images(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png)![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_images_only_single_image(self):
        node = TextNode(
            "![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_images_no_image(self):
        node = TextNode(
            "and another",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("and another", TextType.NORMAL),
            ],
            new_nodes,
        )

class TestSplitNodesLink(unittest.TestCase):
    def test_split_link(self):
        node = TextNode(
            "This is text with a [dotcom link](https://justalink.com) and another [dotnet link](https://justalink.net), capisci?",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.NORMAL),
                TextNode("dotcom link", TextType.LINK, "https://justalink.com"),
                TextNode(" and another ", TextType.NORMAL),
                TextNode("dotnet link", TextType.LINK, "https://justalink.net"),
                TextNode(", capisci?", TextType.NORMAL),
            ],
            new_nodes,
        )

    def test_split_link_double_input(self):
        node = TextNode(
            "This is text with a [dotcom link](https://justalink.com) and another [dotnet link](https://justalink.net), capisci?",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node, node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.NORMAL),
                TextNode("dotcom link", TextType.LINK, "https://justalink.com"),
                TextNode(" and another ", TextType.NORMAL),
                TextNode("dotnet link", TextType.LINK, "https://justalink.net"),
                TextNode(", capisci?", TextType.NORMAL),
                TextNode("This is text with a ", TextType.NORMAL),
                TextNode("dotcom link", TextType.LINK, "https://justalink.com"),
                TextNode(" and another ", TextType.NORMAL),
                TextNode("dotnet link", TextType.LINK, "https://justalink.net"),
                TextNode(", capisci?", TextType.NORMAL),
            ],
            new_nodes,
        )

    def test_split_link_surrouding_links(self):
        node = TextNode(
            "[dotcom link](https://justalink.com) and another [dotnet link](https://justalink.net)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("dotcom link", TextType.LINK, "https://justalink.com"),
                TextNode(" and another ", TextType.NORMAL),
                TextNode("dotnet link", TextType.LINK, "https://justalink.net"),
            ],
            new_nodes,
        )

    def test_split_link_only_links(self):
        node = TextNode(
            "[dotcom link](https://justalink.com)[dotnet link](https://justalink.net)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("dotcom link", TextType.LINK, "https://justalink.com"),
                TextNode("dotnet link", TextType.LINK, "https://justalink.net"),
            ],
            new_nodes,
        )

    def test_split_link_only_link(self):
        node = TextNode(
            "[dotnet link](https://justalink.net)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("dotnet link", TextType.LINK, "https://justalink.net"),
            ],
            new_nodes,
        )

    def test_split_link_with_image(self):
        node = TextNode(
            "[dotnet link](https://justalink.net) and a random image ![random image](https://i.random.com/1234.png)",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("dotnet link", TextType.LINK, "https://justalink.net"),
                TextNode(" and a random image ![random image](https://i.random.com/1234.png)", TextType.NORMAL),
            ],
            new_nodes,
        )

    def test_split_link_no_links(self):
        node = TextNode(
            "just some boring text",
            TextType.NORMAL,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("just some boring text", TextType.NORMAL),
            ],
            new_nodes,
        )

class TestExtractMarkdownImages(unittest.TestCase):
    def test_img(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")])


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_img(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")])

class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_text_nodes_1(self):
        input = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        new_nodes = text_to_textnodes(input)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.NORMAL),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.NORMAL),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.NORMAL),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.NORMAL),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.NORMAL),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            new_nodes,
        )

    def test_text_to_text_nodes_2(self):
        input = "This is _text_ with a [dotcom link](https://justalink.com) and an image ![png image](https://hosting.com/sample.png), **capisci**?"
        new_nodes = text_to_textnodes(input)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.NORMAL),
                TextNode("text", TextType.ITALIC),
                TextNode(" with a ", TextType.NORMAL),
                TextNode("dotcom link", TextType.LINK, "https://justalink.com"),
                TextNode(" and an image ", TextType.NORMAL),
                TextNode("png image", TextType.IMAGE, "https://hosting.com/sample.png"),
                TextNode(", ", TextType.NORMAL),
                TextNode("capisci", TextType.BOLD),
                TextNode("?", TextType.NORMAL),
            ],
            new_nodes,
        )

class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_strip_lines(self):
        md = """
 This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items 
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )


    def test_markdown_to_blocks_remove_excess_of_blank_lines(self):
        md = """
This is **bolded** paragraph


This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

class TestBlockToBlockType(unittest.TestCase):
    def test_heading_blocks(self):
        self.assertEqual(block_to_block_type("# Heading 1"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## Heading 2"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading 6"), BlockType.HEADING)
        # Edge cases
        self.assertNotEqual(block_to_block_type("#No space"), BlockType.HEADING)
        self.assertNotEqual(block_to_block_type("####### Too many hashes"), BlockType.HEADING)

    def test_code_blocks(self):
        self.assertEqual(block_to_block_type("```\nprint('Hello')\n```"), BlockType.CODE)
        self.assertEqual(block_to_block_type("```python\nprint('Hello')\n```"), BlockType.CODE)
        # Edge cases
        self.assertNotEqual(block_to_block_type("``` missing end"), BlockType.CODE)
        self.assertNotEqual(block_to_block_type("missing start ```"), BlockType.CODE)

    def test_quote_blocks(self):
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("> Line 1\n> Line 2"), BlockType.QUOTE)
        # Edge cases
        self.assertNotEqual(block_to_block_type(">Missing space"), BlockType.QUOTE)
        self.assertNotEqual(block_to_block_type("> Line 1\nNot a quote"), BlockType.QUOTE)

    def test_unordered_list_blocks(self):
        self.assertEqual(block_to_block_type("- Item 1"), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type("- Item 1\n- Item 2\n- Item 3"), BlockType.UNORDERED_LIST)
        # Edge cases
        self.assertNotEqual(block_to_block_type("-No space"), BlockType.UNORDERED_LIST)
        self.assertNotEqual(block_to_block_type("- Item 1\nNot a list item"), BlockType.UNORDERED_LIST)
    
    def test_ordered_list_blocks(self):
        self.assertEqual(block_to_block_type("1. Item 1"), BlockType.ORDERED_LIST)
        self.assertEqual(block_to_block_type("1. Item 1\n2. Item 2\n3. Item 3"), BlockType.ORDERED_LIST)
        # Edge cases
        self.assertNotEqual(block_to_block_type("1.No space"), BlockType.ORDERED_LIST)
        self.assertNotEqual(block_to_block_type("2. Wrong first number"), BlockType.ORDERED_LIST)
        self.assertNotEqual(block_to_block_type("1. Item 1\n3. Non-sequential"), BlockType.ORDERED_LIST)
        self.assertNotEqual(block_to_block_type("1. Item 1\nNot a list item"), BlockType.ORDERED_LIST)

    def test_paragraph_blocks(self):
        self.assertEqual(block_to_block_type("This is a paragraph"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("Multi-line\nparagraph\ntext"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("Paragraph with # that isn't a heading"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("Paragraph with - that isn't a list"), BlockType.PARAGRAPH)

        # Edge cases that should be paragraphs
        self.assertEqual(block_to_block_type("#No space so not a heading"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("####### Too many hashes for heading"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("-No space so not a list"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("1.No space so not an ordered list"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("2. Doesn't start with 1 so not an ordered list"), BlockType.PARAGRAPH)

class TestMarkdownToHTML(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff</code></pre></div>",
        )

    def test_heading(self):
        md = """
# Heading 1\n\n## Heading 2\n\n### Heading 3\n"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading 1</h1><h2>Heading 2</h2><h3>Heading 3</h3></div>",
        )

    def test_blockquote(self):
        md = "> This is a quote\n> with two lines"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote\nwith two lines</blockquote></div>",
        )

    def test_unordered_list(self):
        md = "- Item 1\n- Item 2\n- Item 3"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul></div>",
        )

    def test_ordered_list(self):
        md = "1. First\n2. Second\n3. Third"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>First</li><li>Second</li><li>Third</li></ol></div>",
        )

    def test_mixed_blocks(self):
        md = """
# Title\n\nParagraph text here.\n\n- List item 1\n- List item 2\n\n> Quote block\n\n1. First\n2. Second\n"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Title</h1><p>Paragraph text here.</p><ul><li>List item 1</li><li>List item 2</li></ul><blockquote>Quote block</blockquote><ol><li>First</li><li>Second</li></ol></div>",
        )


class TestExtractTitle(unittest.TestCase):
    def test_extract_title(self):
        md = "# Title"
        title = extract_title(md)
        self.assertEqual(title, "Title")

    def test_extract_title_with_newline(self):
        md = "# Title\n"
        title = extract_title(md)
        self.assertEqual(title, "Title")

    def test_no_title(self):
        md = "# Not a title"
        with self.assertRaises(Exception):
            extract_title(md)
    
    def test_many_lines(self):
        md = "> A quote\n\n# Title\n\nParagraph text here."
        title = extract_title(md)
        self.assertEqual(title, "Title")

if __name__ == "__main__":
    unittest.main()
