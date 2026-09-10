import os
import sys
import re
import joblib
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

def norm(t):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', '', str(t).lower())).strip()

def run_leakage_audit():
    print("--- Running Rigorous Leakage Audit ---")
    df_gold = pd.read_csv('evaluation/golden_set.csv')
    df_train = pd.read_csv('data/processed/splits/train.csv')
    df_val = pd.read_csv('data/processed/splits/val.csv')
    idx_data = joblib.load('data/processed/retrieval_index.pkl')

    print(f"Golden set count: {len(df_gold)}")
    print(f"Train split count: {len(df_train)}")
    print(f"Val split count: {len(df_val)}")
    print(f"Retrieval index count: {len(idx_data['metadata'])}")

    train_texts = {}
    for c_id, raw_t in zip(df_train['conversation_id'], df_train['customer_text_raw']):
        n = norm(raw_t)
        if len(n) > 5 and n not in train_texts:
            train_texts[n] = (str(c_id), str(raw_t))

    val_texts = {}
    for c_id, raw_t in zip(df_val['conversation_id'], df_val['customer_text_raw']):
        n = norm(raw_t)
        if len(n) > 5 and n not in val_texts:
            val_texts[n] = (str(c_id), str(raw_t))

    retrieval_convs = set(str(m['conversation_id']) for m in idx_data['metadata'])
    retrieval_texts = {}
    for m in idx_data['metadata']:
        c_id = str(m.get('conversation_id', ''))
        raw_t = str(m.get('customer_text', ''))
        n = norm(raw_t)
        if len(n) > 5 and n not in retrieval_texts:
            retrieval_texts[n] = (c_id, raw_t)

    train_overlaps = []
    val_overlaps = []
    retrieval_conv_overlaps = []
    retrieval_text_overlaps = []

    for _, row in df_gold.iterrows():
        ex_id = str(row['example_id'])
        msg = str(row['customer_message'])
        conv_id = str(row.get('source_conversation_id', ''))
        n_msg = norm(msg)

        if n_msg in train_texts:
            c_id, match_text = train_texts[n_msg]
            train_overlaps.append({
                'example_id': ex_id,
                'golden_message': msg,
                'golden_conv': conv_id,
                'matched_conv': c_id,
                'matched_text': match_text
            })

        if n_msg in val_texts:
            c_id, match_text = val_texts[n_msg]
            val_overlaps.append({
                'example_id': ex_id,
                'golden_message': msg,
                'golden_conv': conv_id,
                'matched_conv': c_id,
                'matched_text': match_text
            })

        if conv_id in retrieval_convs:
            retrieval_conv_overlaps.append({
                'example_id': ex_id,
                'conversation_id': conv_id
            })

        if n_msg in retrieval_texts:
            c_id, match_text = retrieval_texts[n_msg]
            retrieval_text_overlaps.append({
                'example_id': ex_id,
                'golden_message': msg,
                'retrieval_conv': c_id,
                'retrieval_text': match_text
            })

    print(f"\n[LEAKAGE RESULTS]")
    print(f"Training overlap count: {len(train_overlaps)}")
    for item in train_overlaps:
        print(f"  Train Overlap: {item['example_id']} | Golden Conv: {item['golden_conv']} | Matched Conv: {item['matched_conv']}")
        print(f"    Golden Message: {item['golden_message']}")
        print(f"    Matched Train Text: {item['matched_text']}")

    print(f"\nTuning (Val) overlap count: {len(val_overlaps)}")
    for item in val_overlaps:
        print(f"  Val Overlap: {item['example_id']} | Golden Conv: {item['golden_conv']} | Matched Conv: {item['matched_conv']}")
        print(f"    Golden Message: {item['golden_message']}")
        print(f"    Matched Val Text: {item['matched_text']}")

    print(f"\nRetrieval index conversation ID overlap count: {len(retrieval_conv_overlaps)}")
    print(f"Retrieval index normalized text overlap count: {len(retrieval_text_overlaps)}")
    for item in retrieval_text_overlaps:
        print(f"  Retrieval Text Overlap: {item['example_id']} | Retrieval Conv: {item['retrieval_conv']}")
        print(f"    Golden Message: {item['golden_message']}")
        print(f"    Matched Retrieval Text: {item['retrieval_text']}")

    return {
        'training_overlap_count': len(train_overlaps),
        'training_overlaps': train_overlaps,
        'tuning_overlap_count': len(val_overlaps),
        'tuning_overlaps': val_overlaps,
        'retrieval_overlap_count': len(retrieval_text_overlaps),
        'retrieval_conv_overlap_count': len(retrieval_conv_overlaps),
    }

if __name__ == '__main__':
    run_leakage_audit()
