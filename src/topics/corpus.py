class Corpus:
	"""
	A collection of documents. Several methods are available for dealing with
	types across all documents of the corpus.
	"""
	def __init__(self, docs, **kwargs):
		"""
		**Args**

			* ``docs``: the list of documents that this corpus should contain.

		**Keyword Args**

			* ``filter_common [=None]`` (int): if a number, types which appear
			more than ``filter_common`` times across the corpus will be removed 
			from it.

			* ``filter_uncommon [=None]`` (int): if a number, types which appear
			less than ``filter_uncommon`` times across the corpus will be 
			removed from it.
		"""
		self._docs = docs

		filter_common = kwargs.pop("filter_common", None)
		filter_uncommon = kwargs.pop("filter_uncommon", None)
		self.__filter(filter_common, filter_uncommon)

		# A[i][j] is the type index for the jth token in the ith document
		self._types = []

		# A[i] is the type with index i
		self._type_table = []
		type_dict = {}

		for didx, doc in enumerate(self._docs):
			self._types.append([0 for i in range(len(doc))])
			for tidx, token in enumerate(doc):
				if token in type_dict:
					self._types[didx][tidx] = type_dict[token]
				else:
					idx = len(self._type_table)
					type_dict[token] = idx
					self._types[didx][tidx] = idx
					self._type_table.append(token)

	def __filter(self, freq_high, freq_low):
		type_counts = {}
		for doc in self._docs:
			for tok in doc:
				if tok in type_counts:
					type_counts[tok] += 1
				else:
					type_counts[tok] = 1
		
		for tpe, count in type_counts.iteritems():
			if ((freq_high is not None and count > freq_high) or
				(freq_low is not None and count < freq_low)):
				for doc in self._docs:
					doc.filter_type(tpe)

	def __len__(self):
		"""
		Return the number of documents in this corpus.
		"""
		return len(self._docs)

	def __iter__(self):
		"""
		Iterate through documents in the corpus.
		"""
		for doc in self._docs:
			yield doc

	def document(self, idx):
		"""
		Return the document with index ``idx``.
		"""
		return self._docs[idx]

	def count_types(self):
		"""
		Return the number of distinct types in this corpus.
		"""
		return len(self._type_table)

	def get_type_idx_in_doc(self, didx, tok_idx):
		"""
		Obtain the type index of the word with index ``tok_idx`` in the document
		with index ``didx``.
		"""
		return self._types[didx][tok_idx]

	def get_type(self, type_idx):
		"""
		Obtain the type with type index ``type_idx``
		"""
		return self._type_table[type_idx]
