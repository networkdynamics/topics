class TextDocument:
	"""
	This class encapuslates the information contained in a text document such that it can be directly
	used by an .... # TODO

	TODO: Clarify the features of the document (in particular, types and labels)
	TODO: Change all count_ methods to num_ 
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

		# TODO: Check for extra keywords

		self._words = text.split()
		self._labels = labels

		# A[tpe][i] is the index of the ith occurence of type tpe
		self._type_occurrences = {}

		for i, w in enumerate(self._words):
			if w not in self._type_occurrences:
				self._type_occurrences[w] = [i]
			else:
				self._type_occurrences[w].append(i)

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
		Iterate through labels applied to the document.

		TODO: rename to iter_labels
		"""
		return iter(self._labels)

	def has_label(self, lbl):
		"""
		Return whether this document is labelled with ``lbl``.
		"""
		return lbl in self._labels

	def add_label(self, lbl):
		"""
		Add the label ``lbl`` to this document.
		"""
		self._labels.add(lbl)

	def count_labels(self):
		"""
		Return the number of labels applied to this document.
		"""
		return len(self._labels)

	def get_type_occurrence(self, tpe, i):
		"""
		Obtain the token index of the ith occurrence of type ``tpe``.
		"""
		return self._type_occurrences[tpe][i]

	def count_types(self):
		"""
		Return the number of unique types in this document.
		"""
		return len(set(self._words))

	def count_type(self, tpe):
		"""
		Return the number of words with type ``tpe``.
		"""
		return reduce(lambda acc, i: acc + 1 if i == tpe else acc, self._words, 0)

	def filter_type(self, excluded):	
		"""
		Remove the word type ``excluded`` from the document.
		"""
		self._words = [w for w in self._words if w != excluded]
		if excluded in self._type_occurrences:
			del self._type_occurrences[excluded]

	def filter_types(self, excluded):
		"""
		Remove all the word types in the iterable ``excluded`` from the document.
		"""
		self._words = [w for w in self._words if w not in excluded]
		for tpe in excluded:		
			if tpe in self._type_occurrences:
				del self._type_occurrences[tpe]
