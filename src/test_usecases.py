import unittest

from textnode import TextNode, TextType
from usecases import text_node_to_html_node, split_nodes_delimiter


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

if __name__ == "__main__":
    unittest.main()

