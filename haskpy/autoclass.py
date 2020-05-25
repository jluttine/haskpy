from sphinx.ext.autodoc import ClassDocumenter


class MyClassDocumenter(ClassDocumenter):
    objtype = 'class'
    priority = 20  # higher priority than ClassDocumenter

    # @classmethod
    # def can_document_member(cls, member, membername, isattr, parent):
    #     return isinstance(member, class_types) and issubclass(member, Foo)

    # def get_doc(self, encoding=None, ignore=1):
    #     doc = super(MyClassDocumenter, self).get_doc(encoding, ignore)
    #     # do something to modify the output documentation
    #     print(doc)
    #     if len(doc) > 0:
    #         doc[0].insert(0, "ADD SOMETHING TO THE DOC")
    #     return doc

    def get_object_members(self, want_all):
        (x, ms) = super(MyClassDocumenter, self).get_object_members(want_all)
        return (
            x,
            [
                print("{0} has {1}:".format(self.object, m[0])) or m
                for m in ms
                if hasattr(self.object, m[0])
            ]
            #filter(lambda m: hasattr(x, m[0]), ms)
            #filter(lambda m: hasattr(x, m[0]), ms)
        )
        print(ms)
        return (
            x,
            ms + [
                (name, lambda: None)
                #for name in type(self.object).__dict__.keys()
                for name in object.__dir__(self.object)
                if hasattr(self.object, name)
            ]
            # ms + [
            #     ("test_monoid_identity", lambda: None),
            #     ("empty", lambda: None),
            # ]
        )


class MetaclassMethodDocumenter():
    pass


class MetaclassPropertyDocumenter():
    pass


def setup(app):

    app.add_autodocumenter(MyClassDocumenter)

    return {}
