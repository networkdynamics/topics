from topic_model cimport TopicModel
from corpus import Corpus

import numpy as np
cimport numpy as np
from cpython cimport bool

def gibbs_lda_learn(corpus, int num_topics, **kwargs):
	"""
	Use Collapsed Gibbs Sampling to learn topics from a corpus, using the
	Latent Dirichlet Allocation (LDA) model.

	**Args**

		* ``corpus``: the corpus for which to learn topics.
		* ``num_topics``: the number of topics to be learned.

	**Keyword Args**
		* ``num_iterations [=1000]`` (int): the number of iterations of learning.
		* ``alpha [=50/num_topics]`` (float): topics prior
		* ``beta [=0.1]`` (float): words prior

	**Returns**
		A :py:module:TopicModel containing the topic assignments to the corpus.
	"""

	cdef:
		int num_iterations = kwargs.pop("num_iterations", 1000)
		float alpha = kwargs.pop("alpha", 50.0 / num_topics)
		float beta = kwargs.pop("beta", 0.1)
		bool use_labels = kwargs.pop("use_labels", False)

		TopicModel model = TopicModel(corpus, num_topics, alpha, beta)

		# loop iterators
		unsigned int iter_cnt, d_idx, token_idx, topic_idx, i
		
		# Topic variables
		int topic, new_topic, tpe
		float x, by_doc, by_type, by_corpus

		# Probability distribution (allocated here to avoid doing it for every token)
		np.ndarray[np.float_t] p = np.empty(num_topics, np.float_)

		# Typed arrays for fast access to the model
		np.ndarray[np.int_t, ndim=2] _topic_counts_by_type = model._topic_counts_by_type
		np.ndarray[np.int_t, ndim=2] _topic_counts_by_doc = model._topic_counts_by_doc
		np.ndarray[np.int_t] _topic_counts = model._topic_counts



	model.random_topics() 

	for iter_cnt in range(num_iterations):
		for d_idx in range(len(corpus)):
			document = corpus.document(d_idx)
			for token_idx in range(len(document)):

				tpe = corpus.get_type_idx_in_doc(d_idx, token_idx)
				topic = model.get_topic(d_idx, token_idx)
				model.add_to_counts(-1, topic, d_idx, tpe)

				#by_type = _topic_counts_by_type[tpe, 0] + model.beta
				#by_doc = _topic_counts_by_doc[d_idx, 0] + model.alpha
				#by_corpus = _topic_counts[0] + (corpus.count_types() * model.beta)
				#p[0] = by_doc * by_type / by_corpus

				p_sum = 0.0
				for topic_idx in range(model.num_topics):
					by_type = _topic_counts_by_type[tpe, topic_idx] + model.beta
					by_doc = _topic_counts_by_doc[d_idx, topic_idx] + model.alpha
					by_corpus = _topic_counts[topic_idx] + (corpus.count_types() * model.beta)

					#p[topic_idx] = p[topic_idx - 1] + (by_doc * by_type / by_corpus)
					p[topic_idx] = by_doc * by_type / by_corpus
					p_sum += p[topic_idx]
				
				for i in range(len(p)):
					p[i] /= p_sum

				new_topic = 0
				res = np.random.multinomial(1, p)
				for i in range(len(res)):
					if res[i] == 1:
						break
					new_topic += 1

				#x = np.random.uniform(0, p[model.num_topics - 1])
				#new_topic = -1
				#for i in range(len(p)):
				#	new_topic += 1
				#	if(p[i] > x):
				#		break

				model.set_topic(d_idx, token_idx, new_topic, False)
				model.add_to_counts(1, new_topic, d_idx, tpe)

	return model

def gibbs_lda_infer(document, TopicModel model, **kwargs):
	"""
	Use Gibbs sampling to infer the topic distribution of a document, based on
	an existing LDA topic model.

	**Args**

		* ``document``: the document on which to infer the topics
		* ``model``: the model used as a basis for the inference process

	**Keyword Args**

		* ``num_iterations [=25]`` (int): the number of iterations of inference.
		* The same filtering parameters as those that can be passed to a corpus.

	**Returns**
		A :py:module:TopicModel containing the topic assignments for the new
		document, which has index 0 in the model. Topic indices are the same as
		with ``model``.
	"""

	num_iterations = kwargs.pop("num_iterations", 25)
	fh = kwargs.pop("filter_high", None)
	fl = kwargs.pop("filter_low", None)
	fs = kwargs.pop("filter_set", None)
	corpus = Corpus([document], filter_high=fh, filter_low=fl, filter_set=fs)
	new_model = TopicModel(corpus, model.num_topics, model.alpha, model.beta)
	new_model.random_topics()

	cdef:
		# Loop iterators
		int token_idx, topic_idx, i, iter_cnt
		
		# Topic variables
		int topic, new_topic, tpe

		# The sample drawn from the multinomial distribution
		np.ndarray[np.float_t] p = np.empty(model.num_topics, dtype=np.float_)

		float by_type, by_doc, by_corpus

	for iter_cnt in range(num_iterations):
		for token_idx in range(len(document)):

			tpe = corpus.get_type_idx_in_doc(0, token_idx)
			topic = new_model.get_topic(0, token_idx)
			new_model.add_to_counts(-1, topic, 0, tpe)

			# Check types in both corpora
			by_type = (model._topic_counts_by_type[tpe, 0] +
						new_model._topic_counts_by_type[tpe, 0] + 
						model.beta)

			# The new document is not part of the old corpus
			by_doc = new_model._topic_counts_by_doc[0, 0] + model.alpha

			# new_model's corpus is just the one document
			by_corpus = (model._topic_counts[0] + 
						new_model._topic_counts_by_doc[0, 0] + 
						model._corpus.count_types() * model.beta)

			p[0] = (by_doc * by_type / by_corpus)

			for topic_idx in range(1, new_model.num_topics):
				by_type = (model._topic_counts_by_type[tpe, topic_idx] +
						new_model._topic_counts_by_type[tpe, topic_idx] + 
						model.beta)

				by_doc = new_model._topic_counts_by_doc[0, topic_idx] + model.alpha

				by_corpus = (model._topic_counts[topic_idx] + 
							new_model._topic_counts_by_doc[0, topic_idx] + 
							model._corpus.count_types() * model.beta)

				p[topic_idx] = p[topic_idx - 1] + (by_doc * by_type / by_corpus)

			x = np.random.uniform(0, p[model.num_topics - 1])
			new_topic = 0
			for i in range(len(p)):
				if(p[i] > x):
					break
				new_topic += 1

			new_model.set_topic(0, token_idx, new_topic, False)
			new_model.add_to_counts(1, new_topic, 0, tpe)

	return new_model
