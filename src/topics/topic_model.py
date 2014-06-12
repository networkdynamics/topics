import random

class TopicModel:
	def __init__(self, corpus, num_topics, a, b):
		self._corpus = corpus
		self.num_topics = num_topics
		self._alpha = a
		self._beta = b

		# A[i][j] is the topic assigned to the jth word of the ith document
		self._topic_distributions = []
		for doc in corpus:
			self._topic_distributions.append([0 for i in range(len(doc))])

		# A[i,j] is the number of tokens with topic j in the ith document
		self._topic_counts_by_doc = []

		# A[i][j] is the number of tokens with topic j and type i across the corpus
		self._topic_counts_by_type = []

		# A[i] is the number of tokens with ith topic
		self._topic_counts = [num_topics * b for i in range(num_topics)]

		for i in range(corpus.count_types()):
			self._topic_counts_by_type.append([b for i in range(num_topics)])

		for didx, doc in enumerate(corpus):
			self._topic_counts_by_doc.append([a for i in range(num_topics)])
			self._topic_counts_by_doc[len(self._topic_counts_by_doc) - 1][0] += len(doc)
			self._topic_counts[0] += len(doc)

			for tok_idx, tok in enumerate(doc):
				tpe = corpus.get_type_idx_in_doc(didx, tok_idx)
				self._topic_counts_by_type[tpe][0] += 1

	# ============== Model-building methods ==============

	def random_topics(self):
		for i in range(len(self._topic_distributions)):
			doc_topics = self._topic_distributions[i]
			for j in range(len(doc_topics)):
				# Update the topic assignment
				new_topic = random.randrange(self.num_topics)
				old_topic = doc_topics[j]
				doc_topics[j] = new_topic

				# Update the count by document
				self._topic_counts_by_doc[i][new_topic] += 1
				self._topic_counts_by_doc[i][old_topic] -= 1

				# Update the global count
				self._topic_counts[new_topic] += 1
				self._topic_counts[old_topic] -= 1

				# Update the count by type
				tpe = self._corpus.get_type_idx_in_doc(i, j)
				self._topic_counts_by_type[tpe][new_topic] += 1
				self._topic_counts_by_type[tpe][old_topic] -= 1

	def set_topic(self, doc_idx, word_idx, topic, update_counts=True):
		old_topic = self._topic_distributions[doc_idx][word_idx]
		self._topic_distributions[doc_idx][word_idx] = topic

		if update_counts is True:
			self._topic_counts_by_doc[doc_idx][topic] += 1
			self._topic_counts_by_doc[doc_idx][old_topic] -= 1

			self._topic_counts[topic] += 1
			self._topic_counts[old_topic] -= 1

			tpe = self._corpus.get_type_idx_in_doc(i, j)
			self._topic_counts_by_type[tpe][topic] += 1
			self._topic_counts_by_type[tpe][old_topic] -= 1


	def add_to_count_topic_document(self, amt, top_idx, doc_idx):
		self._topic_counts_by_doc[doc_idx][top_idx] += amt

	def add_to_topic_count(self, amt, top_idx):
		self._topic_counts[top_idx] += amt

	def add_to_count_topic_types(self, amt, top_idx, type_idx):
		self._topic_counts_by_type[type_idx][top_idx] += amt

	# ============== Model-querying methods ==============

	def get_topic(self, doc_idx, word_idx):
		return self._topic_distributions[doc_idx][word_idx]

	def count_topic_document(self, top_idx, doc_idx):
		return self._topic_counts_by_doc[doc_idx][top_idx]

	def count_topic_types(self, top_idx, type_idx):
		return self._topic_counts_by_type[type_idx][top_idx]

	def count_topic(self, top_idx):
		return self._topic_counts[top_idx]

	def count_all_topics_type(self, type_idx):
		return self._topic_counts_by_type[type_idx]

	def count_all_topics_document(self, doc_idx):
		return self._topic_counts_by_doc[doc_idx]

	def count_all_topics(self):
		return self._topic_counts

	def describe_document(self, doc_idx):
		# Returns a list of the percentages that each topic contributes to
		# the given document.

		sum_topics = 0
		description = self._topic_counts_by_doc[doc_idx][:]
		for i in range(len(description)):
			description[i] = round(description[i] - self._alpha)
			sum_topics += description[i]

		return [i / sum_topics for i in description]

	def describe_topic(self, top_idx):
		# Returns a list of tuples, where the first field of a tuple is a word, 
		# and the second field is how many times it receives the given topic 
		# (sorted in descending order of this second field)

		type_counts = {}
		for type_idx, counts in enumerate(self._topic_counts_by_type):
			amt = round(counts[top_idx] - self._beta)
			if amt > 0:
				tpe = self._corpus.get_type(type_idx)
				if tpe not in type_counts:
					type_counts[tpe] = amt
				else:
					type_counts[tpe] += amt

		return sorted(type_counts.iteritems(), key=lambda i: i[1], reverse=True)
