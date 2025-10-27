"""
Fine-tuning script cho mDeBERTa NLI model với dữ liệu tiếng Việt
Sử dụng dataset XNLI Vietnamese để cải thiện khả năng phát hiện mâu thuẫn
"""

import os
import pandas as pd
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix


# ============================================================================
# CONFIGURATION
# ============================================================================

class FineTuneConfig:
    """Cấu hình cho quá trình fine-tuning"""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_PATH = BASE_DIR / "data" / "contradictions_xnli_vi.csv"
    OUTPUT_DIR = BASE_DIR / "models" / "mdeberta-vi-nli-finetuned"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Model
    BASE_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
    
    # Labels mapping
    LABEL2ID = {"CONTRADICTION": 0, "NEUTRAL": 1, "ENTAILMENT": 2}
    ID2LABEL = {0: "CONTRADICTION", 1: "NEUTRAL", 2: "ENTAILMENT"}
    
    # Training parameters
    BATCH_SIZE = 16
    LEARNING_RATE = 2e-5
    NUM_EPOCHS = 3
    WARMUP_STEPS = 500
    WEIGHT_DECAY = 0.01
    MAX_LENGTH = 128
    
    # Data split
    TEST_SIZE = 0.2
    VAL_SIZE = 0.1  # From training set
    RANDOM_SEED = 42
    
    # Early stopping
    EARLY_STOPPING_PATIENCE = 3
    EARLY_STOPPING_THRESHOLD = 0.01


# ============================================================================
# DATA LOADING & PREPROCESSING
# ============================================================================

