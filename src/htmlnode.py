class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("Method not implemented in superclass")

    def props_to_html(self):
        if self.props is None:
            return ""
        attributes = ""
        for key in self.props:
            attributes += f" {key}=\"{self.props[key]}\""
        return attributes

    def __repr__(self):
        return f"{ tag: {self.tag}, attributes: {self.props_to_html}, children: {self.children}, value: {self.value} }"

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError("Leaf nodes must have a value")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, children=children, props=props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("Parent nodes must have a tag")
        if self.children is None:
            raise ValueError("Parent nodes must have children")
        str = ""
        for child in self.children:
            str += child.to_html()
        return f"<{self.tag}{self.props_to_html()}>{str}</{self.tag}>"

