from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
import joblib
import os
import time

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False


class ModelFactory:
    """Factory class to create, train, save and load ML models."""

    AVAILABLE_ALGORITHMS = [
        "Logistic Regression",
        "Random Forest",
        "XGBoost",
        "SVM",
    ]

    def __init__(self):
        self.models = {}
        self.current_model = None
        self.model_name = ""
        self.training_history = {}  # Store metrics per model

    def get_model(self, algorithm_name):
        if algorithm_name == "Logistic Regression":
            return LogisticRegression(max_iter=1000, C=1.0, solver='lbfgs')
        elif algorithm_name == "Random Forest":
            return RandomForestClassifier(n_estimators=200, max_depth=30, random_state=42, n_jobs=-1)
        elif algorithm_name == "XGBoost":
            if HAS_XGBOOST:
                return XGBClassifier(
                    use_label_encoder=False, eval_metric='mlogloss',
                    n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42
                )
            else:
                print("[ModelFactory] XGBoost not installed, falling back to GradientBoosting")
                return GradientBoostingClassifier(n_estimators=200, max_depth=6, random_state=42)
        elif algorithm_name == "SVM":
            return SVC(probability=True, kernel='linear', C=1.0)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")

    def train_model(self, X, y, algorithm_name, test_size=0.2):
        """Trains a model and returns the model, X_test, y_test, y_pred."""
        self.model_name = algorithm_name
        model = self.get_model(algorithm_name)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"[ModelFactory] Training {algorithm_name} on {X_train.shape[0]} samples...")
        start_time = time.time()
        model.fit(X_train, y_train)
        elapsed = time.time() - start_time
        print(f"[ModelFactory] {algorithm_name} trained in {elapsed:.2f}s")
        
        y_pred = model.predict(X_test)
        
        self.current_model = model
        self.models[algorithm_name] = model
        self.save_model(algorithm_name)
        
        return model, X_test, y_test, y_pred

    def save_model(self, name):
        os.makedirs("models", exist_ok=True)
        if self.current_model:
            path = os.path.join("models", f"{name.replace(' ', '_').lower()}.pkl")
            joblib.dump(self.current_model, path)
            print(f"[ModelFactory] Model saved to {path}")
            
    def load_model(self, name):
        path = os.path.join("models", f"{name.replace(' ', '_').lower()}.pkl")
        if os.path.exists(path):
            self.current_model = joblib.load(path)
            self.model_name = name
            self.models[name] = self.current_model
            return self.current_model
        return None

    def predict(self, vectorizer_input):
        if self.current_model:
            return self.current_model.predict(vectorizer_input)
        return None
    
    def predict_proba(self, vectorizer_input):
        if self.current_model and hasattr(self.current_model, "predict_proba"):
            return self.current_model.predict_proba(vectorizer_input)
        return None
