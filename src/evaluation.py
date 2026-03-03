from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, roc_curve, auc,
                             classification_report)
from sklearn.preprocessing import label_binarize
import numpy as np


class Evaluator:
    """Evaluation utilities for classification models."""

    @staticmethod
    def calculate_metrics(y_true, y_pred, average='weighted'):
        """Calculates standard classification metrics."""
        return {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average=average, zero_division=0),
            'recall': recall_score(y_true, y_pred, average=average, zero_division=0),
            'f1': f1_score(y_true, y_pred, average=average, zero_division=0)
        }
    
    @staticmethod
    def get_confusion_matrix(y_true, y_pred):
        return confusion_matrix(y_true, y_pred)

    @staticmethod
    def get_classification_report(y_true, y_pred, class_names=None):
        """Returns a formatted classification report string."""
        return classification_report(y_true, y_pred, target_names=class_names, zero_division=0)

    @staticmethod
    def get_roc_data(model, X_test, y_test, classes):
        """Calculates ROC curve points for multiclass."""
        try:
            y_score = model.predict_proba(X_test)
        except Exception:
            return None
            
        y_test_bin = label_binarize(y_test, classes=range(len(classes)))
        n_classes = y_test_bin.shape[1]
        
        roc_data = {}
        for i in range(n_classes):
            fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score[:, i])
            roc_auc = auc(fpr, tpr)
            roc_data[i] = {'fpr': fpr, 'tpr': tpr, 'auc': roc_auc}
            
        return roc_data
