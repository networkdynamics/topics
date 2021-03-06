import re
from topics_exceptions import ParseException
from text_document import *

class Corpus:
	"""
	A collection of documents. Several methods are available for dealing with
	types across all documents of the corpus.

	# TODO: Expand on the point of this class.

	# TODO: Mention that serialization is possible

	# TODO: Replace all count_ with num_

	# TODO: Explain why type access through the corpus is different than through individual documents.
	"""

	FILTER_FREQUENCY = 'FILTER_FREQUENCY'
	FILTER_COUNT = 'FILTER_COUNT' 

	def __init__(self, docs, **kwargs):
		"""
		Create a corpus, based on a list of documents. Documents can have their
		words filtered. By using frequency filtering (Corpus.FILTER_FREQUENCY),
		the most or least frequent words can be removed. By using count filtering
		(Corpus.FILTER_COUNT), counts that appear more (or less) than a certain
		number can be removed.

		# TODO: In the discussion, clarify the relationship between words and types

		**Args**

			* ``docs``: the list of documents that this corpus should contain.

		**Keyword Args**

			* ``filter_high[=None]``: a tuple used to filter words that appear
			too many times, or are among the most frequent. The first element of
			the tuple is either Corpus.FILTER_FREQUENCY or Corpus.FILTER_COUNT,
			and the second element is a number.

			* ``filter_low[=None]``: a tuple used to filter words that appear
			not enough times, or are among the least frequent. The first element
			of the tuple is either Corpus.FILTER_FREQUENCY or Corpus.FILTER_COUNT,
			and the second element is a number.

			* ``filter_set[=None]``: a set containing words to be filtered from
			the corpus.
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

		# A[lbl] is the index of label lbl
		self._label_dict = {}

		# A[i] is the label with index i
		self._label_table = []

		# A[i][j] is a 1 if document i has label j, 0 otherwise
		self._labels_by_doc = []

		if bypass_init:
			return

		self._docs = docs

		if filter_set is not None:
			for doc in self._docs:
				doc.filter_types(filter_set)

		for doc in self._docs:
			for token in doc:
				if token in self._type_counts:
					self._type_counts[token] += 1
				else:
					self._type_counts[token] = 1

		if filter_high is not None:
			self.__filter_types(filter_high[0], filter_high[1], None)
		if filter_low is not None:
			self.__filter_types(filter_low[0], None, filter_low[1])

		label_idx = 0
		for didx, doc in enumerate(self._docs):
			for lbl in doc.iterlabels():
				if lbl not in self._label_dict:
					self._label_table.append(lbl)
					self._label_dict[lbl] = label_idx
					label_idx += 1

			self._types.append([0 for i in range(len(doc))])

			for tidx, token in enumerate(doc):
				if token in self._type_dict:
					self._types[didx][tidx] = self._type_dict[token]
				else:
					idx = len(self._type_table)
					self._type_dict[token] = idx
					self._types[didx][tidx] = idx
					self._type_table.append(token)

		for didx, doc in enumerate(self._docs):
			self._labels_by_doc.append([0 for i in range(len(self._label_dict))])
			for lbl in doc.iterlabels():
				self._labels_by_doc[didx][self._label_dict[lbl]] = 1
			

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

	def __load_labels(self, table):
		types = table.split(" ")[1:]
		for idx, lbl in enumerate(types):
			if len(lbl) == 0:
				continue
			self._label_dict[idx] = lbl
			self._label_table.append(lbl)

	@staticmethod
	def load(fobj):
		"""
		# TODO: Document this
		"""
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
		mobj = re.match(r"label_table:", ln)
		if mobj is None:
			raise ParseException, "Load corpus: missing label table"

		corpus.__load_labels(ln)

		ln = fobj.readline().rstrip()
		mobj = re.match(r"types:", ln)
		if mobj is None:
			raise ParseException, "Load corpus: missing types"

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

		ln = fobj.readline().rstrip()
		mobj = re.match(r"labels:", ln)
		if mobj is None:
			raise ParseException, "Load corpus: missing labels"

		for i in range(num_documents):
			doc_lbls = map(lambda i: int(i), fobj.readline().rstrip().split(" "))
			corpus._labels_by_doc.append([])
			for lbl_idx, has_lbl in enumerate(doc_lbls):
				corpus._labels_by_doc[i].append(has_lbl)
				if has_lbl == 1:
					corpus.document(i).add_label(corpus._label_dict(lbl_idx))

		return corpus

	def save(self, fobj):
		"""
		TODO: Document
		"""
		fobj.write("num_documents: %d\n" % len(self))
		fobj.write("type_table: ")
		for tpe in self._type_table:
			fobj.write("%s " % tpe)
		fobj.write("\nlabel_table: ")
		for lbl in sorted(self._label_dict.iteritems(), key=lambda i: i[1]):
			fobj.write("%s " % lbl)
		fobj.write("\ntypes:\n")
		for doc in self._types:
			for tpe in doc:
				fobj.write("%d " % tpe)
			fobj.write("\n")
		fobj.write("labels:\n")
		for doc in self._labels_by_doc:
			for lbl in doc:
				fobj.write("%d " %lbl)
			fobj.write("\n")

	def iter_types_doc(self, didx):
		"""
		Iterate through the type indices of the document with index ``didx``.
		"""
		return iter(set(self._types[didx]))

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

	def get_type_idx(self, tpe):
		"""
		Obtain the type index of the type ``tpe``.
		"""
		return self._type_dict[tpe]

	def count_labels(self):
		"""
		Return the number of distinct labels in this corpus.
		"""
		return len(self._label_dict)

	def get_label(self, lidx):
		"""
		Return the label with the index ``lidx``.
		"""
		return self._label_table[lidx]

	def get_label_idx(self, label):
		"""
		Return the label index corresponding to ``label``.
		"""
		return self._label_dict[label]

	def document_has_label(didx, lidx):
		"""
		Return whether the document with index ``didx`` is labelled with label
		having index ``lidx``.
		"""
		return self._labels_by_doc[didx][lidx] == 1
