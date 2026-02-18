# 📊 수집된 데이터 형식 분석

## 현재 수집된 데이터 형식

### 우리 데이터 구조:
```json
{
  "text": "에어(골드) 어제 받아서 2일정도 써봤는데요, 진짜 리뷰 올려주신 내용 딱 그거임요...",
  "author": "@mountain_k",
  "like_count": 1,
  "video_title": "내가 산다는 마음으로 아이폰 17 시리즈...",
  "language": "ko",
  "conversion_direction": "iPhone_to_iPhone",
  "conversion_intensity": 1.0,
  "conversion_level": "completed",
  "conversion_description": "이미 전환 완료",
  "sentiment_analysis": {
    "sentiment": "positive",
    "confidence": 0.8
  }
}
```

---

## 제시된 두 가지 형식과의 비교

### 📋 형식 1: 구조화된 리뷰 형식
```json
{
  "id": "001",
  "date": "2024-10-15",
  "rating": 4,
  "prev_device": "iPhone 14",
  "new_device": "Galaxy S24",
  "category": "UI적응",
  "review": "처음엔 뒤로가기 버튼이 어색했는데...",
  "pain_points": ["제스처 차이", "설정 메뉴 구조"],
  "satisfaction": ["커스터마이징 자유도", "멀티태스킹"]
}
```

### 📄 형식 2: 서술형 가이드 형식
```
## UI/UX 적응 문제
- 제스처 내비게이션: iOS 스와이프 vs Android 뒤로가기 버튼
- 제어센터 위치: 위에서 내리기 vs 아래에서 올리기
...
```

---

## 🎯 결론: 우리 데이터는 **중간 형태**

### ✅ 현재 우리 데이터의 장점:
1. **자연스러운 사용자 목소리** - 실제 댓글 그대로
2. **전환 방향 명확** - conversion_direction
3. **전환 강도 정량화** - conversion_intensity (0.0~1.0)
4. **감성 분석 포함** - sentiment, confidence
5. **언어 구분** - ko/en
6. **좋아요 수** - 중요도/신뢰도 지표

### ❌ 부족한 부분:
1. **pain_points 구조화 안됨** - 댓글에서 추출 필요
2. **satisfaction 구조화 안됨** - 댓글에서 추출 필요
3. **category 세분화 안됨** - UI적응, 앱호환성 등
4. **rating 없음** - 만족도 점수
5. **구체적 전/후 기기 모델 미상세** - iPhone 14 → Galaxy S24 같은 정확한 모델명

---

## 💡 변환 전략

### 옵션 1: 형식 1로 변환 (구조화된 리뷰)
```json
{
  "id": "auto_generated",
  "date": "2025-09-20",
  "rating": "감성 분석 기반 자동 산출 (positive=5, neutral=3, negative=1)",
  "prev_device": "댓글에서 추출 (15프맥 → iPhone 15 Pro Max)",
  "new_device": "댓글에서 추출 (에어 골드 → iPhone 17 Air Gold)",
  "category": "키워드 기반 분류 (카메라, 디자인, 배터리 등)",
  "review": "원본 댓글 텍스트",
  "pain_points": "부정 키워드 추출 (시네마틱 안됨, 스피커 구림)",
  "satisfaction": "긍정 키워드 추출 (가볍고 얇음, 이쁨)"
}
```

### 옵션 2: 형식 2로 변환 (서술형 가이드)
- 댓글들을 카테고리별로 그룹화
- 공통 패턴 추출
- 가이드 문서 형태로 재구성

---

## 🔧 추천: 하이브리드 접근

### 1단계: 댓글에서 추가 정보 추출
```python
{
  # 기존 필드
  "text": "...",
  "conversion_direction": "iPhone_to_iPhone",
  "conversion_intensity": 1.0,
  
  # 추가 추출 필드
  "prev_device_model": "iPhone 15 Pro Max",  # 추출
  "new_device_model": "iPhone 17 Air",        # 추출
  "rating": 5,                                # 감성→점수 변환
  "pain_points": ["스피커 품질", "시네마틱 미지원"],  # 추출
  "satisfaction": ["가벼움", "얇음", "디자인"],      # 추출
  "categories": ["디자인", "성능", "배터리"]         # 추출
}
```

### 2단계: 카테고리별 가이드 생성
```
## UI/UX 적응 문제 (iPhone → Galaxy)
- 제스처 차이: "뒤로가기 버튼이 어색했는데..." (87명 언급)
- 앱 배치: "홈화면 구성이 달라서..." (53명 언급)
```

---

## 📊 현재 데이터 → 목표 형식 변환 필요 작업

1. **기기 모델명 정규화**
   - "15프맥" → "iPhone 15 Pro Max"
   - "플립7" → "Galaxy Z Flip 7"

2. **Pain Points 자동 추출**
   - 부정 감성 + 키워드 조합
   - "스피커 구림", "카메라 초점 못 잡음"

3. **Satisfaction 자동 추출**
   - 긍정 감성 + 키워드 조합
   - "가볍다", "디자인 이쁘다"

4. **카테고리 자동 분류**
   - 토픽 분석 결과 활용
   - "UI적응", "하드웨어", "앱호환성" 등

5. **Rating 산출**
   - positive → 5점
   - neutral → 3점
   - negative → 1-2점
   - conversion_intensity 가중치 적용

---

## 🎯 결론

### 현재 우리 데이터는:
✅ **원본 사용자 목소리** - 진정성 높음
✅ **전환 의도 정량화** - conversion_intensity
✅ **방향성 명확** - conversion_direction
✅ **감성 분석 완료** - sentiment
✅ **언어 구분** - ko/en

### 필요한 작업:
📌 **구조화 레이어 추가** - pain_points, satisfaction 추출
📌 **기기 모델명 정규화** - 표준 형식으로 변환
📌 **카테고리 자동 분류** - 토픽 기반
📌 **Rating 점수화** - 감성 → 1-5점 변환

### 최종 형식:
**형식 1 (구조화된 리뷰)에 더 가깝게 변환하되,**
**원본 댓글의 진정성은 유지하는 하이브리드 형식이 최적**

```json
{
  "id": "auto_001",
  "date": "2025-09-20",
  "rating": 5,
  "prev_device": "iPhone 15 Pro Max",
  "new_device": "iPhone 17 Air Gold",
  "conversion_direction": "iPhone_to_iPhone",
  "conversion_intensity": 1.0,
  "category": "디자인",
  "review": "에어(골드) 어제 받아서 2일정도 써봤는데요...",
  "pain_points": ["시네마틱 미지원", "스피커 품질"],
  "satisfaction": ["가벼움", "얇음", "디자인"],
  "language": "ko",
  "engagement": 1  // like_count
}
```

