import re
from topics_exceptions import ParseException
from text_document import *

class Corpus:
	"""
	A collection of documents. Several methods are available for dealing with
	types across all documents of the corpus.
	"""

	FILTER_FREQUENCY = object()
	FILTER_COUNT = object()

	def __init__(self, docs, **kwargs):
		"""
		**Args**

			* ``docs``: the list of documents that this corpus should contain.

		**Keyword Args**

		"""

		bypass_init = kwargs.pop("bypass_init", False)

		filter_high = kwargs.pop("filter_high", None)
		filter_low = kwargs.pop("filter_low", None)
		filter_set = kwargs.pop("filter_set", None)

		# A[i][j] is the type index for the jth token in the ith document
		self._types = []

		# A[i] is the type with index i
		self._type_table = []

		# A[tpe] is the index of type tpe
		self._type_dict = {}

		# A[tpe] is the count of type tpe across the corpus
		self._type_counts = {}

		# A[i] is the document with index i
		self._docs = []

		if bypass_init:
			return

		self._docs = docs

		if filter_set is not None:
			for doc in self._docs:
				doc.filter_types(filter_set)

		if filter_high is not None:
			self.__filter_types(filter_high[0], filter_high[1], None)
		if filter_low is not None:
			self.__filter_types(filter_low[0], None, filter_low[1])

		for doc in self._docs:
			for token in doc:
				if token in self._type_counts:
					self._type_counts[token] += 1
				else:
					self._type_counts[token] = 1

		for didx, doc in enumerate(self._docs):
			self._types.append([0 for i in range(len(doc))])
			for tidx, token in enumerate(doc):
				if token in self._type_dict:
					self._types[didx][tidx] = self._type_dict[token]
				else:
					idx = len(self._type_table)
					self._type_dict[token] = idx
					self._types[didx][tidx] = idx
					self._type_table.append(token)

	def __filter_types(self, filter_kind, high, low):

		to_filter = set()

		if filter_kind is Corpus.FILTER_COUNT:
			for tpe, count in self._type_counts.iteritems():
				if ((high is not None and count > high) or
					(low is not None and count < low)):
					to_filter.add(tpe)					
		elif filter_kind is Corpus.FILTER_FREQUENCY:
			type_list = sorted(self._type_counts.iteritems(), key=lambda i: i[1])
			if low is not None:
				for i in range(low):
					to_filter.add(type_list[i][0])
			if high is not None:
				start = len(type_list) - 1
				end = start - high
				for i in range(start, end, -1):
					to_filter.add(type_list[i][0])
		else:
			raise ValueError, "filter_kind must be Corpus.FILTER_COUNT or Corpus.Filter_FREQUENCY"
		
		for doc in self._docs:
			doc.filter_types(to_filter)

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

	def __load_types(self, table):
		types = table.split(" ")[1:]
		for idx, tpe in enumerate(types):
			if len(tpe) == 0:
				continue
			self._type_table.append(tpe)
			self._type_dict[tpe] = idx

	@staticmethod
	def load(fobj):
		ln = fobj.readline().rstrip()
		mobj = re.match(r"num_documents: (\d+)", ln)
		if mobj is None:
			raise ParseException, "Load corpus: missing number of documents"
		num_documents = int(mobj.group(1))
		
		corpus = Corpus(None, bypass_init=True)

		ln = fobj.readline().rstrip()
		mobj = re.match(r"type_table:", ln)
		if mobj is None:
			raise ParseException, "Load corpus: missing type table"

		corpus.__load_types(ln)

		ln = fobj.readline().rstrip()
		mobj = re.match(r"documents:", ln)
		if mobj is None:
			raise ParseException, "Load corpus: missing documents"

		for i in range(num_documents):
			doc_words = fobj.readline().rstrip().split(" ")
			corpus._types.append([])
			doc = TextDocument("") # TODO Should not necessarily be a text doc.
			for doc_word in doc_words:
				corpus._types[i].append(int(doc_word))
				doc._words.append(corpus._type_table[int(doc_word)])
				if doc_word in corpus._type_counts:
					corpus._type_counts[doc_word] += 1
				else:
					corpus._type_counts[doc_word] = 1
			corpus._docs.append(doc)

		return corpus

	def save(self, fobj):
		fobj.write("num_documents: %d\n" % len(self))
		fobj.write("type_table: ")
		for tpe in self._type_table:
			fobj.write("%s " % tpe)
		fobj.write("\ndocuments:\n")
		for doc in self._types:
			for tpe in doc:
				fobj.write("%d " % tpe)
			fobj.write("\n")

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
