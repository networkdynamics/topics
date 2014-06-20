cimport numpy as np

cdef class TopicModel:
	cdef object _corpus
	cdef readonly int num_topics
	cdef readonly float alpha
	cdef readonly float beta

	cdef list _topic_distributions
	cdef np.ndarray _topic_counts_by_doc
	cdef np.ndarray _topic_counts_by_type
	cdef np.ndarray _topic_counts

	cpdef random_topics(TopicModel self)
	cpdef set_topic(TopicModel self, int doc_idx, int word_idx, int topic, update_counts=*)
	cpdef add_to_counts(TopicModel self, int amt, int top_idx, int doc_idx, int type_idx)
	cpdef int get_topic(TopicModel self, int doc_idx, int word_idx)
	cpdef int count_topic_document(TopicModel self, int top_idx, int doc_idx)
	cpdef int count_topic_types(TopicModel self, int top_idx, int type_idx)
	cpdef int count_topic(TopicModel self, int top_idx)
	cpdef count_all_topics_type(TopicModel self, int type_idx)
	cpdef count_all_topics_document(TopicModel self, int doc_idx)
	cpdef count_all_topics(TopicModel self)
