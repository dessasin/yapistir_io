from elasticsearch_dsl import Document, Text, Integer, Boolean, Completion, analyzer, tokenizer

my_analyzer = analyzer('my_analyzer',
                       tokenizer=tokenizer('trigram', 'edge_ngram', min_gram=1, max_gram=20),
                        filter=["standard", "lowercase", "stop", "snowball"],
                       )


class PasteDoc(Document):
    title = Text(
        analyzer=my_analyzer
    )
    tag = Text(
        analyzer=my_analyzer
    )
    slug = Text()
    id = Integer()
    is_public = Boolean()

    class Index:
        name = 'paste'


def indexing(self):
    obj = PasteDoc(
        meta={'id': self.id},
        title=self.title,
    )
    obj.save()
    return obj.to_dict(include_meta=True)
