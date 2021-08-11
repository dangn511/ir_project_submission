import csv
from gensim.parsing.preprocessing import split_alphanum, strip_non_alphanum
import json
import os
import re
from tqdm import tqdm


def preprocess_document(document):
    '''
    Preprocess documents
    
    Args:
        document: String containing the document's text
    
    Returns:
        Preprocessed string
    '''
    document = re.sub(r'[^ -~]+', ' ', document) # replace characters that aren't printable ascii with a space
    # document = re.sub(r'[^\w\s]', '', document) # replace non-word characters (A-Z, 0-9, _) and non-whitespace characters with nothing
    document = strip_non_alphanum(document)
    document = split_alphanum(document) # didn't work???
    document = document.lower()
    return document


def tokenize_document(document, preprocess=False):
    '''
    Convert document to a list of tokens
    
    Args:
        document: String containing the document's text
        preprocess: Boolean indicating whether the document should be preprocessed
    
    Returns:
        List of tokens
    '''
    # document = document.replace('"', '""') # to escape the " in the csv # does not work satisfactorily
    
    if preprocess:
        document = preprocess_document(document)
    
    return document.split()


def read_json_file(data_file_path):
    '''
    Read .json file
    
    Args:
        data_file_path: File path of the .json file
    
    Returns:
        The JSON but in Python dictionary form
    '''
    if not data_file_path.lower().endswith('.json'):
        raise TypeError('The input file is not a .json file!')
    
    try:
        with open(data_file_path) as data_file:
            data = json.load(data_file)
        return data
    
    except FileNotFoundError:
        print('Please check your current working directory and/or file name and try again!')


def write_block_to_disk(postings_list, block_file_path):
    '''
    Write block (containing the sorted list of terms and the postings list itself) to disk
    
    Args:
        postings_list: Dictionary containing the terms and document IDs that contain those terms
        block_file_path: String representing the file path where the block will be saved
    
    Returns:
        nil
    '''
    alphabetical_list_of_words = [word for word in sorted(postings_list)] # word == dictionary key
    
    with open(block_file_path, 'w', encoding='utf-8') as block_file:
        for word in alphabetical_list_of_words:
            line = '"{}","{}"'.format(word, ' '.join(str(doc_id) for doc_id in postings_list[word])) # "word1","doc_id1 doc_id2 doc_id3"
            block_file.write(line + '\n')
        block_file.flush()
    
    return


def merge_blocks(block_file_paths, index_list_file_path):
    '''
    Merge postings lists
    
    Args:
        block_file_paths: List containing all the file paths of the blocks that were previously written
        index_list_file_path: String representing the file path where the overall index will be saved
    
    Returns:
        nil
    '''
    postings_lists = []
    
    for block_file_path in block_file_paths:
        with open(block_file_path) as block_file:
            for row in csv.reader(block_file): # [['word1', 'doc_id1 doc_id2 doc_id3'], ['word2', 'doc_id1 doc_id4'], ...]
                postings_lists.append(row)
    
    postings_lists.sort(key=lambda x: x[0]) # [['word1', 'doc_id1 doc_id2 doc_id3'], ['word2', 'doc_id1 doc_id4'], ...]
    
    previous_word = ''
    previous_doc_ids = ''
    
    with open(index_list_file_path, 'w', encoding='utf-8') as index_list_file:
        for postings_list in postings_lists:
            if postings_list[0] == previous_word:
                previous_doc_ids += ' ' + postings_list[1]
            else:
                if previous_word != '':
                    previous_doc_ids = ' '.join(list(set(previous_doc_ids.split())))
                    line = '"{}","{}"'.format(previous_word, previous_doc_ids) # "word1","doc_id1 doc_id2 doc_id3"
                    index_list_file.write(line + '\n')
                previous_word = postings_list[0]
                previous_doc_ids = postings_list[1]
    
    return


def construct_index(data_file_path, block_size=500, output_directory='postings-lists', block_file_prefix='block'):
    '''
    Run (slightly modified) SPIMI. A folder will be created to contain the posting lists.
    
    Args:
        data_file_path: File path of the file containing the documents to be indexed; our project's input is specifically a .json file and a TypeError will be raised if the input file is not a .json file
        block_size: Integer referring to the number of documents to be processed in a 'block' - using this instead of available memory
        output_directory: Directory where the postings lists will be saved. Directory will be created if it does not already exist.
        block_file_path: String for the prefix of each block's file path
    
    Returns:
        nil
    '''
    # Check input types
    if type(data_file_path) != str:
        raise TypeError('data_file_path must be a string.')
    if type(block_size) != int:
        raise TypeError('block_size must be an integer.')
    if type(output_directory) != str:
        raise TypeError('output_directory must be a string.')
    if type(block_file_prefix) != str:
        raise TypeError('block_file_prefix must be a string.')
    
    # Read the input file
    # Ideally should read doc by doc, but this file is small enough...
    # Will try to implement ijson.parse() to mimic reading doc by doc if I have the time
    data = read_json_file(data_file_path)
    
    # Create the output directory if it does not already exist
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    
    block_count = 0
    local_doc_count = 0
    postings_list = {}
    block_file_paths = []
    
    for key in tqdm(data.keys()):
        # Read the next document, tokenize (and preprocess) it, and update the postings list accordingly
        doc_id = data[key]['job_id']
        doc_text = tokenize_document(data[key]['job_description'], preprocess=True)
        
        for word in doc_text:
            if word not in postings_list:
                postings_list[word] = []
            if doc_id not in postings_list[word]:
                postings_list[word].append(doc_id)
        
        local_doc_count += 1
        # In place of 'free memory available'
        if local_doc_count == block_size:
            # Write the postings list to disk
            block_file_name = '{}_{}.csv'.format(block_file_prefix, block_count)
            block_file_path = os.path.join(output_directory, block_file_name)
            
            while os.path.isfile(block_file_path):
                continue_program = input('There is an existing file at {} and the program cannot write the postings list to the disk. Please move the file to another location or rename it, then enter "Y" or "y" to continue. Press any other key to exit the program: '.format(block_file_path))
                if continue_program not in ['Y', 'y']:
                    quit()
                else:
                    continue
            
            write_block_to_disk(postings_list, block_file_path)
            block_file_paths.append(block_file_path)
            
            block_count += 1
            
            local_doc_count = 0
            postings_list = {}
    
    # To catch the last partially-filled block
    if local_doc_count > 0:
        # Write the postings list to disk
        block_file_name = '{}_{}.csv'.format(block_file_prefix, block_count)
        block_file_path = os.path.join(output_directory, block_file_name)
        
        while os.path.isfile(block_file_path):
            continue_program = input('There is an existing file at {} and the program cannot write the postings list to the disk. Please move the file to another location or rename it, then enter "Y" or "y" to continue. Press any other key to exit the program: '.format(block_file_path))
            if continue_program not in ['Y', 'y']:
                quit()
            else:
                continue
        
        write_block_to_disk(postings_list, block_file_path)
        block_file_paths.append(block_file_path)
        
        block_count += 1
        
        postings_list = {}
    
    print('{} block(s) created'.format(block_count))
    
    # Merge the blocks
    merge_blocks(block_file_paths, os.path.join(output_directory, 'index_list.csv'))
    print('Postings lists merged')
    
    return


data_file_path = 'master_list_8k_cleaned.json'
construct_index(data_file_path)
