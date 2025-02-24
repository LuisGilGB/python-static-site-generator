import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_tag(self):
        node = HTMLNode("div")
        self.assertEqual(node.tag, "div")

    def test_value(self):
        node = HTMLNode("p", "This is a value")
        self.assertEqual(node.value, "This is a value")

    def test_props_to_html(self):
        node = HTMLNode("button", "Accept", props={ "disabled": "true" })
        self.assertEqual(node.props_to_html(), " disabled=\"true\"")

class TestLeafNode(unittest.TestCase):
    def test_with_tag(self):
        node = LeafNode("strong", "Build something", { "aria-strong": "true" })
        self.assertEqual(node.to_html(), "<strong aria-strong=\"true\">Build something</strong>")
    
    def test_without_tag(self):
        text = "Time to purchase"
        node = LeafNode(None, text)
        self.assertEqual(node.to_html(), text)

class TestParentNode(unittest.TestCase):
    def test_single_str_child(self):
        node = ParentNode("p", [LeafNode(None, "Click me")])
        self.assertEqual(node.to_html(), "<p>Click me</p>")

    def test_single_child(self):
        node = ParentNode("p", [LeafNode("strong", "Purchase!")])
        self.assertEqual(node.to_html(), "<p><strong>Purchase!</strong></p>")

    def test_multi_children(self):
        node = ParentNode("button", [LeafNode(None, "Accept"), LeafNode("span", "Placeholder")], props={ "disabled": "true" })
        self.assertEqual(node.to_html(), "<button disabled=\"true\">Accept<span>Placeholder</span></button>")

    def test_multi_nesting(self):
        node = ParentNode("div", [ParentNode("p", [LeafNode("b", "Remember")])])
        self.assertEqual(node.to_html(), "<div><p><b>Remember</b></p></div>")

if __name__ == "__main__":
    unittest.main()
