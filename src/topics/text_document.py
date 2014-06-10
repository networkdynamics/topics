class TextDocument:
	def __init__(self, text):
		self._types_lookup = {} # Types to lists of token indices
		self._types = [] # Types, indexed by type index
		self._words = text.split()

		for i in range(len(self._words)):
			word = self._words[i]
			if word not in self._types_lookup:
				self._types_lookup[word] = [i]
				self._types.append(word)
			else:
				self._types_lookup[word].append(i)

	def __len__(self):
		return len(self._words)

	def num_types(self):
		return len(self._types_lookup)

	def count_type(self, tpe):
		return len(self._types_lookup[tpe])

	def count_type_(self, tidx):
		return self.count_type(self.get_type_by_tidx(tidx))

	def get_type_by_tidx(self, tidx):
		return self._types[tidx]

	def get_type_by_token_idx(self, token):
		return self._words[token]

	def get_token_idx(self, i, type_idx):
		"""
		Obtain the document-relative index of the ith token of the given type.
		"""
		tpe = self._types[type_idx]
		return self._types_lookup[tpe][i]

	def tokens_iter(self):
		for word in self._words:
			yield word

	def types_iter(self):
		for tpe in self._types:
			yield tpe
