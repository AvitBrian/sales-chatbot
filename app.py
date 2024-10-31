from flask import Flask, request, jsonify, render_template
from dataclasses import dataclass
from typing import List, Dict, Tuple
import torch
from transformers import AutoTokenizer, BertForSequenceClassification
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import re
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class ModelConfig:
    model_path: str = './saved_model'
    semantic_model_path: str = './sent_transf'
    label_mapping_path: str = './label_mapping.json'
    embeddings_path: str = './response_embeddings.npy'
    max_length: int = 512
    top_k: int = 5

class TextPreprocessor:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize input text."""
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

class ModelManager:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.label_mapping = self._load_label_mapping()
        self.bert_model = self._load_bert_model()
        self.tokenizer = self._load_tokenizer()
        self.semantic_model = self._load_semantic_model()
        self.response_embeddings = self._load_response_embeddings()

    def _load_label_mapping(self) -> Dict:
        with open(self.config.label_mapping_path, 'r') as file:
            return json.load(file)

    def _load_bert_model(self) -> BertForSequenceClassification:
        return BertForSequenceClassification.from_pretrained(self.config.model_path)

    def _load_tokenizer(self) -> AutoTokenizer:
        return AutoTokenizer.from_pretrained(self.config.model_path)

    def _load_semantic_model(self) -> SentenceTransformer:
        return SentenceTransformer(self.config.semantic_model_path)

    def _load_response_embeddings(self) -> np.ndarray:
        return np.load(self.config.embeddings_path)

class ResponsePredictor:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.preprocessor = TextPreprocessor()

    def semantic_search(self, query: str) -> List[Tuple[str, float]]:
        """Perform semantic search to find similar responses."""
        query_embedding = self.model_manager.semantic_model.encode([query])
        similarities = cosine_similarity(
            query_embedding, 
            self.model_manager.response_embeddings
        )[0]
        
        top_indices = similarities.argsort()[-self.model_manager.config.top_k:][::-1]
        return [
            (list(self.model_manager.label_mapping.keys())[i], similarities[i]) 
            for i in top_indices
        ]

    def predict_with_bert(self, text: str) -> str:
        """Get BERT model prediction."""
        inputs = self.model_manager.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=self.model_manager.config.max_length
        )

        with torch.no_grad():
            outputs = self.model_manager.bert_model(**inputs)
        
        predicted_class_id = torch.argmax(outputs.logits, dim=-1).item()
        return list(self.model_manager.label_mapping.keys())[
            list(self.model_manager.label_mapping.values()).index(predicted_class_id)
        ]

    def get_response(self, input_text: str) -> str:
        """Get final response using ensemble of BERT and semantic search."""
        cleaned_input = self.preprocessor.clean_text(input_text)
        bert_prediction = self.predict_with_bert(cleaned_input)
        semantic_results = self.semantic_search(cleaned_input)
        
        return bert_prediction if bert_prediction in [result[0] for result in semantic_results] \
            else semantic_results[0][0]

class ChatbotAPI:
    def __init__(self):
        self.config = ModelConfig()
        self.model_manager = ModelManager(self.config)
        self.predictor = ResponsePredictor(self.model_manager)
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/')
        def home():
            return render_template('chatbot.html')

        @self.app.route('/predict', methods=['POST'])
        def predict():
            try:
                data = request.json
                input_text = data.get('input')
                
                if not input_text:
                    return jsonify({'error': 'Invalid input'}), 400
                
                response = self.predictor.get_response(input_text)
                return jsonify({'response': response})
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def run(self, debug: bool = True):
        self.app.run(debug=debug)

if __name__ == '__main__':
    chatbot = ChatbotAPI()
    chatbot.run()