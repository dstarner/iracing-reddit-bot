from textblob.classifiers import NaiveBayesClassifier
import yaml


class ResponseGenerator:
    """
    Using some very basic NLP principles and text parsing, this is designed to
    break down Reddit comments and generate (hopefully) inteligent responses
    """

    def __init__(self, training_file=None, training_data=None):
        if not training_file and not training_data:
            raise AssertionError('training_file or training_data must be passed to constructor')
        self.training_file = training_file

        # Training data ultimately needs to be a list of tuples of (phrase, label)
        training_data = training_data if training_data else self.__parse_yaml_data()
        self.classifier = NaiveBayesClassifier(training_data)

    def __parse_yaml_data(self):
        """Parse out the dataset from the given YAML file
        """
        if not self.training_file:
            raise AssertionError('cannot parse non-existant YAML file!')

        parsed_data = []
        with open(self.training_file, 'r') as f:
            data = yaml.safe_load(f)

        for label_block in data['training_data']:
            for entry in label_block['entries']:
                parsed_data.append((entry, label_block['label']))
        return parsed_data
