import pickle
import collections
person_number_dictionary_used_ID = collections.defaultdict(int)
with open('./person_number_dictionary_used_ID.pickle', 'wb') as f:
    pickle.dump(person_number_dictionary_used_ID, f)

