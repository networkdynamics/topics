class TextDocument:
	"""
	A simple document containing text.
	"""

	def __init__(self, text, labels=set(), **kwargs):
		"""
		**Args**

			* ``text``: a string containing the text for this document.
			* ``labels``: a set containing the labels for this document.
		
		**Keyword args**

			* ``to_lower [=False]`` (boolean): if true, convert the document's
			text to lowercase
		"""
		to_lower = kwargs.pop("to_lower", False)
		if to_lower:
			text = text.lower()

		self._words = text.split()
		self._labels = labels

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

	def iterlabels(self):
		"""
		Iterates through labels applied to the document.
		"""
		return iter(self._labels)

	def has_label(self, lbl):
		"""
		Returns whether this document is labelled with ``lbl``.
		"""
		return lbl in self._labels

	def add_label(self, lbl):
		"""
		Adds the label ``lbl`` to this document.
		"""
		self._labels.add(lbl)

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
