topics
======

A topic modeling suite. Below is an example usage; loading a corpus, discovering
a topic model for it and using that model to infer the topics of a new document.

```python
import topics # Topic modelling library
import sys
from os import listdir
from os.path import isfile, join
import numpy as np


# Create a list of TextDocument based on the files in a directory given at the command line
fpaths = [ join(sys.argv[1], f) for f in listdir(sys.argv[1]) if isfile(join(sys.argv[1], f)) ]
docs = []
for f in fpaths:
	fobj = open(f)
	# Create the document with the contents of the file, lowercasing it
	docs.append(topics.TextDocument(fobj.read(), to_lower=True))
	fobj.close


# Create a corpus based on the list of documents, filtering the 25 most common
# words, words that appear less than 3 times, and some specific words.
filters = {	'filter_high':	(topics.Corpus.FILTER_FREQUENCY, 25),
			'filter_low': 	(topics.Corpus.FILTER_COUNT, 3),
			'filter_set': 	set(["nevertheless", "insofar", "etc"]) }
corp = topics.Corpus(docs, **filters)


# Learn a topic model on the corpus. 10 topics are learned.
NUM_TOPICS = 10
model = topics.gibbs_lda_learn(corp, NUM_TOPICS, num_iterations=1000)


# Show the list of words that contribute to each topic
for topic in range(NUM_TOPICS):
	print model.describe_topic(topic)

# Show the main topic for each document
for doc_idx in range(len(corp)):
	# A list of how each topic contributes to the document, in percent
	topic_percentages = model.describe_document(doc_idx)
	
	main_topic_percent = max(topic_percentages)
	main_topic = topic_percentages.index(main_topic_percent)
	print "Document %d consists mostly of topic %d" % (doc_idx, main_topic)

# Using the model, infer the topic distribution on a new document whose path was
# obtained at the command line. To filter this document, we just remove common
# and uncommon words (removing stop words would be good here too)
fobj = open(sys.argv[2])
new_doc = topics.TextDocument(fobj.read(), to_lower=True)
fobj.close()
new_model = topics.gibbs_lda_infer(new_doc, model, 
							filter_low=(topics.Corpus.FILTER_COUNT, 2),
							filter_high=(topics.Corpus.FILTER_COUNT, 10))
# new_model contains only our new document


# Show how each topic contributes to the new document
print new_model.describe_document(0)
```
