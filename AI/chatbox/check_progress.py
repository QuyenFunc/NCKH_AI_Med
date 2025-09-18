#!/usr/bin/env python3
import pickle
import os

def check_progress():
    """Kiểm tra progress hiện tại"""
    progress_file = os.path.join('data', 'mms_entities_progress.pkl')
    
    if not os.path.exists(progress_file):
        print('❌ Không tìm thấy progress file')
        return
    
    with open(progress_file, 'rb') as f:
        progress_data = pickle.load(f)
    
    seen_uris = progress_data.get('seen_uris', set())
    all_entities = progress_data.get('all_entities', [])
    
    print('📊 Progress hiện tại:')
    print(f'   - Đã xử lý: {len(seen_uris)} URIs')
    print(f'   - Tổng entities: {len(all_entities)}')
    print(f'   - Last update: {progress_data.get("last_update", "N/A")}')
    
    # Kiểm tra xem có entities nào có children chưa được xử lý không
    unprocessed_children = 0
    max_depth = 0
    
    for entity in all_entities:
        entity_data = entity.get('data', {})
        depth = entity.get('depth', 0)
        max_depth = max(max_depth, depth)
        
        if 'child' in entity_data:
            for child_uri in entity_data['child']:
                if child_uri not in seen_uris:
                    unprocessed_children += 1
    
    print(f'   - Max depth đã xử lý: {max_depth}')
    print(f'   - Children chưa xử lý: {unprocessed_children}')
    
    # Kiểm tra một vài entities gần đây
    if all_entities:
        print('\n🔍 Một vài entities gần đây:')
        for i, entity in enumerate(all_entities[-3:], 1):
            title = entity.get('data', {}).get('title', {}).get('@value', 'Unknown')
            depth = entity.get('depth', 0)
            print(f'   {i}. {title} (depth: {depth})')

if __name__ == "__main__":
    check_progress()
