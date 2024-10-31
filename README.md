# sales-chatbot
 a chatbot built on BERT from Google and flask. 
 ![image](https://github.com/user-attachments/assets/bcdcd937-1680-44f3-a413-95ac971626db)

## usage:
steps to replicate:
1. run the notebook to train and rebuild the model.
2. the required packages should be in the notebook if not install requirments.txt
3. ```
   # make sure you're in the right directory
   cd  sales-chatbot
   ```
4. ```
   #run the app
   python app.py  
   ```

## other:
### models:
1. bert-base-uncased (BertForSequenceClassification) for response category prediction.
2. all-MiniLM-L6-v2 (SentenceTransformer) for semantic search.

### dataset:
- [goendalf666/sales-conversations](https://huggingface.co/datasets/goendalf666/sales-conversations)

# DEMO 
- [video](https://drive.google.com/file/d/1wlPwvtLfGfF-v8KR9NLjVRFK_EofYne2/view?usp=sharing)
