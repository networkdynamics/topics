class TextDocument:
	"""
	A simple document containing text.
	"""

	def __init__(self, text, **kwargs):
		"""
		**Args**

			* ``text``: a string containing the text for this document.
		
		**Keyword args**

			* ``to_lower [=False]`` (boolean): if true, convert the document's
			text to lowercase
		"""
		to_lower = kwargs.pop("to_lower", False)
		if to_lower:
			text = text.lower()

		self._words = text.split()

	def __len__(self):
		"""
		Return the length of the document.
		"""
		return len(self._words)

	def __iter__(self):
		"""
		Iterate through words in the document.
		"""
		for word in self._words:
			yield word

	def filter_type(self, excluded):	
		"""
		Remove the word type ``excluded`` from the document.
		"""
		self._words = [w for w in self._words if w != excluded]

	def filter_types(self, excluded):
		"""
		Remove all the word types in the set ``excluded`` from the document.
		"""
		self._words = [w for w in self._words if w not in excluded]
