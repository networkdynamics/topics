class TextDocument:
	def __init__(self, text):
		self._words = text.split()

	def __len__(self):
		return len(self._words)

	def __iter__(self):
		for word in self._words:
			yield word
