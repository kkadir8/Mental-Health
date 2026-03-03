import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import os

# Valid mental health status labels
VALID_STATUSES = {
    'Normal', 'Depression', 'Suicidal', 'Anxiety',
    'Bipolar', 'Stress', 'Personality disorder'
}

class DataPipeline:
    def __init__(self, data_path="data/Combined Data.csv"):
        self.data_path = data_path
        self.df = None
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        self.label_encoder = LabelEncoder()
        
    def load_data(self):
        """Loads data from CSV handling potential errors."""
        if not os.path.exists(self.data_path):
            rel_path = os.path.join(os.getcwd(), self.data_path)
            if os.path.exists(rel_path):
                self.data_path = rel_path
            else:
                raise FileNotFoundError(f"Dataset not found at {self.data_path}")
                
        try:
            self.df = pd.read_csv(self.data_path)
            self.df.columns = self.df.columns.str.strip()
            
            # Drop auto-generated index columns
            unnamed_cols = [c for c in self.df.columns if c.startswith('Unnamed')]
            if unnamed_cols:
                self.df.drop(columns=unnamed_cols, inplace=True)
            
            # Validate required columns exist
            required_cols = ['statement', 'status']
            if not all(col in self.df.columns for col in required_cols):
                if len(self.df.columns) >= 2:
                    mapping = {self.df.columns[0]: 'statement', self.df.columns[-1]: 'status'}
                    self.df.rename(columns=mapping, inplace=True)
            
            # Data cleaning
            self.df.dropna(subset=['statement', 'status'], inplace=True)
            self.df['status'] = self.df['status'].str.strip().str.title()
            
            # Fix common variations
            status_mapping = {
                'Personality Disorder': 'Personality disorder',
            }
            self.df['status'] = self.df['status'].replace(status_mapping)
            
            # Keep only valid mental health labels
            self.df = self.df[self.df['status'].isin(VALID_STATUSES)].reset_index(drop=True)
            
            print(f"[DataPipeline] Loaded {len(self.df)} valid records with {self.df['status'].nunique()} classes")
            return self.df
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")

    def get_raw_data(self):
        if self.df is None:
            self.load_data()
        return self.df

    def preprocess(self):
        """Clean text and prepare X, y for training."""
        if self.df is None:
            self.load_data()
            
        def clean_text(text):
            text = str(text).lower()
            # Remove HTML entities
            text = re.sub(r'&[a-zA-Z#0-9]+;', ' ', text)
            # Remove URLs
            text = re.sub(r'http\S+|www\S+', '', text)
            # Remove special characters but keep apostrophes
            text = re.sub(r"[^a-zA-Z'\s]", '', text)
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text
            
        self.df['processed_text'] = self.df['statement'].apply(clean_text)
        
        # Remove rows with empty text after cleaning
        self.df = self.df[self.df['processed_text'].str.len() > 2].reset_index(drop=True)
        
        # Encoding Target
        y = self.label_encoder.fit_transform(self.df['status'])
        
        # Vectorization with TF-IDF
        X = self.vectorizer.fit_transform(self.df['processed_text'])
        
        print(f"[DataPipeline] Preprocessed: {X.shape[0]} samples, {X.shape[1]} features, {len(self.label_encoder.classes_)} classes")
        return X, y, self.label_encoder.classes_
        
    def get_class_distribution(self):
        if self.df is None:
            self.load_data()
        return self.df['status'].value_counts()
