#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
댓글 데이터를 구조화된 리뷰 형식으로 변환
- pain_points 자동 추출
- satisfaction 자동 추출
- 기기 모델명 정규화
- 카테고리 자동 분류
- Rating 점수화
"""

import json
import re
from datetime import datetime
from collections import defaultdict, Counter

class StructuredReviewConverter:
    def __init__(self):
        """변환기 초기화"""
        
        # 기기 모델명 정규화 매핑
        self.device_normalization = {
            # iPhone
            r'아이폰\s*17\s*프로\s*맥스|17\s*프로맥스|17프맥|17pm': 'iPhone 17 Pro Max',
            r'아이폰\s*17\s*프로|17프로': 'iPhone 17 Pro',
            r'아이폰\s*17|17일반|17기본': 'iPhone 17',
            r'아이폰\s*에어|에어': 'iPhone 17 Air',
            r'아이폰\s*16\s*프로\s*맥스|16\s*프로맥스|16프맥': 'iPhone 16 Pro Max',
            r'아이폰\s*16\s*프로|16프로': 'iPhone 16 Pro',
            r'아이폰\s*16|16': 'iPhone 16',
            r'아이폰\s*15\s*프로\s*맥스|15\s*프로맥스|15프맥': 'iPhone 15 Pro Max',
            r'아이폰\s*15\s*프로|15프로': 'iPhone 15 Pro',
            r'아이폰\s*15': 'iPhone 15',
            r'아이폰\s*14': 'iPhone 14',
            r'아이폰\s*13': 'iPhone 13',
            r'아이폰\s*12': 'iPhone 12',
            
            # Galaxy
            r'갤럭시\s*z\s*폴드\s*7|폴드\s*7|폴드7|z\s*fold\s*7': 'Galaxy Z Fold 7',
            r'갤럭시\s*z\s*플립\s*7|플립\s*7|플립7|z\s*flip\s*7': 'Galaxy Z Flip 7',
            r'갤럭시\s*z\s*폴드\s*6|폴드\s*6|폴드6': 'Galaxy Z Fold 6',
            r'갤럭시\s*z\s*플립\s*6|플립\s*6|플립6': 'Galaxy Z Flip 6',
            r'갤럭시\s*s25\s*울트라|s25\s*울트라|s25울트라': 'Galaxy S25 Ultra',
            r'갤럭시\s*s25|s25': 'Galaxy S25',
            r'갤럭시\s*s24\s*울트라|s24\s*울트라': 'Galaxy S24 Ultra',
            r'갤럭시\s*s24|s24': 'Galaxy S24',
        }
        
        # Pain Points 키워드 (부정적 언급)
        self.pain_keywords = {
            'UI적응': ['익숙.*?않', '어색', '불편', '복잡', '헷갈', 'confusing', 'awkward', 'uncomfortable'],
            '데이터이전': ['이전', '옮기', '백업', '복원', 'transfer', 'migration', 'backup'],
            '앱호환성': ['앱.*?없', '앱.*?안됨', '호환', 'app.*?not', 'compatibility'],
            '생태계단절': ['워치', '에어팟', '맥북', '아이패드', '연동.*?안', 'watch', 'airpods', 'ecosystem'],
            '스피커품질': ['스피커.*?별로', '스피커.*?구리', '스피커.*?나쁨', '모노', 'speaker.*?bad', 'mono'],
            '카메라': ['카메라.*?별로', '사진.*?안좋', '초점', 'camera.*?bad', 'focus'],
            '배터리': ['배터리.*?짧', '방전', '조루', 'battery.*?bad', 'drain'],
            '발열': ['발열', '뜨겁', '열나', 'heating', 'hot', 'warm'],
            '내구성': ['고장', '깨짐', '부서', '약함', 'broken', 'fragile', 'crack'],
            '가격': ['비싸', '가격.*?부담', 'expensive', 'costly', 'overpriced'],
            '성능': ['느리', '버벅', '렉', 'slow', 'lag', 'sluggish'],
            '크림주름': ['주름', '크림', '접힘자국', 'crease', 'fold mark'],
            'S펜제거': ['s펜', '펜.*?없', 'spen', 'pen.*?removed', 'no.*?pen'],
        }
        
        # Satisfaction 키워드 (긍정적 언급)
        self.satisfaction_keywords = {
            '디자인': ['예쁘', '이쁘', '멋있', '세련', '고급', 'beautiful', 'gorgeous', 'elegant'],
            '가벼움': ['가볍', '얇', 'light', 'thin', 'slim'],
            '화면': ['화면.*?좋', '디스플레이.*?좋', 'screen.*?good', 'display.*?good'],
            '성능': ['빠르', '부드럽', '성능.*?좋', 'fast', 'smooth', 'performance.*?good'],
            '카메라': ['카메라.*?좋', '사진.*?좋', 'camera.*?good', 'photo.*?good'],
            '배터리': ['배터리.*?좋', '오래.*?가', 'battery.*?good', 'long.*?battery'],
            '폴더블': ['폴더블', '접는', '펼치는', '신세계', 'foldable', 'fold', 'flip'],
            '생태계': ['연동', '동기화', '편해', 'ecosystem', 'integration', 'seamless'],
            '커스터마이징': ['커스터마이징', '자유', '설정', 'customization', 'freedom', 'flexible'],
            '삼성페이': ['삼성페이', '교통카드', '간편결제', 'samsung pay', 'payment'],
            '가성비': ['가성비', '합리적', '저렴', 'value', 'affordable', 'reasonable'],
        }
        
        # 카테고리 분류
        self.categories = {
            'UI적응': ['UI', '인터페이스', '제스처', '조작', '설정'],
            '하드웨어': ['디자인', '무게', '크기', '두께', '색상'],
            '성능': ['속도', '성능', '프로세서', '칩셋', '게임'],
            '카메라': ['카메라', '사진', '촬영', '화질'],
            '배터리': ['배터리', '충전', '방전'],
            '앱호환성': ['앱', '프로그램', '소프트웨어'],
            '생태계': ['생태계', '연동', '동기화', '워치', '에어팟'],
            '데이터이전': ['이전', '옮기기', '백업'],
            '가격': ['가격', '비용', '할인'],
        }

    def normalize_device_name(self, text):
        """기기 이름 정규화"""
        text_lower = text.lower()
        
        for pattern, normalized in self.device_normalization.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return normalized
        
        return None

    def extract_device_models(self, text, conversion_direction):
        """전/후 기기 모델 추출"""
        prev_device = None
        new_device = None
        
        # 전환 방향에 따라 기본값 설정
        if conversion_direction == 'iPhone_to_iPhone':
            prev_device = 'iPhone (구형)'
            new_device = 'iPhone (신형)'
        elif conversion_direction == 'Galaxy_to_Galaxy':
            prev_device = 'Galaxy (구형)'
            new_device = 'Galaxy (신형)'
        elif conversion_direction == 'iPhone_to_Galaxy':
            prev_device = 'iPhone'
            new_device = 'Galaxy'
        elif conversion_direction == 'Galaxy_to_iPhone':
            prev_device = 'Galaxy'
            new_device = 'iPhone'
        
        # 텍스트에서 구체적 모델명 추출
        text_lower = text.lower()
        
        # "X에서 Y로" 패턴
        transition_patterns = [
            r'(\w+)\s*에서\s*(\w+)\s*(?:로|으로)',
            r'from\s+(\w+.*?)\s+to\s+(\w+)',
            r'(\w+)\s*쓰다가\s*(\w+)',
        ]
        
        for pattern in transition_patterns:
            match = re.search(pattern, text_lower)
            if match:
                prev_candidate = self.normalize_device_name(match.group(1))
                new_candidate = self.normalize_device_name(match.group(2))
                if prev_candidate:
                    prev_device = prev_candidate
                if new_candidate:
                    new_device = new_candidate
        
        # 단일 모델명 추출 (새 기기)
        for pattern, normalized in self.device_normalization.items():
            if re.search(pattern, text_lower):
                if conversion_direction in ['iPhone_to_iPhone', 'Galaxy_to_iPhone']:
                    if 'iPhone' in normalized:
                        new_device = normalized
                elif conversion_direction in ['Galaxy_to_Galaxy', 'iPhone_to_Galaxy']:
                    if 'Galaxy' in normalized:
                        new_device = normalized
                break
        
        return prev_device, new_device

    def extract_pain_points(self, text, sentiment):
        """Pain Points 추출"""
        if sentiment == 'positive':
            return []
        
        text_lower = text.lower()
        pain_points = []
        
        for category, keywords in self.pain_keywords.items():
            for keyword in keywords:
                if re.search(keyword, text_lower, re.IGNORECASE):
                    if category not in pain_points:
                        pain_points.append(category)
                    break
        
        return pain_points

    def extract_satisfaction(self, text, sentiment):
        """Satisfaction 추출"""
        if sentiment == 'negative':
            return []
        
        text_lower = text.lower()
        satisfactions = []
        
        for category, keywords in self.satisfaction_keywords.items():
            for keyword in keywords:
                if re.search(keyword, text_lower, re.IGNORECASE):
                    if category not in satisfactions:
                        satisfactions.append(category)
                    break
        
        return satisfactions

    def classify_category(self, text):
        """카테고리 분류"""
        text_lower = text.lower()
        category_scores = defaultdict(int)
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    category_scores[category] += 1
        
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return '일반'

    def sentiment_to_rating(self, sentiment, conversion_intensity):
        """감성 → Rating 변환 (1-5점)"""
        base_rating = {
            'positive': 5,
            'neutral': 3,
            'negative': 2
        }.get(sentiment, 3)
        
        # 전환 강도로 조정 (완료됐으면 만족도 높음)
        if conversion_intensity >= 0.8:
            base_rating = min(5, base_rating + 1)
        elif conversion_intensity <= 0.2:
            base_rating = max(1, base_rating - 1)
        
        return base_rating

    def convert_comment(self, comment, idx):
        """댓글 하나를 구조화된 리뷰로 변환"""
        text = comment.get('text', '')
        sentiment = comment.get('sentiment_analysis', {}).get('sentiment', 'neutral') if isinstance(comment.get('sentiment_analysis'), dict) else 'neutral'
        
        # 전환 정보 (있는 경우)
        conversion_direction = comment.get('conversion_direction', 'N/A')
        conversion_intensity = comment.get('conversion_intensity', 0.0)
        conversion_level = comment.get('conversion_level', 'N/A')
        
        # 기기 모델 추출
        prev_device, new_device = self.extract_device_models(text, conversion_direction)
        
        # Pain Points & Satisfaction 추출
        pain_points = self.extract_pain_points(text, sentiment)
        satisfaction = self.extract_satisfaction(text, sentiment)
        
        # 카테고리 분류
        category = self.classify_category(text)
        
        # Rating 산출
        rating = self.sentiment_to_rating(sentiment, conversion_intensity)
        
        # 날짜 추출
        published_at = comment.get('published_at', '')
        date = published_at.split('T')[0] if published_at else datetime.now().strftime('%Y-%m-%d')
        
        structured_review = {
            'id': f"review_{idx:06d}",
            'date': date,
            'rating': rating,
            'prev_device': prev_device,
            'new_device': new_device,
            'conversion_direction': conversion_direction,
            'conversion_intensity': conversion_intensity,
            'conversion_level': conversion_level,
            'category': category,
            'review': text,
            'pain_points': pain_points,
            'satisfaction': satisfaction,
            'language': comment.get('language', 'unknown'),
            'engagement': comment.get('like_count', 0),
            'author': comment.get('author', ''),
            'video_title': comment.get('video_title', ''),
            'sentiment': sentiment
        }
        
        return structured_review

    def convert_dataset(self, comments):
        """전체 데이터셋 변환"""
        structured_reviews = []
        
        for idx, comment in enumerate(comments, 1):
            structured = self.convert_comment(comment, idx)
            structured_reviews.append(structured)
        
        return structured_reviews

def main():
    """메인 실행 함수"""
    print("🚀 구조화된 리뷰 형식으로 변환 시작...")
    
    # 데이터 로드
    print("📂 데이터 로드 중...")
    with open("data/precise_conversion_scores_20251020_220539.json", 'r', encoding='utf-8') as f:
        conversion_data = json.load(f)
    
    converter = StructuredReviewConverter()
    
    # iPhone 데이터 변환
    print("📱 iPhone 댓글 변환 중...")
    iphone_comments = conversion_data['iphone']['conversion_comments']
    iphone_reviews = converter.convert_dataset(iphone_comments)
    print(f"   변환 완료: {len(iphone_reviews)}개")
    
    # Galaxy 데이터 변환
    print("📱 Galaxy 댓글 변환 중...")
    galaxy_comments = conversion_data['galaxy']['conversion_comments']
    galaxy_reviews = converter.convert_dataset(galaxy_comments)
    print(f"   변환 완료: {len(galaxy_reviews)}개")
    
    # 결과 저장
    output = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'conversion_method': 'automated_structure_extraction',
            'total_reviews': len(iphone_reviews) + len(galaxy_reviews)
        },
        'iphone_reviews': iphone_reviews,
        'galaxy_reviews': galaxy_reviews
    }
    
    output_file = f"data/structured_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 샘플 출력
    print("\n" + "="*80)
    print("📊 변환 결과 샘플 (iPhone)")
    print("="*80)
    
    for review in iphone_reviews[:3]:
        print(f"\n{'='*80}")
        print(f"ID: {review['id']}")
        print(f"날짜: {review['date']}")
        print(f"Rating: {review['rating']}/5")
        print(f"전환: {review['prev_device']} → {review['new_device']}")
        print(f"방향: {review['conversion_direction']}")
        print(f"강도: {review['conversion_intensity']} ({review['conversion_level']})")
        print(f"카테고리: {review['category']}")
        print(f"언어: {review['language']}")
        print(f"좋아요: {review['engagement']}개")
        print(f"\nPain Points: {review['pain_points']}")
        print(f"Satisfaction: {review['satisfaction']}")
        print(f"\n리뷰: {review['review'][:150]}...")
    
    print("\n" + "="*80)
    print("📊 변환 결과 샘플 (Galaxy)")
    print("="*80)
    
    for review in galaxy_reviews[:3]:
        print(f"\n{'='*80}")
        print(f"ID: {review['id']}")
        print(f"날짜: {review['date']}")
        print(f"Rating: {review['rating']}/5")
        print(f"전환: {review['prev_device']} → {review['new_device']}")
        print(f"방향: {review['conversion_direction']}")
        print(f"강도: {review['conversion_intensity']} ({review['conversion_level']})")
        print(f"카테고리: {review['category']}")
        print(f"언어: {review['language']}")
        print(f"좋아요: {review['engagement']}개")
        print(f"\nPain Points: {review['pain_points']}")
        print(f"Satisfaction: {review['satisfaction']}")
        print(f"\n리뷰: {review['review'][:150]}...")
    
    # 통계 출력
    print("\n\n" + "="*80)
    print("📊 변환 통계")
    print("="*80)
    
    # Rating 분포
    iphone_ratings = Counter(r['rating'] for r in iphone_reviews)
    galaxy_ratings = Counter(r['rating'] for r in galaxy_reviews)
    
    print(f"\n📱 iPhone Rating 분포:")
    for rating in sorted(iphone_ratings.keys(), reverse=True):
        count = iphone_ratings[rating]
        pct = count / len(iphone_reviews) * 100
        print(f"   {rating}점: {count}개 ({pct:.1f}%)")
    
    print(f"\n📱 Galaxy Rating 분포:")
    for rating in sorted(galaxy_ratings.keys(), reverse=True):
        count = galaxy_ratings[rating]
        pct = count / len(galaxy_reviews) * 100
        print(f"   {rating}점: {count}개 ({pct:.1f}%)")
    
    # 카테고리 분포
    iphone_categories = Counter(r['category'] for r in iphone_reviews)
    galaxy_categories = Counter(r['category'] for r in galaxy_reviews)
    
    print(f"\n📱 iPhone 카테고리 분포:")
    for category, count in iphone_categories.most_common(5):
        pct = count / len(iphone_reviews) * 100
        print(f"   {category}: {count}개 ({pct:.1f}%)")
    
    print(f"\n📱 Galaxy 카테고리 분포:")
    for category, count in galaxy_categories.most_common(5):
        pct = count / len(galaxy_reviews) * 100
        print(f"   {category}: {count}개 ({pct:.1f}%)")
    
    print(f"\n💾 저장 완료: {output_file}")

if __name__ == "__main__":
    main()

