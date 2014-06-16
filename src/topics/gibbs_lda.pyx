from topic_model import TopicModel
from corpus import Corpus

import numpy as np
cimport numpy as np

cdef compute_multinomial_step(model, int tidx, int didx, int tpe, float a, float b):
	cdef:	
		float numerator = ((model.count_topic_document(tidx, didx) + a) *
				(model.count_topic_types(tidx, tpe) + b))
		float denominator = (model.count_topic(tidx) + model.num_topics * b)
	return numerator / denominator

def gibbs_lda(corpus, int num_topics, **kwargs):

	cdef:
		int num_iterations = kwargs.pop("num_iterations", 1000)
		float alpha = kwargs.pop("alpha", 50.0 / num_topics)
		float beta = kwargs.pop("beta", 0.1)

		# loop iterators
		int iter_cnt, d_idx, token_idx, t, i

		int topic, new_topic, tpe

		np.ndarray[np.int_t] sample
		np.ndarray[np.float_t] p = np.empty(num_topics, np.float_)


	model = TopicModel(corpus, num_topics, alpha, beta)
	model.random_topics() 

	for iter_cnt in range(num_iterations):
		print iter_cnt
		for d_idx in range(len(corpus)):
			document = corpus.document(d_idx)
			for token_idx in range(len(document)):

				tpe = corpus.get_type_idx_in_doc(d_idx, token_idx)
				topic = model.get_topic(d_idx, token_idx)
				model.add_to_count_topic_document(-1, topic, d_idx)
				model.add_to_count_topic_types(-1, topic, tpe)
				model.add_to_topic_count(-1, topic)

				for t in range(num_topics):
					p[t] = (model.count_all_topics_type(tpe)[t] * 
							model.count_all_topics_document(d_idx)[t] /
							float(model.count_all_topics()[t]))

				p /= p.sum()
				
				sample = np.random.multinomial(1, p)
				new_topic = 0
				for i in range(len(sample)):
					if(sample[i] == 1): 
						break
					new_topic += 1

				model.set_topic(d_idx, token_idx, new_topic, False)
				model.add_to_count_topic_document(1, new_topic, d_idx)
				model.add_to_count_topic_types(1, new_topic, tpe)
				model.add_to_topic_count(1, new_topic)

	return model
					