def load_and_preprocess_data(config: FineTuneConfig) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load và chia dataset thành train/val/test
    
    Returns:
        Tuple[train_df, val_df, test_df]
    """
    print(f"\n{'='*70}")
    print("LOADING DATA")
    print(f"{'='*70}")
    
    # Load CSV
    print(f"Loading data from: {config.DATA_PATH}")
    df = pd.read_csv(config.DATA_PATH)
    
    print(f"Total samples: {len(df)}")
    print(f"\nLabel distribution:")
    print(df['label'].value_counts())
    
    # Map labels to IDs
    df['label_id'] = df['label'].map(config.LABEL2ID)
    
    # Split train/test
    train_val_df, test_df = train_test_split(
        df, 
        test_size=config.TEST_SIZE, 
        random_state=config.RANDOM_SEED,
        stratify=df['label']
    )
    
    # Split train/val
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=config.VAL_SIZE,
        random_state=config.RANDOM_SEED,
        stratify=train_val_df['label']
    )
    
    print(f"\nData split:")
    print(f"  Train: {len(train_df)} samples")
    print(f"  Val:   {len(val_df)} samples")
    print(f"  Test:  {len(test_df)} samples")
    
    return train_df, val_df, test_df


def create_dataset(df: pd.DataFrame, tokenizer, config: FineTuneConfig) -> Dataset:
    """
    Tạo HuggingFace Dataset từ DataFrame
    """
    def tokenize_function(examples):
        return tokenizer(
            examples['text_a'],
            examples['text_b'],
            truncation=True,
            padding='max_length',
            max_length=config.MAX_LENGTH
        )
    
    # Convert to HuggingFace Dataset
    dataset = Dataset.from_pandas(df[['text_a', 'text_b', 'label_id']])
    dataset = dataset.rename_column('label_id', 'labels')
    
    # Tokenize
    dataset = dataset.map(tokenize_function, batched=True)
    dataset = dataset.remove_columns(['text_a', 'text_b'])
    dataset.set_format('torch')
    
    return dataset


# ============================================================================
# METRICS & EVALUATION
# ============================================================================

def compute_metrics(eval_pred) -> Dict:
    """
    Tính toán metrics cho evaluation
    """
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    # Accuracy
    accuracy = accuracy_score(labels, predictions)
    
    # Precision, Recall, F1
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average='weighted'
    )
    
    # Per-class metrics
    precision_per_class, recall_per_class, f1_per_class, _ = precision_recall_fscore_support(
        labels, predictions, average=None
    )
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'contradiction_f1': f1_per_class[0],
        'neutral_f1': f1_per_class[1],
        'entailment_f1': f1_per_class[2],
    }


def print_evaluation_report(trainer: Trainer, test_dataset: Dataset, config: FineTuneConfig):
    """
    In báo cáo chi tiết về evaluation
    """
    print(f"\n{'='*70}")
    print("EVALUATION ON TEST SET")
    print(f"{'='*70}")
    
    # Predict
    predictions = trainer.predict(test_dataset)
    pred_labels = np.argmax(predictions.predictions, axis=1)
    true_labels = predictions.label_ids
    
    # Metrics
    print("\nMetrics:")
    for key, value in predictions.metrics.items():
        if key.startswith('test_'):
            print(f"  {key.replace('test_', '')}: {value:.4f}")
    
    # Confusion Matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(true_labels, pred_labels)
    print("            Pred:")
    print("           ", "  ".join([f"{config.ID2LABEL[i][:4]:>6}" for i in range(3)]))
    for i, row in enumerate(cm):
        print(f"True {config.ID2LABEL[i][:4]:>6}:", "  ".join([f"{val:>6}" for val in row]))
    
    # Per-class accuracy
    print("\nPer-class Accuracy:")
    for i in range(3):
        class_acc = cm[i, i] / cm[i].sum() if cm[i].sum() > 0 else 0
        print(f"  {config.ID2LABEL[i]}: {class_acc:.4f}")


# ============================================================================
# TRAINING
# ============================================================================

def train_model(config: FineTuneConfig):
    """
    Main training function
    """
    print(f"\n{'='*70}")
    print("FINE-TUNING mDeBERTa FOR VIETNAMESE NLI")
    print(f"{'='*70}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create directories
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    train_df, val_df, test_df = load_and_preprocess_data(config)
    
    # Load tokenizer and model
    print(f"\n{'='*70}")
    print("LOADING MODEL")
    print(f"{'='*70}")
    print(f"Base model: {config.BASE_MODEL}")
    
    tokenizer = AutoTokenizer.from_pretrained(config.BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        config.BASE_MODEL,
        num_labels=3,
        id2label=config.ID2LABEL,
        label2id=config.LABEL2ID
    )
    
    # Create datasets
    print(f"\n{'='*70}")
    print("PREPARING DATASETS")
    print(f"{'='*70}")
    
    train_dataset = create_dataset(train_df, tokenizer, config)
    val_dataset = create_dataset(val_df, tokenizer, config)
    test_dataset = create_dataset(test_df, tokenizer, config)
    
    print(f"Train dataset: {len(train_dataset)} samples")
    print(f"Val dataset: {len(val_dataset)} samples")
    print(f"Test dataset: {len(test_dataset)} samples")
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(config.OUTPUT_DIR),
        num_train_epochs=config.NUM_EPOCHS,
        per_device_train_batch_size=config.BATCH_SIZE,
        per_device_eval_batch_size=config.BATCH_SIZE,
        learning_rate=config.LEARNING_RATE,
        warmup_steps=config.WARMUP_STEPS,
        weight_decay=config.WEIGHT_DECAY,
        logging_dir=str(config.LOGS_DIR),
        logging_steps=100,
        eval_strategy="steps",
        eval_steps=500,
        save_strategy="steps",
        save_steps=500,
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        push_to_hub=False,
        report_to="none",  # Disable wandb/tensorboard
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[
            EarlyStoppingCallback(
                early_stopping_patience=config.EARLY_STOPPING_PATIENCE,
                early_stopping_threshold=config.EARLY_STOPPING_THRESHOLD
            )
        ]
    )
    
    # Train
    print(f"\n{'='*70}")
    print("TRAINING")
    print(f"{'='*70}")
    print(f"Device: {training_args.device}")
    print(f"Batch size: {config.BATCH_SIZE}")
    print(f"Learning rate: {config.LEARNING_RATE}")
    print(f"Epochs: {config.NUM_EPOCHS}")
    print(f"\nStarting training...")
    
    trainer.train()
    
    # Evaluate on test set
    print_evaluation_report(trainer, test_dataset, config)
    
    # Save model
    print(f"\n{'='*70}")
    print("SAVING MODEL")
    print(f"{'='*70}")
    
    final_model_path = config.OUTPUT_DIR / "final"
    trainer.save_model(str(final_model_path))
    tokenizer.save_pretrained(str(final_model_path))
    
    print(f"Model saved to: {final_model_path}")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    config = FineTuneConfig()
    
    # Check CUDA
    if torch.cuda.is_available():
        print(f"CUDA available: {torch.cuda.get_device_name(0)}")
        print(f"CUDA version: {torch.version.cuda}")
    else:
        print("CUDA not available. Training on CPU (will be slow!)")
    
    # Train
    train_model(config)
