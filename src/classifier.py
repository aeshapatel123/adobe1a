import pickle

class HeadingClassifier:
    def __init__(self, model_path):
        # Load the trained XGBoost model from pickle file
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    def predict(self, features):
        # Map numeric class back to label
        label_map = {0: "BODY", 1: "TITLE", 2: "H1", 3: "H2", 4: "H3"}
        return label_map[self.model.predict([features])[0]]
