class Corpus:
	def __init__(self, docs):
		self._docs = docs

	def __len__(self):
		return len(self._docs)

	def __iter__(self):
		for doc in self._docs:
			yield doc

	def add_document(self, doc):
		self._docs.append(doc)

	def document(self, idx):
		return self._docs[idx]

