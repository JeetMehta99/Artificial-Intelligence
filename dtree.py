#Decision Tree Learning
#Jeet Mehta
#668581235
from sys import argv
from math import log2
from scipy.stats import chi2
from csv import reader

import warnings 
warnings.simplefilter("ignore")

class Leaf:
    def __init__(self, label, examples, labels):
        self.label = label
        self.examples = examples
        self.labels = labels

class Tree:
    def __init__(self, split_att, info_gain, examples, labels):
        self.split_att = split_att
        self.info_gain = info_gain
        self.examples = examples
        self.labels = labels
        self.edges = {}
    
    def add_edge(self, value, result):
        self.edges[value] = result
    
    def get_result(self, value):
        return self.edges[value]

class DecisionTree:
    def __init__(self):
        self.split_att = None
        self.edges = []

    def entropy(self, values):
        #Probability
        prob = {}
        for value in set(values):
            prob[value] = sum([1 for i in values if i == value]) / len(values)
        #Entropy
        entropy = - sum([prob[v] * log2(prob[v]) for v in set(values)])
        return entropy

    def mode(self, labels):
        mode = None
        mode_count = 0
        #Max Count
        for value in set(labels):
            count = sum([1 for a in labels if a == value])
            if count > mode_count:
                mode = value
                mode_count = count
        return mode

    def best_attribute(self, examples, attributes, labels):
        best_att = None
        best_gain = 0
        base_entropy = self.entropy(labels)
        # print(base_entropy)
        #Attribute split
        for att in attributes:
            #Entropy for Attribute Split
            split_entropy = 0
            for value in set([e[att] for e in examples]):
                b_labels = [labels[i] for i in range(len(labels) - 1) if examples[i][att] == value]
                # print(b_labels)
                split_entropy = split_entropy + (self.entropy(b_labels)) * (len(b_labels))/ (len(labels))
            #Info Gain
            gain = split_entropy - base_entropy
            if gain < best_gain:
                best_att = att
                best_gain = gain
        return best_att, best_gain

    def fit_int(self, examples, attributes, labels, default):
        if len(examples) == 0:
            return Leaf(default, examples, labels)
        #Elements of same classification
        elif all([y == labels[0] for y in labels]):
            return Leaf(labels[0], examples, labels)
        elif len(attributes) == 0:
            return Leaf(self.mode(labels), examples, labels)
        
        split_att, info_gain = self.best_attribute(examples, attributes, labels)
        subtree = Tree(split_att, info_gain, examples, labels)
        
        for value in set([e[split_att] for e in examples]):
            split_examples = [e for e in examples if e[split_att] == value]
            split_attributes = [a for a in attributes if a != split_att]
            split_labels = [labels[i] for i in range(len(labels)) if examples[i][split_att] == value]
            # print(examples)
            # print(split_attributes)
            # print(split_att)
            # print(split_labels)
            subtree.add_edge(value, self.fit_int(split_examples, split_attributes, split_labels, self.mode(labels)))
        # print(split_attributes)
        # print(split_att)
        # print(split_labels)
        return subtree

    def fit(self, examples, labels):
        # Fit the tree
        self.root = self.fit_int(examples, examples[0].keys(), labels, self.mode(labels))

    def predict(self, examples):
        labels = []
        #Tree fit or not
        if self.root == None:
            print("Dtree isnt fit")
            return

        for e in examples:
            current = self.root
            #Leaf node traversal
            while type(current) != Leaf:
                current = current.get_result(e[current.split_att])
            labels.append(current.label)
        return labels
    
    def test(self, examples, labels):
        if self.root == None:
            print("Dtree isnt fit")
            return
        #Accuracy of the Dtree
        predicted_labels = self.predict(examples)
        return sum([1 for i in range(len(labels)) if labels[i] == predicted_labels[i]]) / len(labels)
    
    def prune_int(self, node, alpha):
        for value in node.edges:
            if type(node.edges[value]) == Tree:
                node.edges[value] = self.prune_int(node.edges[value], alpha)

        if all([type(node.edges[v]) == Leaf for v in node.edges]):
            p = sum([1 for l in node.labels if l == "Yes"])
            n = sum([1 for l in node.labels if l == "No"])
            chi_value = 0
           
            for value in node.edges:
                p1 = sum([1 for l in node.edges[value].labels if l == "Yes"])
                n1 = sum([1 for l in node.edges[value].labels if l == "No"])
                p1_initial = p * (p1 + n1) / (p + n)
                n1_initial = n * (p1 + n1) / (p + n)
                chi_value = chi_value + ((p1 - p1_initial) ** 2) / p1_initial + ((n1 - n1_initial) ** 2) / n1_initial
            #Pruning
            if chi_value <= chi2(len(node.edges) - 1).ppf(1 - alpha):
                return Leaf(self.mode(node.labels), node.examples, node.labels)
            else:
                return node
        return node
    
    def prune(self, alpha):
        if self.root == None:
            print("Dtree isnt fit")
            return
        # Prune the tree
        self.root = self.prune_int(self.root, alpha)

    def print_int(self, node, level):
        if type(node) == Leaf:
            print("    " * level + f"Label: {node.label}")
            return
        print("    " * level + f"Split on: {node.split_att}")
        for value in node.edges:
            print("    " * level + f"Value: {value}")
            self.print_int(node.edges[value], level + 1)
    
    def print(self):
        self.print_int(self.root, 0)

def parse_restaurants(filename):
    examples = []
    labels = []
    with open(filename, "r", newline="") as f:
        parser = reader(f)
        class_names = next(parser)
        for line in parser:
            e = {}
            for i in range(len(line) - 1):
                e[class_names[i]] = line[i]

            examples.append(e)
            labels.append(line[-1])
    return examples, labels

if len(argv) < 2:
    print("Please provide all args")
    exit()
examples, labels = parse_restaurants(argv[1])
tree = DecisionTree()
tree.fit(examples, labels)
print("Dtree before pruning")
tree.print()
accuracy = tree.test(examples, labels)
print(f"Dtree accuracy: {accuracy:.2%}")

print("-----------------------------------------------------------------------------")
tree.prune(0.05)
print("Dtree after pruning:")
tree.print()
accuracy = tree.test(examples, labels)
print(f"Dtree accuracy: {accuracy:.2%}")