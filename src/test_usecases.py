import unittest

from textnode import TextNode, TextType
from usecases import text_node_to_html_node, split_nodes_delimiter, split_nodes_image, split_nodes_link, extract_markdown_links, extract_markdown_images


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


if __name__ == "__main__":
    unittest.main()

