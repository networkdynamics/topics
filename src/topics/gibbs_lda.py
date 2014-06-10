from topic_model import TopicModel

import numpy as np

def compute_multinomial_step(model, tidx, didx, tpe, a, b):
	numerator = ((model.count_topic_document(tidx, didx) + a) *
				(model.count_topic_types(tidx, tpe) + b))
	denominator = (model.count_topic(tidx) + model.num_topics * b)
	return numerator / denominator

def gibbs_lda(corpus, num_topics, **kwargs):
	num_iterations = kwargs.pop("num_iterations", 1000)
	alpha = kwargs.pop("alpha", 50.0 / num_topics)
	beta = kwargs.pop("beta", 0.1)

	model = TopicModel(corpus, num_topics)
	model.random_topics()

	p = np.empty(num_topics)

	for iter_cnt in range(num_iterations):
		
		for d_idx in range(len(corpus)):
			document = corpus.document(d_idx)
			for type_idx in range(document.num_types()):
				v = document.get_type_by_tidx(type_idx)
				sampleTimes = document.count_type_(type_idx)
				for i in range(sampleTimes):
					token_idx = document.get_token_idx(i, type_idx)
					topic = model.get_topic(d_idx, token_idx)

					model.add_to_count_topic_document(-1, topic, d_idx)
					model.add_to_count_topic_types(-1, topic, v)
					model.add_to_topic_count(-1, topic)

					p[0] = compute_multinomial_step(model, 0, d_idx, v, alpha, beta)
					for k in range(1, num_topics):
						p[k] = (p[k - 1] + compute_multinomial_step(model, 
								k, d_idx, v, alpha, beta))
					x = np.random.uniform(high=p[num_topics - 1])
					new_topic = np.searchsorted(p, x)
					
					model.set_topic(d_idx, token_idx, new_topic, False)
					model.add_to_count_topic_document(1, new_topic, d_idx)
					model.add_to_count_topic_types(1, new_topic, v)
					model.add_to_topic_count(1, new_topic)

	return model
					
