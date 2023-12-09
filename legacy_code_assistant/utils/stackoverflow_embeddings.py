import json
import lzma
import xml.etree.ElementTree as ET
from collections import namedtuple
from typing import Mapping
import numpy as np
from tqdm import tqdm

ParamsTuple = namedtuple('ParamsTuple', ['stack_posts_path', 'stack_meta_path', 'vecs_path',
                                         'min_techs_in_question'])


def questions_iter(file):
    context = ET.iterparse(file, events=("start", "end"))
    context = iter(context)
    event, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag == 'row' and elem.attrib['PostTypeId'] == '1':
            tags = elem.attrib['Tags'][1:].replace('>', '').split('<')
            yield elem.attrib['CreationDate'], tags
            root.clear()


def create_question_vecs(params):
    with open(params.stack_meta_path, 'r') as f_obj:
        metadata = json.load(f_obj)
    questions_list = []
    with tqdm(total=metadata['questions_count']) as pbar:
        with lzma.open(params.stack_posts_path) as fin:
            for question_ttl, question_tgs in questions_iter(fin):
                questions_list.append(question_ttl)
                pbar.update(1)
    with open(params.vecs_path, 'w') as f_obj:
        json.dump({'data': questions_list}, f_obj)


def get_vecs_from_file(path: str) -> Mapping:
    with open(path, 'r') as file_obj:
        vecs = json.load(file_obj)
    return vecs


def store_embeddings_to_file(index_faiss, path: str):
    faiss.write_index(index_faiss, path)


def derive_topics_from_vecs(path_vecs: str, path_embeddings: str, dimensions: int) -> None:
    vecs = get_vecs_from_file(path_vecs)
    vecs_data = [vec for tech_ids in vecs['data'] for vec in tech_ids]
    index = faiss.IndexFlatL2(len(vecs_data[0]))
    vecs_data_faiss = np.asarray(vecs_data).astype('float32')
    index.add(vecs_data_faiss)
    store_embeddings_to_file(index, path_embeddings)
